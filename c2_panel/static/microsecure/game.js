// ============================================================
// MicroSecure v3 — Insight + Multiple Choice + Niveles
// Flujo: Ver insight (8s) → Pregunta 1-clic (MC) → Feedback → Recompensa → Nivel
// ============================================================

const TIMER_SEGUNDOS = 8;
const META_DOLARES   = 5.00;

// NIVELES
const NIVELES = [
    { min: 0,   max: 149,  nombre: "Novato",       emoji: "🔵", desc: "Acabás de empezar. ¡Todo lo que aprendas desde acá es ganancia!" },
    { min: 150, max: 349,  nombre: "Consciente",   emoji: "🟡", desc: "Ya sabés más que el 80% de la población sobre ciberseguridad." },
    { min: 350, max: 599,  nombre: "Informado",    emoji: "🟠", desc: "Pensás como alguien que sabe protegerse en el mundo digital." },
    { min: 600, max: 9999, nombre: "Avanzado",     emoji: "🔴", desc: "Nivel profesional. Podés enseñarle a otros y monetizarlo." }
];

function obtenerNivel(pts) {
    return NIVELES.find(n => pts >= n.min && pts <= n.max) || NIVELES[0];
}

// BANCO DE INSIGHTS con pregunta MC integrada
const INSIGHTS = [
    {
        emoji: "📶",
        stat: { number: "147", unit: "contraseñas robadas por hora en Wi-Fi pública" },
        headline: "Tu Wi-Fi pública es una trampa silenciosa.",
        context: "Un atacante en la misma red puede capturar tu tráfico con herramientas gratuitas. Una VPN cifra todo tu tráfico y lo hace ilegible para cualquiera en la red.",
        categoria: "WI-FI", bgAccent: "rgba(239,68,68,0.12)", color: "#f87171",
        sponsor: "Patrocinado por NordVPN",
        rewardBase: 0.07,
        pregunta: "¿Qué herramienta protege tu tráfico en redes públicas?",
        opciones: [
            { texto: "Un antivirus actualizado", correcta: false },
            { texto: "Una VPN (Red Privada Virtual)", correcta: true },
            { texto: "Navegar en modo incógnito", correcta: false },
            { texto: "Usar solo HTTPS", correcta: false }
        ],
        explicacion: "Una VPN cifra todo tu tráfico antes de que salga de tu dispositivo. El modo incógnito solo esconde el historial local — no te protege en la red."
    },
    {
        emoji: "🎣",
        stat: { number: "91%", unit: "de los hackeos empieza con un email falso" },
        headline: "El phishing es la arma #1 del cibercrimen.",
        context: "Un atacante puede clonar el email de tu banco en minutos. La diferencia entre el real y el falso suele estar en una letra del dominio del remitente.",
        categoria: "PHISHING", bgAccent: "rgba(245,158,11,0.1)", color: "#fbbf24",
        sponsor: "Patrocinado por Proofpoint",
        rewardBase: 0.06,
        pregunta: "Recibes un email de 'seguridad@bancc0.com'. ¿Qué hacés?",
        opciones: [
            { texto: "Clic en el link si parece urgente", correcta: false },
            { texto: "Verificar el dominio exacto del remitente", correcta: true },
            { texto: "Responder para confirmar que es legítimo", correcta: false },
            { texto: "Abrir el adjunto para ver de qué trata", correcta: false }
        ],
        explicacion: "'bancc0.com' no es el dominio real de ningún banco. Los atacantes usan dominios casi idénticos. Verificar el dominio exacto (no el nombre visible) es la defensa clave."
    },
    {
        emoji: "🔑",
        stat: { number: "23M", unit: "personas usan '123456' como contraseña" },
        headline: "La contraseña más fácil = la primera que prueban.",
        context: "Los atacantes usan diccionarios con millones de contraseñas comunes. Una contraseña de 12 caracteres aleatorios tardaría miles de años en crackearse.",
        categoria: "CONTRASEÑAS", bgAccent: "rgba(99,102,241,0.12)", color: "#818cf8",
        sponsor: "Patrocinado por 1Password",
        rewardBase: 0.05,
        pregunta: "¿Cuál de estas contraseñas es más segura?",
        opciones: [
            { texto: "MiPerro2024!", correcta: false },
            { texto: "P@ssw0rd", correcta: false },
            { texto: "kX#9mQ2!vLpR", correcta: true },
            { texto: "123456789", correcta: false }
        ],
        explicacion: "'kX#9mQ2!vLpR' es aleatoria, larga y mezcla tipos de caracteres. Las basadas en palabras o patrones conocidos son vulnerables a ataques de diccionario."
    },
    {
        emoji: "📱",
        stat: { number: "99.9%", unit: "de los ataques automáticos bloqueados por 2FA" },
        headline: "El doble factor tarda 30 segundos en activarse.",
        context: "El 2FA exige dos pruebas: algo que sabés (contraseña) + algo que tenés (teléfono). Aunque te roben la contraseña, sin el código del teléfono no pueden entrar.",
        categoria: "2FA", bgAccent: "rgba(6,182,212,0.1)", color: "#22d3ee",
        sponsor: "Patrocinado por Authy",
        rewardBase: 0.07,
        pregunta: "¿Cuál es el segundo 'factor' en la autenticación de dos factores?",
        opciones: [
            { texto: "Una contraseña más larga", correcta: false },
            { texto: "Un código enviado a tu teléfono o app", correcta: true },
            { texto: "Tu nombre de usuario", correcta: false },
            { texto: "Un CAPTCHA", correcta: false }
        ],
        explicacion: "El segundo factor es algo físico que tenés: tu teléfono. Aunque el atacante tenga tu contraseña, no puede acceder sin ese código temporal."
    },
    {
        emoji: "💉",
        stat: { number: "#1", unit: "vulnerabilidad más reportada en HackerOne: IDOR" },
        headline: "Cambiar un número en la URL puede exponer datos ajenos.",
        context: "IDOR (Insecure Direct Object Reference): si la app no verifica que sos el dueño del recurso, cambiar /usuario/123 a /usuario/124 puede mostrar datos de otro usuario.",
        categoria: "BUG BOUNTY", bgAccent: "rgba(16,185,129,0.1)", color: "#34d399",
        sponsor: "Patrocinado por HackerOne",
        rewardBase: 0.09,
        pregunta: "Una app muestra /api/perfil/100 con tus datos. Cambiás a /api/perfil/101 y ves datos de otra persona. ¿Qué vulnerabilidad es?",
        opciones: [
            { texto: "SQL Injection", correcta: false },
            { texto: "XSS (Cross-Site Scripting)", correcta: false },
            { texto: "IDOR (Referencia directa insegura)", correcta: true },
            { texto: "CSRF", correcta: false }
        ],
        explicacion: "IDOR ocurre cuando el servidor no verifica que el usuario autenticado es el dueño del objeto solicitado. Es la vulnerabilidad #1 en Bug Bounty por su alto impacto y fácil detección."
    },
    {
        emoji: "⚡",
        stat: { number: "60%", unit: "de brechas explotan vulnerabilidades ya parcheadas" },
        headline: "'Actualizar después' puede costarte todo.",
        context: "Cuando aparece un parche de seguridad, los atacantes analizan el código para crear exploits en horas. Las máquinas sin actualizar son blancos fáciles y conocidos.",
        categoria: "ACTUALIZACIONES", bgAccent: "rgba(245,158,11,0.1)", color: "#fbbf24",
        sponsor: "Patrocinado por Microsoft",
        rewardBase: 0.05,
        pregunta: "¿Por qué es urgente instalar actualizaciones de seguridad el mismo día que salen?",
        opciones: [
            { texto: "Para tener las últimas funciones del sistema", correcta: false },
            { texto: "Porque los atacantes crean exploits en horas tras el parche", correcta: true },
            { texto: "Para mejorar la velocidad del equipo", correcta: false },
            { texto: "Porque lo pide el fabricante", correcta: false }
        ],
        explicacion: "El parche publica qué bug fue corregido. Los atacantes lo usan como mapa para atacar sistemas sin actualizar. Cuanto más tardás, más expuesto estás."
    },
    {
        emoji: "💸",
        stat: { number: "$1.50", unit: "vale tu perfil completo en la dark web" },
        headline: "Tus datos se venden al por mayor sin que lo sepas.",
        context: "Las filtraciones masivas de bases de datos se venden en mercados ilegales. Tu email, contraseña y fecha de nacimiento combinados permiten ataques de 'credential stuffing' en otros sitios.",
        categoria: "DATA BREACH", bgAccent: "rgba(239,68,68,0.1)", color: "#f87171",
        sponsor: "Patrocinado por HaveIBeenPwned",
        rewardBase: 0.08,
        pregunta: "¿Qué podés hacer HOY para saber si tus datos fueron filtrados?",
        opciones: [
            { texto: "Cambiar todas las contraseñas por 'admin123'", correcta: false },
            { texto: "Consultar haveibeenpwned.com con tu email", correcta: true },
            { texto: "Formatear la computadora", correcta: false },
            { texto: "No hay forma de saberlo", correcta: false }
        ],
        explicacion: "HaveIBeenPwned.com (Troy Hunt) indexa todas las filtraciones conocidas. Ingresás tu email y te dice si aparece en alguna base de datos comprometida."
    },
    {
        emoji: "💾",
        stat: { number: "11s", unit: "— cada 11 segundos una empresa es atacada con ransomware" },
        headline: "Sin backup, un ataque borra años de trabajo.",
        context: "El ransomware cifra todos tus archivos y pide rescate. La única defensa real es una copia offline. Regla 3-2-1: 3 copias, en 2 medios distintos, 1 fuera del sitio.",
        categoria: "RANSOMWARE", bgAccent: "rgba(139,92,246,0.1)", color: "#a78bfa",
        sponsor: "Patrocinado por Backblaze",
        rewardBase: 0.09,
        pregunta: "Si un ransomware cifra tu disco, ¿cuál es la única defensa real?",
        opciones: [
            { texto: "Pagar el rescate rápidamente", correcta: false },
            { texto: "Tener backups offline actualizados", correcta: true },
            { texto: "Apagar la computadora inmediatamente", correcta: false },
            { texto: "Usar Windows Defender", correcta: false }
        ],
        explicacion: "Pagar no garantiza recuperar los archivos. Un antivirus no puede descifrar lo que ya fue cifrado. Solo una copia de seguridad offline (no conectada a la red) te garantiza recuperación total."
    }
];

