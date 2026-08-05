// MicroSecure V6 — Economía Realista, Energía y Perfilamiento
const META_DOLARES = 5.00;

// Multiplicadores Base de Mercado
const MULTS = {
  'BUG BOUNTY':     {m: 3.0, l: '3x BOUNTY',  c: '#f59e0b'},
  'CLOUD SECURITY': {m: 2.5, l: '2.5x CLOUD', c: '#06b6d4'},
  'INCIDENTES':     {m: 2.0, l: '2x SOC',     c: '#a78bfa'},
  'SOCIAL':         {m: 1.5, l: '1.5x HUMAN', c: '#fbbf24'},
  'BASE':           {m: 1.0, l: '1x BASE',    c: '#64748b'},
};
const getMInfo = cat => MULTS[cat] || MULTS['BASE'];

// Grafo Narrativo - Recompensas realistas ($0.01 - $0.05)
const NODOS = {
  "inicio": {
    categoria: "SOCIAL",
    titulo: "El Gancho Perfecto",
    narracion: "Es viernes a las 17:45. Llega un mail de 'RRHH': 'Actualización de política salarial 2026. Acción requerida hoy'. Tiene un PDF adjunto.",
    videoPrompt: "🎬 POV Escritorio. Pantalla muestra notificación de correo. Asunto jugoso. Reloj de PC marca 17:45.",
    sponsor: "Patrocinado por Proofpoint",
    opciones: [
      { t: "Abrir el PDF rápido para ver el bono.", next: "caida_phishing", rew: 0, exp: "La curiosidad mató al gato. Los PDFs pueden ejecutar malware. Perdiste energía." },
      { t: "Revisar la dirección del remitente.", next: "analisis_remitente", rew: 0.01, exp: "Excelente instinto. La pausa táctica es tu mejor defensa. +Energía." },
      { t: "Ignorarlo, RRHH avisa estas cosas por Slack.", next: "ignorar_seguro", rew: 0.01, exp: "Decisión segura, pero dejaste pasar la oportunidad de cazar una amenaza. +Energía." },
      { t: "Subir el PDF a VirusTotal sin abrirlo.", next: "virustotal_win", rew: 0.02, exp: "Pensamiento avanzado. Analizar antes de detonar es de profesionales. ++Energía." }
    ]
  },
  "virustotal_win": {
    categoria: "INCIDENTES",
    titulo: "Cazador de Malware",
    narracion: "VirusTotal marca el archivo con 45/70 detecciones. Es un troyano Emotet.",
    videoPrompt: "🎬 Pantalla de VirusTotal en rojo 'MALICIOUS'.",
    sponsor: "Patrocinado por VirusTotal",
    opciones: [
      { t: "Avisar al equipo de seguridad (SOC).", next: "soc_hero", rew: 0.03, exp: "Protocolo perfecto. La inteligencia compartida salva redes enteras." },
      { t: "Ejecutarlo en una máquina virtual propia.", next: "analisis_forense", rew: 0.02, exp: "Riesgoso pero útil para análisis forense." },
      { t: "Borrar el mail y seguir con tu vida.", next: "ignorar_seguro", rew: 0, exp: "Destruiste evidencia. Pésimo." },
      { t: "Responderle al hacker con un meme.", next: "error_novato", rew: 0, exp: "Nunca confirmes que existís." }
    ]
  },
  "caida_phishing": {
    categoria: "INCIDENTES",
    titulo: "Día Cero",
    narracion: "Abriste el PDF. El fondo de pantalla cambia a negro y aparece un candado rojo.",
    videoPrompt: "🎬 Pantalla inunda de calaveras ASCII rojas. Ransomware activo.",
    sponsor: "Patrocinado por CrowdStrike",
    opciones: [
      { t: "Desconectar la PC de la red y el WiFi.", next: "apagon_hard", rew: 0.02, exp: "Contención nivel hardware. Evitaste propagación lateral." },
      { t: "Pagar el rescate en Bitcoin.", next: "fin_quiebra", rew: 0, exp: "Financiar terrorismo digital no garantiza nada." },
      { t: "Llamar a tu jefe llorando.", next: "fin_despido", rew: 0, exp: "El pánico no resuelve incidentes." },
      { t: "Matar el proceso desde el Administrador de Tareas.", next: "malware_persistente", rew: 0, exp: "Demasiado tarde. Ya inyectó en svchost.exe." }
    ]
  },
  "analisis_remitente": {
    categoria: "SOCIAL",
    titulo: "El Truco Visual",
    narracion: "El correo viene de 'rrhh@empresa-corp.co' (falta la 'm'). Es Typosquatting.",
    videoPrompt: "🎬 Zoom a la barra 'De:'. El '.co' brilla en rojo.",
    sponsor: "Patrocinado por Cloudflare",
    opciones: [
      { t: "Reportarlo con el botón de Phishing.", next: "soc_hero", rew: 0.03, exp: "Entrenás los filtros de correo. Héroe anónimo." },
      { t: "Comprar el dominio .com real.", next: "cloud_hero", rew: 0.01, exp: "Iniciativa de marca, pero el ataque vino desde el .co." },
      { t: "Insultar al remitente.", next: "error_novato", rew: 0, exp: "Mala Opsec. Confirmaste tu existencia." },
      { t: "Hacer Ing. Inversa al server atacante.", next: "analisis_forense", rew: 0.03, exp: "Hack-back es ilegal, pero en simulación suma." }
    ]
  },
  "ignorar_seguro": {
    categoria: "INCIDENTES",
    titulo: "Propagación Silenciosa",
    narracion: "10 minutos después, tu compañero abre el PDF y su PC se congela.",
    videoPrompt: "🎬 Compañero haciendo doble clic. Susurrás 'No...' en cámara lenta.",
    sponsor: "Patrocinado por SentinelOne",
    opciones: [
      { t: "Tirarle del cable de red a su PC.", next: "apagon_hard", rew: 0.02, exp: "Aislar el nodo infectado es regla #1." },
      { t: "Hacerte el distraído.", next: "fin_quiebra", rew: 0, exp: "La inacción te hace cómplice." },
      { t: "Sacar una foto para Twitter.", next: "fin_despido", rew: 0, exp: "Violar confidencialidad = despido." },
      { t: "Reportar el incidente desde tu PC.", next: "soc_hero", rew: 0.02, exp: "Notificaste a los que pueden resolverlo." }
    ]
  },
  "soc_hero": {
    categoria: "CLOUD SECURITY",
    titulo: "Ascenso a la Nube",
    narracion: "IT te agradece. Te piden auditar AWS. Encontrás un Bucket S3 marcado 'Público'.",
    videoPrompt: "🎬 Consola AWS. Cartel naranja 'Publicly Accessible' en bucket 'backups'.",
    sponsor: "Patrocinado por Wiz",
    opciones: [
      { t: "Cambiar permisos a 'Privado' inmediatamente.", next: "cloud_hero", rew: 0.04, exp: "Remediación instantánea. Salvaste la empresa." },
      { t: "Descargar archivos para ver si son reales.", next: "error_legal", rew: 0, exp: "Violar leyes de privacidad (GDPR). Es un delito." },
      { t: "Mandar un ticket a DevOps.", next: "cloud_lento", rew: 0, exp: "La burocracia no frena a los bots." },
      { t: "Escribir script para buscar más buckets.", next: "bounty_recon", rew: 0.03, exp: "Mentalidad de Red Team." }
    ]
  },
  "cloud_hero": {
    categoria: "BUG BOUNTY",
    titulo: "El Cazador",
    narracion: "Te invitan al programa de Bug Bounty. Te pagan por encontrar vulnerabilidades. ¿Por dónde empezás?",
    videoPrompt: "🎬 Perfil HackerOne abriéndose.",
    sponsor: "Patrocinado por HackerOne",
    opciones: [
      { t: "Interceptar API con Burp Suite.", next: "bounty_idor", rew: 0.04, exp: "Análisis dinámico. Mina de oro." },
      { t: "Escanear subdominios abandonados.", next: "bounty_recon", rew: 0.03, exp: "Reconocimiento de superficie." },
      { t: "Lanzar escáner automatizado.", next: "error_ruido", rew: 0, exp: "Genera mucho ruido y WAF te bloquea." },
      { t: "Buscar credenciales en GitHub.", next: "bounty_github", rew: 0.04, exp: "OSINT. Los devs dejan llaves expuestas." }
    ]
  },
  "analisis_forense": {
    categoria: "INCIDENTES",
    titulo: "Juego Peligroso",
    narracion: "El troyano intenta conectarse a un C2 en Rusia. Tenés la IP.",
    videoPrompt: "🎬 Wireshark fluyendo. Filtro IP aplicado.",
    sponsor: "Patrocinado por Wireshark",
    opciones: [
      { t: "Bloquear IP en firewall.", next: "soc_hero", rew: 0.03, exp: "Contención inteligente (IOC)." },
      { t: "Atacar el servidor C2 (DDoS).", next: "error_legal", rew: 0, exp: "Hack-back es un crimen." },
      { t: "Vender la IP en la Dark Web.", next: "fin_quiebra", rew: 0, exp: "Perdiste tu brújula moral." },
      { t: "Analizar qué datos enviaba.", next: "cloud_hero", rew: 0.02, exp: "Descubrís que apuntaban a AWS." }
    ]
  },
  "bounty_idor": {
    categoria: "BUG BOUNTY",
    titulo: "Vulnerabilidad Lógica",
    narracion: "Endpoint `/api/factura/4040`. Cambiás a `4041` y ves la factura de otra empresa.",
    videoPrompt: "🎬 Interfaz de Burp. Se edita el ID y arroja datos de otra corp.",
    sponsor: "Patrocinado por PortSwigger",
    opciones: [
      { t: "Reportar IDOR crítico.", next: "boss_aws", rew: 0.05, exp: "Reporte perfecto de impacto alto." },
      { t: "Bajar todas las facturas.", next: "error_legal", rew: 0, exp: "Excediste límites éticos." },
      { t: "Cobrar rescate a la empresa.", next: "fin_quiebra", rew: 0, exp: "Extorsión." },
      { t: "Probar modificar la factura.", next: "boss_aws", rew: 0.05, exp: "Mass Assignment. Aún más crítico." }
    ]
  },
  "bounty_github": {
    categoria: "BUG BOUNTY",
    titulo: "Secretos a Voces",
    narracion: "Encontrás un archivo `.env` con credenciales de DB de producción en GitHub.",
    videoPrompt: "🎬 Búsqueda en GitHub. Archivo .env crudo.",
    sponsor: "Patrocinado por Truffle Security",
    opciones: [
      { t: "Reportar pidiendo rotación de llave.", next: "boss_aws", rew: 0.05, exp: "Riesgo Crítico P1." },
      { t: "Loguearte a la DB.", next: "error_legal", rew: 0, exp: "Nunca uses credenciales ajenas." },
      { t: "Crear Pull Request borrándolo.", next: "error_novato", rew: 0, exp: "Borrar no lo saca del historial de git." },
      { t: "Escribir regla de CI/CD.", next: "boss_aws", rew: 0.06, exp: "Solución de raíz. DevSecOps puro." }
    ]
  },
  
  // BOSS NODE (Examen Técnico)
  "boss_aws": {
    categoria: "CLOUD SECURITY",
    titulo: "BOSS: Arquitectura de Escala",
    narracion: "Llegaste a la etapa técnica de una entrevista. Te preguntan: '¿Cómo asegurarías un bucket S3 que necesita ser público para imágenes de una web, pero bloqueando bots raspatodo?'",
    videoPrompt: "🎬 Panel de entrevistadores serios. Un cronómetro invisible de presión.",
    sponsor: "ENTREVISTA PATROCINADA POR MERCADO LIBRE TECH",
    isBoss: true,
    opciones: [
      { t: "Poner un WAF (CloudFront + AWS WAF) delante del Bucket.", next: "fin_victoria", rew: 0.15, exp: "¡EXCELENTE! Respuesta arquitectónica correcta de Nivel Senior. Te llevás el jackpot de energía." },
      { t: "Hacer el Bucket privado y usar presigned URLs.", next: "fin_victoria", rew: 0.10, exp: "Respuesta válida para casos específicos, pero poco escalable para imágenes estáticas." },
      { t: "Ocultar la URL del bucket en el código fuente.", next: "error_ruido", rew: 0, exp: "Seguridad por oscuridad. Fallaste la entrevista técnica." },
      { t: "Configurar un CAPTCHA en el bucket.", next: "error_novato", rew: 0, exp: "AWS S3 no soporta lógica de CAPTCHA nativa. Falta de conocimientos Cloud." }
    ]
  },

  // Retornos
  "apagon_hard": {
    categoria: "INCIDENTES",
    titulo: "Control de Daños",
    narracion: "IT te agradece, pero el equipo está frito.",
    videoPrompt: "🎬 Placa base humeando.",
    sponsor: "Patrocinado por Mandiant",
    opciones: [
      { t: "Pedir aprender forense de RAM.", next: "analisis_forense", rew: 0.02, exp: "Hambre de conocimiento." },
      { t: "Exigir aumento.", next: "soc_hero", rew: 0.01, exp: "Audaz." },
      { t: "Volver al puesto en silencio.", next: "ignorar_seguro", rew: 0, exp: "Apatía." },
      { t: "Culpar a RRHH.", next: "fin_despido", rew: 0, exp: "Cero profesionalismo." }
    ]
  },
  "malware_persistente": {
    categoria: "INCIDENTES",
    titulo: "Rootkit Inmortal",
    narracion: "El malware inyectó un Rootkit.",
    videoPrompt: "🎬 Ventanas multiplicándose solas.",
    sponsor: "Patrocinado por Malwarebytes",
    opciones: [
      { t: "Desconectar disco duro.", next: "apagon_hard", rew: 0.02, exp: "Hardware beats software." },
      { t: "Reinstalar Windows encima.", next: "error_novato", rew: 0, exp: "Persistencia de BIOS/UEFI existe." },
      { t: "Huir corriendo.", next: "fin_despido", rew: 0, exp: "Abandono." },
      { t: "Lanzar AV portátil.", next: "virustotal_win", rew: 0.01, exp: "Los rootkits se esconden de AVs simples." }
    ]
  },
  "cloud_lento": {
    categoria: "CLOUD SECURITY",
    titulo: "Demasiado Tarde",
    narracion: "Ransomware robó los datos del bucket.",
    videoPrompt: "🎬 TV: 'Empresa sufre mega filtración'.",
    sponsor: "Patrocinado por Varonis",
    opciones: [
      { t: "Escalar al CISO.", next: "cloud_hero", rew: 0.01, exp: "Fallaste el proceso, pero corregís." },
      { t: "Decir 'Yo avisé'.", next: "fin_despido", rew: 0, exp: "Tener razón no sirve si quiebran." },
      { t: "Rastrear logs de AWS (CloudTrail).", next: "analisis_forense", rew: 0.02, exp: "Mentalidad forense." },
      { t: "Buscar nuevo trabajo.", next: "fin_quiebra", rew: 0, exp: "Cobardía." }
    ]
  },
  "error_novato": {
    categoria: "SOCIAL",
    titulo: "Ataque Dirigido (Vishing)",
    narracion: "Llama tu 'Jefe' (voz clonada por IA) pidiendo una transferencia.",
    videoPrompt: "🎬 Teléfono suena: 'Jefe (Urgente)'.",
    sponsor: "Patrocinado por ElevenLabs Security",
    opciones: [
      { t: "Hacer transferencia.", next: "fin_despido", rew: 0, exp: "Caíste en Deepfake." },
      { t: "Cortar y llamar por Slack oficial.", next: "soc_hero", rew: 0.02, exp: "Verificación Fuera de Banda (OOB)." },
      { t: "Preguntar algo privado.", next: "soc_hero", rew: 0.01, exp: "Autenticación basada en conocimiento." },
      { t: "Insultar a la IA.", next: "inicio", rew: 0, exp: "Mantén el profesionalismo." }
    ]
  },
  "error_legal": {
    categoria: "CLOUD SECURITY",
    titulo: "Problemas de Compliance",
    narracion: "Por extraer datos/atacar, Legal te investiga.",
    videoPrompt: "🎬 Oficina gris. Abogado investigando.",
    sponsor: "Patrocinado por LegalTech",
    opciones: [
      { t: "Contratar abogado y renunciar.", next: "fin_quiebra", rew: 0, exp: "Fin de carrera." },
      { t: "Colaborar mostrando falta de intención.", next: "inicio", rew: 0, exp: "Zafás pero volvés a cero." },
      { t: "Borrar logs de AWS.", next: "fin_despido", rew: 0, exp: "Obstrucción de justicia." },
      { t: "Escribir reporte post-mortem asumiendo culpa.", next: "cloud_hero", rew: 0.01, exp: "Madurez corporativa." }
    ]
  },
  "error_ruido": {
    categoria: "BUG BOUNTY",
    titulo: "Fuerza Bruta Ciega",
    narracion: "Tu escáner tiró el servidor de staging y tu IP fue bloqueada.",
    videoPrompt: "🎬 'Error 403 Forbidden - WAF Blocked'.",
    sponsor: "Patrocinado por Imperva",
    opciones: [
      { t: "Usar VPN y seguir escaneando.", next: "error_legal", rew: 0, exp: "Evasión maliciosa." },
      { t: "Hacer escaneos pausados.", next: "bounty_recon", rew: 0.02, exp: "La precisión gana a la fuerza bruta." },
      { t: "Reportar 'se cae fácil' (DoS).", next: "fin_despido", rew: 0, exp: "DoS está fuera de scope." },
      { t: "Usar Google Dorks (Pasivo).", next: "bounty_github", rew: 0.03, exp: "OSINT no hace ruido." }
    ]
  },
  "bounty_recon": {
    categoria: "BUG BOUNTY",
    titulo: "Subdominio Abandonado",
    narracion: "Subdominio soporte apunta a un S3 que devuelve 404 NoSuchBucket.",
    videoPrompt: "🎬 Ping devuelve '404 NoSuchBucket'.",
    sponsor: "Patrocinado por ProjectDiscovery",
    opciones: [
      { t: "Registrar el bucket vacío a tu nombre.", next: "boss_aws", rew: 0.04, exp: "Subdomain Takeover." },
      { t: "Adivinar archivos adentro.", next: "error_ruido", rew: 0, exp: "Pérdida de tiempo, no existe." },
      { t: "Buscar credenciales en el HTML.", next: "bounty_github", rew: 0.02, exp: "Buen pivote." },
      { t: "Reportar 404 como 'Informativo'.", next: "error_novato", rew: 0, exp: "Desperdiciaste un impacto Crítico." }
    ]
  },
  "fin_quiebra": { categoria: "BASE", titulo: "Carrera Terminada", narracion: "Perdiste credibilidad profesional.", videoPrompt: "🎬 Fondos Insuficientes.", sponsor: "MicroSecure Awareness", opciones: [ { t: "Reflexionar y reiniciar.", next: "inicio", rew: 0, exp: "Hard reset mental." }, { t: "Estudiar programación.", next: "inicio", rew: 0, exp: "Saber construir ayuda a destruir seguro." }, { t: "Crear otro LinkedIn.", next: "inicio", rew: 0, exp: "La DB no olvida." }, { t: "Culpar a todos.", next: "inicio", rew: 0, exp: "Cero autocrítica." } ] },
  "fin_despido": { categoria: "BASE", titulo: "Despedido", narracion: "Tu badge corporativo fue desactivado.", videoPrompt: "🎬 Guardia pide tu tarjeta.", sponsor: "MicroSecure Training", opciones: [ { t: "Entrenar control de pánico.", next: "inicio", rew: 0, exp: "50% técnica, 50% pánico." }, { t: "Análisis post-mortem.", next: "inicio", rew: 0, exp: "Vital." }, { t: "Hackear ex-empresa.", next: "error_legal", rew: 0, exp: "Criminal." }, { t: "Estudiar Compliance.", next: "cloud_lento", rew: 0, exp: "Giro de carrera." } ] },
  "fin_victoria": { categoria: "BASE", titulo: "Agente Validado", narracion: "Has demostrado madurez técnica.", videoPrompt: "🎬 'Misión Completada'.", sponsor: "Patrocinado por MicroSecure", opciones: [ { t: "Registrar mi perfil vocacional.", next: "registro_lead", rew: 0, exp: "Guarda tu data." }, { t: "Ver mi portafolio directo.", next: "resumen", rew: 0, exp: "Vamos al reporte." }, { t: "Farmear más simulaciones.", next: "inicio", rew: 0, exp: "Sigue el minado." }, { t: "Desafiar al sistema.", next: "registro_lead", rew: 0, exp: "Audaz." } ] },
  "registro_lead": { categoria: "BASE", titulo: "Perfil Forense", narracion: "Guardá tu mapa vocacional para ofertas laborales patrocinadas.", videoPrompt: "🎬 Escaneo biométrico.", sponsor: "MicroSecure Talent Hub", isLeadCapture: true, opciones: [] },
  "resumen": { isResumen: true }
};

