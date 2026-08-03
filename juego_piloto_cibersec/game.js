// ============================================================
// MicroSecure — Feed de Micro-Insights
// Concepto: Ver un insight real → confirmar con 1 clic → ganar micro-recompensa
// ============================================================

// BANCO DE INSIGHTS (no quizzes — el conocimiento está EN el reel)
const INSIGHTS = [
    {
        emoji: "📶",
        stat: { number: "147", unit: "contraseñas robadas por hora" },
        headline: "Tu Wi-Fi pública es una trampa.",
        context: "En redes públicas sin VPN, un atacante puede capturar tus credenciales con herramientas gratuitas en menos de 30 segundos.",
        categoria: "WI-FI",
        rewardBase: 0.07,
        bgAccent: "rgba(239,68,68,0.12)",
        color: "#f87171",
        sponsor: "Patrocinado por NordVPN"
    },
    {
        emoji: "🎣",
        stat: { number: "91%", unit: "de los hackeos empieza con un email" },
        headline: "El phishing es la arma #1 de los hackers.",
        context: "Un atacante puede crear un email idéntico al de tu banco en 5 minutos. La diferencia está en el dominio del remitente — siempre verificalo.",
        categoria: "PHISHING",
        rewardBase: 0.06,
        bgAccent: "rgba(245,158,11,0.1)",
        color: "#fbbf24",
        sponsor: "Patrocinado por Proofpoint"
    },
    {
        emoji: "🔑",
        stat: { number: "23M", unit: "personas usan '123456' como contraseña" },
        headline: "Tu contraseña más fácil es la primera que prueban.",
        context: "Los atacantes usan listas de millones de contraseñas comunes. Una contraseña de 12 caracteres mixtos tardaría 34,000 años en crackearse por fuerza bruta.",
        categoria: "CONTRASEÑAS",
        rewardBase: 0.05,
        bgAccent: "rgba(99,102,241,0.12)",
        color: "#818cf8",
        sponsor: "Patrocinado por 1Password"
    },
    {
        emoji: "🔒",
        stat: { number: "58%", unit: "de los sitios web aún no fuerzan HTTPS" },
        headline: "Sin el candado, cualquiera puede leer tus datos.",
        context: "HTTPS cifra la comunicación entre vos y el servidor. Sin él, tu contraseña viaja en texto plano por la red. Siempre buscá el 🔒 en la barra del navegador.",
        categoria: "HTTPS/TLS",
        rewardBase: 0.06,
        bgAccent: "rgba(16,185,129,0.1)",
        color: "#34d399",
        sponsor: "Patrocinado por Let's Encrypt"
    },
    {
        emoji: "📱",
        stat: { number: "99.9%", unit: "de los ataques automáticos bloqueados por 2FA" },
        headline: "Agregar el doble factor toma 30 segundos.",
        context: "El 2FA requiere algo que sabés (contraseña) + algo que tenés (teléfono). Aunque te roben la contraseña, sin el código SMS o la app, no pueden entrar.",
        categoria: "2FA",
        rewardBase: 0.07,
        bgAccent: "rgba(6,182,212,0.1)",
        color: "#22d3ee",
        sponsor: "Patrocinado por Authy"
    },
    {
        emoji: "⚡",
        stat: { number: "60%", unit: "de las brechas explotan vulnerabilidades ya parcheadas" },
        headline: "El botón 'Actualizar' es tu escudo.",
        context: "Cuando sale una actualización de seguridad, los atacantes analizan el parche para crear exploits en horas. Las máquinas sin actualizar son blancos fáciles.",
        categoria: "ACTUALIZACIONES",
        rewardBase: 0.05,
        bgAccent: "rgba(245,158,11,0.1)",
        color: "#fbbf24",
        sponsor: "Patrocinado por Microsoft"
    },
    {
        emoji: "💸",
        stat: { number: "$1.50", unit: "vale tu perfil completo en la dark web" },
        headline: "Tus datos personales se venden al por mayor.",
        context: "Nombre, email, fecha de nacimiento y contraseña se combinan en bases de datos filtradas. Verificá si tu email fue comprometido en haveibeenpwned.com",
        categoria: "DATA BREACH",
        rewardBase: 0.08,
        bgAccent: "rgba(239,68,68,0.1)",
        color: "#f87171",
        sponsor: "Patrocinado por HaveIBeenPwned"
    },
    {
        emoji: "💾",
        stat: { number: "11s", unit: "cada 11 segundos una empresa es atacada con ransomware" },
        headline: "Sin backup, un ataque lo borra todo.",
        context: "El ransomware cifra todos tus archivos y pide rescate. La única defensa real es tener copias de seguridad offline actualizadas. Regla 3-2-1: 3 copias, 2 medios, 1 offsite.",
        categoria: "RANSOMWARE",
        rewardBase: 0.09,
        bgAccent: "rgba(139,92,246,0.1)",
        color: "#a78bfa",
        sponsor: "Patrocinado por Backblaze"
    }
];