// ESTADO
let E = {
    indexActual: 0,
    orden: [],
    puntos: 0,
    wallet: 0,
    correctas: 0,
    racha: 0,
    rachaMax: 0,
    timerInterval: null,
    respondido: false,
    enTimer: false,
};

// ============================================================
// FLUJO
// ============================================================
function iniciarFeed() {
    E.orden = INSIGHTS.map((_,i) => i);
    for (let i = E.orden.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [E.orden[i], E.orden[j]] = [E.orden[j], E.orden[i]];
    }
    Object.assign(E, { indexActual:0, puntos:0, wallet:0, correctas:0, racha:0, rachaMax:0 });
    construirBarraEpisodios();
    cambiarPantalla('screen-intro','screen-feed');
    mostrarInsight();
}

function cambiarPantalla(ocultar, mostrar) {
    document.getElementById(ocultar).classList.remove('active');
    const el = document.getElementById(mostrar);
    el.classList.add('active');
    window.scrollTo(0,0);
}

function mostrarInsight() {
    if (E.indexActual >= E.orden.length) { mostrarResumen(); return; }

    const ins = INSIGHTS[E.orden[E.indexActual]];
    E.respondido = false;
    E.enTimer = true;

    // Reset panels
    document.getElementById('action-panel').style.display = 'none';
    document.getElementById('mc-feedback').style.display = 'none';

    // Contenido
    document.getElementById('reel-sponsor').textContent = ins.sponsor;
    document.getElementById('reel-body').innerHTML = `
        <div class="reel-hero" style="background:${ins.bgAccent}">
            <div class="reel-emoji">${ins.emoji}</div>
            <div class="reel-stat-wrapper">
                <div class="reel-stat-number" style="color:${ins.color}">${ins.stat.number}</div>
                <div class="reel-stat-unit">${ins.stat.unit}</div>
            </div>
            <div class="reel-headline">${ins.headline}</div>
            <div class="reel-context">${ins.context}</div>
        </div>
        <div class="reel-footer">
            <div class="reel-category" style="color:${ins.color}">${ins.categoria}</div>
            <div class="reel-reward-preview">+$${ins.rewardBase.toFixed(2)}</div>
        </div>`;

    // Re-trigger animation
    const card = document.getElementById('reel-card');
    card.style.animation = 'none'; card.offsetWidth; card.style.animation = '';

    actualizarBarraEpisodios();
    iniciarTimer(ins);
}

