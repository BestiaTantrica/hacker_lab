// MicroSecure V5 — Motor "Choose Your Own Adventure"
const META_DOLARES = 5.00;

// Multiplicadores por Mercado Laboral
const MULTS = {
  'BUG BOUNTY':     {m: 3.0, l: '3x BOUNTY',  c: '#f59e0b'},
  'CLOUD SECURITY': {m: 2.5, l: '2.5x CLOUD', c: '#06b6d4'},
  'INCIDENTES':     {m: 2.0, l: '2x SOC',     c: '#a78bfa'},
  'SOCIAL':         {m: 1.5, l: '1.5x HUMAN', c: '#fbbf24'},
  'BASE':           {m: 1.0, l: '1x BASE',    c: '#64748b'},
};
const getMInfo = cat => MULTS[cat] || MULTS['BASE'];

// Grafo Narrativo de Nodos
const NODOS = {
  "inicio": {
    categoria: "SOCIAL",
    titulo: "El Gancho Perfecto",
    narracion: "Es viernes a las 17:45. Llega un mail de 'Recursos Humanos': 'Actualización de política de bonos 2026. Acción requerida hoy'. Tiene un link a un portal de login.",
    videoPrompt: "🎬 POV Escritorio. Pantalla muestra notificación de correo. Asunto jugoso. Reloj marca 17:45. Música de tensión sutil.",
    sponsor: "Patrocinado por Proofpoint",
    opciones: [
      { t: "Hacer clic rápido para no perder el bono.", next: "caida_phishing", rew: 0, exp: "La urgencia es la táctica #1 del phishing. Acabás de caer en la trampa." },
      { t: "Revisar la dirección del remitente cuidadosamente.", next: "analisis_remitente", rew: 0.10, exp: "Excelente instinto. Detenerse a mirar es tu primera línea de defensa." },
      { t: "Ignorarlo, RH siempre avisa por Slack.", next: "ignorar_seguro", rew: 0.05, exp: "Opción segura, pero como analista dejaste pasar un posible ataque a la empresa." }
    ]
  },
  "caida_phishing": {
    categoria: "INCIDENTES",
    titulo: "Credenciales Comprometidas",
    narracion: "El link te llevó a un login idéntico al de la empresa. Ingresaste tu clave. De repente, la pantalla se congela y un archivo .exe se descarga en background.",
    videoPrompt: "🎬 Pantalla de login clonada. El usuario teclea. Al apretar 'Enter', glitch digital. Terminal oculta descargando payload.",
    sponsor: "Patrocinado por CrowdStrike",
    opciones: [
      { t: "Apagar la computadora de un tirón (Hard Reset).", next: "apagon_hard", rew: 0.15, exp: "Medida drástica pero efectiva para detener un cifrado en progreso por Ransomware." },
      { t: "Llamar a IT de inmediato sin tocar nada.", next: "reporte_incidente", rew: 0.20, exp: "Protocolo correcto. Preservar la escena permite a IT contener la brecha." },
      { t: "Borrar el historial del navegador para que no te reten.", next: "peor_error", rew: 0, exp: "Acabás de destruir la evidencia forense y el atacante sigue en la red." }
    ]
  },
  "analisis_remitente": {
    categoria: "SOCIAL",
    titulo: "La Letra Oculta",
    narracion: "Mirás de cerca. El correo viene de 'rrhh@empresa-corp.co' en lugar de '.com'. Es un dominio registrado hace 2 días.",
    videoPrompt: "🎬 Zoom extremo al cliente de correo. Resaltado en rojo intenso: '.co' en lugar de '.com'. Efecto de revelación sonora.",
    sponsor: "Patrocinado por Cloudflare",
    opciones: [
      { t: "Reportarlo como phishing al equipo de seguridad.", next: "reporte_exitoso", rew: 0.25, exp: "¡Perfecto! Identificaste el IOC (Indicador de Compromiso) y protegiste a tus compañeros." },
      { t: "Responderle al atacante insultándolo.", next: "error_novato", rew: 0, exp: "Pésima idea. Le confirmaste al atacante que tu correo está activo y que lo lees." }
    ]
  },
  "ignorar_seguro": {
    categoria: "INCIDENTES",
    titulo: "Propagación Silenciosa",
    narracion: "Lo ignoraste, pero 10 minutos después, escuchás a tu compañero decir 'Uy, me pidieron el login para el bono'.",
    videoPrompt: "🎬 POV mirando al compañero. Él hace clic. Vos sabés lo que va a pasar. Tensión.",
    sponsor: "Patrocinado por Microsoft Security",
    opciones: [
      { t: "Gritarle que desconecte el cable de red YA.", next: "apagon_hard", rew: 0.15, exp: "Aislar la máquina es el paso 1 de contención." },
      { t: "Reenviar el correo de advertencia a todos.", next: "reporte_exitoso", rew: 0.10, exp: "Buena iniciativa, aunque IT debería coordinar la comunicación." }
    ]
  },
  "peor_error": {
    categoria: "INCIDENTES",
    titulo: "Día Cero",
    narracion: "Por ocultar tu error, el ransomware tuvo tiempo de escanear la red. Al día siguiente, todos los servidores están cifrados.",
    videoPrompt: "🎬 Time-lapse de noche. Pantallas de toda la oficina encendiéndose rojas con calaveras. Fin del juego corporativo.",
    sponsor: "Patrocinado por Backblaze",
    opciones: [
      { t: "Aceptar tu error y reiniciar tu carrera.", next: "inicio", rew: 0, exp: "La transparencia en seguridad salva empresas. Ocultarlo las destruye." }
    ]
  },
  "apagon_hard": {
    categoria: "INCIDENTES",
    titulo: "Contención Brutal",
    narracion: "Tiraste del cable. La máquina se apagó. IT llega corriendo. Te dicen que salvaste la red principal por segundos.",
    videoPrompt: "🎬 Acción rápida: mano arranca cable Ethernet. Fundido a negro. IT llega agitado.",
    sponsor: "Patrocinado por Mandiant",
    opciones: [
      { t: "Exigir un aumento de sueldo.", next: "exploracion_cloud", rew: 0.20, exp: "Salvaste el día. Ahora pasemos a ligas mayores: Seguridad en la Nube." },
      { t: "Pedir que te enseñen qué pasó exactamente.", next: "exploracion_cloud", rew: 0.25, exp: "Esa es la actitud de un verdadero profesional de seguridad." }
    ]
  },
  "error_novato": {
    categoria: "SOCIAL",
    titulo: "Ataque Dirigido",
    narracion: "Al responderle, el atacante sabe que existís. Al día siguiente, recibís un SMS en tu celular privado simulando ser tu banco.",
    videoPrompt: "🎬 Plano de celular vibrando. Notificación de SMS urgente. El atacante pivoteó del email corporativo a tu vida personal.",
    sponsor: "Patrocinado por Authy",
    opciones: [
      { t: "Empezar de nuevo y ser más cauteloso.", next: "inicio", rew: 0, exp: "En seguridad, nunca interactúes con la infraestructura del atacante." }
    ]
  },
  "reporte_exitoso": {
    categoria: "CLOUD SECURITY",
    titulo: "Ascenso a la Nube",
    narracion: "Por tu buen accionar, te dan acceso a auditar la infraestructura en la nube de la empresa (AWS). Encontrás un bucket S3 llamado 'backups-2026' configurado como 'Público'.",
    videoPrompt: "🎬 Pantalla de AWS S3. Un switch amarillo enorme dice 'Público'. Adentro hay archivos .sql con datos de clientes.",
    sponsor: "Patrocinado por AWS Security",
    opciones: [
      { t: "Descargar los datos para ver si son reales.", next: "error_legal", rew: 0, exp: "Acabás de violar la cadena de custodia y las leyes de privacidad (GDPR). No extraigas datos." },
      { t: "Cambiar el bucket a 'Privado' inmediatamente.", next: "cloud_hero", rew: 0.40, exp: "Remediación instantánea. Frenaste una fuga masiva de datos (Data Breach)." },
      { t: "Dejarlo así y reportarlo pasivamente a DevOps.", next: "cloud_lento", rew: 0.10, exp: "Mientras DevOps lee el ticket, un bot de Telegram ya indexó el bucket." }
    ]
  },
  "error_legal": {
    categoria: "CLOUD SECURITY",
    titulo: "Problemas Legales",
    narracion: "Al descargar la base de datos de clientes, el sistema DLP (Data Loss Prevention) te marca como amenaza interna. RRHH te llama a la oficina.",
    videoPrompt: "🎬 Notificación de alerta roja en consola de SOC. Perfil del empleado (tú) marcado como 'Amenaza Severa'.",
    sponsor: "Patrocinado por Varonis",
    opciones: [
      { t: "Aprender la lección sobre leyes forenses.", next: "inicio", rew: 0, exp: "En Bug Bounty y auditorías, NUNCA exfiltres datos de usuarios reales." }
    ]
  },
  "cloud_lento": {
    categoria: "CLOUD SECURITY",
    titulo: "Demasiado Tarde",
    narracion: "DevOps tardó 2 días en leer el ticket. En ese tiempo, el grupo de ransomware LockBit descargó la base de datos y la publicó en la Dark Web.",
    videoPrompt: "🎬 Foro de la Dark Web. Un post anuncia: 'Database EMPRESA-CORP leaked'. Precio: $500.",
    sponsor: "Patrocinado por HaveIBeenPwned",
    opciones: [
      { t: "Aprender que la criticidad requiere acción inmediata.", next: "inicio", rew: 0, exp: "Un bucket público es un incidente activo (P1), no un ticket normal." }
    ]
  },
  "cloud_hero": {
    categoria: "BUG BOUNTY",
    titulo: "Cazador de Recompensas",
    narracion: "Cerraste la brecha. Te das cuenta que tenés talento para esto. Descubrís que empresas como Uber y Airbnb pagan miles de dólares por encontrar vulnerabilidades legalmente en HackerOne.",
    videoPrompt: "🎬 Pantalla mostrando un reporte aprobado en HackerOne. Bounty Awarded: $5,000. Lluvia de billetes sutil.",
    sponsor: "Patrocinado por HackerOne",
    opciones: [
      { t: "Probar interceptar peticiones con Burp Suite.", next: "bounty_idor", rew: 0.30, exp: "Bienvenido al lado técnico. El proxy HTTP es tu mejor amigo." },
      { t: "Buscar subdominios olvidados (Takeovers).", next: "bounty_recon", rew: 0.30, exp: "El reconocimiento pasivo es la base del Bug Bounty moderno." }
    ]
  },
  "bounty_idor": {
    categoria: "BUG BOUNTY",
    titulo: "El IDOR de $3,000",
    narracion: "Usando Burp Suite, notás que la API pide tus datos en `/api/user/100`. Cambiás el 100 por el 101... ¡y ves los datos de otra persona!",
    videoPrompt: "🎬 Interfaz de Burp Suite Repeater. Número 100 se borra, se tipea 101. Botón SEND. El Response muestra 'Juan Perez' y su tarjeta.",
    sponsor: "Patrocinado por PortSwigger",
    opciones: [
      { t: "Reportarlo inmediatamente en HackerOne.", next: "fin_victoria", rew: 0.50, exp: "IDOR (Insecure Direct Object Reference) es la vulnerabilidad más lucrativa." }
    ]
  },
  "bounty_recon": {
    categoria: "BUG BOUNTY",
    titulo: "Subdomain Takeover",
    narracion: "Encontrás un subdominio `soporte.empresa.com` que apunta a un bucket de AWS que ya no existe (404 NoSuchBucket).",
    videoPrompt: "🎬 Consola negra. Herramienta 'nuclei' encuentra un target. Texto verde brilla: [takeover] soporte.empresa.com.",
    sponsor: "Patrocinado por ProjectDiscovery",
    opciones: [
      { t: "Registrar un bucket con ese mismo nombre.", next: "fin_victoria", rew: 0.50, exp: "Al hacerlo, tomas control del subdominio de la empresa. Impacto crítico." }
    ]
  },
  "fin_victoria": {
    categoria: "BASE",
    titulo: "Operador de Élite",
    narracion: "Recibís tu primer pago de Bug Bounty de $3,000. Has demostrado que podés pensar como un atacante para defender a otros. Tu viaje recién comienza.",
    videoPrompt: "🎬 Notificación de transferencia bancaria entrante. Fondo oscuro hacker. Texto final: 'El conocimiento es poder'.",
    sponsor: "Patrocinado por MicroSecure",
    opciones: [
      { t: "Registrarme para más misiones y guardar mi progreso.", next: "registro_lead", rew: 0.0, exp: "Fidelización de talento." },
      { t: "Volver al inicio.", next: "inicio", rew: 0.0, exp: "Reiniciar el loop." }
    ]
  },
  "registro_lead": {
    categoria: "BASE",
    titulo: "Únete a la Red",
    narracion: "Para guardar tu billetera y subir al ranking global, necesitamos tu email. No enviamos spam, solo alertas de misiones nuevas.",
    videoPrompt: "🎬 Interfaz futurista de creación de identidad digital.",
    sponsor: "MicroSecure Network",
    isLeadCapture: true,
    opciones: []
  }
};

