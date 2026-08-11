// Astro-Currículum MVP — Motor Lógico

const STORAGE_KEY = 'astro_curriculum_v1';

// ── ESTADO GLOBAL ───────────────────────────────────────────
let E = {
    email: '', fechaNac: '', horaNac: '',
    puntos: 0, 
    carta: {}, // Aquí guardaremos la carta real completa
    respuestas: []
};

// ── PERSISTENCIA ────────────────────────────────────────────
function cargarDatos() {
    try {
        const d = localStorage.getItem(STORAGE_KEY);
        if(d) {
            const data = JSON.parse(d);
            E.puntos = data.puntos || 0;
            if(data.email) {
                document.getElementById('user-email').value = data.email;
                document.getElementById('user-date').value = data.fechaNac;
                document.getElementById('user-time').value = data.horaNac;
            }
        }
    } catch(e){}
}
function guardarDatos() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(E));
}

// ── INICIO ──────────────────────────────────────────────────
window.onload = () => {
    cargarDatos();
};

async function iniciarAstroViaje() {
    const email = document.getElementById('user-email').value;
    const date = document.getElementById('user-date').value;
    const time = document.getElementById('user-time').value;

    if(!email || !date || !time) {
        alert("Necesitamos tus datos para calcular tu cielo.");
        return;
    }

    E.email = email; E.fechaNac = date; E.horaNac = time;
    guardarDatos();
    
    const btn = document.querySelector('.btn-primary');
    if(btn) { btn.textContent = "Calculando Efemérides..."; btn.disabled = true; }

    try {
        const response = await fetch("http://143.47.115.34:8000/api/astrology/natal", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                fecha: date,
                hora: time,
                utc_offset: "-03:00", 
                lat: -34.6037,
                lon: -58.3816
            })
        });
        
        const data = await response.json();
        if(data.status === "success") {
            E.carta = data.carta; // Sol, Luna, Asc, Mercurio, Venus, Marte, Jupiter, Saturno, Urano, Neptuno, Pluton, MC
            guardarDatos();
        } else {
            console.error("Error del motor:", data.message);
            alert("Error calculando tu carta.");
        }
    } catch(err) {
        console.error("Error de conexión:", err);
        alert("Sin conexión con el OCI-2.");
    }
    
    if(btn) { btn.textContent = "CALCULAR MAPA →"; btn.disabled = false; }

    generarColumnaVertebral();
    cambiarPantalla('screen-intro', 'screen-feed');
}

function cambiarPantalla(ocultar, mostrar) {
    document.getElementById(ocultar).classList.remove('active');
    document.getElementById(mostrar).classList.add('active');
    window.scrollTo(0,0);
}

// ── COLUMNA VERTEBRAL (MAPA NATAL REAL) ───────────────────────

const PLANETAS_INFO = {
    'sol': { emoji: '☀️', nombre: 'Sol', desc: 'Tu identidad consciente.' },
    'luna': { emoji: '🌙', nombre: 'Luna', desc: 'Tu mundo emocional.' },
    'asc': { emoji: '⬆️', nombre: 'Ascendente', desc: 'Tu máscara y destino.' },
    'mc': { emoji: '⛰️', nombre: 'Medio Cielo', desc: 'Tu vocación y carrera.' },
    'mercurio': { emoji: '☿️', nombre: 'Mercurio', desc: 'Tu forma de pensar y comunicar.' },
    'venus': { emoji: '♀️', nombre: 'Venus', desc: 'Lo que valorás y cómo amás.' },
    'marte': { emoji: '♂️', nombre: 'Marte', desc: 'Tu acción y deseo.' },
    'jupiter': { emoji: '♃', nombre: 'Júpiter', desc: 'Expansión y suerte.' },
    'saturno': { emoji: '♄', nombre: 'Saturno', desc: 'Límites y estructura.' },
    'urano': { emoji: '♅', nombre: 'Urano', desc: 'Revolución y originalidad.' },
    'neptuno': { emoji: '♆', nombre: 'Neptuno', desc: 'Intuición y espiritualidad.' },
    'pluton': { emoji: '♇', nombre: 'Plutón', desc: 'Transformación y poder.' }
};

