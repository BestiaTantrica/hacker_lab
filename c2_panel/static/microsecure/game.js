// MicroSecure V4 — game.js
const TIMER_S=8, META=5.00;

const MULTS={
  'BUG BOUNTY':     {m:3.0,l:'3x BOUNTY',c:'#f59e0b'},
  '2FA':            {m:2.0,l:'2x',        c:'#6366f1'},
  'RANSOMWARE':     {m:2.0,l:'2x',        c:'#a78bfa'},
  'PHISHING':       {m:1.5,l:'1.5x',      c:'#fbbf24'},
  'DATA BREACH':    {m:1.5,l:'1.5x',      c:'#f87171'},
  'CONTRASEÑAS':    {m:1.2,l:'1.2x',      c:'#94a3b8'},
  'WI-FI':          {m:1.0,l:'1x',        c:'#64748b'},
  'ACTUALIZACIONES':{m:1.0,l:'1x',        c:'#64748b'},
};

const HITOS=[
  {id:'h1',pts:100, emoji:'🎯',titulo:'¡Primer Acierto!',       desc:'Desbloqueaste el modo básico de protección digital.',          bonus:0,    badge:'INICIADO',          txt:'Completé mi primer desafío de ciberseguridad en MicroSecure 🛡️ #CyberSecurity #LearnToEarn'},
  {id:'h2',pts:300, emoji:'🎓',titulo:'Consciente Digital',      desc:'Equivale al Módulo 1 del Google Cybersecurity Cert. +10%.',    bonus:0.10, badge:'GOOGLE CERT MOD.1',  txt:'Alcancé "Consciente Digital" en MicroSecure 🎓 Equivale al Google Cybersecurity Cert Módulo 1. #LearnToEarn'},
  {id:'h3',pts:600, emoji:'🛡️',titulo:'Guardaespaldas Digital', desc:'Dominás los vectores de ataque principales. +25% permanente.', bonus:0.25, badge:'SECURITY+ READY',    txt:'Alcancé "Guardaespaldas Digital" en MicroSecure 🛡️ #CyberSecurity #BugBounty'},
  {id:'h4',pts:1000,emoji:'🏆',titulo:'Bug Hunter Nivel 1',      desc:'Listo para Bug Bounty en HackerOne. +50% permanente.',         bonus:0.50, badge:'H1 HUNTER',          txt:'Alcancé "Bug Hunter Nivel 1" en MicroSecure 🏆 Listo para HackerOne. #BugBounty #HackerOne'},
];

const NIVELES=[
  {min:0,   max:149,  nombre:'Novato',     emoji:'🔵',desc:'¡Todo lo que aprendás es ganancia!'},
  {min:150, max:349,  nombre:'Consciente', emoji:'🟡',desc:'Sabés más que el 80% de la población.'},
  {min:350, max:599,  nombre:'Informado',  emoji:'🟠',desc:'Pensás como alguien que sabe protegerse.'},
  {min:600, max:9999, nombre:'Avanzado',   emoji:'🔴',desc:'Nivel profesional. Podés enseñarle a otros.'},
];

const getNivel=pts=>NIVELES.find(n=>pts>=n.min&&pts<=n.max)||NIVELES[0];
const getMult =cat=>(MULTS[cat]||{m:1.0}).m;
const getMInfo=cat=> MULTS[cat]||{m:1.0,l:'1x',c:'#64748b'};