// ESTADO V5
let E = {
  nodoActual: "inicio",
  wallet: 0.0,
  walletTotal: 0.0,
  historial: [],
  email: null
};

// PERSISTENCIA
function cargar(){
  E.walletTotal = parseFloat(localStorage.getItem('ms5_wt') || '0');
  E.email = localStorage.getItem('ms5_mail');
}
function guardar(){
  localStorage.setItem('ms5_wt', E.walletTotal.toFixed(4));
  if(E.email) localStorage.setItem('ms5_mail', E.email);
}

// INTRO
function initIntro(){
  cargar();
  const wp = document.getElementById('wallet-prev');
  if(wp) wp.textContent = '$' + E.walletTotal.toFixed(2);
  
  if(E.email) {
    const s = document.querySelector('.sponsor-note');
    if(s) s.innerHTML = `Bienvenido de vuelta, <b>${E.email}</b>.`;
  }
}

// FLUJO CYOA
function iniciarHistoria(){
  E.wallet = 0.0;
  E.historial = [];
  E.nodoActual = "inicio";
  cambiarPantalla('screen-intro', 'screen-feed');
  mostrarNodo(E.nodoActual);
}

function cambiarPantalla(a,b){
  document.getElementById(a).classList.remove('active');
  document.getElementById(b).classList.add('active');
  window.scrollTo(0,0);
}

