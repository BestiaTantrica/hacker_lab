// MicroSecure V5.1 — CYOA con Mapa de Decisiones
const META_DOLARES = 5.00;

// Multiplicadores
const MULTS = {
  'BUG BOUNTY':     {m: 3.0, l: '3x BOUNTY',  c: '#f59e0b'},
  'CLOUD SECURITY': {m: 2.5, l: '2.5x CLOUD', c: '#06b6d4'},
  'INCIDENTES':     {m: 2.0, l: '2x SOC',     c: '#a78bfa'},
  'SOCIAL':         {m: 1.5, l: '1.5x HUMAN', c: '#fbbf24'},
  'BASE':           {m: 1.0, l: '1x BASE',    c: '#64748b'},
};
const getMInfo = cat => MULTS[cat] || MULTS['BASE'];

// Grafo Narrativo - TODAS 4 OPCIONES
const NODOS = {
  "inicio": {
    categoria: "SOCIAL",
    titulo: "El Gancho Perfecto",
    narracion: "Es viernes a las 17:45. Llega un mail de 'RRHH': 'Actualización de política salarial 2026. Acción requerida hoy'. Tiene un PDF adjunto.",
    videoPrompt: "🎬 POV Escritorio. Pantalla muestra notificación de correo. Asunto jugoso. Reloj de PC marca 17:45. Música de tensión sutil.",
    sponsor: "Patrocinado por Proofpoint",
    opciones: [
      { t: "Abrir el PDF rápido para ver el bono.", next: "caida_phishing", rew: 0, exp: "La curiosidad mató al gato. Los PDFs pueden ejecutar código malicioso." },
      { t: "Revisar la dirección del remitente detalladamente.", next: "analisis_remitente", rew: 0.10, exp: "Excelente instinto. La pausa táctica es tu mejor defensa." },
      { t: "Ignorarlo, RRHH avisa estas cosas por Slack.", next: "ignorar_seguro", rew: 0.05, exp: "Decisión segura, pero dejaste pasar la oportunidad de cazar una amenaza activa." },
      { t: "Subir el PDF a VirusTotal sin abrirlo.", next: "virustotal_win", rew: 0.20, exp: "Pensamiento avanzado. Analizar antes de detonar es de profesionales." }
    ]
  },
  "virustotal_win": {
    categoria: "INCIDENTES",
    titulo: "Cazador de Malware",
    narracion: "VirusTotal marca el archivo con 45/70 detecciones. Es un troyano Emotet. Acabás de evitar que toda tu empresa se infecte.",
    videoPrompt: "🎬 Pantalla de VirusTotal. Interfaz roja parpadeando con la palabra 'MALICIOUS'. Zoom a la firma 'Emotet'.",
    sponsor: "Patrocinado por VirusTotal",
    opciones: [
      { t: "Avisar al equipo de seguridad (SOC) urgente.", next: "soc_hero", rew: 0.30, exp: "Protocolo perfecto. La inteligencia compartida salva redes enteras." },
      { t: "Ejecutarlo en una máquina virtual propia para analizarlo.", next: "analisis_forense", rew: 0.25, exp: "Riesgoso, pero es lo que hace un analista de malware de élite." },
      { t: "Borrar el mail y seguir con tu vida.", next: "ignorar_seguro", rew: 0, exp: "Destruiste evidencia y otros empleados podrían caer. Pésimo." },
      { t: "Responderle al hacker con un meme.", next: "error_novato", rew: 0, exp: "Nunca confirmes que existís interactuando con la infraestructura atacante." }
    ]
  },
  "caida_phishing": {
    categoria: "INCIDENTES",
    titulo: "Día Cero",
    narracion: "Abriste el PDF. Adobe Reader se cuelga un segundo. De repente, el fondo de pantalla cambia a negro y aparece un candado rojo.",
    videoPrompt: "🎬 Mouse hace doble clic. El cursor gira cargando. Glitch visual y la pantalla se inunda de calaveras ASCII rojas.",
    sponsor: "Patrocinado por CrowdStrike",
    opciones: [
      { t: "Desconectar la PC de la red y el WiFi brutalmente.", next: "apagon_hard", rew: 0.15, exp: "Contención nivel hardware. Evitaste que el ransomware salte a servidores." },
      { t: "Pagar el rescate en Bitcoin con tu tarjeta.", next: "fin_quiebra", rew: 0, exp: "Financiar el terrorismo digital no garantiza que te devuelvan los datos." },
      { t: "Llamar a tu jefe llorando.", next: "fin_despido", rew: 0, exp: "El pánico no resuelve incidentes. Hay que accionar técnicamente." },
      { t: "Intentar matar el proceso desde el Administrador de Tareas.", next: "malware_persistente", rew: 0.05, exp: "Demasiado tarde. El malware ya inyectó código en procesos del sistema (svchost.exe)." }
    ]
  },
  "analisis_remitente": {
    categoria: "SOCIAL",
    titulo: "El Truco Visual",
    narracion: "El correo viene de 'rrhh@empresa-corp.co' (falta la 'm'). Es un ataque de 'Typosquatting'.",
    videoPrompt: "🎬 Zoom extremo a la barra 'De:'. El '.co' brilla en rojo mientras suena un efecto sonoro de revelación (inception horn).",
    sponsor: "Patrocinado por Cloudflare",
    opciones: [
      { t: "Reportarlo con el botón de Outlook 'Phishing'.", next: "soc_hero", rew: 0.25, exp: "Entrenás los filtros de correo de toda la compañía. Héroe anónimo." },
      { t: "Comprar el dominio .com real para protegerlo.", next: "cloud_hero", rew: 0.15, exp: "Buena iniciativa de marca, pero el ataque vino desde el .co." },
      { t: "Insultar al remitente por correo.", next: "error_novato", rew: 0, exp: "Mala Opsec. Ahora saben que tu correo es válido y lo lee un humano irascible." },
      { t: "Hacer Ingeniería Inversa al servidor del atacante.", next: "analisis_forense", rew: 0.30, exp: "Hackear al hacker (Hack-back) es ilegal, pero en simulación... ¡vamos a ver!" }
    ]
  },
  "ignorar_seguro": {
    categoria: "INCIDENTES",
    titulo: "Propagación Silenciosa",
    narracion: "Lo ignoraste. 10 minutos después, ves a tu compañero de finanzas abrir exactamente ese mismo PDF. Su PC se congela.",
    videoPrompt: "🎬 Vista de reojo a la pantalla del compañero. Él hace doble clic. Susurrás 'No...' en cámara lenta.",
    sponsor: "Patrocinado por SentinelOne",
    opciones: [
      { t: "Gritar '¡Fuego!' y tirarle del cable de red a su PC.", next: "apagon_hard", rew: 0.20, exp: "Extremo, pero aislar el nodo infectado es la regla #1 de contención." },
      { t: "Hacerte el distraído e ir a buscar café.", next: "fin_quiebra", rew: 0, exp: "La inacción en seguridad te convierte en cómplice de la brecha." },
      { t: "Sacar una foto para subir a Twitter.", next: "fin_despido", rew: 0, exp: "Violar políticas de confidencialidad de incidentes te asegura el despido." },
      { t: "Reportar el incidente desde tu PC mientras él entra en pánico.", next: "soc_hero", rew: 0.15, exp: "Cabeza fría. Notificaste a los que pueden resolverlo." }
    ]
  },
  "soc_hero": {
    categoria: "CLOUD SECURITY",
    titulo: "Ascenso a la Nube",
    narracion: "IT te agradece por frenar el ataque. Como premio por tu instinto, te piden revisar una migración a la nube (AWS). Encontrás un Bucket S3 marcado 'Público'.",
    videoPrompt: "🎬 Consola de AWS. Un enorme cartel naranja dice 'Publicly Accessible' en un bucket llamado 'backups-db-clientes'.",
    sponsor: "Patrocinado por AWS Security",
    opciones: [
      { t: "Cambiar permisos a 'Privado' inmediatamente.", next: "cloud_hero", rew: 0.40, exp: "Reflejos de tigre. Acabás de evitar una demanda millonaria." },
      { t: "Descargar los archivos para ver si tienen datos reales.", next: "error_legal", rew: 0, exp: "Violar leyes de privacidad (GDPR/HIPAA). Convertiste un hallazgo en un delito." },
      { t: "Mandar un ticket a DevOps y esperar.", next: "cloud_lento", rew: 0.05, exp: "La burocracia no frena a los bots que escanean buckets abiertos 24/7." },
      { t: "Escribir un script de Python para buscar más buckets abiertos.", next: "bounty_recon", rew: 0.30, exp: "Mentalidad ofensiva (Red Team). Escalar el descubrimiento." }
    ]
  },
  "cloud_hero": {
    categoria: "BUG BOUNTY",
    titulo: "El Camino del Cazador",
    narracion: "Impresionados por tu agilidad, te invitan al programa privado de Bug Bounty de la empresa. Te pagan por encontrar agujeros. ¿Por dónde empezás?",
    videoPrompt: "🎬 Perfil de HackerOne abriéndose. Estadísticas en cero, pero tu reputación corporativa te da acceso VIP.",
    sponsor: "Patrocinado por HackerOne",
    opciones: [
      { t: "Interceptar tráfico API con Burp Suite.", next: "bounty_idor", rew: 0.35, exp: "El análisis dinámico de API es la mina de oro moderna." },
      { t: "Escanear subdominios abandonados.", next: "bounty_recon", rew: 0.30, exp: "Reconocimiento de superficie de ataque. Fundamental." },
      { t: "Lanzar un escáner automatizado (Nessus) ruidoso.", next: "error_ruido", rew: 0.05, exp: "Mucho ruido, poco valor. El WAF te va a bloquear en 3 minutos." },
      { t: "Buscar credenciales hardcodeadas en GitHub.", next: "bounty_github", rew: 0.40, exp: "Inteligencia de fuentes abiertas (OSINT). Los developers dejan llaves por todos lados." }
    ]
  },
  "analisis_forense": {
    categoria: "INCIDENTES",
    titulo: "Juego Peligroso",
    narracion: "Ejecutás el malware en tu laboratorio. El troyano intenta conectarse a un servidor de Comando y Control (C2) en Rusia. Tenés la IP.",
    videoPrompt: "🎬 Terminal Wireshark fluyendo a mil por hora. Filtro IP aplicado. Se ilumina una conexión saliente misteriosa.",
    sponsor: "Patrocinado por Wireshark",
    opciones: [
      { t: "Bloquear esa IP en el firewall de la empresa.", next: "soc_hero", rew: 0.30, exp: "Contención inteligente basada en Indicadores de Compromiso (IOCs)." },
      { t: "Atacar el servidor C2 ruso con DDoS.", next: "error_legal", rew: 0, exp: "Atacar infraestructura extranjera te convierte en un objetivo estatal. Ilegal." },
      { t: "Vender la IP en un foro de ciberseguridad.", next: "fin_quiebra", rew: 0, exp: "Tráfico de inteligencia ilícito. Perdiste tu brújula moral." },
      { t: "Analizar qué datos intentaba enviar el malware.", next: "cloud_hero", rew: 0.20, exp: "Descubrís que apuntaban a robar tokens de la Nube." }
    ]
  },
  "bounty_idor": {
    categoria: "BUG BOUNTY",
    titulo: "Vulnerabilidad Lógica",
    narracion: "Encontrás un endpoint `/api/factura/4040`. Cambiás el ID a `4041` en Burp Suite y... ¡ves la factura de otra empresa!",
    videoPrompt: "🎬 Interfaz de Repeater en Burp. Se edita el número. Botón SEND. El panel derecho arroja datos JSON de otra corporación.",
    sponsor: "Patrocinado por PortSwigger",
    opciones: [
      { t: "Reportar Insecure Direct Object Reference (IDOR).", next: "fin_victoria", rew: 0.50, exp: "IDOR crítico. Es la vulnerabilidad web que más paga hoy." },
      { t: "Escribir un script para bajar todas las facturas.", next: "error_legal", rew: 0, exp: "Demostraste el impacto excediendo los límites éticos. Te banean." },
      { t: "Cobrar rescate a la otra empresa por su factura.", next: "fin_quiebra", rew: 0, exp: "Extorsión. Te convertiste en el villano de la historia." },
      { t: "Probar si podés modificar la factura además de verla.", next: "fin_victoria", rew: 0.60, exp: "Escalar el impacto. Mass Assignment IDOR. ¡Bono extra!" }
    ]
  },
  "bounty_github": {
    categoria: "BUG BOUNTY",
    titulo: "Secretos a Voces",
    narracion: "Buscás en repositorios públicos de GitHub. Un dev subió por error un archivo `.env` con la llave maestra de la base de datos de producción.",
    videoPrompt: "🎬 Búsqueda en GitHub. Un archivo .env crudo con el texto 'AWS_SECRET_ACCESS_KEY=AKIA...'. Lluvia dorada.",
    sponsor: "Patrocinado por Truffle Security",
    opciones: [
      { t: "Reportarlo de inmediato pidiendo rotación de llave.", next: "fin_victoria", rew: 0.60, exp: "Riesgo Crítico P1. Reporte perfecto." },
      { t: "Loguearte a la DB para confirmar que funciona.", next: "error_legal", rew: 0, exp: "Nunca uses credenciales filtradas de producción en Bug Bounty." },
      { t: "Crear un Pull Request borrando el archivo.", next: "error_novato", rew: 0, exp: "Borrarlo no lo elimina del historial de Git. Hay que rotar la llave." },
      { t: "Reportar y escribir una regla de detección para el CI/CD.", next: "fin_victoria", rew: 0.80, exp: "DevSecOps puro. Solucionás el problema de raíz." }
    ]
  },
  // Nodos de "Retorno/Castigo" - Ahora con 4 opciones
  "apagon_hard": {
    categoria: "INCIDENTES",
    titulo: "Control de Daños",
    narracion: "Tiraste del cable. IT te agradece, pero el equipo está inutilizable. Hay que investigar por qué el antivirus no saltó.",
    videoPrompt: "🎬 Placa base humeando (metafóricamente). Un técnico forense conecta un pendrive de arranque.",
    sponsor: "Patrocinado por Mandiant",
    opciones: [
      { t: "Exigir un aumento por salvar el día.", next: "soc_hero", rew: 0.15, exp: "Audaz. Te envían a entrenarte en Seguridad Cloud." },
      { t: "Pedir que te enseñen a hacer análisis de memoria RAM.", next: "analisis_forense", rew: 0.25, exp: "El hambre de conocimiento forense es invaluable." },
      { t: "Volver a tu puesto y hacer de cuenta que no pasó nada.", next: "ignorar_seguro", rew: 0, exp: "La apatía es enemiga de la seguridad." },
      { t: "Culpar a RRHH por mandar correos tan obvios.", next: "fin_despido", rew: 0, exp: "Falta de profesionalismo. La seguridad es un problema de todos." }
    ]
  },
  "malware_persistente": {
    categoria: "INCIDENTES",
    titulo: "El Bicho Inmortal",
    narracion: "El administrador de tareas no sirvió. El malware inyectó un Rootkit. Has perdido control total de la máquina.",
    videoPrompt: "🎬 Ventanas multiplicándose solas. El puntero del mouse se mueve solo. Hackers controlando tu sesión por VNC.",
    sponsor: "Patrocinado por Malwarebytes",
    opciones: [
      { t: "Desenroscar el disco duro físico.", next: "apagon_hard", rew: 0.10, exp: "Hardware beats Software. Frenaste la exfiltración." },
      { t: "Reinstalar Windows encima.", next: "error_novato", rew: 0, exp: "Borrás la evidencia forense sin entender la persistencia de BIOS/UEFI." },
      { t: "Dejar un cartel de 'HACKEADA' y salir corriendo.", next: "fin_despido", rew: 0, exp: "Abandono de puesto." },
      { t: "Intentar lanzar un antivirus portátil desde un USB.", next: "virustotal_win", rew: 0.15, exp: "Buena reacción técnica, aunque los rootkits suelen esconderse de AVs básicos." }
    ]
  },
  "cloud_lento": {
    categoria: "CLOUD SECURITY",
    titulo: "Dormirse en los Laureles",
    narracion: "DevOps ignoró tu ticket. Un grupo de Ransomware robó los datos y extorsiona al CEO amenazando con publicar todo.",
    videoPrompt: "🎬 Noticiero en TV. Titular urgente: 'Empresa sufre mega filtración. Acciones caen 40%'.",
    sponsor: "Patrocinado por Varonis",
    opciones: [
      { t: "Aprender que las fallas de Nube son incidentes críticos.", next: "cloud_hero", rew: 0, exp: "Lección aprendida: Escalar al CISO si es necesario." },
      { t: "Decir 'Yo les avisé' y cruzarse de brazos.", next: "fin_despido", rew: 0, exp: "Tener razón no sirve si la empresa quiebra." },
      { t: "Ofrecerte a rastrear los logs de AWS para ver qué robaron.", next: "analisis_forense", rew: 0.20, exp: "Mentalidad de respuesta a incidentes (IR). Resiliencia." },
      { t: "Buscar nuevo trabajo antes de que se sepa.", next: "fin_quiebra", rew: 0, exp: "Cobardía corporativa." }
    ]
  },
  "error_novato": {
    categoria: "SOCIAL",
    titulo: "Ataque Dirigido",
    narracion: "El atacante sabe que existís. Al otro día, te llama por teléfono tu 'Jefe' (voz clonada por IA) pidiendo una transferencia urgente.",
    videoPrompt: "🎬 Teléfono sonando. La pantalla dice 'Jefe (Urgente)'. Audio distorsionado clonando su voz.",
    sponsor: "Patrocinado por ElevenLabs Security",
    opciones: [
      { t: "Hacer la transferencia, es tu jefe.", next: "fin_despido", rew: 0, exp: "Deepfake de voz (Vishing). Caíste en la estafa moderna más peligrosa." },
      { t: "Cortar y llamarlo vos por otro canal (Slack/Teléfono oficial).", next: "soc_hero", rew: 0.25, exp: "Verificación Fuera de Banda (OOB). Evitaste el fraude." },
      { t: "Preguntarle algo que solo él sabría.", next: "soc_hero", rew: 0.15, exp: "Autenticación basada en conocimiento. Buena estrategia humana." },
      { t: "Empezar a insultar a la voz robot.", next: "inicio", rew: 0, exp: "Volvé a empezar y aprendé a mantener el profesionalismo." }
    ]
  },
  "error_legal": {
    categoria: "CLOUD SECURITY",
    titulo: "Problemas Legales",
    narracion: "Por extraer datos o atacar de vuelta, el área legal (Compliance) frena tus operaciones. Estás bajo investigación.",
    videoPrompt: "🎬 Oficina gris. Abogado de la empresa empujando papeles. Cartel 'Confidential Investigation'.",
    sponsor: "Patrocinado por LegalTech",
    opciones: [
      { t: "Contratar un abogado propio y renunciar.", next: "fin_quiebra", rew: 0, exp: "Fin de tu carrera de ciberseguridad corporativa." },
      { t: "Colaborar mostrando que fue sin mala intención (Mens rea).", next: "inicio", rew: 0, exp: "Zafás del despido, pero volvés a cero. Lección: Cuidado con las leyes (CFAA/GDPR)." },
      { t: "Intentar borrar los logs de AWS CloudTrail.", next: "fin_despido", rew: 0, exp: "Obstrucción de justicia. Ahora es un caso criminal." },
      { t: "Escribir un reporte post-mortem asumiendo la culpa procesal.", next: "cloud_hero", rew: 0.10, exp: "Admitir errores de proceso demuestra madurez gerencial." }
    ]
  },
  "error_ruido": {
    categoria: "BUG BOUNTY",
    titulo: "El Elefante en la Cacharrería",
    narracion: "Tu escáner automatizado mandó 10,000 requests por segundo. Tiraste el servidor de staging y tu IP fue bloqueada permanentemente por el WAF.",
    videoPrompt: "🎬 Pantalla inyectando logs a lo loco. De repente: 'Error 403 Forbidden - WAF Blocked'.",
    sponsor: "Patrocinado por Imperva",
    opciones: [
      { t: "Cambiar tu IP con una VPN y seguir escaneando igual.", next: "error_legal", rew: 0, exp: "Evasión activa. Estás cruzando la línea a atacante malicioso." },
      { t: "Aprender a hacer escaneos sigilosos y pausados.", next: "bounty_recon", rew: 0.20, exp: "La precisión siempre le gana a la fuerza bruta." },
      { t: "Reportar como vuln que 'el servidor se cae fácil' (DoS).", next: "fin_despido", rew: 0, exp: "Los DoS están casi siempre fuera de scope. No hagas perder tiempo." },
      { t: "Usar Google Dorks pasivamente para no tocar el server.", next: "bounty_github", rew: 0.30, exp: "OSINT no genera ruido. Inteligencia táctica pura." }
    ]
  },
  "bounty_recon": {
    categoria: "BUG BOUNTY",
    titulo: "Reconocimiento de Área",
    narracion: "Haciendo recon pasivo, encontrás un subdominio `soporte.empresa.com` que apunta a un bucket de AWS que ya fue borrado.",
    videoPrompt: "🎬 Consola negra. Herramienta 'subfinder' encuentra un target. Un ping devuelve '404 NoSuchBucket'.",
    sponsor: "Patrocinado por ProjectDiscovery",
    opciones: [
      { t: "Registrar ese bucket vacío con tu cuenta de AWS.", next: "fin_victoria", rew: 0.50, exp: "¡Subdomain Takeover! Tenés control total del dominio de la empresa." },
      { t: "Tratar de adivinar archivos dentro del bucket 404.", next: "error_ruido", rew: 0, exp: "Pérdida de tiempo. El bucket ya no existe físicamente." },
      { t: "Buscar credenciales de AWS en el código fuente de la página.", next: "bounty_github", rew: 0.25, exp: "Buen pivote de ataque." },
      { t: "Reportar el 404 como 'Informativo'.", next: "error_novato", rew: 0, exp: "Desperdiciaste un impacto Crítico (Takeover) reportándolo como un error de diseño." }
    ]
  },
  "fin_quiebra": {
    categoria: "BASE",
    titulo: "Carrera Terminada",
    narracion: "Tus decisiones erráticas llevaron a pérdidas financieras y reputacionales irreparables. Ya nadie confía en tu criterio.",
    videoPrompt: "🎬 Pantalla de cajero automático diciendo 'Fondos Insuficientes'. Lluvia.",
    sponsor: "MicroSecure Awareness",
    opciones: [
      { t: "Reflexionar sobre qué es el profesionalismo y reiniciar.", next: "inicio", rew: 0, exp: "A veces la vida requiere un hard reset." },
      { t: "Culpar a la 'Matrix' corporativa.", next: "inicio", rew: 0, exp: "Cero auto-percepción." },
      { t: "Empezar a estudiar programación desde cero.", next: "inicio", rew: 0, exp: "Saber construir ayuda a saber destruir de forma segura." },
      { t: "Crear una nueva cuenta en LinkedIn y empezar otra vez.", next: "inicio", rew: 0, exp: "El ecosistema olvida, pero la base de datos no." }
    ]
  },
  "fin_despido": {
    categoria: "BASE",
    titulo: "Tarjeta Roja",
    narracion: "Seguridad Corporativa desactivó tu badge. Estás afuera. Tomaste decisiones irracionales bajo presión.",
    videoPrompt: "🎬 Puerta de vidrio corporativa. Un guardia de seguridad pide tu tarjeta. Fundido a negro.",
    sponsor: "MicroSecure Training",
    opciones: [
      { t: "Entrenar tu inteligencia emocional y volver a intentar.", next: "inicio", rew: 0, exp: "Ciberseguridad es 50% técnica, 50% control del pánico." },
      { t: "Revisar los logs mentales de dónde fallaste.", next: "inicio", rew: 0, exp: "Análisis post-mortem personal. Vital." },
      { t: "Intentar hackear a tu ex-empresa por venganza.", next: "error_legal", rew: 0, exp: "Insistís con la criminalidad." },
      { t: "Estudiar leyes de cumplimiento (Compliance) para entenderlos.", next: "cloud_lento", rew: 0, exp: "Interesante giro de carrera." }
    ]
  },
  "fin_victoria": {
    categoria: "BASE",
    titulo: "Operador de Élite",
    narracion: "Resolviste brechas, descubriste bugs y demostraste madurez técnica. Has sobrevivido a la simulación con saldo a favor.",
    videoPrompt: "🎬 Pantalla estilo matriz verde. Texto fluyendo: 'Misión Completada. Estatus: Agente Validado'.",
    sponsor: "Patrocinado por MicroSecure",
    opciones: [
      { t: "Registrar mi identidad en la base de datos (Guardar progreso).", next: "registro_lead", rew: 0, exp: "Inmortaliza tu nombre en la red." },
      { t: "Descargar mi portafolio forense directamente.", next: "resumen", rew: 0, exp: "Vamos al reporte final." },
      { t: "Volver a jugar para maximizar recompensas.", next: "inicio", rew: 0, exp: "Loop infinito de minado de atención." },
      { t: "Desafiar al creador de la simulación.", next: "registro_lead", rew: 0, exp: "Solo los audaces sobreviven." }
    ]
  },
  "registro_lead": {
    categoria: "BASE",
    titulo: "Conexión a la Red",
    narracion: "Para archivar tu mapa de decisiones en el ranking global, necesitamos autenticar tu entidad. Ingresa tu correo cifrado.",
    videoPrompt: "🎬 Interfaz futurista de escaneo biométrico simulado. 'Esperando input humano...'",
    sponsor: "MicroSecure Network",
    isLeadCapture: true,
    opciones: []
  },
  "resumen": {
    isResumen: true // Atajo técnico para salir
  }
};