const INSIGHTS=[
  {emoji:'📶',stat:{n:'147',u:'contraseñas robadas por hora en Wi-Fi pública'},
   headline:'Tu Wi-Fi pública es una trampa silenciosa.',
   context:'Un atacante en la misma red captura tu tráfico con herramientas gratuitas. Una VPN cifra todo y lo hace ilegible.',
   categoria:'WI-FI',bg:'rgba(239,68,68,0.12)',col:'#f87171',sponsor:'Patrocinado por NordVPN',rb:0.07,
   vp:{esc:'Café lleno de gente. Overlay: paquetes de red interceptados en tiempo real.',nar:'147 contraseñas robadas por hora en Wi-Fi pública. Una VPN lo previene.',cta:'¿Cuántas redes públicas usaste hoy sin protección?'},
   q:'¿Qué herramienta protege tu tráfico en redes públicas?',
   opts:[{t:'Un antivirus actualizado',c:false},{t:'Una VPN (Red Privada Virtual)',c:true},{t:'Modo incógnito',c:false},{t:'Usar solo HTTPS',c:false}],
   exp:'Una VPN cifra todo el tráfico antes de salir del dispositivo. El modo incógnito solo oculta el historial local.'},

  {emoji:'🎣',stat:{n:'91%',u:'de los hackeos empieza con un email falso'},
   headline:'El phishing es el arma #1 del cibercrimen.',
   context:'Un atacante clona el email de tu banco en minutos. La diferencia está en una sola letra del dominio del remitente.',
   categoria:'PHISHING',bg:'rgba(245,158,11,0.1)',col:'#fbbf24',sponsor:'Patrocinado por Proofpoint',rb:0.06,
   vp:{esc:'Email del banco en pantalla. Zoom al remitente: "bancc0.com" resaltado en rojo.',nar:'91% de los hackeos empieza con un email falso. La trampa es casi invisible.',cta:'Verificá siempre el dominio exacto. No el nombre visible, el dominio.'},
   q:'Recibes un email de "seguridad@bancc0.com". ¿Qué hacés?',
   opts:[{t:'Clic en el link si parece urgente',c:false},{t:'Verificar el dominio exacto del remitente',c:true},{t:'Responder para confirmar',c:false},{t:'Abrir el adjunto',c:false}],
   exp:'"bancc0.com" no es el dominio real de ningún banco. Verificar el dominio exacto (no el nombre visible) es la defensa clave.'},

  {emoji:'🔑',stat:{n:'23M',u:'personas usan "123456" como contraseña'},
   headline:'La contraseña más fácil = la primera que prueban.',
   context:'Los atacantes usan diccionarios con millones de contraseñas comunes. Una de 12 caracteres aleatorios tardaría miles de años.',
   categoria:'CONTRASEÑAS',bg:'rgba(99,102,241,0.12)',col:'#818cf8',sponsor:'Patrocinado por 1Password',rb:0.05,
   vp:{esc:'Terminal corriendo un diccionario de contraseñas. En 2 segundos: "123456: FOUND".',nar:'23 millones de personas usan la contraseña que prueban primero.',cta:'Tu contraseña más débil es la puerta de entrada a todo lo demás.'},
   q:'¿Cuál de estas contraseñas es más segura?',
   opts:[{t:'MiPerro2024!',c:false},{t:'P@ssw0rd',c:false},{t:'kX#9mQ2!vLpR',c:true},{t:'123456789',c:false}],
   exp:'"kX#9mQ2!vLpR" es aleatoria, larga y mezcla tipos de caracteres. Las basadas en palabras son vulnerables a ataques de diccionario.'},

  {emoji:'📱',stat:{n:'99.9%',u:'de ataques automáticos bloqueados por 2FA'},
   headline:'El doble factor tarda 30 segundos en activarse.',
   context:'El 2FA exige contraseña + código de teléfono. Aunque te roben la contraseña, sin el código no pueden entrar.',
   categoria:'2FA',bg:'rgba(6,182,212,0.1)',col:'#22d3ee',sponsor:'Patrocinado por Authy',rb:0.07,
   vp:{esc:'Login con contraseña exitoso. Sistema pide 2FA. Atacante en otra ciudad: acceso bloqueado.',nar:'99.9% de los hackeos automáticos fallan con 2FA activo. 30 segundos de configuración.',cta:'Activá 2FA en tu email hoy. Es lo más importante que podés hacer.'},
   q:'¿Cuál es el segundo "factor" en la autenticación de dos factores?',
   opts:[{t:'Una contraseña más larga',c:false},{t:'Un código enviado a tu teléfono o app',c:true},{t:'Tu nombre de usuario',c:false},{t:'Un CAPTCHA',c:false}],
   exp:'El segundo factor es algo físico que tenés: tu teléfono. Sin ese código temporal, el atacante no puede acceder aunque tenga tu contraseña.'},

  {emoji:'💉',stat:{n:'#1',u:'vulnerabilidad más reportada en HackerOne: IDOR'},
   headline:'Cambiar un número en la URL puede exponer datos ajenos.',
   context:'IDOR: si la app no verifica que sos el dueño, cambiar /usuario/123 a /usuario/124 puede mostrar datos de otro usuario.',
   categoria:'BUG BOUNTY',bg:'rgba(16,185,129,0.1)',col:'#34d399',sponsor:'Patrocinado por HackerOne',rb:0.09,
   vp:{esc:'Browser: URL /api/perfil/100. Mano cambia "100" a "101". Aparecen datos de otra persona.',nar:'Esta vulnerabilidad se llama IDOR. Es la más pagada en HackerOne y solo requiere cambiar un número.',cta:'Se paga hasta $10,000 por encontrarla. El conocimiento es el activo que no te pueden robar.'},
   q:'Una app muestra /api/perfil/100. Cambiás a /api/perfil/101 y ves datos de otro usuario. ¿Qué vulnerabilidad es?',
   opts:[{t:'SQL Injection',c:false},{t:'XSS (Cross-Site Scripting)',c:false},{t:'IDOR (Referencia directa insegura)',c:true},{t:'CSRF',c:false}],
   exp:'IDOR ocurre cuando el servidor no verifica que el usuario es el dueño del objeto solicitado. Es la vulnerabilidad #1 en Bug Bounty por su alto impacto.'},

  {emoji:'⚡',stat:{n:'60%',u:'de brechas explotan vulnerabilidades ya parcheadas'},
   headline:'"Actualizar después" puede costarte todo.',
   context:'Cuando aparece un parche, los atacantes crean exploits en horas. Sin actualizar sos un blanco conocido y documentado.',
   categoria:'ACTUALIZACIONES',bg:'rgba(245,158,11,0.1)',col:'#fbbf24',sponsor:'Patrocinado por Microsoft',rb:0.05,
   vp:{esc:'Notificación de actualización ignorada 3 veces. Luego: pantalla de ransomware.',nar:'60% de los hackeos usan vulnerabilidades que ya tenían parche disponible.',cta:'Actualizar hoy es la diferencia entre ser víctima o no serlo.'},
   q:'¿Por qué es urgente instalar actualizaciones de seguridad el mismo día que salen?',
   opts:[{t:'Para tener las últimas funciones',c:false},{t:'Porque los atacantes crean exploits en horas tras el parche',c:true},{t:'Para mejorar la velocidad',c:false},{t:'Porque lo pide el fabricante',c:false}],
   exp:'El parche publica qué bug fue corregido. Los atacantes lo usan como mapa para atacar sistemas sin actualizar. Cuanto más tardás, más expuesto estás.'},

  {emoji:'💸',stat:{n:'$1.50',u:'vale tu perfil completo en la dark web'},
   headline:'Tus datos se venden al por mayor sin que lo sepas.',
   context:'Las filtraciones masivas se venden en mercados ilegales. Tu email + contraseña + fecha de nacimiento permiten ataques en cadena.',
   categoria:'DATA BREACH',bg:'rgba(239,68,68,0.1)',col:'#f87171',sponsor:'Patrocinado por HaveIBeenPwned',rb:0.08,
   vp:{esc:'Marketplace dark web. Lista de emails y contraseñas. Precio: $1.50 por perfil completo.',nar:'Tu identidad digital completa vale $1.50 en la dark web. ¿Ya fue filtrada?',cta:'Buscá tu email en haveibeenpwned.com. Es gratis y tarda 5 segundos.'},
   q:'¿Qué podés hacer HOY para saber si tus datos fueron filtrados?',
   opts:[{t:'Cambiar contraseñas por "admin123"',c:false},{t:'Consultar haveibeenpwned.com con tu email',c:true},{t:'Formatear la computadora',c:false},{t:'No hay forma de saberlo',c:false}],
   exp:'HaveIBeenPwned.com indexa todas las filtraciones conocidas. Ingresás tu email y te dice si fue comprometido en segundos.'},

  {emoji:'💾',stat:{n:'11s',u:'— cada 11 segundos una empresa es atacada con ransomware'},
   headline:'Sin backup, un ataque borra años de trabajo.',
   context:'El ransomware cifra todo y pide rescate. La única defensa real es una copia offline. Regla 3-2-1: 3 copias, 2 medios, 1 fuera del sitio.',
   categoria:'RANSOMWARE',bg:'rgba(139,92,246,0.1)',col:'#a78bfa',sponsor:'Patrocinado por Backblaze',rb:0.09,
   vp:{esc:'Reloj en pantalla. Cada 11 segundos: nueva empresa con pantalla de rescate ransomware.',nar:'Cada 11 segundos una empresa paga rescate por sus propios archivos. Un backup los habría salvado.',cta:'¿Cuándo fue tu último backup? Si no recordás la fecha, es demasiado tarde.'},
   q:'Si un ransomware cifra tu disco, ¿cuál es la única defensa real?',
   opts:[{t:'Pagar el rescate rápidamente',c:false},{t:'Tener backups offline actualizados',c:true},{t:'Apagar la computadora',c:false},{t:'Usar Windows Defender',c:false}],
   exp:'Pagar no garantiza recuperar los archivos. Solo un backup offline garantiza recuperación total sin depender del atacante.'},
];

