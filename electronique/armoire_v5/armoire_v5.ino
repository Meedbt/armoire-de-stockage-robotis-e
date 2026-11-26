// =====================================================================
//  Armoire automatisée V5 - programme de l'ESP32
//
//  Carte à choisir dans l'IDE Arduino : "ESP32 Dev Module"
//  (paquet "esp32" by Espressif Systems, version 2.x ou 3.x)
//  Bibliothèque à installer : "ESP32Servo" (Kevin Harrington)
//
//  Une fois téléversé : se connecter au Wi-Fi "Armoire-V5"
//  (mot de passe dans config.h) puis ouvrir http://192.168.4.1
// =====================================================================
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include <ESP32Servo.h>
#include "config.h"
#include "page.h"

// ---------------------------------------------------------------------
//  Numérotation
//  Servos : 0 = X arrière, 1 = X nacelle, 2 = Z, 3 = poussoir.
//  Le fin de course n° i correspond au servo n° i.
//  Cases : n = rangée * 3 + colonne, rangée 0 = en bas, colonne 0 = à gauche.
//  Sens "+" : X vers la droite (loin de l'origine), Z vers le haut,
//             poussoir vers les boîtes.
// ---------------------------------------------------------------------
enum { S_XAR = 0, S_XNA = 1, S_Z = 2, S_POU = 3 };
const uint8_t PIN_SERVO[4] = {PIN_SERVO_XAR, PIN_SERVO_XNA, PIN_SERVO_Z, PIN_SERVO_POU};
const uint8_t PIN_FC[4]    = {PIN_FC_XAR, PIN_FC_XNA, PIN_FC_Z, PIN_FC_POU};
const char* NOM_SERVO[4]   = {"X arrière", "X nacelle", "Z", "poussoir"};
const int NB_CASES = 9;
const int COLONNE_TRAPPE = 3;  // la trappe est sous la colonne de droite

// ---------------------------------------------------------------------
//  Réglages enregistrés dans la mémoire de l'ESP32
// ---------------------------------------------------------------------
struct Reglages {
  uint16_t version;
  uint8_t  inv[4];          // 1 = inverser le sens du servo
  uint16_t neutre[4];       // impulsion d'arrêt (µs), 1500 en principe
  uint16_t vRapide;         // écart au neutre en marche rapide (µs)
  uint16_t vLente;          // écart au neutre en approche (µs)
  uint16_t zFronts[3];      // fronts du codeur Z depuis l'origine, par rangée
  uint16_t zLente;          // on ralentit ce nombre de fronts avant la cible
  uint16_t xDepasseMs;      // on continue ce temps après l'entrée dans la fente
  uint16_t pousseExtraMs;   // le poussoir continue ce temps après détection
  uint16_t pousseMaxMs;     // au-delà : case vide
  uint16_t rentreMaxMs;     // délai max pour rentrer le poussoir
  uint16_t tMaxXms;         // délai max d'un mouvement X
  uint16_t tMaxZms;         // délai max d'un mouvement Z
  uint8_t  niveauFente;     // niveau lu sur D0 quand la fourche voit une fente
  uint8_t  niveauPresence;  // niveau lu sur D0 quand une boîte est vue
};
const uint16_t VERSION_REGLAGES = 1;
Reglages R;

void reglagesParDefaut() {
  R.version = VERSION_REGLAGES;
  for (int i = 0; i < 4; i++) { R.inv[i] = 0; R.neutre[i] = 1500; }
  R.vRapide = 200;
  R.vLente = 70;
  R.zFronts[0] = 56;   // (82 - 54) mm / 0,5 mm
  R.zFronts[1] = 114;  // (111 - 54) mm / 0,5 mm
  R.zFronts[2] = 172;  // (140 - 54) mm / 0,5 mm
  R.zLente = 6;
  R.xDepasseMs = 60;
  R.pousseExtraMs = 300;
  R.pousseMaxMs = 4000;
  R.rentreMaxMs = 5000;
  R.tMaxXms = 10000;
  R.tMaxZms = 25000;
  R.niveauFente = 1;
  R.niveauPresence = 0;
}

