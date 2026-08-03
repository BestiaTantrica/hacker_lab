// ============================================================
// HackerQuest — Game Logic
// Desafíos rápidos de ciberseguridad con sistema de puntos y recompensas
// ============================================================

// BANCO DE DESAFÍOS (12 preguntas de 5 segundos)
const DESAFIOS = [
    {
        categoria: "🔐 CRIPTOGRAFÍA",
        headline: "Un atacante intercepta tu tráfico.\n¿Qué protocolo <code>encripta</code> tus datos en la web?",
        pregunta: "¿Cuál de estas tecnologías protege la conexión entre tu navegador y el servidor?",
        opciones: ["HTTP (sin cifrado)", "HTTPS / TLS", "FTP", "Telnet"],
        correcta: 1,
        explicacion: "HTTPS usa TLS (Transport Layer Security) para cifrar todo el tráfico. Sin él, un atacante en la misma red Wi-Fi puede leer tus contraseñas en texto plano. Siempre busca el 🔒 en la barra de tu navegador.",
        puntos: 100
    },
    {
        categoria: "🐟 INGENIERÍA SOCIAL",
        headline: "Recibes un email que dice:\n<code>\"Tu cuenta será bloqueada. Haz clic aquí.\"</code>",
        pregunta: "¿Qué tipo de ataque es este?",
        opciones: ["Ransomware", "DDoS", "Phishing", "Exploit de día cero"],
        correcta: 2,
        explicacion: "Phishing es cuando los atacantes se hacen pasar por entidades legítimas (bancos, empresas) para robar tus credenciales. Siempre verifica el remitente real del email y nunca hagas clic en links sospechosos.",
        puntos: 100
    },
    {
        categoria: "🕵️ RECON PASIVO",
        headline: "Un hacker busca subdominios de una empresa\nsin enviarle ni un solo paquete de datos.",
        pregunta: "¿Cómo se llama esta técnica de reconocimiento sin contacto directo?",
        opciones: ["Port Scanning", "Passive Reconnaissance", "SQL Injection", "Brute Force"],
        correcta: 1,
        explicacion: "El Passive Recon usa fuentes públicas (Google, Shodan, crt.sh, Wayback Machine) para mapear la superficie de ataque sin alertar al objetivo. Es la base del Bug Bounty profesional.",
        puntos: 150
    },
    {
        categoria: "🪪 AUTENTICACIÓN",
        headline: "Un banco solo pide tu contraseña para entrar.\n¿Qué le falta para ser seguro?",
        pregunta: "¿Qué mecanismo de seguridad debería agregar?",
        opciones: ["Un CAPTCHA", "Una contraseña más larga", "2FA (Doble Factor)", "Cifrar la contraseña en el cliente"],
        correcta: 2,
        explicacion: "El 2FA (Autenticación de Dos Factores) requiere algo que SABÉS (contraseña) + algo que TENÉS (teléfono/código). Aunque tu contraseña sea robada, el atacante no puede acceder sin el segundo factor.",
        puntos: 100
    },
    {
        categoria: "💉 INYECCIÓN",
        headline: "Un login acepta el usuario:\n<code>' OR '1'='1</code>\ny deja entrar sin contraseña.",
        pregunta: "¿Qué vulnerabilidad clásica es esta?",
        opciones: ["XSS (Cross-Site Scripting)", "CSRF", "SQL Injection", "Path Traversal"],
        correcta: 2,
        explicacion: "SQL Injection ocurre cuando el input del usuario se concatena directamente en una query SQL sin validación. La solución son las Prepared Statements (consultas parametrizadas) que tratan el input como dato, nunca como código.",
        puntos: 150
    },
    {
        categoria: "🌐 SUBDOMINIOS",
        headline: "El subdominio <code>viejo.empresa.com</code> apunta a\nun servicio en la nube que ya no existe.",
        pregunta: "¿Qué vulnerabilidad puede tener un Bug Hunter aquí?",
        opciones: ["CORS Misconfiguration", "Subdomain Takeover", "Open Redirect", "JWT Bypass"],
        correcta: 1,
        explicacion: "Subdomain Takeover: si el registro DNS apunta a un recurso reclamable (GitHub Pages, S3, Heroku), un atacante puede 'tomarlo' y servir contenido malicioso desde un dominio de confianza. Vale entre $300 y $3000 en HackerOne.",
        puntos: 200
    },
    {
        categoria: "🔑 SECRETOS",
        headline: "Un desarrollador sube su proyecto a GitHub\ny olvida incluir el archivo <code>.env</code> en .gitignore.",
        pregunta: "¿Cuál es el riesgo inmediato?",
        opciones: ["Pérdida de performance", "Exposición de API keys y contraseñas", "Error de compilación", "Incompatibilidad de versiones"],
        correcta: 1,
        explicacion: "El archivo .env contiene API keys, tokens y contraseñas de base de datos. Si se sube a un repositorio público, cualquier persona (o bot) puede encontrarlo con Google Dorks o Gitleaks y abusar de esas credenciales.",
        puntos: 150
    },
    {
        categoria: "🛡️ DEFENSA",
        headline: "Una app web incluye los headers:\n<code>Content-Security-Policy</code> y <code>X-Frame-Options</code>.",
        pregunta: "¿Para qué sirven estos headers de respuesta HTTP?",
        opciones: ["Mejorar el SEO", "Prevenir XSS y Clickjacking", "Comprimir los datos", "Autenticar al servidor"],
        correcta: 1,
        explicacion: "Los Security Headers son la primera línea de defensa del servidor. CSP previene inyección de scripts maliciosos (XSS). X-Frame-Options evita que tu página sea embebida en un iframe para ataques de Clickjacking.",
        puntos: 150
    },
    {
        categoria: "☁️ CLOUD HACKING",
        headline: "Una API devuelve el mismo objeto para cualquier\nvalor de ID sin verificar si eres el dueño.",
        pregunta: "¿Cómo se llama esta vulnerabilidad de lógica de negocio?",
        opciones: ["SSRF", "IDOR", "RCE", "XXE"],
        correcta: 1,
        explicacion: "IDOR (Insecure Direct Object Reference) permite acceder a recursos de otros usuarios cambiando un ID. Ejemplo: cambiar /api/user/123 a /api/user/124 y ver datos ajenos. Es la vulnerabilidad #1 más reportada en HackerOne.",
        puntos: 200
    },
    {
        categoria: "🔓 CONTRASEÑAS",
        headline: "Una base de datos filtrada tiene las contraseñas\nalmacenadas como <code>MD5('password123')</code>.",
        pregunta: "¿Por qué esto es inseguro incluso si está 'hasheada'?",
        opciones: ["MD5 es reversible matemáticamente", "MD5 es muy lento para calcular", "Las Rainbow Tables pueden crackearla en segundos", "MD5 no es un algoritmo real"],
        correcta: 2,
        explicacion: "MD5 es vulnerable a Rainbow Tables (tablas precalculadas de hashes). Para contraseñas se debe usar bcrypt, scrypt o Argon2, que incluyen un 'salt' (valor aleatorio) y están diseñados para ser computacionalmente costosos.",
        puntos: 150
    },
    {
        categoria: "🕸️ WEB ATTACKS",
        headline: "El servidor hace un request HTTP a una URL\nque el atacante controla: <code>file:///etc/passwd</code>",
        pregunta: "¿Qué tipo de vulnerabilidad es esta?",
        opciones: ["XSS Reflejado", "CORS", "SSRF (Server-Side Request Forgery)", "CSRF"],
        correcta: 2,
        explicacion: "SSRF le permite al atacante hacer que el SERVIDOR realice requests arbitrarios (a la red interna, metadata de cloud, sistemas internos). En AWS, el endpoint 169.254.169.254 puede devolver credenciales IAM válidas.",
        puntos: 200
    },
    {
        categoria: "🎓 BOUNTY HUNTER",
        headline: "Encontrás un bug en una empresa que paga recompensas.\nEscribís el reporte y lo enviás. ¿Cuál es el camino correcto?",
        pregunta: "¿Qué es lo PRIMERO que debés verificar antes de reportar?",
        opciones: ["Que el bug sea crítico", "Que el dominio esté dentro del Scope del programa", "Que tengas capturas de pantalla", "Que el bug sea nuevo"],
        correcta: 1,
        explicacion: "El Scope define exactamente qué dominios y funciones están autorizados a testear. Reportar fuera del scope puede resultar en el rechazo del reporte e incluso acciones legales. Siempre leé las reglas del programa antes.",
        puntos: 300
    }
];