// CONFIGURACIÓN
const TIMER_SEGUNDOS = 8;
const REWARD_MULTIPLIER_NEW = 1.0;   // "Aprendí algo nuevo" → 100% de la recompensa
const REWARD_MULTIPLIER_KNEW = 0.4;  // "Ya lo sabía" → 40% (igual sumaste atención)
const META_DOLARES = 5.00;

// ESTADO
let estado = {
    indexActual: 0,
    orden: [],
    walletTotal: 0,
    sesionGanado: 0,
    sesionVistos: 0,
    sesionNuevos: 0,
    rachaActual: 0,
    rachaMax: 0,
    timerInterval: null,
    tiempoRestante: TIMER_SEGUNDOS,
    enEjecucion: false,
    segFill: null,   // referencia al segmento de progreso activo
};

// ============================================================
// FLUJO PRINCIPAL
// ============================================================
function iniciarFeed() {
    // Mezclar insights
    estado.orden = INSIGHTS.map((_, i) => i);
    for (let i = estado.orden.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [estado.orden[i], estado.orden[j]] = [estado.orden[j], estado.orden[i]];
    }

    estado.indexActual = 0;
    estado.walletTotal = 0;
    estado.sesionGanado = 0;
    estado.sesionVistos = 0;
    estado.sesionNuevos = 0;
    estado.rachaActual = 0;
    estado.rachaMax = 0;

    construirBarraEpisodios();
    cambiarPantalla('screen-intro', 'screen-feed');
    mostrarInsight();
}

function cambiarPantalla(ocultar, mostrar) {
    document.getElementById(ocultar).classList.remove('active');
    const el = document.getElementById(mostrar);
    el.classList.add('active');
    window.scrollTo(0, 0);
}

function mostrarInsight() {
    if (estado.indexActual >= estado.orden.length) {
        mostrarResumen();
        return;
    }

    const idx = estado.orden[estado.indexActual];
    const insight = INSIGHTS[idx];

    estado.enEjecucion = true;
    estado.tiempoRestante = TIMER_SEGUNDOS;

    // Resetear panels
    document.getElementById('action-panel').style.display = 'none';
    document.getElementById('reward-flash').style.display = 'none';

    // Actualizar sponsor
    document.getElementById('reel-sponsor').textContent = insight.sponsor;

    // Inyectar contenido
    document.getElementById('reel-body').innerHTML = `
        <div class="reel-hero" style="background: ${insight.bgAccent};">
            <div class="reel-emoji">${insight.emoji}</div>
            <div class="reel-stat-wrapper">
                <div class="reel-stat-number" style="color: ${insight.color}">${insight.stat.number}</div>
                <div class="reel-stat-unit">${insight.stat.unit}</div>
            </div>
            <div class="reel-headline">${insight.headline}</div>
            <div class="reel-context">${insight.context}</div>
        </div>
        <div class="reel-footer">
            <div class="reel-category" style="color: ${insight.color}">${insight.categoria}</div>
            <div class="reel-reward-preview">+$${insight.rewardBase.toFixed(2)}</div>
        </div>
    `;

    // Reiniciar card (re-trigger animation)
    const card = document.getElementById('reel-card');
    card.style.animation = 'none';
    card.offsetWidth; // reflow
    card.style.animation = '';

    iniciarTimer(insight);
    actualizarBarraEpisodios();
}