Preferences prefs;
char nomCase[NB_CASES][25];
int16_t stockCase[NB_CASES];

void chargerMemoire() {
  prefs.begin("armoire", false);
  reglagesParDefaut();
  if (prefs.getBytesLength("reg") == sizeof(Reglages)) {
    Reglages lu;
    prefs.getBytes("reg", &lu, sizeof(lu));
    if (lu.version == VERSION_REGLAGES) R = lu;
  }
  for (int n = 0; n < NB_CASES; n++) {
    char cle[8];
    snprintf(cle, sizeof(cle), "nom%d", n);
    String nom = prefs.getString(cle, String("Case ") + String(n + 1));
    strlcpy(nomCase[n], nom.c_str(), sizeof(nomCase[n]));
    snprintf(cle, sizeof(cle), "st%d", n);
    stockCase[n] = prefs.getShort(cle, 0);
  }
}
void sauverReglages() { prefs.putBytes("reg", &R, sizeof(R)); }
void sauverCase(int n) {
  char cle[8];
  snprintf(cle, sizeof(cle), "nom%d", n);
  prefs.putString(cle, nomCase[n]);
  snprintf(cle, sizeof(cle), "st%d", n);
  prefs.putShort(cle, stockCase[n]);
}

// ---------------------------------------------------------------------
//  État partagé entre la page web et la tâche de mouvement
// ---------------------------------------------------------------------
SemaphoreHandle_t verrou;
char etatPhase[48] = "Démarrage";
char etatMessage[120] = "";
volatile bool etatErreur = false;
volatile bool occupe = false;
volatile bool attenteRetrait = false;
volatile bool arretDemande = false;
volatile int caseEnCours = -1;

void setEtat(const char* phase, const char* message, bool erreur) {
  xSemaphoreTake(verrou, portMAX_DELAY);
  strlcpy(etatPhase, phase, sizeof(etatPhase));
  strlcpy(etatMessage, message ? message : "", sizeof(etatMessage));
  etatErreur = erreur;
  xSemaphoreGive(verrou);
  Serial.printf("[%s] %s\n", phase, message ? message : "");
}

// ---------------------------------------------------------------------
//  Entrées
// ---------------------------------------------------------------------
bool fc(int i) { return digitalRead(PIN_FC[i]) == LOW; }
bool presence() { return digitalRead(PIN_PRESENCE) == R.niveauPresence; }
float tension6V() { return analogReadMilliVolts(PIN_MESURE_6V) / 1000.0f * PONT_RAPPORT; }
bool rail6V() { return !VERIFIER_6V || tension6V() > SEUIL_6V; }

// Compteurs mis à jour par interruptions
volatile int32_t frontsZ = 0;
volatile int8_t sensZ = 1;          // signe appliqué aux fronts du codeur Z
volatile uint32_t dernierZ = 0;
volatile int16_t fentes[2] = {0, 0};  // fentes franchies depuis l'origine X
volatile uint32_t dernierX[2] = {0, 0};

void IRAM_ATTR isrCodeurZ() {
  uint32_t t = millis();
  if (t - dernierZ < ANTI_REBOND_Z_MS) return;
  dernierZ = t;
  frontsZ += sensZ;
}
void IRAM_ATTR isrFourcheXar() {
  uint32_t t = millis();
  if (digitalRead(PIN_FOURCHE_XAR) != R.niveauFente) return;
  if (t - dernierX[0] < ANTI_REBOND_X_MS) return;
  dernierX[0] = t;
  fentes[0]++;
}
void IRAM_ATTR isrFourcheXna() {
  uint32_t t = millis();
  if (digitalRead(PIN_FOURCHE_XNA) != R.niveauFente) return;
  if (t - dernierX[1] < ANTI_REBOND_X_MS) return;
  dernierX[1] = t;
  fentes[1]++;
}

// ---------------------------------------------------------------------
//  Servos à rotation continue
//  vitesse = écart au neutre en µs (signe = sens logique, voir plus haut).
//  0 = arrêt : on coupe les impulsions, le servo ne bouge plus et ne
//  consomme presque rien.
// ---------------------------------------------------------------------
Servo servo[4];
int vitesseActuelle[4] = {0, 0, 0, 0};