// ESTADO V6
let E = {
  nodoActual: "inicio",
  wallet: 0.0, // Sesión actual
  walletTotal: 0.0, // Histórico
  historial: [], 
  email: null,
  racha: 1.0 // Sistema de Energía
};

// PERSISTENCIA FIXEADA
function cargar(){
  E.walletTotal = parseFloat(localStorage.getItem('ms6_wt') || '0');
  E.email = localStorage.getItem('ms6_mail');
  try {
    const hs = localStorage.getItem('ms6_hist');
    if(hs) E.historial = JSON.parse(hs);
  } catch(e) { E.historial = []; }
}
function guardar(){
  localStorage.setItem('ms6_wt', E.walletTotal.toFixed(4));
  if(E.email) localStorage.setItem('ms6_mail', E.email);
  localStorage.setItem('ms6_hist', JSON.stringify(E.historial));
}

function initIntro(){
  cargar();
  const wp = document.getElementById('wallet-prev');
  if(wp) wp.textContent = '$' + E.walletTotal.toFixed(2);
  if(E.email) {
    const s = document.querySelector('.sponsor-note');
    if(s) s.innerHTML = `Identidad verificada: <b>${E.email}</b>.`;
  }
}

function iniciarHistoria(){
  E.wallet = 0.0;
  E.racha = 1.0; 
  // No vaciamos E.historial para que el portafolio sea acumulativo a lo largo de las vidas
  cambiarPantalla('screen-intro', 'screen-feed');
  mostrarNodo("inicio");
}