// ============================================================
// TIMER
// ============================================================
function iniciarTimer(ins) {
    clearInterval(E.timerInterval);
    const ring  = document.getElementById('ring-fill');
    const sec   = document.getElementById('timer-seconds');
    const CIRC  = 163.36;

    ring.style.transition = 'none';
    ring.style.strokeDashoffset = '0';
    ring.classList.remove('urgent');
    sec.textContent = TIMER_SEGUNDOS;

    // Segmento de episodio
    const segFill = document.querySelector(`.ep-seg:nth-child(${E.indexActual + 1}) .ep-seg-fill`);
    if (segFill) {
        segFill.style.transition = 'none'; segFill.style.width = '0%'; segFill.offsetWidth;
        segFill.style.transition = `width ${TIMER_SEGUNDOS}s linear`; segFill.style.width = '100%';
    }

    let elapsed = 0;
    E.timerInterval = setInterval(() => {
        elapsed += 100;
        ring.style.strokeDashoffset = String(CIRC * elapsed / (TIMER_SEGUNDOS * 1000));
        const rem = Math.ceil((TIMER_SEGUNDOS * 1000 - elapsed) / 1000);
        sec.textContent = Math.max(0, rem);
        if (rem <= 2) ring.classList.add('urgent');
        if (elapsed >= TIMER_SEGUNDOS * 1000) {
            clearInterval(E.timerInterval);
            E.enTimer = false;
            if (!E.respondido) mostrarPregunta(ins);
        }
    }, 100);
}