void moteur(int i, int vitesse) {
  if (vitesse == vitesseActuelle[i]) return;
  vitesseActuelle[i] = vitesse;
  if (vitesse == 0) {
    if (servo[i].attached()) {
      servo[i].writeMicroseconds(R.neutre[i]);
      delay(30);
      servo[i].detach();
    }
    return;
  }
  int v = R.inv[i] ? -vitesse : vitesse;
  if (!servo[i].attached()) {
    servo[i].setPeriodHertz(50);
    servo[i].attach(PIN_SERVO[i], 500, 2500);
  }
  servo[i].writeMicroseconds(R.neutre[i] + v);
}

void toutArreter() {
  for (int i = 0; i < 4; i++) moteur(i, 0);
}

// ---------------------------------------------------------------------
//  Attentes avec contrôles de sécurité
// ---------------------------------------------------------------------
enum Res { OK = 0, ERR_DELAI, ERR_ARRET, ERR_6V };

template <typename F>
Res attendre(F condition, uint32_t maxMs) {
  uint32_t t0 = millis();
  while (!condition()) {
    if (arretDemande) return ERR_ARRET;
    if (!rail6V()) return ERR_6V;
    if (millis() - t0 > maxMs) return ERR_DELAI;
    delay(2);
  }
  return OK;
}

Res pause(uint32_t ms) {
  Res r = attendre([] { return false; }, ms);
  return r == ERR_DELAI ? OK : r;
}

// ---------------------------------------------------------------------
//  Mouvements élémentaires
// ---------------------------------------------------------------------
Res rentrerPoussoir() {
  if (fc(S_POU)) return OK;
  moteur(S_POU, -R.vRapide);
  Res r = attendre([] { return fc(S_POU); }, R.rentreMaxMs);
  moteur(S_POU, 0);
  return r;
}

Res origineZ() {
  if (!fc(S_Z)) {
    sensZ = -1;
    moteur(S_Z, -R.vRapide);
    Res r = attendre([] { return fc(S_Z); }, R.tMaxZms);
    moteur(S_Z, 0);
    if (r != OK) return r;
  }
  delay(100);
  frontsZ = 0;
  return OK;
}

// rangee : 0 = en bas. Suppose que Z part de l'origine (frontsZ = 0).
Res allerRangee(int rangee) {
  int32_t cible = R.zFronts[rangee];
  sensZ = 1;
  moteur(S_Z, R.vRapide);
  Res r = attendre([cible] { return frontsZ >= cible - (int32_t)R.zLente; }, R.tMaxZms);
  if (r == OK) {
    moteur(S_Z, R.vLente);
    r = attendre([cible] { return frontsZ >= cible; }, R.tMaxZms);
  }
  moteur(S_Z, 0);
  return r;
}

// Les deux chariots X reculent ensemble jusqu'à leur fin de course.
Res origineX() {
  // 1) se dégager si un chariot est déjà sur sa butée
  for (int i = 0; i < 2; i++) if (fc(i)) moteur(i, R.vLente);
  Res r = attendre([] { return !fc(S_XAR) && !fc(S_XNA); }, 3000);
  moteur(S_XAR, 0);
  moteur(S_XNA, 0);
  if (r != OK) return r;
  // 2) aller sur la butée
  bool fini[2] = {false, false};
  moteur(S_XAR, -R.vRapide);
  moteur(S_XNA, -R.vRapide);
  uint32_t t0 = millis();
  while (!(fini[0] && fini[1])) {
    for (int i = 0; i < 2; i++)
      if (!fini[i] && fc(i)) { moteur(i, 0); fini[i] = true; }
    if (arretDemande) { r = ERR_ARRET; break; }
    if (!rail6V()) { r = ERR_6V; break; }
    if (millis() - t0 > R.tMaxXms) { r = ERR_DELAI; break; }
    delay(2);
  }
  moteur(S_XAR, 0);
  moteur(S_XNA, 0);
  noInterrupts();
  fentes[0] = 0;
  fentes[1] = 0;
  interrupts();
  return r;
}