// ESTADO V5.1
let E = {
  nodoActual: "inicio",
  wallet: 0.0,
  walletTotal: 0.0,
  historial: [], // Array de { id, txt, esBuena }
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
    if(s) s.innerHTML = `Identidad verificada: <b>${E.email}</b>.`;
  }
}

// FLUJO CYOA
function iniciarHistoria(){
  E.wallet = 0.0;
  E.historial = [];
  cambiarPantalla('screen-intro', 'screen-feed');
  mostrarNodo("inicio");
}

function cambiarPantalla(a,b){
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(b).classList.add('active');
  window.scrollTo(0,0);
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
  
  document.getElementById('reel-sponsor').textContent = nodo.sponsor;
  document.getElementById('nodo-titulo').textContent = nodo.titulo;
  document.getElementById('nodo-narracion').textContent = nodo.narracion;
  document.getElementById('vp-text').textContent = nodo.videoPrompt;
  
  const optsContainer = document.getElementById('opciones-container');
  optsContainer.innerHTML = '';
  
  if(nodo.isLeadCapture) {
    optsContainer.innerHTML = `
      <div class="lead-form">
        <input type="email" id="lead-email" placeholder="agente@dominio.com" class="lead-input" value="${E.email || ''}">
        <button class="btn-lead" onclick="guardarLead()">Autenticar Identidad</button>
        <button class="btn-lead-skip" onclick="mostrarResumen()">Omitir (Forense Anónimo)</button>
      </div>
    `;
  } else {
    // Mezclar opciones para que no sea predecible
    const orden = [...nodo.opciones].sort(() => Math.random() - 0.5);
    orden.forEach(op => {
      const mult = mi.m;
      const recompensaReal = op.rew * mult;
      const btn = document.createElement('button');
      btn.className = 'btn-opcion-narrativa';
      let rewardHTML = recompensaReal > 0 ? `<span class="op-reward-tag">+$${recompensaReal.toFixed(2)}</span>` : '';
      btn.innerHTML = `<div class="op-texto">${op.t}</div> ${rewardHTML}`;
      btn.onclick = () => procesarDecision(id, op, recompensaReal, nodo.titulo);
      optsContainer.appendChild(btn);
    });
  }

  const card = document.getElementById('reel-card');
  card.style.animation = 'none'; card.offsetWidth; card.style.animation = '';
  
  document.getElementById('feedback-panel').style.display = 'none';
  optsContainer.style.display = 'flex';
}