// ESTADO
let E={
  idx:0,orden:[],pts:0,wallet:0,correctas:0,racha:0,rachaMax:0,
  timerInt:null,respondido:false,enTimer:false,hitoPend:null,
  walletTotal:0,ptsTotal:0,hitosOk:[],multBonus:0,
};

// PERSISTENCIA
function cargar(){
  E.walletTotal=parseFloat(localStorage.getItem('ms_wt')||'0');
  E.ptsTotal   =parseInt(  localStorage.getItem('ms_pt')||'0');
  E.hitosOk    =JSON.parse(localStorage.getItem('ms_h') ||'[]');
  E.multBonus  =parseFloat(localStorage.getItem('ms_mb')||'0');
}
function guardar(){
  localStorage.setItem('ms_wt',E.walletTotal.toFixed(4));
  localStorage.setItem('ms_pt',E.ptsTotal);
  localStorage.setItem('ms_h', JSON.stringify(E.hitosOk));
  localStorage.setItem('ms_mb',E.multBonus.toFixed(4));
}

// INTRO
function initIntro(){
  cargar();
  const wp=document.getElementById('wallet-prev');
  if(wp) wp.textContent='$'+E.walletTotal.toFixed(2);
  const hb=document.getElementById('hitos-prev');
  if(hb&&E.hitosOk.length){
    hb.innerHTML=E.hitosOk.map(id=>{const h=HITOS.find(x=>x.id===id);return h?`<span class="hito-prev-badge">${h.emoji} ${h.badge}</span>`:''}).join('');
    hb.style.display='flex';
  }
}
function iniciarFeed(){
  E.orden=INSIGHTS.map((_,i)=>i);
  for(let i=E.orden.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[E.orden[i],E.orden[j]]=[E.orden[j],E.orden[i]];}
  Object.assign(E,{idx:0,pts:0,wallet:0,correctas:0,racha:0,rachaMax:0});
  construirBarra();cambiarPantalla('screen-intro','screen-feed');mostrarInsight();
}
function cambiarPantalla(a,b){
  document.getElementById(a).classList.remove('active');
  document.getElementById(b).classList.add('active');
  window.scrollTo(0,0);
}
function mostrarInsight(){
  if(E.idx>=E.orden.length){mostrarResumen();return;}
  const ins=INSIGHTS[E.orden[E.idx]];
  E.respondido=false;E.enTimer=true;
  document.getElementById('action-panel').style.display='none';
  document.getElementById('mc-feedback').style.display='none';
  document.getElementById('vp-accordion').style.display='none';
  const mi=getMInfo(ins.categoria);
  const mult=mi.m*(1+E.multBonus);
  const mb=document.getElementById('mult-badge');
  mb.textContent=mi.l;
  mb.style.cssText='color:'+mi.c+';border-color:'+mi.c+'55;background:'+mi.c+'18;';
  document.getElementById('reel-sponsor').textContent=ins.sponsor;
  document.getElementById('reel-body').innerHTML=
    '<div class="reel-hero" style="background:'+ins.bg+'">'
    +'<div class="reel-emoji">'+ins.emoji+'</div>'
    +'<div class="reel-stat-wrapper">'
    +'<div class="reel-stat-number" style="color:'+ins.col+'">'+ins.stat.n+'</div>'
    +'<div class="reel-stat-unit">'+ins.stat.u+'</div></div>'
    +'<div class="reel-headline">'+ins.headline+'</div>'
    +'<div class="reel-context">'+ins.context+'</div></div>'
    +'<div class="reel-footer">'
    +'<div class="reel-category" style="color:'+ins.col+'">'+ins.categoria+'</div>'
    +'<div class="reel-reward-preview">+$'+(ins.rb*mult).toFixed(2)+' &middot; '+mi.l+'</div></div>';
  document.getElementById('vp-escena').textContent    =ins.vp.esc;
  document.getElementById('vp-narracion').textContent =ins.vp.nar;
  document.getElementById('vp-cta').textContent       =ins.vp.cta;
  const card=document.getElementById('reel-card');
  card.style.animation='none';card.offsetWidth;card.style.animation='';
  actualizarBarra();iniciarTimer(ins);
}
function iniciarTimer(ins){
  clearInterval(E.timerInt);
  const ring=document.getElementById('ring-fill'),sec=document.getElementById('timer-seconds'),CIRC=163.36;
  ring.style.transition='none';ring.style.strokeDashoffset='0';ring.classList.remove('urgent');
  sec.textContent=TIMER_S;
  const sf=document.querySelector('.ep-seg:nth-child('+(E.idx+1)+') .ep-seg-fill');
  if(sf){sf.style.transition='none';sf.style.width='0%';sf.offsetWidth;sf.style.transition='width '+TIMER_S+'s linear';sf.style.width='100%';}
  let elapsed=0;
  E.timerInt=setInterval(function(){
    elapsed+=100;
    ring.style.strokeDashoffset=String(CIRC*elapsed/(TIMER_S*1000));
    const rem=Math.ceil((TIMER_S*1000-elapsed)/1000);
    sec.textContent=Math.max(0,rem);
    if(rem<=2)ring.classList.add('urgent');
    if(elapsed>=TIMER_S*1000){clearInterval(E.timerInt);E.enTimer=false;if(!E.respondido)mostrarPregunta(ins);}
  },100);
}
function mostrarPregunta(ins){
  document.getElementById('mc-question').textContent=ins.q;
  const letras=['A','B','C','D'],orden=[0,1,2,3].sort(function(){return Math.random()-0.5;});
  const el=document.getElementById('mc-options');el.innerHTML='';
  orden.forEach(function(opIdx,i){
    const op=ins.opts[opIdx],btn=document.createElement('button');
    btn.className='mc-opt';btn.dataset.c=op.c;
    btn.innerHTML='<span class="opt-letter">'+letras[i]+'</span> '+op.t;
    btn.onclick=function(){responder(btn,ins);};
    el.appendChild(btn);
  });
  document.getElementById('action-panel').style.display='block';
}
function responder(btn,ins){
  if(E.respondido)return;
  E.respondido=true;
  const ok=btn.dataset.c==='true';
  document.querySelectorAll('.mc-opt').forEach(function(b){
    b.disabled=true;
    if(b.dataset.c==='true')b.classList.add('correct-opt');
    else if(b===btn&&!ok)b.classList.add('wrong-opt');
  });
  const mult=getMult(ins.categoria)*(1+E.multBonus);
  var pts,rew;
  if(ok){
    pts=100;rew=ins.rb*mult;E.correctas++;E.racha++;
    if(E.racha>E.rachaMax)E.rachaMax=E.racha;
    if(E.racha>1){pts+=20*(E.racha-1);rew+=0.01*(E.racha-1)*mult;}
    actualizarCombo();
  }else{
    pts=20;rew=ins.rb*0.2;E.racha=0;
    document.getElementById('combo-badge').classList.remove('show');
    document.getElementById('reel-card').classList.remove('combo-glow');
  }
  E.pts+=pts;E.wallet+=rew;E.ptsTotal+=pts;E.walletTotal+=rew;
  actualizarWalletHUD(rew);actualizarNivelHUD();checkHitos();mostrarFeedback(ok,pts,rew,ins);
}
function checkHitos(){
  for(var i=0;i<HITOS.length;i++){
    var h=HITOS[i];
    if(E.hitosOk.indexOf(h.id)>=0)continue;
    if(E.ptsTotal>=h.pts){E.hitosOk.push(h.id);E.multBonus+=h.bonus;E.hitoPend=h;guardar();}
  }
}
function mostrarFeedback(ok,pts,rew,ins){
  document.getElementById('action-panel').style.display='none';
  document.getElementById('mc-fb-icon').textContent=ok?'X correcto':'X incorrecto';
  document.getElementById('mc-fb-icon').textContent=ok?'OK':'ERROR';
  document.getElementById('mc-fb-msg').innerHTML=(ok?'+'+pts+' pts / +$'+rew.toFixed(2):'+'+pts+' pts / +$'+rew.toFixed(2)+' (viste el contenido)')+'<br>'+ins.exp;
  document.getElementById('mc-feedback').style.display='flex';
  document.getElementById('vp-accordion').style.display='block';
  if(E.hitoPend){var h=E.hitoPend;E.hitoPend=null;setTimeout(function(){mostrarModalHito(h);},800);}
}
function siguienteInsight(){
  document.getElementById('mc-feedback').style.display='none';
  document.getElementById('vp-accordion').style.display='none';
  marcarDone();E.idx++;mostrarInsight();
}
function actualizarWalletHUD(delta){
  document.getElementById('wallet-display').textContent='$'+E.wallet.toFixed(2);
  var d=document.getElementById('wallet-delta');
  d.textContent='+$'+delta.toFixed(2);d.classList.add('show');
  setTimeout(function(){d.classList.remove('show');},1200);
}
function actualizarNivelHUD(){document.getElementById('level-badge').textContent='Nv. '+getNivel(E.pts).nombre;}
function actualizarCombo(){
  var badge=document.getElementById('combo-badge');
  if(E.racha>=3){
    badge.textContent=E.racha>=5?'COMBO x'+E.racha:'RACHA x'+E.racha;
    badge.classList.add('show');
    document.getElementById('reel-card').classList.toggle('combo-glow',E.racha>=5);
  }
}
function construirBarra(){
  var bar=document.getElementById('episodes-bar');bar.innerHTML='';
  E.orden.forEach(function(){
    var s=document.createElement('div');s.className='ep-seg';
    var f=document.createElement('div');f.className='ep-seg-fill';
    s.appendChild(f);bar.appendChild(s);
  });
}
function actualizarBarra(){document.querySelectorAll('.ep-seg').forEach(function(s,i){s.classList.toggle('done',i<E.idx);});}
function marcarDone(){var segs=document.querySelectorAll('.ep-seg');if(segs[E.idx])segs[E.idx].classList.add('done');}
function mostrarModalHito(h){
  document.getElementById('hito-emoji').textContent    =h.emoji;
  document.getElementById('hito-titulo').textContent   =h.titulo;
  document.getElementById('hito-desc').textContent     =h.desc;
  document.getElementById('hito-badge-txt').textContent=h.badge;
  document.getElementById('hito-bonus-txt').textContent=h.bonus>0?'+'+Math.round(h.bonus*100)+'% multiplicador permanente':'';
  document.getElementById('hito-li-btn').dataset.txt   =h.txt;
  document.getElementById('hito-x-btn').dataset.txt    =h.txt;
  document.getElementById('modal-hito').classList.add('show');
  lanzarConfetti();
}
function cerrarModalHito(){document.getElementById('modal-hito').classList.remove('show');}
function compartirLI(){
  var txt=document.getElementById('hito-li-btn').dataset.txt;
  window.open('https://www.linkedin.com/feed/?shareActive=true&text='+encodeURIComponent(txt+'\n'+location.href),'_blank');
}
function compartirX(){
  var txt=document.getElementById('hito-x-btn').dataset.txt;
  window.open('https://twitter.com/intent/tweet?text='+encodeURIComponent(txt)+'&url='+encodeURIComponent(location.href),'_blank');
}
function lanzarConfetti(){
  var c=document.getElementById('confetti-container');if(!c)return;c.innerHTML='';
  var cols=['#6366f1','#f59e0b','#10b981','#f87171','#22d3ee','#a78bfa'];
  for(var i=0;i<48;i++){
    var p=document.createElement('div');p.className='confetti-piece';
    p.style.cssText='left:'+Math.random()*100+'%;background:'+cols[i%cols.length]+';animation-delay:'+Math.random()*0.4+'s;animation-duration:'+(0.7+Math.random()*0.8)+'s;width:'+(5+Math.random()*7)+'px;height:'+(5+Math.random()*7)+'px;border-radius:'+(Math.random()>0.5?'50%':'2px');
    c.appendChild(p);
  }
  setTimeout(function(){c.innerHTML='';},2000);
}
function descargarShareCard(){
  var nv=getNivel(E.ptsTotal);
  var canvas=document.createElement('canvas');canvas.width=1080;canvas.height=566;
  var ctx=canvas.getContext('2d');
  var g=ctx.createLinearGradient(0,0,1080,566);g.addColorStop(0,'#060810');g.addColorStop(1,'#0d0f1e');
  ctx.fillStyle=g;ctx.fillRect(0,0,1080,566);
  var ga=ctx.createRadialGradient(150,80,0,150,80,380);ga.addColorStop(0,'rgba(99,102,241,0.35)');ga.addColorStop(1,'transparent');
  ctx.fillStyle=ga;ctx.fillRect(0,0,1080,566);
  ctx.fillStyle='#818cf8';ctx.font='bold 26px monospace';ctx.fillText('MicroSecure',60,72);
  ctx.fillStyle='rgba(255,255,255,0.05)';ctx.fillRect(60,100,960,130);
  ctx.fillStyle='#f1f5f9';ctx.font='bold 60px monospace';ctx.fillText(nv.emoji+'  '+nv.nombre.toUpperCase(),80,188);
  ctx.fillStyle='#94a3b8';ctx.font='22px monospace';ctx.fillText(nv.desc,80,245);
  ctx.fillStyle='#10b981';ctx.font='bold 52px monospace';ctx.fillText('$'+E.walletTotal.toFixed(2),80,340);
  ctx.fillStyle='#64748b';ctx.font='18px monospace';ctx.fillText('RECOMPENSA ACUMULADA',80,374);
  ctx.fillStyle='#6366f1';ctx.font='bold 20px monospace';ctx.fillText(E.ptsTotal+' pts  |  '+E.hitosOk.length+' hitos',80,428);
  ctx.fillStyle='#3f4a5e';ctx.font='16px monospace';ctx.fillText('Aprende ciberseguridad en 8 segundos - link.mercadopago.com.ar/trwe',80,510);
  var url=canvas.toDataURL('image/png');
  var a=document.createElement('a');a.download='microsecure-logro.png';a.href=url;a.click();
}
function mostrarResumen(){
  guardar();
  cambiarPantalla('screen-feed','screen-summary');
  var nv=getNivel(E.pts);
  document.getElementById('summary-amount').textContent    ='$'+E.wallet.toFixed(2);
  document.getElementById('wallet-bar-current').textContent='$'+E.walletTotal.toFixed(2);
  document.getElementById('wallet-total-label').textContent='Total acumulado: $'+E.walletTotal.toFixed(2);
  document.getElementById('ss-pts').textContent    =E.pts;
  document.getElementById('ss-correct').textContent=E.correctas+'/'+E.orden.length;
  document.getElementById('ss-streak').textContent =E.rachaMax;
  document.getElementById('level-result-icon').textContent=nv.emoji;
  document.getElementById('level-result-name').textContent=nv.nombre.toUpperCase();
  document.getElementById('level-result-desc').textContent=nv.desc;
  var pct=Math.min((E.walletTotal/META)*100,100);
  setTimeout(function(){document.getElementById('wallet-bar-fill').style.width=pct+'%';},600);
  var hBox=document.getElementById('hitos-sesion');
  if(hBox&&E.hitosOk.length){
    hBox.innerHTML=E.hitosOk.map(function(id){var h=HITOS.find(function(x){return x.id===id;});return h?'<span class="hito-chip">'+h.emoji+' '+h.badge+'</span>':'';}).join('');
    hBox.style.display='flex';
  }
}
function abrirRetiro(m){
  var urls={mp:'https://link.mercadopago.com.ar/trwe',paypal:'https://www.paypal.com/donate/?business=tomasreis44%40gmail.com&currency_code=USD'};
  window.open(urls[m]||urls.mp,'_blank');
}
function compartir(){
  var nv=getNivel(E.pts);
  var txt='Alcance el nivel "'+nv.nombre+'" en MicroSecure y gane $'+E.wallet.toFixed(2)+' aprendiendo ciberseguridad!';
  if(navigator.share)navigator.share({title:'MicroSecure',text:txt,url:location.href});
  else navigator.clipboard.writeText(txt+'\n'+location.href).then(function(){alert('Copiado!');});
}
function irProfundidad(){window.open('https://www.youtube.com/@BestiaTantrica','_blank');}
function reiniciar(){
  Object.assign(E,{idx:0,pts:0,wallet:0,correctas:0,racha:0,rachaMax:0});
  for(var i=E.orden.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var tmp=E.orden[i];E.orden[i]=E.orden[j];E.orden[j]=tmp;}
  construirBarra();cambiarPantalla('screen-summary','screen-feed');mostrarInsight();
}
function toggleVP(){
  var body=document.getElementById('vp-body'),icon=document.getElementById('vp-icon');
  var open=body.style.display==='block';
  body.style.display=open?'none':'block';
  icon.textContent=open?'ABRIR':'CERRAR';
}
document.addEventListener('keydown',function(e){
  if(e.key==='Enter'&&document.getElementById('mc-feedback').style.display!=='none')siguienteInsight();
});
window.addEventListener('DOMContentLoaded',initIntro);