function cambiarPantalla(a,b){
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(b).classList.add('active');
  window.scrollTo(0,0);
}

function actualizarEnergiaUI() {
  const energyDisplay = document.getElementById('racha-display');
  if(energyDisplay) {
    energyDisplay.textContent = `⚡ ${E.racha.toFixed(1)}x`;
    energyDisplay.style.color = E.racha < 1 ? '#ef4444' : (E.racha >= 2 ? '#f59e0b' : '#10b981');
  }
}

function mostrarNodo(id) {
  if (id === "resumen") return mostrarResumen();
  
  E.nodoActual = id;
  const nodo = NODOS[id];
  if(!nodo) return;

  const mi = getMInfo(nodo.categoria);
  const mb = document.getElementById('mult-badge');
  mb.textContent = mi.l;
  mb.style.cssText = `color:${mi.c};border-color:${mi.c}55;background:${mi.c}18;`;
  
  actualizarEnergiaUI();
  
  document.getElementById('reel-sponsor').innerHTML = nodo.isBoss ? `<a href="https://mercadolibre.com/empleos" target="_blank" style="color:inherit;text-decoration:underline;">${nodo.sponsor}</a>` : nodo.sponsor;
  document.getElementById('nodo-titulo').textContent = nodo.titulo;
  
  if(nodo.isBoss) document.getElementById('nodo-titulo').style.color = '#f59e0b';
  else document.getElementById('nodo-titulo').style.color = '#fff';

  document.getElementById('nodo-narracion').textContent = nodo.narracion;
  document.getElementById('vp-text').textContent = nodo.videoPrompt;
  
  const optsContainer = document.getElementById('opciones-container');
  optsContainer.innerHTML = '';
  
  if(nodo.isLeadCapture) {
    optsContainer.innerHTML = `
      <div class="lead-form">
        <input type="email" id="lead-email" placeholder="agente@dominio.com" class="lead-input" value="${E.email || ''}">
        <button class="btn-lead" onclick="guardarLead()">Conectar Perfil Vocacional</button>
        <button class="btn-lead-skip" onclick="mostrarResumen()">Omitir (Forense Anónimo)</button>
      </div>
    `;
  } else {
    const orden = [...nodo.opciones].sort(() => Math.random() - 0.5);
    orden.forEach(op => {
      const btn = document.createElement('button');
      btn.className = 'btn-opcion-narrativa';
      // OCULTANDO RECOMPENSA PREVIA
      btn.innerHTML = `<div class="op-texto">${op.t}</div>`;
      btn.onclick = () => procesarDecision(id, op, nodo);
      optsContainer.appendChild(btn);
    });
  }

  const card = document.getElementById('reel-card');
  card.style.animation = 'none'; card.offsetWidth; card.style.animation = '';
  
  document.getElementById('feedback-panel').style.display = 'none';
  optsContainer.style.display = 'flex';
}