function procesarDecision(nodeId, opcion, recompensaReal, tituloNodo) {
  document.getElementById('opciones-container').style.display = 'none';
  
  const esBuena = recompensaReal > 0;
  
  // Guardar en historial rico para el Mapa
  E.historial.push({
    id: nodeId,
    titulo: tituloNodo,
    decision: opcion.t,
    buena: esBuena
  });

  if(esBuena) {
    E.wallet += recompensaReal;
    E.walletTotal += recompensaReal;
    actualizarWalletHUD(recompensaReal);
    guardar();
  }
  
  const fbPanel = document.getElementById('feedback-panel');
  document.getElementById('fb-icon').textContent = esBuena ? '📈' : '📉';
  document.getElementById('fb-icon').className = 'fb-icon ' + (esBuena ? 'buena' : 'mala');
  
  document.getElementById('fb-recompensa').textContent = esBuena ? `+$${recompensaReal.toFixed(2)} ganados` : `Sin recompensa`;
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
    
    // Feedback visual antes de saltar
    const btn = document.querySelector('.btn-lead');
    btn.textContent = "¡Identidad Validada! ✔️";
    btn.style.background = "#10b981";
    setTimeout(() => { mostrarResumen(); }, 800);
  } else {
    alert("Formato de correo cifrado (email) inválido.");
  }
}