function generarColumnaVertebral() {
    const container = document.getElementById('columna-vertebral');
    container.innerHTML = '';
    
    // Iteramos los planetas definidos
    for (const [key, info] of Object.entries(PLANETAS_INFO)) {
        const signo = E.carta[key] || "Desconocido";
        
        const card = document.createElement('div');
        card.className = 'planet-card';
        card.onclick = () => abrirVideoPlaneta(key, info.nombre, signo);
        
        card.innerHTML = `
            <div class="planet-info">
                <h3>${info.emoji} ${info.nombre} en ${signo}</h3>
                <p>${info.desc}</p>
            </div>
            <div class="planet-status">▶️</div>
        `;
        container.appendChild(card);
    }
    
    document.getElementById('wallet-display').textContent = `${E.puntos} XP`;
}

// ── REPRODUCTOR DE VIDEO ────────────────────────────────────

function abrirVideoPlaneta(idPlaneta, nombrePlaneta, signo) {
    const modal = document.getElementById('video-modal');
    const vid = document.getElementById('planet-video');
    
    // Por ahora, todos apuntan a un video ligero genérico.
    // Futuro: src = `assets/${idPlaneta}_${signo.toLowerCase()}.mp4` generado por la Fábrica Mágica
    vid.src = "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4";
    
    document.getElementById('video-category').textContent = "ANÁLISIS PROFUNDO";
    document.getElementById('video-headline').textContent = `${nombrePlaneta} en ${signo}`;
    document.getElementById('video-context').textContent = `Descubrí el poder oculto de tu ${nombrePlaneta}.`;
    
    modal.style.display = 'flex';
}

function cerrarVideo() {
    document.getElementById('video-modal').style.display = 'none';
    const vid = document.getElementById('planet-video');
    vid.pause();
    vid.src = "";
}

// ── GAMIFICACIÓN Y PREGUNTAS ───────────────────────────────

function abrirPregunta() {
    const modal = document.getElementById('action-panel');
    document.getElementById('mc-question').textContent = "Tras ver el análisis, ¿cómo sentís que se manifiesta esta energía en tu día a día?";
    
    const opts = document.getElementById('mc-options');
    opts.innerHTML = '';
    
    const opciones = [
        "Me siento completamente identificado, es mi talento natural.",
        "Aún me cuesta integrarlo, a veces lo bloqueo.",
        "Es un desafío constante, pero estoy aprendiendo."
    ];
    
    opciones.forEach(texto => {
        const btn = document.createElement('button');
        btn.className = 'mc-opt';
        btn.innerHTML = `<span>${texto}</span>`;
        btn.onclick = () => procesarRespuesta(btn, 50); // 50 XP
        opts.appendChild(btn);
    });
    
    modal.style.display = 'block';
}

function procesarRespuesta(btn, puntosGanados) {
    document.querySelectorAll('.mc-opt').forEach(b => b.disabled = true);
    btn.style.borderColor = "var(--green)";
    btn.style.background = "rgba(16,185,129,0.15)";
    btn.style.color = "#34d399";
    
    E.puntos += puntosGanados;
    guardarDatos();
    
    document.getElementById('wallet-display').textContent = `${E.puntos} XP`;
    const delta = document.getElementById('wallet-delta');
    delta.textContent = `+${puntosGanados} XP`;
    delta.classList.add('show');
    
    document.getElementById('action-panel').style.display = 'none';
    
    const fb = document.getElementById('mc-feedback');
    document.getElementById('mc-fb-msg').innerHTML = `<span class="reward-line">+${puntosGanados} XP Obtenidos</span>Tu Avatar Cósmico está evolucionando.`;
    fb.style.display = 'flex';
}

function volverAlMapa() {
    document.getElementById('mc-feedback').style.display = 'none';
    cerrarVideo();
}