// colonne : 1 à 3 = numéro de la fente du peigne à atteindre depuis l'origine.
// Les deux chariots avancent ensemble, chacun s'arrête sur sa propre fente.
Res allerColonne(int colonne) {
  bool fini[2];
  uint32_t tEntree[2] = {0, 0};
  for (int i = 0; i < 2; i++) {
    fini[i] = fentes[i] >= colonne;
    if (!fini[i]) moteur(i, fentes[i] >= colonne - 1 ? R.vLente : R.vRapide);
  }
  Res r = OK;
  uint32_t t0 = millis();
  while (!(fini[0] && fini[1])) {
    for (int i = 0; i < 2; i++) {
      if (fini[i]) continue;
      if (tEntree[i] == 0) {
        if (fentes[i] >= colonne) tEntree[i] = millis();
        else if (fentes[i] >= colonne - 1) moteur(i, R.vLente);
      } else if (millis() - tEntree[i] >= R.xDepasseMs) {
        moteur(i, 0);
        fini[i] = true;
      }
    }
    if (arretDemande) { r = ERR_ARRET; break; }
    if (!rail6V()) { r = ERR_6V; break; }
    if (millis() - t0 > R.tMaxXms) { r = ERR_DELAI; break; }
    delay(2);
  }
  moteur(S_XAR, 0);
  moteur(S_XNA, 0);
  return r;
}

// Pousse jusqu'à voir la boîte dans la nacelle. vide = rien vu à temps.
Res pousser(bool& vide) {
  vide = false;
  moteur(S_POU, R.vRapide);
  Res r = attendre([] { return presence(); }, R.pousseMaxMs);
  if (r == ERR_DELAI) {
    vide = true;
    r = OK;
  } else if (r == OK) {
    r = pause(R.pousseExtraMs);
  }
  moteur(S_POU, 0);
  return r;
}

// ---------------------------------------------------------------------
//  Séquences complètes
// ---------------------------------------------------------------------
bool echec(Res r, const char* etape) {
  if (r == OK) return false;
  toutArreter();
  char msg[120];
  switch (r) {
    case ERR_DELAI: snprintf(msg, sizeof(msg), "Délai dépassé pendant : %s. Vérifier le mécanisme et le capteur.", etape); break;
    case ERR_ARRET: snprintf(msg, sizeof(msg), "Arrêt demandé pendant : %s.", etape); break;
    case ERR_6V:    snprintf(msg, sizeof(msg), "Plus de 6 V sur les servos (arrêt d'urgence ?) pendant : %s.", etape); break;
    default:        snprintf(msg, sizeof(msg), "Erreur pendant : %s.", etape); break;
  }
  setEtat("Erreur", msg, true);
  return true;
}

void sequenceOrigine() {
  if (!rail6V()) { setEtat("Erreur", "Pas de 6 V sur les servos (arrêt d'urgence enfoncé ?).", true); return; }
  setEtat("Initialisation", "Poussoir, puis Z, puis X.", false);
  if (echec(rentrerPoussoir(), "rentrée du poussoir")) return;
  if (echec(origineZ(), "origine Z")) return;
  if (echec(origineX(), "origine X")) return;
  setEtat("Prêt", "Machine en position d'origine.", false);
}