function actualizarWalletHUD(delta){
  document.getElementById('wallet-display').textContent = '$' + E.wallet.toFixed(2);
  const d = document.getElementById('wallet-delta');
  d.textContent = '+$' + delta.toFixed(2); d.classList.add('show');
  setTimeout(() => d.classList.remove('show'), 1200);
}

// RENDER MAPA DECISIONES
function renderizarMapaDecisiones() {
  const container = document.getElementById('mapa-decisiones-lista');
  if(!container) return;
  container.innerHTML = '';
  
  if(E.historial.length === 0) {
    container.innerHTML = '<div class="mapa-vacio">No hay datos forenses en esta sesión.</div>';
    return;
  }

  E.historial.forEach((h, i) => {
    const div = document.createElement('div');
    div.className = 'mapa-nodo';
    div.innerHTML = `
      <div class="mapa-linea"></div>
      <div class="mapa-punto ${h.buena ? 'punto-ok' : 'punto-err'}"></div>
      <div class="mapa-info">
        <div class="mapa-titulo">${i+1}. ${h.titulo}</div>
        <div class="mapa-decision">↳ ${h.decision}</div>
      </div>
    `;
    container.appendChild(div);
  });
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
  
  ctx.fillStyle = '#6366f1'; ctx.font = 'bold 20px monospace'; ctx.fillText(`${E.historial.length} decisiones en bitácora`, 80, 428);
  ctx.fillStyle = '#3f4a5e'; ctx.font = '16px monospace'; ctx.fillText('Sobreviví vos también en link.mercadopago.com.ar/trwe', 80, 510);
  
  const url = canvas.toDataURL('image/png');
  const a = document.createElement('a'); a.download = 'microsecure-agente.png'; a.href = url; a.click();
}

// RESUMEN
function mostrarResumen(){
  guardar();
  cambiarPantalla('screen-feed', 'screen-summary');
  
  document.getElementById('summary-amount').textContent = '$' + E.wallet.toFixed(2);
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
  
  // Fallback robusto para PC/HTTP
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