function mostrarNodo(id) {
  E.nodoActual = id;
  const nodo = NODOS[id];
  if(!nodo) return; // Error de ruta

  E.historial.push(id);
  
  // UI de la Tarjeta
  const mi = getMInfo(nodo.categoria);
  
  // Actualizar Badge Multiplicador
  const mb = document.getElementById('mult-badge');
  mb.textContent = mi.l;
  mb.style.cssText = `color:${mi.c};border-color:${mi.c}55;background:${mi.c}18;`;
  
  document.getElementById('reel-sponsor').textContent = nodo.sponsor;
  document.getElementById('nodo-titulo').textContent = nodo.titulo;
  document.getElementById('nodo-narracion').textContent = nodo.narracion;
  
  // Video Prompt (Integrado en el diseño principal, no acordeón)
  const vpText = document.getElementById('vp-text');
  vpText.textContent = nodo.videoPrompt;
  
  // Generar Opciones Dinámicas
  const optsContainer = document.getElementById('opciones-container');
  optsContainer.innerHTML = '';
  
  if(nodo.isLeadCapture) {
    // Renderizar Formulario de Lead
    optsContainer.innerHTML = `
      <div class="lead-form">
        <input type="email" id="lead-email" placeholder="tu@email.com" class="lead-input" required>
        <button class="btn-lead" onclick="guardarLead()">Guardar Progreso</button>
        <button class="btn-lead-skip" onclick="mostrarResumen()">Omitir y ver resumen</button>
      </div>
    `;
  } else {
    // Renderizar Botones Narrativos
    nodo.opciones.forEach((op, i) => {
      const mult = mi.m;
      const recompensaReal = op.rew * mult;
      const btn = document.createElement('button');
      btn.className = 'btn-opcion-narrativa';
      
      let rewardHTML = '';
      if(recompensaReal > 0) {
        rewardHTML = `<span class="op-reward-tag">+$${recompensaReal.toFixed(2)}</span>`;
      }
      
      btn.innerHTML = `<div class="op-texto">${op.t}</div> ${rewardHTML}`;
      btn.onclick = () => procesarDecision(op, recompensaReal, mi);
      optsContainer.appendChild(btn);
    });
  }

  // Animación de entrada de la tarjeta
  const card = document.getElementById('reel-card');
  card.style.animation = 'none'; card.offsetWidth; card.style.animation = '';
  
  // Limpiar panel de feedback
  document.getElementById('feedback-panel').style.display = 'none';
  optsContainer.style.display = 'flex';
}

