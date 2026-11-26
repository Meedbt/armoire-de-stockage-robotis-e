// Page web servie par l'ESP32 (téléphone). Aucune connexion Internet nécessaire.
#pragma once

const char PAGE_HTML[] PROGMEM = R"rawliteral(<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Armoire</title>
<style>
:root{--fond:#f4f5f7;--carte:#fff;--texte:#1d2330;--doux:#667085;--bord:#e1e4ea;--accent:#2563eb;--ok:#16a34a;--warn:#d97706;--err:#dc2626}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--fond);color:var(--texte)}
header{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;background:var(--carte);border-bottom:1px solid var(--bord);position:sticky;top:0;z-index:2}
h1{font-size:18px;margin:0}main{padding:14px;max-width:560px;margin:0 auto 80px}
.pastille{font-size:12px;padding:4px 10px;border-radius:99px;background:#e8f0fe;color:var(--accent);font-weight:600}
.pastille.err{background:#fde8e8;color:var(--err)}.pastille.ok{background:#e7f6ec;color:var(--ok)}
.etat{background:var(--carte);border:1px solid var(--bord);border-radius:14px;padding:14px;margin-bottom:14px}
.etat .phase{font-size:20px;font-weight:700}.etat .msg{color:var(--doux);margin-top:4px;min-height:20px}
.etat.err{border-color:var(--err)}.etat.retrait{border-color:var(--ok);background:#f0fbf3}
.actions{display:flex;gap:10px;margin-top:12px}
button{font:inherit;border:0;border-radius:10px;padding:12px 14px;font-weight:600;cursor:pointer}
button:disabled{opacity:.45}
.b1{background:var(--accent);color:#fff}.b2{background:#eef0f4;color:var(--texte)}.bs{background:var(--err);color:#fff;flex:1}
.grille{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.case{background:var(--carte);border:1px solid var(--bord);border-radius:14px;padding:12px 8px;text-align:center;min-height:96px;display:flex;flex-direction:column;justify-content:center;gap:4px}
.case .num{font-size:11px;color:var(--doux)}.case .nom{font-weight:700;word-break:break-word}
.case .st{font-size:13px;color:var(--doux)}.case.vide .st{color:var(--err)}.case.encours{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent) inset}
.legende{font-size:12px;color:var(--doux);text-align:center;margin:8px 0 0}
nav{position:fixed;bottom:0;left:0;right:0;display:flex;background:var(--carte);border-top:1px solid var(--bord)}
nav button{flex:1;background:none;border-radius:0;color:var(--doux);padding:14px 4px}nav button.actif{color:var(--accent)}
.panneau{display:none}.panneau.actif{display:block}
.bloc{background:var(--carte);border:1px solid var(--bord);border-radius:14px;padding:14px;margin-bottom:14px}
.bloc h2{font-size:15px;margin:0 0 10px}
.ligne{display:flex;gap:8px;align-items:center;margin-bottom:8px}.ligne label{flex:1;font-size:14px}
input{font:inherit;padding:9px 10px;border:1px solid var(--bord);border-radius:8px;width:100%;background:#fff}
input.court{width:84px}
table{width:100%;border-collapse:collapse;font-size:14px}td{padding:6px 4px;border-bottom:1px solid var(--bord)}
.on{color:var(--ok);font-weight:700}.off{color:var(--doux)}
.servo{display:grid;grid-template-columns:1fr auto auto auto;gap:6px;align-items:center;margin-bottom:8px}
.note{font-size:12px;color:var(--doux);margin:6px 0 0}
#fond{position:fixed;inset:0;background:rgba(0,0,0,.4);display:none;align-items:center;justify-content:center;z-index:5}
#fond .boite{background:var(--carte);border-radius:16px;padding:18px;width:min(92vw,360px)}
#fond p{margin:0 0 14px;font-size:17px}#fond .actions{justify-content:flex-end}
#toast{position:fixed;left:50%;bottom:72px;transform:translateX(-50%);background:#1d2330;color:#fff;padding:10px 14px;border-radius:10px;display:none;z-index:6;font-size:14px}
</style></head><body>
<header><h1>Armoire à médicaments</h1><span id="pastille" class="pastille">…</span></header>
<main>
<div id="etat" class="etat"><div class="phase" id="phase">Connexion…</div><div class="msg" id="msg"></div>
<div class="actions"><button class="b2" id="bInit">Initialiser</button><button class="b2" id="bOk" style="display:none">OK, vu</button><button class="bs" id="bStop">ARRÊT</button></div></div>

<section class="panneau actif" id="p-distribuer">
<div class="grille" id="grille"></div>
<p class="legende">Touchez une case pour distribuer une boîte. La rangée du haut est en haut.</p>
</section>

<section class="panneau" id="p-gestion">
<div class="bloc"><h2>Code</h2><div class="ligne"><input id="code" type="password" inputmode="numeric" placeholder="Code de gestion"></div>
<p class="note">Le code est dans config.h (1234 par défaut).</p></div>
<div class="bloc"><h2>Cases et stock</h2><div id="listeCases"></div>
<button class="b1" id="bSauverCases" style="width:100%">Enregistrer</button></div>
</section>

<section class="panneau" id="p-reglages">
<div class="bloc"><h2>Capteurs (en direct)</h2><table id="capteurs"></table>
<button class="b2" id="bRaz" style="margin-top:10px">Remettre les compteurs à 0</button></div>
<div class="bloc"><h2>Essai des servos</h2>
<div id="servos"></div>
<div class="ligne"><label>Durée d'un essai (ms)</label><input class="court" id="dureeEssai" type="number" value="500"></div>
<p class="note">« + » doit aller à droite (X), vers le haut (Z), vers les boîtes (poussoir). Sinon, cocher « inverser » plus bas. « Neutre » envoie l'arrêt 30 s : tourner la vis du servo jusqu'à ce qu'il ne bouge plus.</p></div>
<div class="bloc"><h2>Réglages</h2><div id="reglages"></div>
<div class="actions"><button class="b1" id="bSauverReg">Enregistrer</button><button class="b2" id="bDefaut">Valeurs d'origine</button></div></div>
</section>
</main>
<nav><button class="actif" data-p="distribuer">Distribuer</button><button data-p="gestion">Gestion</button><button data-p="reglages">Réglages</button></nav>
<div id="fond"><div class="boite"><p id="question"></p><div class="actions"><button class="b2" id="bNon">Annuler</button><button class="b1" id="bOui">Distribuer</button></div></div></div>
<div id="toast"></div>
<script>
const $=s=>document.querySelector(s);
let E=null,choix=-1;
const lire=k=>{try{return localStorage.getItem(k)||''}catch(e){return''}};
const ecrire=(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}};
$('#code').value=lire('code');$('#code').onchange=()=>ecrire('code',$('#code').value);
function toast(t){const b=$('#toast');b.textContent=t;b.style.display='block';clearTimeout(b._t);b._t=setTimeout(()=>b.style.display='none',2600)}
async function post(url,data,admin){const b=new URLSearchParams(data||{});if(admin)b.append('code',$('#code').value);
 try{const r=await fetch(url,{method:'POST',body:b});const t=await r.text();if(!r.ok){toast(t);return false}return true}catch(e){toast('Pas de connexion');return false}}
const echap=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

function rendu(){
 $('#phase').textContent=E.phase;$('#msg').textContent=E.message;
 const z=$('#etat');z.className='etat'+(E.erreur?' err':'')+(E.retrait?' retrait':'');
 const p=$('#pastille');p.textContent=E.occupe?'En mouvement':(E.erreur?'Erreur':(E.tension<4.5?'Servos sans 6 V':'Prêt'));
 p.className='pastille'+(E.erreur||E.tension<4.5?' err':(E.occupe?'':' ok'));
 $('#bInit').disabled=E.occupe;$('#bOk').style.display=(E.erreur&&!E.occupe)?'':'none';
 let h='';for(const r of [2,1,0])for(let c=0;c<3;c++){const n=r*3+c,k=E.cases[n];
  const off=E.occupe||E.retrait||k.stock<=0;
  h+=`<button class="case${k.stock<=0?' vide':''}${E.caseEnCours==n?' encours':''}" ${off?'disabled':''} onclick="demander(${n})"><span class="num">Case ${n+1}</span><span class="nom">${echap(k.nom)}</span><span class="st">${k.stock<=0?'Vide':'Stock : '+k.stock}</span></button>`}
 $('#grille').innerHTML=h;
 if($('#p-reglages').classList.contains('actif'))renduCapteurs();
}
function etiquette(v,oui,non){return v?`<span class="on">${oui}</span>`:`<span class="off">${non}</span>`}
function renduCapteurs(){
 const f=E.fc,fo=E.fourches,L=[
 ['Tension rail servos',E.tension.toFixed(2)+' V'],
 ['Origine X arrière (32)',etiquette(f[0],'appuyé','libre')],['Origine X nacelle (33)',etiquette(f[1],'appuyé','libre')],
 ['Origine Z (18)',etiquette(f[2],'appuyé','libre')],['Poussoir rentré (19)',etiquette(f[3],'appuyé','libre')],
 ['Fourche X arrière (34)','niveau '+fo[0]+' · fentes '+E.fentes[0]],['Fourche X nacelle (35)','niveau '+fo[1]+' · fentes '+E.fentes[1]],
 ['Codeur Z (39)','niveau '+fo[2]+' · fronts '+E.frontsZ],['Présence nacelle (23)',etiquette(E.presence,'boîte vue','rien')]];
 $('#capteurs').innerHTML=L.map(l=>`<tr><td>${l[0]}</td><td style="text-align:right">${l[1]}</td></tr>`).join('');
}
function demander(n){choix=n;$('#question').textContent='Distribuer « '+E.cases[n].nom+' » (case '+(n+1)+') ?';$('#fond').style.display='flex'}
$('#bNon').onclick=()=>$('#fond').style.display='none';
$('#bOui').onclick=async()=>{$('#fond').style.display='none';if(await post('/api/distribuer',{case:choix}))maj()};
$('#bInit').onclick=()=>post('/api/origine');
$('#bStop').onclick=()=>post('/api/stop');
$('#bOk').onclick=()=>post('/api/acquitter');
$('#bRaz').onclick=()=>post('/api/raz');

function renduGestion(){
 if(!E)return;let h='';for(let n=0;n<9;n++){const k=E.cases[n];
  h+=`<div class="ligne"><label style="flex:0 0 52px">Case ${n+1}</label><input id="nom${n}" maxlength="24" value="${echap(k.nom)}"><input class="court" id="st${n}" type="number" min="0" max="99" value="${k.stock}"></div>`}
 $('#listeCases').innerHTML=h}
$('#bSauverCases').onclick=async()=>{let ok=true;for(let n=0;n<9;n++){ok=await post('/api/case',{n:n,nom:$('#nom'+n).value,stock:$('#st'+n).value},true)&&ok;if(!ok)break}
 if(ok)toast('Enregistré');maj()};

const SERVOS=['X arrière','X nacelle','Z','Poussoir'];
$('#servos').innerHTML=SERVOS.map((s,i)=>`<div class="servo"><span>${s}</span><button class="b2" onclick="essai(${i},-1)">−</button><button class="b2" onclick="essai(${i},1)">+</button><button class="b2" onclick="neutre(${i})">Neutre</button></div>`).join('');
function essai(i,s){post('/api/essai',{servo:i,v:s*(+lireReg('vLente')||70),ms:$('#dureeEssai').value},true)}
function neutre(i){post('/api/neutre',{servo:i},true)}

const REG=[['inv0','Inverser X arrière','b'],['inv1','Inverser X nacelle','b'],['inv2','Inverser Z','b'],['inv3','Inverser poussoir','b'],
['neutre0','Neutre X arrière (µs)'],['neutre1','Neutre X nacelle (µs)'],['neutre2','Neutre Z (µs)'],['neutre3','Neutre poussoir (µs)'],
['vRapide','Vitesse rapide (µs d\'écart)'],['vLente','Vitesse lente (µs d\'écart)'],
['z1','Fronts Z rangée 1 (bas)'],['z2','Fronts Z rangée 2'],['z3','Fronts Z rangée 3 (haut)'],['zLente','Ralentir Z à N fronts de la cible'],
['xDepasseMs','X : continuer après la fente (ms)'],['pousseExtraMs','Poussoir : continuer après détection (ms)'],
['pousseMaxMs','Poussoir : délai avant « case vide » (ms)'],['rentreMaxMs','Poussoir : délai de rentrée (ms)'],
['tMaxXms','Délai max X (ms)'],['tMaxZms','Délai max Z (ms)'],
['niveauFente','Niveau des fourches sur une fente (0 ou 1)'],['niveauPresence','Niveau du TCRT5000 quand il voit la boîte (0 ou 1)']];
let REGV={};const lireReg=k=>REGV[k];
async function chargerReg(){try{REGV=await (await fetch('/api/reglages')).json()}catch(e){return}
 $('#reglages').innerHTML=REG.map(r=>r[2]=='b'
  ?`<div class="ligne"><label for="r_${r[0]}">${r[1]}</label><input id="r_${r[0]}" type="checkbox" style="width:22px;height:22px" ${REGV[r[0]]?'checked':''}></div>`
  :`<div class="ligne"><label for="r_${r[0]}">${r[1]}</label><input class="court" id="r_${r[0]}" type="number" value="${REGV[r[0]]}"></div>`).join('')}
$('#bSauverReg').onclick=async()=>{const d={};for(const r of REG){const e=$('#r_'+r[0]);d[r[0]]=r[2]=='b'?(e.checked?1:0):e.value}
 if(await post('/api/reglages',d,true)){toast('Réglages enregistrés');chargerReg()}};
$('#bDefaut').onclick=async()=>{if(await post('/api/reglages',{defaut:1},true)){toast('Valeurs d\'origine remises');chargerReg()}};

document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{
 document.querySelectorAll('nav button').forEach(x=>x.classList.toggle('actif',x==b));
 document.querySelectorAll('.panneau').forEach(x=>x.classList.toggle('actif',x.id=='p-'+b.dataset.p));
 if(b.dataset.p=='gestion')renduGestion();if(b.dataset.p=='reglages'){chargerReg();if(E)renduCapteurs()}});

async function maj(){try{const r=await fetch('/api/etat');E=await r.json();rendu()}catch(e){$('#phase').textContent='Connexion perdue';$('#msg').textContent='Vérifiez que le téléphone est sur le Wi-Fi Armoire-V5.'}}
setInterval(maj,700);maj();chargerReg();
</script></body></html>)rawliteral";