// ============================================================
// TIMER CIRCULAR SVG
// ============================================================
function iniciarTimer(insight) {
    clearInterval(estado.timerInterval);

    const ring = document.getElementById('ring-fill');
    const sec = document.getElementById('timer-seconds');
    const CIRCUMFERENCE = 163.36; // 2π × 26

    // Reset ring
    ring.style.transition = 'none';
    ring.style.strokeDashoffset = '0';
    ring.classList.remove('urgent');
    sec.textContent = TIMER_SEGUNDOS;
    estado.tiempoRestante = TIMER_SEGUNDOS;

    // Activar animación CSS del segmento
    const segFill = document.querySelector(`.ep-seg:nth-child(${estado.indexActual + 1}) .ep-seg-fill`);
    if (segFill) {
        segFill.style.transition = 'none';
        segFill.style.width = '0%';
        segFill.offsetWidth;
        segFill.style.transition = `width ${TIMER_SEGUNDOS}s linear`;
        segFill.style.width = '100%';
    }

    // Animar el ring con JS para mayor control
    let elapsed = 0;
    const TICK = 100; // ms
    const TOTAL_MS = TIMER_SEGUNDOS * 1000;

    estado.timerInterval = setInterval(() => {
        elapsed += TICK;
        const progress = elapsed / TOTAL_MS;
        const offset = CIRCUMFERENCE * progress;
        ring.style.transition = 'none';
        ring.style.strokeDashoffset = offset.toString();

        const remaining = Math.ceil((TOTAL_MS - elapsed) / 1000);
        sec.textContent = Math.max(0, remaining);

        if (remaining <= 2) {
            ring.classList.add('urgent');
        }

        if (elapsed >= TOTAL_MS) {
            clearInterval(estado.timerInterval);
            if (estado.enEjecucion) {
                terminarInsight();
            }
        }
    }, TICK);
}

function terminarInsight() {
    estado.enEjecucion = false;
    clearInterval(estado.timerInterval);
    const panel = document.getElementById('action-panel');
    panel.style.display = 'block';
}

// ============================================================
// ACCIÓN DE 1 CLIC
// ============================================================
function confirmar(esNuevo) {
    if (!document.getElementById('action-panel').style.display || document.getElementById('action-panel').style.display === 'none') return;

    document.getElementById('action-panel').style.display = 'none';

    const idx = estado.orden[estado.indexActual];
    const insight = INSIGHTS[idx];
    const rewardMult = esNuevo ? REWARD_MULTIPLIER_NEW : REWARD_MULTIPLIER_KNEW;
    const rewardAmount = insight.rewardBase * rewardMult;

    // Actualizar estado
    estado.sesionGanado += rewardAmount;
    estado.walletTotal += rewardAmount;
    estado.sesionVistos++;
    if (esNuevo) {
        estado.sesionNuevos++;
        estado.rachaActual++;
        if (estado.rachaActual > estado.rachaMax) estado.rachaMax = estado.rachaActual;
    } else {
        estado.rachaActual = 0;
    }

    actualizarWallet(rewardAmount);
    mostrarFlash(esNuevo, rewardAmount, insight);
}

function mostrarFlash(esNuevo, amount, insight) {
    const flash = document.getElementById('reward-flash');
    const inner = document.getElementById('reward-flash-inner');

    inner.innerHTML = `
        <div class="flash-emoji">${esNuevo ? '🎉' : '✅'}</div>
        <div class="flash-title">${esNuevo ? '¡Nuevo conocimiento!' : '¡Repaso confirmado!'}</div>
        <div class="flash-amount">+$${amount.toFixed(2)}</div>
        <div class="flash-sub">Balance total: $${estado.walletTotal.toFixed(2)}</div>
    `;

    flash.style.display = 'flex';

    // Auto-cerrar después de 1.6s y pasar al siguiente
    setTimeout(() => {
        flash.style.display = 'none';
        marcarEpisodioCompleto();
        estado.indexActual++;
        mostrarInsight();
    }, 1600);
}