function procesarDecision(opcion, recompensaReal, mi) {
  // Ocultar opciones, mostrar feedback
  document.getElementById('opciones-container').style.display = 'none';
  
  // Actualizar Billetera
  if(recompensaReal > 0) {
    E.wallet += recompensaReal;
    E.walletTotal += recompensaReal;
    actualizarWalletHUD(recompensaReal);
    guardar();
  }
  
  const fbPanel = document.getElementById('feedback-panel');
  const esBuena = recompensaReal > 0;
  
  document.getElementById('fb-icon').textContent = esBuena ? '📈' : '📉';
  document.getElementById('fb-icon').className = 'fb-icon ' + (esBuena ? 'buena' : 'mala');
  
  document.getElementById('fb-recompensa').textContent = esBuena ? `+$${recompensaReal.toFixed(2)} ganados` : `Sin recompensa`;
  document.getElementById('fb-recompensa').style.color = esBuena ? '#10b981' : '#f87171';
  
  document.getElementById('fb-explicacion').textContent = opcion.exp;
  
  // Configurar botón "Siguiente Escena"
  const btnSig = document.getElementById('btn-siguiente-escena');
  btnSig.onclick = () => mostrarNodo(opcion.next);
  
  fbPanel.style.display = 'flex';
}

function guardarLead() {
  const mail = document.getElementById('lead-email').value;
  if(mail && mail.includes('@')) {
    E.email = mail;
    guardar();
    mostrarResumen();
  } else {
    alert("Por favor ingresa un correo válido.");
  }
}