function procesarDecision(nodeId, opcion, nodoObj) {
  document.getElementById('opciones-container').style.display = 'none';
  
  const mi = getMInfo(nodoObj.categoria);
  const esBuena = opcion.rew > 0;
  
  // SISTEMA DE ENERGÍA (RACHA)
  if(esBuena) {
    E.racha = Math.min(E.racha + 0.2, 2.5);
  } else {
    // Si falla en un BOSS, castigo severo. Sino castigo normal.
    E.racha = nodoObj.isBoss ? 0.1 : Math.max(E.racha - 0.4, 0.1);
  }

  // CÁLCULO FINAL RECOMPENSA
  const recompensaFinal = opcion.rew * mi.m * E.racha;
  
  // Guardar en historial rico para el Mapa/Perfil Vocacional
  E.historial.push({
    id: nodeId,
    titulo: nodoObj.titulo,
    categoria: nodoObj.categoria,
    decision: opcion.t,
    buena: esBuena
  });

  if(recompensaFinal > 0) {
    E.wallet += recompensaFinal;
    E.walletTotal += recompensaFinal;
    actualizarWalletHUD(recompensaFinal);
    guardar();
  }
  
  actualizarEnergiaUI();

  const fbPanel = document.getElementById('feedback-panel');
  document.getElementById('fb-icon').textContent = esBuena ? '📈' : '📉';
  document.getElementById('fb-icon').className = 'fb-icon ' + (esBuena ? 'buena' : 'mala');
  
  document.getElementById('fb-recompensa').textContent = esBuena ? `+$${recompensaFinal.toFixed(3)} ganados (Racha ${E.racha.toFixed(1)}x)` : `Sin recompensa. Energía reducida.`;
  document.getElementById('fb-recompensa').style.color = esBuena ? '#10b981' : '#f87171';
  document.getElementById('fb-explicacion').textContent = opcion.exp;
  
  const btnSig = document.getElementById('btn-siguiente-escena');
  btnSig.onclick = () => mostrarNodo(opcion.next);
  
  fbPanel.style.display = 'flex';
}