// ============================================================
// PREGUNTA MC
// ============================================================
function mostrarPregunta(ins) {
    const panel = document.getElementById('action-panel');
    document.getElementById('mc-question').textContent = ins.pregunta;

    // Mezclar opciones
    const letras = ['A','B','C','D'];
    const orden = [0,1,2,3].sort(() => Math.random() - 0.5);
    const optsEl = document.getElementById('mc-options');
    optsEl.innerHTML = '';

    orden.forEach((opIdx, i) => {
        const op = ins.opciones[opIdx];
        const btn = document.createElement('button');
        btn.className = 'mc-opt';
        btn.dataset.correcta = op.correcta;
        btn.dataset.opIdx = opIdx;
        btn.innerHTML = `<span class="opt-letter">${letras[i]}</span> ${op.texto}`;
        btn.onclick = () => responder(btn, ins, orden);
        optsEl.appendChild(btn);
    });

    panel.style.display = 'block';
}

function responder(btnClickeado, ins, orden) {
    if (E.respondido) return;
    E.respondido = true;

    const esCorrecta = btnClickeado.dataset.correcta === 'true';
    const allBtns = document.querySelectorAll('.mc-opt');

    // Colorear
    allBtns.forEach(b => {
        b.disabled = true;
        if (b.dataset.correcta === 'true') b.classList.add('correct-opt');
        else if (b === btnClickeado && !esCorrecta) b.classList.add('wrong-opt');
    });

    // Puntaje
    let ptsGanados, rewardGanada;
    if (esCorrecta) {
        ptsGanados  = 100;
        rewardGanada = ins.rewardBase;
        E.correctas++;
        E.racha++;
        if (E.racha > E.rachaMax) E.rachaMax = E.racha;
        // Bonus racha
        if (E.racha > 1) { ptsGanados += 20 * (E.racha - 1); rewardGanada += 0.01 * (E.racha - 1); }
    } else {
        ptsGanados  = 20;
        rewardGanada = ins.rewardBase * 0.2; // Viste el contenido igual
        E.racha = 0;
    }

    E.puntos  += ptsGanados;
    E.wallet  += rewardGanada;

    // Actualizar HUD
    actualizarWalletHUD(rewardGanada);
    actualizarNivelHUD();

    // Feedback inline
    mostrarFeedbackMC(esCorrecta, ptsGanados, rewardGanada, ins);
}

function mostrarFeedbackMC(esCorrecta, pts, reward, ins) {
    document.getElementById('action-panel').style.display = 'none';
    const fb = document.getElementById('mc-feedback');
    document.getElementById('mc-fb-icon').textContent = esCorrecta ? '✅' : '❌';
    document.getElementById('mc-fb-msg').innerHTML =
        `<strong>${esCorrecta ? `+${pts} pts · +$${reward.toFixed(2)}` : `+${pts} pts · +$${reward.toFixed(2)} (viste el contenido)`}</strong>${ins.explicacion}`;
    fb.style.display = 'flex';
}