// HUD
function actualizarWalletHUD(delta){
  document.getElementById('wallet-display').textContent = '$' + E.wallet.toFixed(2);
  const d = document.getElementById('wallet-delta');
  d.textContent = '+$' + delta.toFixed(2);
  d.classList.add('show');
  setTimeout(() => d.classList.remove('show'), 1200);
}

// SHARE CARD V5
function descargarShareCard(){
  const canvas = document.createElement('canvas'); canvas.width = 1080; canvas.height = 566;
  const ctx = canvas.getContext('2d');
  
  const g = ctx.createLinearGradient(0,0,1080,566);
  g.addColorStop(0,'#060810'); g.addColorStop(1,'#0d0f1e');
  ctx.fillStyle = g; ctx.fillRect(0,0,1080,566);
  
  const ga = ctx.createRadialGradient(150,80,0,150,80,380);
  ga.addColorStop(0,'rgba(99,102,241,0.35)'); ga.addColorStop(1,'transparent');
  ctx.fillStyle = ga; ctx.fillRect(0,0,1080,566);
  
  ctx.fillStyle = '#818cf8'; ctx.font = 'bold 26px monospace'; ctx.fillText('MicroSecure', 60, 72);
  
  ctx.fillStyle = 'rgba(255,255,255,0.05)'; ctx.beginPath();
  if(ctx.roundRect) ctx.roundRect(60,100,960,130,16); else ctx.rect(60,100,960,130);
  ctx.fill();
  
  ctx.fillStyle = '#f1f5f9'; ctx.font = 'bold 64px monospace'; 
  ctx.fillText(`CIBER-AGENTE`, 80, 188);
  
  ctx.fillStyle = '#94a3b8'; ctx.font = '22px monospace'; 
  ctx.fillText('Ha sobrevivido a la simulación corporativa.', 80, 248);
  
  ctx.fillStyle = '#10b981'; ctx.font = 'bold 52px monospace'; ctx.fillText('$' + E.walletTotal.toFixed(2), 80, 340);
  ctx.fillStyle = '#64748b'; ctx.font = '18px monospace'; ctx.fillText('RECOMPENSA ACUMULADA', 80, 374);
  
  ctx.fillStyle = '#6366f1'; ctx.font = 'bold 20px monospace'; ctx.fillText(`${E.historial.length} decisiones tomadas`, 80, 428);
  
  ctx.fillStyle = '#3f4a5e'; ctx.font = '16px monospace'; ctx.fillText('Sobrevive vos también en link.mercadopago.com.ar/trwe', 80, 510);
  
  const url = canvas.toDataURL('image/png');
  const a = document.createElement('a'); a.download = 'microsecure-logro.png'; a.href = url; a.click();
}

