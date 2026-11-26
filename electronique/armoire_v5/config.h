// =====================================================================
//  Armoire automatisée V5 - configuration matérielle
//  Les réglages fins (vitesses, nombre de fronts, sens des servos...)
//  se changent depuis la page web, onglet "Réglages" : pas besoin de
//  recompiler pour ça.
// =====================================================================
#pragma once

// ---------- Wi-Fi ----------
// L'ESP32 crée son propre réseau. Mot de passe : 8 caractères minimum.
#define WIFI_AP_NOM   "Armoire-V5"
#define WIFI_AP_MDP   "pharmacie5"
// Optionnel : se connecter AUSSI au Wi-Fi de la maison / du lycée.
// Laisser "" pour ne pas l'utiliser.
#define WIFI_MAISON_NOM ""
#define WIFI_MAISON_MDP ""
// Nom sur le réseau : http://armoire.local (si le téléphone le gère)
#define NOM_MDNS "armoire"

// Code demandé pour la gestion du stock et les réglages
#define CODE_ADMIN "1234"

// ---------- Servos (signal, via 330 ohms) ----------
#define PIN_SERVO_XAR 25   // X chariot arrière (poussoir)
#define PIN_SERVO_XNA 26   // X nacelle
#define PIN_SERVO_Z   27   // Z (vis T8)
#define PIN_SERVO_POU 13   // poussoir

// ---------- Capteurs à fourche (sortie D0, module alimenté en 3,3 V) ----------
#define PIN_FOURCHE_XAR 34 // peigne du chariot arrière
#define PIN_FOURCHE_XNA 35 // peigne de la nacelle
#define PIN_CODEUR_Z    39 // disque 8 fentes sur la vis T8

// ---------- Fins de course (COM -> GND, NO -> broche) ----------
#define PIN_FC_XAR 32      // origine X arrière
#define PIN_FC_XNA 33      // origine X nacelle
#define PIN_FC_Z   18      // origine Z (en bas = hauteur de la trappe)
#define PIN_FC_POU 19      // poussoir rentré

// ---------- Divers ----------
#define PIN_PRESENCE  23   // TCRT5000 dans la nacelle (sortie D0)
#define PIN_MESURE_6V 36   // pont 10k (vers +6 V rail) / 6,8k (vers GND)
#define PIN_LED       2    // LED bleue de la carte

// Pont diviseur de la mesure du rail servos
#define PONT_RAPPORT  ((10.0f + 6.8f) / 6.8f)
// En dessous de cette tension, on considère le rail coupé (arrêt d'urgence)
#define SEUIL_6V      4.5f
// Mettre à 0 pour faire des essais SANS le pont de mesure (déconseillé)
#define VERIFIER_6V   1

// Anti-rebond des capteurs à fourche (ms)
#define ANTI_REBOND_X_MS 100  // les fentes du peigne sont espacées de 58 mm
#define ANTI_REBOND_Z_MS 20   // un front tous les 0,5 mm