// ESTADO DEL JUEGO
let estado = {
    desafioActual: 0,
    desafiosOrden: [],
    puntaje: 0,
    racha: 0,
    rachaMax: 0,
    correctas: 0,
    resultados: [], // 'correct' | 'wrong' | 'timeout'
    timerInterval: null,
    timerAnimFrame: null,
    tiempoRestante: 5,
    respondido: false,
    acumuladoTotal: 0 // simulado
};

// ============================================================
// MATRIX RAIN ANIMATION
// ============================================================
function iniciarMatrixRain() {
    const canvas = document.getElementById('matrix-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&<>{}[]|/\\;:';
    const fontSize = 14;
    const cols = Math.floor(canvas.width / fontSize);
    const drops = Array(cols).fill(1);

    function draw() {
        ctx.fillStyle = 'rgba(5, 6, 15, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#6366f1';
        ctx.font = fontSize + 'px JetBrains Mono, monospace';
        drops.forEach((y, i) => {
            const char = chars[Math.floor(Math.random() * chars.length)];
            ctx.fillText(char, i * fontSize, y * fontSize);
            if (y * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
            drops[i]++;
        });
    }

    setInterval(draw, 60);
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

iniciarMatrixRain();

// ============================================================
// FLUJO DEL JUEGO
// ============================================================
function iniciarJuego() {
    // Mezclar desafíos de forma aleatoria (Fisher-Yates shuffle)
    estado.desafiosOrden = DESAFIOS.map((_, i) => i);
    for (let i = estado.desafiosOrden.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [estado.desafiosOrden[i], estado.desafiosOrden[j]] = [estado.desafiosOrden[j], estado.desafiosOrden[i]];
    }

    // Tomar los primeros 8 desafíos
    estado.desafiosOrden = estado.desafiosOrden.slice(0, 8);
    estado.desafioActual = 0;
    estado.puntaje = 0;
    estado.racha = 0;
    estado.rachaMax = 0;
    estado.correctas = 0;
    estado.resultados = [];

    cambiarPantalla('screen-intro', 'screen-game');
    mostrarDesafio();
}

function cambiarPantalla(ocultar, mostrar) {
    document.getElementById(ocultar).classList.remove('active');
    const el = document.getElementById(mostrar);
    el.classList.add('active');
    el.scrollTop = 0;
}

function mostrarDesafio() {
    const idx = estado.desafiosOrden[estado.desafioActual];
    const desafio = DESAFIOS[idx];

    estado.respondido = false;
    actualizarHUD();
    construirPuntos();

    // Resetear UI
    document.getElementById('feedback-panel').style.display = 'none';
    document.getElementById('options-grid').style.display = 'grid';

    // Inyectar contenido del desafío
    document.getElementById('challenge-category').innerHTML = desafio.categoria;
    document.getElementById('challenge-headline').innerHTML = desafio.headline;
    document.getElementById('challenge-question').textContent = desafio.pregunta;

    // Generar opciones mezcladas
    const letras = ['A', 'B', 'C', 'D'];
    const opcionesGrid = document.getElementById('options-grid');
    opcionesGrid.innerHTML = '';

    // Mapear índice real → índice mezclado
    const orden = [0, 1, 2, 3].sort(() => Math.random() - 0.5);
    const mapeoCorrecta = orden.indexOf(desafio.correcta);

    orden.forEach((opIdx, i) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.id = `option-${i}`;
        btn.innerHTML = `<span class="option-letter">${letras[i]}.</span> ${desafio.opciones[opIdx]}`;
        btn.onclick = () => responder(i, mapeoCorrecta, desafio);
        opcionesGrid.appendChild(btn);
    });

    iniciarTimer(desafio);
}

function iniciarTimer(desafio) {
    clearInterval(estado.timerInterval);
    estado.tiempoRestante = 5;

    const timerDisplay = document.getElementById('timer-display');
    const timerBar = document.getElementById('timer-bar');

    timerDisplay.textContent = '5';
    timerDisplay.classList.remove('urgent');
    timerBar.style.transition = 'none';
    timerBar.style.width = '100%';

    // Forzar reflow para que la transición funcione
    timerBar.offsetWidth;
    timerBar.style.transition = 'width 5s linear';
    timerBar.style.width = '0%';

    estado.timerInterval = setInterval(() => {
        estado.tiempoRestante--;
        timerDisplay.textContent = estado.tiempoRestante;

        if (estado.tiempoRestante <= 2) {
            timerDisplay.classList.add('urgent');
        }

        if (estado.tiempoRestante <= 0) {
            clearInterval(estado.timerInterval);
            if (!estado.respondido) {
                tiempoAgotado(desafio);
            }
        }
    }, 1000);
}

function responder(indiceSeleccionado, indiceCorrectoMezclado, desafio) {
    if (estado.respondido) return;
    estado.respondido = true;
    clearInterval(estado.timerInterval);

    const esCorrecta = indiceSeleccionado === indiceCorrectoMezclado;
    const btns = document.querySelectorAll('.option-btn');

    // Marcar visual
    btns.forEach((btn, i) => {
        btn.disabled = true;
        if (i === indiceCorrectoMezclado) btn.classList.add('correct');
        else if (i === indiceSeleccionado && !esCorrecta) btn.classList.add('wrong');
    });

    if (esCorrecta) {
        estado.racha++;
        estado.correctas++;
        const bonus = estado.racha > 3 ? Math.floor(desafio.puntos * 0.5) : (estado.racha > 1 ? Math.floor(desafio.puntos * 0.2) : 0);
        const puntosGanados = desafio.puntos + bonus;
        estado.puntaje += puntosGanados;
        if (estado.racha > estado.rachaMax) estado.rachaMax = estado.racha;
        estado.resultados.push('correct');
        mostrarFeedback(true, desafio, puntosGanados);
    } else {
        estado.racha = 0;
        estado.resultados.push('wrong');
        mostrarFeedback(false, desafio, 0);
    }

    actualizarHUD();
}

function tiempoAgotado(desafio) {
    estado.respondido = true;
    estado.racha = 0;
    estado.resultados.push('timeout');

    const btns = document.querySelectorAll('.option-btn');
    btns.forEach((btn, i) => {
        btn.disabled = true;
    });
    // Revelar la correcta
    const correctaBtn = document.querySelector(`#option-0`);
    // Buscar el botón con la respuesta correcta (es el que tiene 'correct' class)
    // En este caso el índice correcto ya está mapeado en el HTML

    mostrarFeedback(null, desafio, 0); // null = timeout
}

function mostrarFeedback(esCorrecta, desafio, puntosGanados) {
    const panel = document.getElementById('feedback-panel');
    const icon = document.getElementById('feedback-icon');
    const text = document.getElementById('feedback-text');
    const exp = document.getElementById('feedback-explanation');

    panel.style.display = 'block';
    document.getElementById('options-grid').style.display = 'none';

    if (esCorrecta === true) {
        icon.textContent = '✅';
        text.style.color = '#34d399';
        const rachaMsg = estado.racha > 1 ? ` 🔥 Racha x${estado.racha}!` : '';
        text.textContent = `¡Correcto! +${puntosGanados} pts${rachaMsg}`;
    } else if (esCorrecta === false) {
        icon.textContent = '❌';
        text.style.color = '#f87171';
        text.textContent = 'Incorrecto — así se aprende.';
    } else {
        icon.textContent = '⏱️';
        text.style.color = '#f59e0b';
        text.textContent = '¡Se acabó el tiempo!';
    }

    exp.innerHTML = `<strong>💡 Explicación:</strong> ${desafio.explicacion}`;
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function siguienteDesafio() {
    estado.desafioActual++;

    if (estado.desafioActual >= estado.desafiosOrden.length) {
        mostrarResultados();
    } else {
        actualizarHUD();
        mostrarDesafio();
    }
}

// ============================================================
// HUD Y PUNTOS
// ============================================================
function actualizarHUD() {
    const nivel = Math.floor(estado.puntaje / 500) + 1;
    document.getElementById('hud-level').textContent = nivel;
    document.getElementById('hud-score').textContent = estado.puntaje.toLocaleString();
    document.getElementById('hud-streak').textContent = `🔥 ${estado.racha}`;
    construirPuntos();
}

function construirPuntos() {
    const container = document.getElementById('progress-dots');
    container.innerHTML = '';
    for (let i = 0; i < estado.desafiosOrden.length; i++) {
        const dot = document.createElement('div');
        dot.className = 'dot';
        if (i < estado.desafioActual) {
            dot.classList.add(estado.resultados[i] === 'correct' ? 'done' : 'wrong-dot');
        } else if (i === estado.desafioActual) {
            dot.classList.add('current');
        }
        container.appendChild(dot);
    }
}

// ============================================================
// RESULTADOS
// ============================================================
function mostrarResultados() {
    cambiarPantalla('screen-game', 'screen-results');

    const total = estado.desafiosOrden.length;
    const pct = estado.correctas / total;

    // Trofeo y rank
    let trophy, rankLabel, titulo, subtitulo;
    if (pct >= 0.9) { trophy = '🏆'; rankLabel = 'S'; titulo = '¡Sos un Hacker Élite!'; subtitulo = 'Puntuación perfecta. El Bug Bounty te espera.'; }
    else if (pct >= 0.75) { trophy = '🥇'; rankLabel = 'A'; titulo = '¡Excelente Trabajo!'; subtitulo = 'Dominás los conceptos fundamentales de ciberseguridad.'; }
    else if (pct >= 0.5) { trophy = '🥈'; rankLabel = 'B'; titulo = 'Buen Intento'; subtitulo = 'Seguí aprendiendo. Cada error te hace más fuerte.'; }
    else { trophy = '📚'; rankLabel = 'C'; titulo = 'Hay que Entrenar Más'; subtitulo = 'La ciberseguridad se aprende jugando. ¡Intentalo de nuevo!'; }

    document.getElementById('results-trophy').textContent = trophy;
    document.getElementById('results-title').textContent = titulo;
    document.getElementById('results-subtitle').textContent = subtitulo;
    document.getElementById('res-score').textContent = estado.puntaje.toLocaleString();
    document.getElementById('res-correct').textContent = `${estado.correctas}/${total}`;
    document.getElementById('res-streak').textContent = estado.rachaMax;
    document.getElementById('res-rank').textContent = rankLabel;

    // SISTEMA DE RECOMPENSA SIMULADO
    const recompensa = (estado.puntaje / 1000 * 0.5).toFixed(2); // $0.50 por cada 1000 pts
    estado.acumuladoTotal = parseFloat(recompensa);
    const meta = 5.00;
    const pctRecompensa = Math.min((estado.acumuladoTotal / meta) * 100, 100);

    document.getElementById('reward-amount').textContent = `$${recompensa}`;
    setTimeout(() => {
        document.getElementById('reward-bar').style.width = pctRecompensa + '%';
    }, 600);
}

function abrirDonacion() {
    // Por ahora, redirigir a Ko-fi o una futura página de pago
    window.open('https://ko-fi.com/', '_blank');
}

function reiniciarJuego() {
    cambiarPantalla('screen-results', 'screen-intro');
    // Resetear estado
    estado = {
        desafioActual: 0,
        desafiosOrden: [],
        puntaje: 0,
        racha: 0,
        rachaMax: 0,
        correctas: 0,
        resultados: [],
        timerInterval: null,
        tiempoRestante: 5,
        respondido: false,
        acumuladoTotal: 0
    };
}

// Presionar Enter en opciones
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        const nextBtn = document.getElementById('btn-next');
        if (nextBtn && nextBtn.closest('#feedback-panel') && document.getElementById('feedback-panel').style.display !== 'none') {
            siguienteDesafio();
        }
    }
    // Teclas 1-4 para seleccionar opciones
    const keyMap = { '1': 0, '2': 1, '3': 2, '4': 3 };
    if (keyMap[e.key] !== undefined && !estado.respondido) {
        const idx = estado.desafiosOrden[estado.desafioActual];
        const desafio = DESAFIOS[idx];
        const btns = document.querySelectorAll('.option-btn');
        if (btns[keyMap[e.key]] && document.getElementById('screen-game').classList.contains('active')) {
            btns[keyMap[e.key]].click();
        }
    }
});