void sequenceDistribuer(int n) {
  int rangee = n / 3;
  int colonne = n % 3 + 1;
  char msg[120];
  if (presence()) { setEtat("Erreur", "Une boîte est déjà dans la nacelle : la retirer d'abord.", true); return; }
  if (!rail6V()) { setEtat("Erreur", "Pas de 6 V sur les servos (arrêt d'urgence enfoncé ?).", true); return; }

  snprintf(msg, sizeof(msg), "%s : mise en position d'origine.", nomCase[n]);
  setEtat("Préparation", msg, false);
  if (echec(rentrerPoussoir(), "rentrée du poussoir")) return;
  if (echec(origineZ(), "origine Z")) return;
  if (echec(origineX(), "origine X")) return;

  snprintf(msg, sizeof(msg), "%s : colonne %d, rangée %d.", nomCase[n], colonne, rangee + 1);
  setEtat("Va à la case", msg, false);
  if (echec(allerColonne(colonne), "déplacement X vers la case")) return;
  if (echec(allerRangee(rangee), "montée Z vers la case")) return;

  setEtat("Prend la boîte", nomCase[n], false);
  bool vide = false;
  if (echec(pousser(vide), "poussée")) return;
  if (echec(rentrerPoussoir(), "rentrée du poussoir")) return;

  setEtat("Descend à la trappe", nomCase[n], false);
  if (echec(allerColonne(COLONNE_TRAPPE), "déplacement X vers la trappe")) return;
  if (echec(origineZ(), "descente Z vers la trappe")) return;

  if (vide) {
    stockCase[n] = 0;
    sauverCase(n);
    snprintf(msg, sizeof(msg), "Aucune boîte poussée depuis \"%s\" : stock mis à 0.", nomCase[n]);
    setEtat("Case vide", msg, true);
    return;
  }
  if (stockCase[n] > 0) stockCase[n]--;
  sauverCase(n);
  attenteRetrait = true;
  snprintf(msg, sizeof(msg), "%s est dans la trappe.", nomCase[n]);
  setEtat("Récupérez votre boîte", msg, false);
}

// Essai manuel d'un servo (page Réglages)
void sequenceEssai(int i, int vitesse, int ms) {
  char msg[120];
  snprintf(msg, sizeof(msg), "Servo %s, %+d µs pendant %d ms.", NOM_SERVO[i], vitesse, ms);
  setEtat("Essai", msg, false);
  if (i == S_Z) sensZ = vitesse > 0 ? 1 : -1;
  moteur(i, vitesse);
  // en marche arrière, on s'arrête sur le fin de course
  Res r = attendre([i, vitesse] { return vitesse < 0 && fc(i); }, ms);
  moteur(i, 0);
  if (r == ERR_DELAI || r == OK) setEtat("Prêt", "Essai terminé.", false);
  else echec(r, "essai");
}

// Envoie le neutre en continu : on tourne la vis du servo jusqu'à l'arrêt
void sequenceNeutre(int i) {
  char msg[120];
  snprintf(msg, sizeof(msg), "Servo %s reçoit %d µs pendant 30 s : tourner sa vis jusqu'à l'arrêt complet.", NOM_SERVO[i], R.neutre[i]);
  setEtat("Réglage du neutre", msg, false);
  servo[i].setPeriodHertz(50);
  servo[i].attach(PIN_SERVO[i], 500, 2500);
  servo[i].writeMicroseconds(R.neutre[i]);
  vitesseActuelle[i] = 1;  // force moteur(i, 0) à couper ensuite
  pause(30000);
  moteur(i, 0);
  setEtat("Prêt", "Réglage du neutre terminé.", false);
}

// ---------------------------------------------------------------------
//  Tâche de mouvement : exécute une commande à la fois
// ---------------------------------------------------------------------
enum { CMD_ORIGINE = 1, CMD_DISTRIBUER, CMD_ESSAI, CMD_NEUTRE };
struct Commande { uint8_t type; int16_t a; int16_t b; int32_t c; };
QueueHandle_t fileCommandes;

void tacheMouvement(void*) {
  Commande c;
  for (;;) {
    if (xQueueReceive(fileCommandes, &c, portMAX_DELAY) != pdTRUE) continue;
    arretDemande = false;
    switch (c.type) {
      case CMD_ORIGINE:    sequenceOrigine(); break;
      case CMD_DISTRIBUER: caseEnCours = c.a; sequenceDistribuer(c.a); caseEnCours = -1; break;
      case CMD_ESSAI:      sequenceEssai(c.a, c.b, c.c); break;
      case CMD_NEUTRE:     sequenceNeutre(c.a); break;
    }
    toutArreter();
    occupe = false;
  }
}

// Réserve la machine puis envoie la commande. false si déjà occupée.
bool lancer(uint8_t type, int16_t a = 0, int16_t b = 0, int32_t c = 0) {
  bool libre = false;
  xSemaphoreTake(verrou, portMAX_DELAY);
  if (!occupe) { occupe = true; libre = true; }
  xSemaphoreGive(verrou);
  if (!libre) return false;
  Commande cmd = {type, a, b, c};
  xQueueSend(fileCommandes, &cmd, 0);
  return true;
}