// ============================================================
// WALLET Y HUD
// ============================================================
function actualizarWallet(delta) {
    const display = document.getElementById('wallet-display');
    const deltaEl = document.getElementById('wallet-delta');

    display.textContent = `$${estado.walletTotal.toFixed(2)}`;

    // Flash del delta
    deltaEl.textContent = `+$${delta.toFixed(2)}`;
    deltaEl.classList.add('show');
    setTimeout(() => {
        deltaEl.classList.remove('show');
        deltaEl.style.transform = '';
    }, 1000);
}

// ============================================================
// BARRA DE EPISODIOS
// ============================================================
function construirBarraEpisodios() {
    const bar = document.getElementById('episodes-bar');
    bar.innerHTML = '';
    estado.orden.forEach(() => {
        const seg = document.createElement('div');
        seg.className = 'ep-seg';
        const fill = document.createElement('div');
        fill.className = 'ep-seg-fill';
        seg.appendChild(fill);
        bar.appendChild(seg);
    });
}

function actualizarBarraEpisodios() {
    const segs = document.querySelectorAll('.ep-seg');
    segs.forEach((seg, i) => {
        if (i < estado.indexActual) seg.classList.add('done');
        else seg.classList.remove('done');
    });
}

function marcarEpisodioCompleto() {
    const segs = document.querySelectorAll('.ep-seg');
    if (segs[estado.indexActual]) {
        segs[estado.indexActual].classList.add('done');
    }
}

// ============================================================
// RESUMEN FINAL
// ============================================================
function mostrarResumen() {
    cambiarPantalla('screen-feed', 'screen-summary');

    const ganado = estado.sesionGanado;
    document.getElementById('summary-amount').textContent = `$${ganado.toFixed(2)}`;
    document.getElementById('wallet-bar-current').textContent = `$${ganado.toFixed(2)}`;
    document.getElementById('ss-watched').textContent = estado.sesionVistos;
    document.getElementById('ss-new').textContent = estado.sesionNuevos;
    document.getElementById('ss-streak').textContent = estado.rachaMax;

    const pct = Math.min((ganado / META_DOLARES) * 100, 100);
    setTimeout(() => {
        document.getElementById('wallet-bar-fill').style.width = pct + '%';
    }, 600);
}

function abrirRetiro(metodo) {
    const urls = {
        paypal: 'https://www.paypal.com/donate',
        crypto: 'https://coinbase.com',
        kofi: 'https://ko-fi.com/'
    };
    window.open(urls[metodo] || urls.kofi, '_blank');
}

function compartir() {
    const url = window.location.href;
    const text = `Acabo de aprender sobre ciberseguridad y gané $${estado.sesionGanado.toFixed(2)}. ¡Vos también podés! 🛡️`;
    if (navigator.share) {
        navigator.share({ title: 'MicroSecure', text, url });
    } else {
        navigator.clipboard.writeText(`${text}\n${url}`).then(() => {
            alert('¡Enlace copiado! Compartilo con quien quieras.');
        });
    }
}

function irProfundidad() {
    window.open('https://www.youtube.com/@BestiaTantrica', '_blank');
}

function reiniciar() {
    estado.indexActual = 0;
    estado.sesionGanado = 0;
    estado.sesionVistos = 0;
    estado.sesionNuevos = 0;
    estado.rachaActual = 0;
    estado.rachaMax = 0;

    // Re-mezclar
    for (let i = estado.orden.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [estado.orden[i], estado.orden[j]] = [estado.orden[j], estado.orden[i]];
    }

    construirBarraEpisodios();
    cambiarPantalla('screen-summary', 'screen-feed');
    mostrarInsight();
}