function guardarLead() {
  const mail = document.getElementById('lead-email').value;
  if(mail && mail.includes('@')) {
    E.email = mail;
    guardar();
    const btn = document.querySelector('.btn-lead');
    btn.textContent = "¡Perfil Enlazado! ✔️";
    btn.style.background = "#10b981";
    setTimeout(() => { mostrarResumen(); }, 800);
  } else {
    alert("Formato de correo inválido.");
  }
}

function actualizarWalletHUD(delta){
  document.getElementById('wallet-display').textContent = '$' + E.wallet.toFixed(3);
  const d = document.getElementById('wallet-delta');
  d.textContent = '+$' + delta.toFixed(3); d.classList.add('show');
  setTimeout(() => d.classList.remove('show'), 1200);
}

// RENDER MAPA Y PERFIL VOCACIONAL
function renderizarMapaDecisiones() {
  const container = document.getElementById('mapa-decisiones-lista');
  const perfilContainer = document.getElementById('perfil-vocacional');
  if(!container) return;
  container.innerHTML = '';
  
  if(E.historial.length === 0) {
    container.innerHTML = '<div class="mapa-vacio">No hay datos forenses acumulados.</div>';
    if(perfilContainer) perfilContainer.innerHTML = '';
    return;
  }

  // Vocacional Stats
  let stats = {};
  let totalBuenas = 0;
  
  E.historial.forEach((h, i) => {
    // Render Lista
    const div = document.createElement('div');
    div.className = 'mapa-nodo';
    div.innerHTML = `
      <div class="mapa-linea"></div>
      <div class="mapa-punto ${h.buena ? 'punto-ok' : 'punto-err'}"></div>
      <div class="mapa-info">
        <div class="mapa-titulo">${i+1}. ${h.titulo} <span style="opacity:0.5;font-size:10px">(${h.categoria})</span></div>
        <div class="mapa-decision">↳ ${h.decision}</div>
      </div>
    `;
    container.appendChild(div);
    
    // Contar vocacional
    if(h.buena) {
      stats[h.categoria] = (stats[h.categoria] || 0) + 1;
      totalBuenas++;
    }
  });
  
  // Dibujar Perfil Vocacional
  if(perfilContainer && totalBuenas > 0) {
    let topCat = Object.keys(stats).reduce((a, b) => stats[a] > stats[b] ? a : b);
    perfilContainer.innerHTML = `
      <div style="font-family:monospace;font-size:13px;color:#818cf8;margin-bottom:8px;">💡 Análisis Vocacional:</div>
      <div style="font-size:14px;line-height:1.5;color:#f1f5f9;">
        Tu perfil forense indica una alta afinidad hacia <b>${topCat}</b>. 
        <br>Las empresas que buscan este perfil están monitoreando simulaciones como esta.
      </div>
    `;
  }
  
  // Scrollear el mapa al fondo para ver las últimas decisiones
  setTimeout(() => {
    const mapaPanel = document.querySelector('.mapa-lista');
    if(mapaPanel) mapaPanel.scrollTop = mapaPanel.scrollHeight;
  }, 100);
}