// ---------------------------------------------------------------------
//  Serveur web
// ---------------------------------------------------------------------
WebServer serveur(80);

String jsonTexte(const char* s) {
  String o = "\"";
  for (const char* p = s; *p; p++) {
    if (*p == '"' || *p == '\\') { o += '\\'; o += *p; }
    else if ((uint8_t)*p < 0x20) o += ' ';
    else o += *p;
  }
  return o + "\"";
}

bool codeOk() {
  if (serveur.arg("code") == CODE_ADMIN) return true;
  serveur.send(403, "text/plain; charset=utf-8", "Code incorrect");
  return false;
}

void repondreOccupe() {
  serveur.send(409, "text/plain; charset=utf-8", "La machine est occupée");
}

void apiEtat() {
  String j;
  j.reserve(1400);
  xSemaphoreTake(verrou, portMAX_DELAY);
  j = "{\"phase\":" + jsonTexte(etatPhase) + ",\"message\":" + jsonTexte(etatMessage);
  xSemaphoreGive(verrou);
  j += ",\"erreur\":" + String(etatErreur ? "true" : "false");
  j += ",\"occupe\":" + String(occupe ? "true" : "false");
  j += ",\"retrait\":" + String(attenteRetrait ? "true" : "false");
  j += ",\"caseEnCours\":" + String(caseEnCours);
  j += ",\"tension\":" + String(tension6V(), 2);
  j += ",\"presence\":" + String(presence() ? "true" : "false");
  j += ",\"fc\":[";
  for (int i = 0; i < 4; i++) { j += fc(i) ? "1" : "0"; if (i < 3) j += ","; }
  j += "],\"fourches\":[" + String(digitalRead(PIN_FOURCHE_XAR)) + "," + String(digitalRead(PIN_FOURCHE_XNA)) + "," + String(digitalRead(PIN_CODEUR_Z)) + "]";
  j += ",\"fentes\":[" + String(fentes[0]) + "," + String(fentes[1]) + "]";
  j += ",\"frontsZ\":" + String(frontsZ);
  j += ",\"cases\":[";
  for (int n = 0; n < NB_CASES; n++) {
    j += "{\"nom\":" + jsonTexte(nomCase[n]) + ",\"stock\":" + String(stockCase[n]) + "}";
    if (n < NB_CASES - 1) j += ",";
  }
  j += "]}";
  serveur.send(200, "application/json", j);
}

void apiDistribuer() {
  int n = serveur.arg("case").toInt();
  if (n < 0 || n >= NB_CASES || !serveur.hasArg("case")) { serveur.send(400, "text/plain; charset=utf-8", "Case inconnue"); return; }
  if (stockCase[n] <= 0) { serveur.send(409, "text/plain; charset=utf-8", "Cette case est vide"); return; }
  if (attenteRetrait || presence()) { serveur.send(409, "text/plain; charset=utf-8", "Retirez d'abord la boîte de la trappe"); return; }
  if (!lancer(CMD_DISTRIBUER, n)) { repondreOccupe(); return; }
  serveur.send(200, "text/plain; charset=utf-8", "OK");
}

void apiOrigine() {
  if (!lancer(CMD_ORIGINE)) { repondreOccupe(); return; }
  serveur.send(200, "text/plain; charset=utf-8", "OK");
}

void apiStop() {
  arretDemande = true;
  serveur.send(200, "text/plain; charset=utf-8", "OK");
}

void apiAcquitter() {
  if (occupe) { repondreOccupe(); return; }
  attenteRetrait = false;
  setEtat("Prêt", "", false);
  serveur.send(200, "text/plain; charset=utf-8", "OK");
}