// RESUMEN
function mostrarResumen(){
  guardar();
  cambiarPantalla('screen-feed', 'screen-summary');
  
  document.getElementById('summary-amount').textContent = '$' + E.wallet.toFixed(2);
  document.getElementById('wallet-bar-current').textContent = '$' + E.walletTotal.toFixed(2);
  document.getElementById('wallet-total-label').textContent = 'Total acumulado histórico: $' + E.walletTotal.toFixed(2);
  
  document.getElementById('ss-pts').textContent = E.historial.length; // Nodos visitados
  document.getElementById('ss-correct').textContent = E.email ? "Sí" : "No"; // Registrado
  
  const pct = Math.min((E.walletTotal / META_DOLARES) * 100, 100);
  setTimeout(() => { document.getElementById('wallet-bar-fill').style.width = pct + '%'; }, 600);
}

// DONACIONES Y LINKS
function abrirRetiro(m){
  const urls = {
    mp: 'https://link.mercadopago.com.ar/trwe',
    paypal: 'https://www.paypal.com/donate/?business=tomasreis44%40gmail.com&currency_code=USD'
  };
  window.open(urls[m] || urls.mp, '_blank');
}

function compartir(){
  const txt = `Acabo de completar una simulación de ciberseguridad en MicroSecure y gané $${E.wallet.toFixed(2)}. ¿Podrías sobrevivir vos? 🛡️`;
  if(navigator.share) navigator.share({title:'MicroSecure', text:txt, url:location.href});
  else navigator.clipboard.writeText(txt + '\n' + location.href).then(() => alert('¡Copiado al portapapeles!'));
}

function reiniciar(){
  iniciarHistoria();
}

window.addEventListener('DOMContentLoaded', initIntro);
