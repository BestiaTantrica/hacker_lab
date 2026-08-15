// MicroSecure v7 — Real MVP (Multimedia, Persistencia, Minijuego)

// ── PERSISTENCIA (localStorage) ─────────────────────────────
const STORAGE_KEY = 'microsecure_v7_data';
function cargarDatos() {
    const defaultData = { wallet:0, rachaMax:0, puntos:0, perfilVocacional:{} };
    try {
        const guardado = localStorage.getItem(STORAGE_KEY);
        return guardado ? JSON.parse(guardado) : defaultData;
    } catch(e) { return defaultData; }
}
function guardarDatos() {
    const data = { wallet: E.wallet, rachaMax: E.rachaMax, puntos: E.puntos, perfilVocacional: E.perfilVocacional };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

// ── CONSTANTES ──────────────────────────────────────────────
const META_TOKENS = 50;

const NIVELES = [
    { min:0,   max:149,  nombre:"Operario Novato",       emoji:"👷",  desc:"Acabás de empezar. Todo lo que aprendas puede salvar vidas." },
    { min:150, max:349,  nombre:"Técnico Consciente",    emoji:"🦺",  desc:"Ya conocés los riesgos básicos y cómo mitigarlos." },
    { min:350, max:599,  nombre:"Supervisor Seguro",     emoji:"🏗️", desc:"Pensás en la seguridad de todo tu equipo." },
    { min:600, max:9999, nombre:"Especialista Validado", emoji:"🏅",  desc:"Listo para la entrevista técnica directa." }
];

const PERFILES = {
    seguridad:  { titulo:"Guardián de Equipos",     emoji:"🛡️", desc:"Tu instinto es proteger personas. Ideal: Supervisor HSE / Seguridad Operacional." },
    transito:   { titulo:"Coordinador de Flota",    emoji:"🚛", desc:"Pensás en movimiento y logística. Ideal: Jefe de Tránsito Minero." },
    atmosferas: { titulo:"Analista de Atmósferas",  emoji:"🧪", desc:"Detectás riesgos invisibles. Ideal: Técnico en Higiene Industrial." },
    tecnologia: { titulo:"Técnico OT / SCADA",      emoji:"💻", desc:"Afinidad por sistemas industriales. Ideal: Ingeniero de Control SCADA." },
    altura:     { titulo:"Especialista en Altura",  emoji:"🧗", desc:"Trabajo en estructuras complejas. Ideal: Inspector de Andamios / Rigger." },
    electrica:  { titulo:"Técnico Eléctrico",       emoji:"⚡", desc:"Entendés los riesgos de la energía. Ideal: Técnico Eléctrico Certificado." }
};

const INSIGHTS = [
    {
        tipo:"minijuego_loto",
        video:"assets/loto.mp4",
        emoji:"🔒", stat:{number:"100%",unit:"de certeza requerida"},
        headline:"Nunca confíes en el botón de apagado.",
        context:"Apagar una máquina no elimina la energía residual. Arrastrá tu candado al tablero para aislar la fuente antes de intervenir.",
        categoria:"LOTO", color:"#f87171", bgAccent:"rgba(239,68,68,0.3)",
        sponsor:"Minera San Juan", rewardBase:10, vocacion:"seguridad",
        explicacion:"¡Excelente! Un candado personal asegura que nadie más pueda encender el equipo mientras trabajás. Solo vos tenés la llave."
    },
    {
        tipo:"mc",
        video:"assets/truck.mp4",
        emoji:"🚛", stat:{number:"50m",unit:"de punto ciego tiene un camión"},
        headline:"Si no ves sus ojos en el espejo, él no te ve a vos.",
        context:"Los camiones fuera de ruta tienen puntos ciegos enormes. Un vehículo liviano puede ser aplastado sin que el operador lo note.",
        categoria:"TRÁNSITO", color:"#fbbf24", bgAccent:"rgba(245,158,11,0.3)",
        sponsor:"CAT", rewardBase:5, vocacion:"transito",
        pregunta:"¿Qué hacés si manejás una camioneta cerca de un camión de acarreo?",
        opciones:[
            {texto:"Tocar bocina y pasarlo rápido",correcta:false},
            {texto:"Mantener 50m y pedir autorización por radio",correcta:true},
            {texto:"Prender las luces altas",correcta:false},
            {texto:"Acercarte a la rueda trasera izquierda",correcta:false}
        ],
        explicacion:"Nunca adelantés sin confirmación explícita. Los espejos no cubren los laterales traseros — esa zona es letal."
    },
    {
        tipo:"mc",
        video:"assets/gas.mp4",
        emoji:"💨", stat:{number:"0%",unit:"de olor tiene el Monóxido de Carbono"},
        headline:"El gas letal que no podés oler ni ver.",
        context:"En labores subterráneas, el CO produce somnolencia antes de que notes el peligro.",
        categoria:"ATMÓSFERAS", color:"#34d399", bgAccent:"rgba(16,185,129,0.3)",
        sponsor:"MSA Safety", rewardBase:6, vocacion:"atmosferas",
        pregunta:"¿Cómo verificás si es seguro entrar a un túnel post-voladura?",
        opciones:[
            {texto:"Esperar 10 minutos y oler si hay humo",correcta:false},
            {texto:"Usar un detector multigás portátil calibrado",correcta:true},
            {texto:"Llevar un barbijo N95",correcta:false},
            {texto:"Entrar rápido y salir si te mareas",correcta:false}
        ],
        explicacion:"Solo un detector calibrado mide gases invisibles y letales como el CO o el H2S."
    },
    {
        tipo:"mc",
        video:"assets/scada.mp4",
        emoji:"💻", stat:{number:"1",unit:"USB basta para paralizar la planta"},
        headline:"Los 200 toneladas de acero también tienen SO.",
        context:"Un USB infectado en una consola de operación puede alterar parámetros y causar accidentes físicos graves.",
        categoria:"OT / SCADA", color:"#818cf8", bgAccent:"rgba(99,102,241,0.3)",
        sponsor:"Minera San Juan", rewardBase:8, vocacion:"tecnologia",
        pregunta:"Encontrás un USB cerca de la consola. ¿Qué hacés?",
        opciones:[
            {texto:"Lo conectás para ver de quién es",correcta:false},
            {texto:"Lo formateás y lo usás",correcta:false},
            {texto:"Lo entregás a Seguridad Informática sin conectarlo",correcta:true},
            {texto:"Lo dejás ahí",correcta:false}
        ],
        explicacion:"Conectar un USB desconocido en sistemas OT puede causar desastres físicos reales."
    },
    {
        tipo:"mc",
        video:"assets/altura.mp4",
        emoji:"🧗", stat:{number:"1.8m",unit:"altura mínima para arnés"},
        headline:"Una caída corta es fatal.",
        context:"La energía de choque de un cuerpo cayendo 2 metros supera los 900 kg de fuerza.",
        categoria:"ALTURA", color:"#22d3ee", bgAccent:"rgba(6,182,212,0.3)",
        sponsor:"3M", rewardBase:6, vocacion:"altura",
        pregunta:"¿A qué punto debés enganchar tu línea de vida?",
        opciones:[
            {texto:"A una tubería de agua firme",correcta:false},
            {texto:"A la baranda del andamio",correcta:false},
            {texto:"A un anclaje estructural certificado ≥ 2200 kg",correcta:true},
            {texto:"A tu cinturón de herramientas",correcta:false}
        ],
        explicacion:"Solo los puntos de anclaje estructurales absorben la energía de choque de una caída."
    },
    {
        tipo:"mc",
        video:"assets/electrico.mp4",
        emoji:"⚡", stat:{number:"0.1A",unit:"de alterna para tu corazón"},
        headline:"El voltaje no mata. La corriente sí.",
        context:"100mA pueden inducir fibrilación. Incluso 220V son letales en condiciones húmedas.",
        categoria:"ELÉCTRICO", color:"#facc15", bgAccent:"rgba(250,204,21,0.3)",
        sponsor:"ABB", rewardBase:7, vocacion:"electrica",
        pregunta:"¿Primera acción ante un electrocutado?",
        opciones:[
            {texto:"Agarrarlo para separarlo del cable",correcta:false},
            {texto:"Desconectar la energía primero",correcta:true},
            {texto:"Llamar a emergencias mientras tirás de él",correcta:false},
            {texto:"Echarle agua",correcta:false}
        ],
        explicacion:"Si agarrás a alguien bajo tensión, sos la segunda víctima. Siempre cortá la energía primero."
    }
];

// ── ESTADO GLOBAL ───────────────────────────────────────────
let E = {
    indexActual:0, orden:[], correctas:0, incorrectas:0, racha:0,
    respondido:false, tiempoInicio:null, tiempoLectura:0, bonusEsfuerzo:0,
    wallet:0, rachaMax:0, puntos:0, perfilVocacional:{} // Se pisan con cargarDatos()
};

// ── AUDIO REAL ──────────────────────────────────────────────
function sfx(id) {
    const a = document.getElementById('sfx-'+id);
    if(a) { a.currentTime=0; a.play().catch(e=>console.warn("Audio bloqueado por navegador",e)); }
}

// ── INICIALIZACIÓN ──────────────────────────────────────────
function arrancar() {
    // Cargar historial
    const db = cargarDatos();
    E.wallet = db.wallet; E.rachaMax = db.rachaMax; 
    E.puntos = db.puntos; E.perfilVocacional = db.perfilVocacional;
    
    document.getElementById('wallet-display-intro').textContent = `${E.wallet} TKS`;
}
window.onload = arrancar;

function iniciarFeed() {
    E.orden = INSIGHTS.map((_,i)=>i);
    // Shuffle (menos el loto que queremos probar)
    for(let i=E.orden.length-1;i>1;i--){
        const j=Math.floor(Math.random()*(i-1))+1;
        [E.orden[i],E.orden[j]]=[E.orden[j],E.orden[i]];
    }
    
    // Reset sesión pero conservar DB
    E.indexActual=0; E.correctas=0; E.incorrectas=0; E.racha=0; E.tiempoLectura=0; E.bonusEsfuerzo=0;
    
    generarFeed();
    construirBarraEpisodios();
    cambiarPantalla('screen-intro','screen-feed');
    scrollToInsight(0);
    E.tiempoInicio = Date.now();
    actualizarWalletHUD(0);
}

function generarFeed() {
    const container = document.getElementById('feed-scroll');
    container.innerHTML = '';
    E.orden.forEach((insIdx, pos) => {
        const ins = INSIGHTS[insIdx];
        container.appendChild(construirSeccion(ins, pos));
    });
}

function construirSeccion(ins, idx) {
    const sec = document.createElement('section');
    sec.className = 'insight-section';
    sec.dataset.index = idx;

    sec.innerHTML = `
        <video class="bg-video" src="${ins.video}" autoplay loop muted playsinline></video>
        <div class="insight-overlay"></div>
        <div class="insight-content">
            <div class="ins-sponsor">${ins.sponsor}</div>
            <div class="ins-category" style="color:${ins.color}; border-color:${ins.color}">${ins.categoria}</div>
            <div class="ins-emoji">${ins.emoji}</div>
            <div class="ins-stat-number" style="color:${ins.color}">${ins.stat.number}</div>
            <div class="ins-stat-unit">${ins.stat.unit}</div>
            <div class="ins-headline">${ins.headline}</div>
            <div class="ins-context">${ins.context}</div>
        </div>
        <div class="insight-footer">
            <button class="btn-responder" id="btn-resp-${idx}" onclick="activarInteraccion(${idx})">
                ${ins.tipo==='minijuego_loto' ? 'JUGAR SIMULACIÓN 🎮' : 'RESPONDER →'}
            </button>
        </div>
        <div class="ins-reward-badge" style="color:${ins.color}; border-color:${ins.color}; background:${ins.bgAccent}">+${ins.rewardBase} TKS</div>
    `;
    return sec;
}

function scrollToInsight(idx) {
    sfx('swoosh');
    const sec = document.querySelector(`.insight-section[data-index="${idx}"]`);
    if (sec) sec.scrollIntoView({behavior:'smooth', block:'start'});
}

function cambiarPantalla(ocultar, mostrar) {
    document.getElementById(ocultar).classList.remove('active');
    document.getElementById(mostrar).classList.add('active');
    window.scrollTo(0,0);
}

// ── INTERACCIÓN (MC o Minijuego) ────────────────────────────
function activarInteraccion(idx) {
    sfx('swoosh');
    if (E.tiempoInicio) {
        E.tiempoLectura += Math.round((Date.now()-E.tiempoInicio)/1000);
        E.tiempoInicio = null;
    }
    const btn = document.getElementById(`btn-resp-${idx}`);
    if (btn) btn.style.display = 'none';
    
    const ins = INSIGHTS[E.orden[idx]];
    if(ins.tipo === 'minijuego_loto') mostrarMinijuegoLOTO(ins);
    else mostrarPreguntaMC(ins);
}

// ── MULTIPLE CHOICE ──
function mostrarPreguntaMC(ins) {
    document.getElementById('action-mc').style.display = 'block';
    document.getElementById('action-loto').style.display = 'none';
    
    document.getElementById('mc-question').textContent = ins.pregunta;
    const letras=['A','B','C','D'];
    const orden=[0,1,2,3].sort(()=>Math.random()-0.5);
    const optsEl = document.getElementById('mc-options');
    optsEl.innerHTML='';
    orden.forEach((opIdx,i)=>{
        const op=ins.opciones[opIdx];
        const btn=document.createElement('button');
        btn.className='mc-opt';
        btn.dataset.correcta=op.correcta;
        btn.innerHTML=`<span class="opt-letter">${letras[i]}</span> ${op.texto}`;
        btn.onclick=()=>procesarRespuesta(btn, ins, op.correcta);
        optsEl.appendChild(btn);
    });
    document.getElementById('action-panel').style.display='block';
}

// ── MINIJUEGO LOTO (Drag & Drop rudimentario con clics) ──
function mostrarMinijuegoLOTO(ins) {
    document.getElementById('action-mc').style.display = 'none';
    document.getElementById('action-loto').style.display = 'block';
    
    const lock = document.getElementById('loto-lock');
    lock.classList.remove('locked');
    lock.style.display = 'block';
    
    document.getElementById('action-panel').style.display='block';
    document.getElementById('loto-breaker').onclick = () => {
        if(E.respondido) return;
        lock.classList.add('locked');
        setTimeout(() => {
            procesarRespuesta(null, ins, true);
        }, 800);
    };
}

// ── EVALUACIÓN Y FEEDBACK ───────────────────────────────────
function procesarRespuesta(btn, ins, esCorrecta) {
    if (E.respondido) return;
    E.respondido = true;
    
    if(btn) {
        document.querySelectorAll('.mc-opt').forEach(b=>{
            b.disabled=true;
            if(b.dataset.correcta==='true') b.classList.add('correct-opt');
            else if(b===btn&&!esCorrecta) b.classList.add('wrong-opt');
        });
    }

    let pts=0, reward=0;
    if (esCorrecta) {
        sfx('coin');
        pts=100; reward=ins.rewardBase;
        E.correctas++; E.racha++;
        if(E.racha>E.rachaMax) E.rachaMax=E.racha;
        if(E.racha>1){ const m=Math.min(1.3,1+(E.racha-1)*0.1); pts=Math.floor(pts*m); reward=Math.floor(reward*m); }
        E.puntos+=pts; E.wallet+=reward;
        E.perfilVocacional[ins.vocacion]=(E.perfilVocacional[ins.vocacion]||0)+2;
        actualizarWalletHUD(reward);
    } else {
        sfx('error');
        pts=20; E.puntos+=pts; E.racha=0; E.incorrectas++;
        E.perfilVocacional[ins.vocacion]=(E.perfilVocacional[ins.vocacion]||0)+1;
    }
    
    guardarDatos(); // Persistir en cada paso
    actualizarNivelHUD();
    mostrarFeedback(esCorrecta, pts, reward, ins);
}

function mostrarFeedback(esCorrecta,pts,reward,ins) {
    document.getElementById('action-panel').style.display='none';
    const fb=document.getElementById('mc-feedback');
    document.getElementById('mc-fb-icon').textContent=esCorrecta?'✅':'❌';
    const rewardLine=esCorrecta
        ?`<span class="reward-line">+${reward} TKS acreditados</span>`
        :`<span class="effort-line">📊 Tu esfuerzo suma al bonus de sesión</span>`;
    document.getElementById('mc-fb-msg').innerHTML=
        `${rewardLine}<br><span class="fb-explicacion">${ins.explicacion}</span>`;
    fb.style.display='flex';
}

function siguienteInsight() {
    document.getElementById('mc-feedback').style.display='none';
    E.respondido=false;
    marcarEpisodioCompleto();
    E.indexActual++;
    E.tiempoInicio=Date.now();
    if(E.indexActual>=E.orden.length){ mostrarResumen(); return; }
    scrollToInsight(E.indexActual);
}

// ── HUD Y EPISODIOS ─────────────────────────────────────────
function actualizarWalletHUD(delta) {
    document.getElementById('wallet-display').textContent=`${E.wallet} TKS`;
    const d=document.getElementById('wallet-delta');
    if(delta>0) {
        d.textContent=`+${delta} TKS`; d.classList.add('show');
        setTimeout(()=>d.classList.remove('show'),1400);
    }
}
function actualizarNivelHUD() {
    const nv=obtenerNivel(E.puntos);
    document.getElementById('level-badge').textContent=`Nv. ${nv.nombre}`;
}
function obtenerNivel(pts){ return NIVELES.find(n=>pts>=n.min&&pts<=n.max)||NIVELES[0]; }

function construirBarraEpisodios() {
    const bar=document.getElementById('episodes-bar'); bar.innerHTML='';
    E.orden.forEach(()=>{
        const seg=document.createElement('div'); seg.className='ep-seg';
        const fill=document.createElement('div'); fill.className='ep-seg-fill';
        seg.appendChild(fill); bar.appendChild(seg);
    });
}
function actualizarBarraEpisodios() {
    document.querySelectorAll('.ep-seg').forEach((s,i)=>s.classList.toggle('done',i<E.indexActual));
}
function marcarEpisodioCompleto() {
    const segs=document.querySelectorAll('.ep-seg');
    if(segs[E.indexActual]) segs[E.indexActual].classList.add('done');
}

// ── RESUMEN FINAL ───────────────────────────────────────────
function calcularBonusEsfuerzo() {
    const total=E.orden.length;
    const part=(E.correctas+E.incorrectas)/total;
    const tNorm=Math.min(E.tiempoLectura/Math.max(1,total)/30,1);
    return Math.round((part*0.6+tNorm*0.4)*8);
}
function calcularPerfilVocacional() {
    let top=null, maxScore=0;
    Object.entries(E.perfilVocacional).forEach(([k,v])=>{
        if(v>maxScore){ maxScore=v; top=k; }
    });
    return top ? PERFILES[top] : PERFILES['seguridad'];
}

function mostrarResumen() {
    cambiarPantalla('screen-feed','screen-summary');
    const bonus=calcularBonusEsfuerzo();
    E.wallet+=bonus;
    guardarDatos();
    
    sfx('coin'); // Fanfarria final

    const nv=obtenerNivel(E.puntos);
    const perfil=calcularPerfilVocacional();

    document.getElementById('summary-amount').textContent=`${E.wallet} TKS`;
    document.getElementById('wallet-bar-current').textContent=`${E.wallet} TKS`;
    document.getElementById('ss-pts').textContent=E.puntos;
    document.getElementById('ss-correct').textContent=`${E.correctas}/${E.orden.length}`;
    document.getElementById('ss-streak').textContent=E.rachaMax;

    const bonusEl=document.getElementById('bonus-esfuerzo');
    if(bonusEl){ bonusEl.style.display=bonus>0?'block':'none'; bonusEl.textContent=bonus>0?`+${bonus} TKS — Bonus de esfuerzo`:''; }

    document.getElementById('level-result-icon').textContent=nv.emoji;
    document.getElementById('level-result-name').textContent=nv.nombre.toUpperCase();
    document.getElementById('level-result-desc').textContent=nv.desc;

    const vEl=document.getElementById('vocational-result');
    if(vEl){ vEl.innerHTML=`<div class="voc-emoji">${perfil.emoji}</div><div class="voc-title">${perfil.titulo}</div><div class="voc-desc">${perfil.desc}</div>`; }

    const pct=Math.min((E.wallet/META_TOKENS)*100,100);
    setTimeout(()=>{ document.getElementById('wallet-bar-fill').style.width=pct+'%'; },600);
}

function compartir() {
    const txt=`Alcancé el nivel "${obtenerNivel(E.puntos).nombre}" en MicroSecure y gané ${E.wallet} TKS con casos reales de la industria. 👷🏽‍♂️💎\n`;
    if(navigator.share){ navigator.share({title:'MicroSecure RIGI',text:txt,url:window.location.href}); }
    else { navigator.clipboard.writeText(txt+window.location.href).then(()=>alert('¡Copiado!')); }
}
function reiniciar() {
    document.getElementById('feed-scroll').innerHTML='';
    iniciarFeed();
    cambiarPantalla('screen-summary','screen-feed');
}