void apiCase() {
  if (!codeOk()) return;
  int n = serveur.arg("n").toInt();
  if (n < 0 || n >= NB_CASES || !serveur.hasArg("n")) { serveur.send(400, "text/plain; charset=utf-8", "Case inconnue"); return; }
  if (serveur.hasArg("nom")) {
    String nom = serveur.arg("nom");
    nom.trim();
    if (nom.length() == 0) nom = "Case " + String(n + 1);
    strlcpy(nomCase[n], nom.c_str(), sizeof(nomCase[n]));
  }
  if (serveur.hasArg("stock")) stockCase[n] = constrain(serveur.arg("stock").toInt(), 0, 99);
  sauverCase(n);
  serveur.send(200, "text/plain; charset=utf-8", "OK");
}

void apiEssai() {
  if (!codeOk()) return;
  int i = serveur.arg("servo").toInt();
  int v = constrain(serveur.arg("v").toInt(), -500, 500);
  int ms = constrain(serveur.arg("ms").toInt(), 50, 3000);
  if (i < 0 || i > 3) { serveur.send(400, "text/plain; charset=utf-8", "Servo inconnu"); return; }
  if (!lancer(CMD_ESSAI, i, v, ms)) { repondreOccupe(); return; }
  serveur.send(200, "text/plain; charset=utf-8", "OK");
}

void apiNeutre() {
  if (!codeOk()) return;
  int i = serveur.arg("servo").toInt();
  if (i < 0 || i > 3) { serveur.send(400, "text/plain; charset=utf-8", "Servo inconnu"); return; }
  if (!lancer(CMD_NEUTRE, i)) { repondreOccupe(); return; }
  serveur.send(200, "text/plain; charset=utf-8", "OK");
}

void apiRazCompteurs() {
  noInterrupts();
  fentes[0] = 0; fentes[1] = 0; frontsZ = 0;
  interrupts();
  serveur.send(200, "text/plain; charset=utf-8", "OK");
}

// Liste des réglages exposés à la page : nom, pointeur, taille
struct Champ { const char* nom; void* p; uint8_t taille; };
Champ champs[] = {
  {"inv0", &R.inv[0], 1}, {"inv1", &R.inv[1], 1}, {"inv2", &R.inv[2], 1}, {"inv3", &R.inv[3], 1},
  {"neutre0", &R.neutre[0], 2}, {"neutre1", &R.neutre[1], 2}, {"neutre2", &R.neutre[2], 2}, {"neutre3", &R.neutre[3], 2},
  {"vRapide", &R.vRapide, 2}, {"vLente", &R.vLente, 2},
  {"z1", &R.zFronts[0], 2}, {"z2", &R.zFronts[1], 2}, {"z3", &R.zFronts[2], 2}, {"zLente", &R.zLente, 2},
  {"xDepasseMs", &R.xDepasseMs, 2},
  {"pousseExtraMs", &R.pousseExtraMs, 2}, {"pousseMaxMs", &R.pousseMaxMs, 2}, {"rentreMaxMs", &R.rentreMaxMs, 2},
  {"tMaxXms", &R.tMaxXms, 2}, {"tMaxZms", &R.tMaxZms, 2},
  {"niveauFente", &R.niveauFente, 1}, {"niveauPresence", &R.niveauPresence, 1},
};
const int NB_CHAMPS = sizeof(champs) / sizeof(champs[0]);

void apiReglagesLire() {
  String j = "{";
  for (int k = 0; k < NB_CHAMPS; k++) {
    int v = champs[k].taille == 1 ? *(uint8_t*)champs[k].p : *(uint16_t*)champs[k].p;
    j += "\"" + String(champs[k].nom) + "\":" + String(v);
    if (k < NB_CHAMPS - 1) j += ",";
  }
  serveur.send(200, "application/json", j + "}");
}

void apiReglagesEcrire() {
  if (!codeOk()) return;
  if (occupe) { repondreOccupe(); return; }
  if (serveur.hasArg("defaut")) {
    reglagesParDefaut();
  } else {
    for (int k = 0; k < NB_CHAMPS; k++) {
      if (!serveur.hasArg(champs[k].nom)) continue;
      long v = serveur.arg(champs[k].nom).toInt();
      if (champs[k].taille == 1) *(uint8_t*)champs[k].p = constrain(v, 0, 1);
      else *(uint16_t*)champs[k].p = constrain(v, 0, 60000);
    }
  }
  sauverReglages();
  serveur.send(200, "text/plain; charset=utf-8", "OK");
}