// SHARE CARD
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
  
  ctx.fillStyle = '#f1f5f9'; ctx.font = 'bold 64px monospace'; ctx.fillText(`CIBER-AGENTE`, 80, 188);
  ctx.fillStyle = '#94a3b8'; ctx.font = '22px monospace'; ctx.fillText('Ha sobrevivido a la simulación corporativa.', 80, 248);
  
  ctx.fillStyle = '#10b981'; ctx.font = 'bold 52px monospace'; ctx.fillText('$' + E.walletTotal.toFixed(2), 80, 340);
  ctx.fillStyle = '#64748b'; ctx.font = '18px monospace'; ctx.fillText('RECOMPENSA ACUMULADA', 80, 374);
  
  ctx.fillStyle = '#6366f1'; ctx.font = 'bold 20px monospace'; ctx.fillText(`${E.historial.length} decisiones analizadas`, 80, 428);
  ctx.fillStyle = '#3f4a5e'; ctx.font = '16px monospace'; ctx.fillText('Postulate para entrevistas en link.mercadopago.com.ar/trwe', 80, 510);
  
  const url = canvas.toDataURL('image/png');
  const a = document.createElement('a'); a.download = 'microsecure-agente.png'; a.href = url; a.click();
}

function mostrarResumen(){
  guardar();
  cambiarPantalla('screen-feed', 'screen-summary');
  
  document.getElementById('summary-amount').textContent = '$' + E.wallet.toFixed(3);
  document.getElementById('wallet-bar-current').textContent = '$' + E.walletTotal.toFixed(2);
  document.getElementById('wallet-total-label').textContent = 'Total histórico: $' + E.walletTotal.toFixed(2);
  
  document.getElementById('ss-pts').textContent = E.historial.length;
  document.getElementById('ss-correct').textContent = E.email ? "Sí" : "No";
  
  const pct = Math.min((E.walletTotal / META_DOLARES) * 100, 100);
  setTimeout(() => { document.getElementById('wallet-bar-fill').style.width = pct + '%'; }, 600);

  renderizarMapaDecisiones();
}

function abrirRetiro(m){
  const urls = {
    mp: 'https://link.mercadopago.com.ar/trwe',
    paypal: 'https://www.paypal.com/donate/?business=tomasreis44%40gmail.com&currency_code=USD'
  };
  window.open(urls[m] || urls.mp, '_blank');
}

function compartir(){
  const txt = `Acabo de completar un análisis forense en MicroSecure y gané $${E.wallet.toFixed(2)}. ¿Podrías sobrevivir vos? 🛡️\n${location.href}`;
  if(navigator.share && navigator.canShare && navigator.canShare({text:txt})) {
    navigator.share({title:'MicroSecure', text:txt, url:location.href}).catch(console.error);
  } else {
    navigator.clipboard.writeText(txt).then(() => {
      alert('¡Reporte copiado al portapapeles! Pegalo en tus redes sociales para desafiar a otros.');
    }).catch(() => {
      alert('Tuvimos un problema al copiar. Usá el botón de descargar tarjeta.');
    });
  }
}

function reiniciar(){ iniciarHistoria(); }
window.addEventListener('DOMContentLoaded', initIntro);