function siguienteInsight() {
    document.getElementById('mc-feedback').style.display = 'none';
    marcarEpisodioCompleto();
    E.indexActual++;
    mostrarInsight();
}

// ============================================================
// HUD
// ============================================================
function actualizarWalletHUD(delta) {
    document.getElementById('wallet-display').textContent = `$${E.wallet.toFixed(2)}`;
    const d = document.getElementById('wallet-delta');
    d.textContent = `+$${delta.toFixed(2)}`;
    d.classList.add('show');
    setTimeout(() => { d.classList.remove('show'); d.style.transform=''; }, 1200);
}

function actualizarNivelHUD() {
    const nv = obtenerNivel(E.puntos);
    document.getElementById('level-badge').textContent = `Nv. ${nv.nombre}`;
}

// ============================================================
// BARRA DE EPISODIOS
// ============================================================
function construirBarraEpisodios() {
    const bar = document.getElementById('episodes-bar');
    bar.innerHTML = '';
    E.orden.forEach(() => {
        const seg = document.createElement('div'); seg.className = 'ep-seg';
        const fill = document.createElement('div'); fill.className = 'ep-seg-fill';
        seg.appendChild(fill); bar.appendChild(seg);
    });
}
function actualizarBarraEpisodios() {
    document.querySelectorAll('.ep-seg').forEach((s,i) => {
        s.classList.toggle('done', i < E.indexActual);
    });
}
function marcarEpisodioCompleto() {
    const segs = document.querySelectorAll('.ep-seg');
    if (segs[E.indexActual]) segs[E.indexActual].classList.add('done');
}

// ============================================================
// RESUMEN
// ============================================================
function mostrarResumen() {
    cambiarPantalla('screen-feed','screen-summary');
    const nv = obtenerNivel(E.puntos);

    document.getElementById('summary-amount').textContent    = `$${E.wallet.toFixed(2)}`;
    document.getElementById('wallet-bar-current').textContent = `$${E.wallet.toFixed(2)}`;
    document.getElementById('ss-pts').textContent            = E.puntos;
    document.getElementById('ss-correct').textContent        = `${E.correctas}/${E.orden.length}`;
    document.getElementById('ss-streak').textContent         = E.rachaMax;

    // Nivel
    document.getElementById('level-result-icon').textContent = nv.emoji;
    document.getElementById('level-result-name').textContent = nv.nombre.toUpperCase();
    document.getElementById('level-result-desc').textContent = nv.desc;

    const pct = Math.min((E.wallet / META_DOLARES) * 100, 100);
    setTimeout(() => { document.getElementById('wallet-bar-fill').style.width = pct + '%'; }, 600);
}

function abrirRetiro(m) {
    const urls = { paypal:'https://www.paypal.com/donate', crypto:'https://coinbase.com', kofi:'https://ko-fi.com/' };
    window.open(urls[m] || urls.kofi, '_blank');
}

function compartir() {
    const txt = `Alcancé el nivel "${obtenerNivel(E.puntos).nombre}" en MicroSecure y gané $${E.wallet.toFixed(2)} aprendiendo ciberseguridad 🛡️`;
    if (navigator.share) {
        navigator.share({ title:'MicroSecure', text:txt, url: window.location.href });
    } else {
        navigator.clipboard.writeText(txt + '\n' + window.location.href)
            .then(() => alert('¡Copiado! Compartilo con quien quieras.'));
    }
}

function irProfundidad() { window.open('https://www.youtube.com/@BestiaTantrica','_blank'); }

function reiniciar() {
    Object.assign(E, { indexActual:0, puntos:0, wallet:0, correctas:0, racha:0, rachaMax:0 });
    for (let i = E.orden.length-1; i>0; i--) {
        const j = Math.floor(Math.random()*(i+1));
        [E.orden[i],E.orden[j]] = [E.orden[j],E.orden[i]];
    }
    construirBarraEpisodios();
    cambiarPantalla('screen-summary','screen-feed');
    mostrarInsight();
}

// Tecla Enter para avanzar si el feedback está visible
document.addEventListener('keydown', e => {
    if (e.key === 'Enter' && document.getElementById('mc-feedback').style.display !== 'none') {
        siguienteInsight();
    }
});