void pageAccueil() {
  serveur.send_P(200, "text/html; charset=utf-8", PAGE_HTML);
}

// ---------------------------------------------------------------------
//  Démarrage
// ---------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println("\nArmoire V5 - démarrage");

  for (int i = 0; i < 4; i++) pinMode(PIN_FC[i], INPUT_PULLUP);
  pinMode(PIN_FOURCHE_XAR, INPUT);
  pinMode(PIN_FOURCHE_XNA, INPUT);
  pinMode(PIN_CODEUR_Z, INPUT);
  pinMode(PIN_PRESENCE, INPUT_PULLUP);
  pinMode(PIN_LED, OUTPUT);
  analogSetPinAttenuation(PIN_MESURE_6V, ADC_11db);

  verrou = xSemaphoreCreateMutex();
  fileCommandes = xQueueCreate(4, sizeof(Commande));
  chargerMemoire();

  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);

  attachInterrupt(digitalPinToInterrupt(PIN_CODEUR_Z), isrCodeurZ, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_FOURCHE_XAR), isrFourcheXar, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_FOURCHE_XNA), isrFourcheXna, CHANGE);

  // Wi-Fi : point d'accès, plus le réseau de la maison si configuré
  if (strlen(WIFI_MAISON_NOM) > 0) {
    WiFi.mode(WIFI_AP_STA);
    WiFi.begin(WIFI_MAISON_NOM, WIFI_MAISON_MDP);
  } else {
    WiFi.mode(WIFI_AP);
  }
  WiFi.softAP(WIFI_AP_NOM, WIFI_AP_MDP);
  Serial.printf("Wi-Fi \"%s\" : http://%s\n", WIFI_AP_NOM, WiFi.softAPIP().toString().c_str());
  if (MDNS.begin(NOM_MDNS)) MDNS.addService("http", "tcp", 80);

  serveur.on("/", HTTP_GET, pageAccueil);
  serveur.on("/api/etat", HTTP_GET, apiEtat);
  serveur.on("/api/distribuer", HTTP_POST, apiDistribuer);
  serveur.on("/api/origine", HTTP_POST, apiOrigine);
  serveur.on("/api/stop", HTTP_POST, apiStop);
  serveur.on("/api/acquitter", HTTP_POST, apiAcquitter);
  serveur.on("/api/case", HTTP_POST, apiCase);
  serveur.on("/api/essai", HTTP_POST, apiEssai);
  serveur.on("/api/neutre", HTTP_POST, apiNeutre);
  serveur.on("/api/raz", HTTP_POST, apiRazCompteurs);
  serveur.on("/api/reglages", HTTP_GET, apiReglagesLire);
  serveur.on("/api/reglages", HTTP_POST, apiReglagesEcrire);
  serveur.onNotFound([] { serveur.send(404, "text/plain", "Introuvable"); });
  serveur.begin();

  xTaskCreatePinnedToCore(tacheMouvement, "mouvement", 6144, nullptr, 1, nullptr, 1);

  setEtat("Prêt", "Appuyez sur Initialiser avant la première distribution.", false);
}

// ---------------------------------------------------------------------
//  Boucle : serveur web, fin d'attente de retrait, LED
// ---------------------------------------------------------------------
uint32_t debutAbsence = 0;

void loop() {
  serveur.handleClient();

  // La boîte a été retirée de la trappe depuis 1 s : retour à "Prêt"
  if (attenteRetrait && !occupe) {
    if (presence()) debutAbsence = 0;
    else if (debutAbsence == 0) debutAbsence = millis();
    else if (millis() - debutAbsence > 1000) {
      attenteRetrait = false;
      debutAbsence = 0;
      setEtat("Prêt", "Boîte retirée.", false);
    }
  }

  // LED : fixe = occupé, clignote = erreur, éteinte = prêt
  bool led = occupe || (etatErreur && (millis() / 250) % 2);
  digitalWrite(PIN_LED, led);
  delay(2);
}
