/**
 * reloj_engine.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Motor Astronómico y de Renderizado Cinemático en Tiempo Real
 * Proyecto: El Glifo Maestro — Reloj Astrológico Universal
 * ─────────────────────────────────────────────────────────────────────────────
 */

const ZODIAC_SIGNS = [
  { nombre: "Aries", simbolo: "♈", elemento: "Fuego", color: "#ef4444", regente: "Marte" },
  { nombre: "Tauro", simbolo: "♉", elemento: "Tierra", color: "#10b981", regente: "Venus" },
  { nombre: "Géminis", simbolo: "♊", elemento: "Aire", color: "#f59e0b", regente: "Mercurio" },
  { nombre: "Cáncer", simbolo: "♋", elemento: "Agua", color: "#38bdf8", regente: "Luna" },
  { nombre: "Leo", simbolo: "♌", elemento: "Fuego", color: "#f97316", regente: "Sol" },
  { nombre: "Virgo", simbolo: "♍", elemento: "Tierra", color: "#059669", regente: "Mercurio" },
  { nombre: "Libra", simbolo: "♎", elemento: "Aire", color: "#eab308", regente: "Venus" },
  { nombre: "Escorpio", simbolo: "♏", elemento: "Agua", color: "#818cf8", regente: "Plutón / Marte" },
  { nombre: "Sagitario", simbolo: "♐", elemento: "Fuego", color: "#dc2626", regente: "Júpiter" },
  { nombre: "Capricornio", simbolo: "♑", elemento: "Tierra", color: "#047857", regente: "Saturno" },
  { nombre: "Acuario", simbolo: "♒", elemento: "Aire", color: "#06b6d4", regente: "Urano / Saturno" },
  { nombre: "Piscis", simbolo: "♓", elemento: "Agua", color: "#6366f1", regente: "Neptuno / Júpiter" }
];

const GLYPHS = {
  'Sol': '☉', 'Luna': '☽', 'Mercurio': '☿', 'Venus': '♀', 'Marte': '♂',
  'Júpiter': '♃', 'Saturno': '♄', 'Urano': '♅', 'Neptuno': '♆', 'Plutón': '♇',
  'Quirón': '⚷', 'Nodo Norte': '☊'
};

const PLANET_COLORS = {
  'Sol': '#f6c445',
  'Luna': '#e2e8f0',
  'Mercurio': '#94a3b8',
  'Venus': '#ec4899',
  'Marte': '#ef4444',
  'Júpiter': '#f97316',
  'Saturno': '#d97706',
  'Urano': '#06b6d4',
  'Neptuno': '#3b82f6',
  'Plutón': '#a855f7',
  'Nodo Norte': '#10b981'
};

const ASPECT_COLORS = {
  'Conjunción': '#f1c40f',
  'Oposición': '#ef4444',
  'Trígono': '#38bdf8',
  'Cuadratura': '#f97316',
  'Sextil': '#10b981',
  'Quincuncio': '#a855f7'
};

// Parámetros orbitales keplerianos (J2000)
const KEPLER = {
  Mercurio: { a: 0.38709927, e: 0.20563593, I: 7.004979, L: 252.25032350, longPeri: 77.45779628, longNode: 48.33076593,
              rates: { a: 0.00000037, e: 0.00001906, I: -0.005947, L: 149472.67411175, longPeri: 0.16047689, longNode: -0.12534081 } },
  Venus:    { a: 0.72333566, e: 0.00677672, I: 3.394676, L: 181.97909950, longPeri: 131.60246718, longNode: 76.67984255,
              rates: { a: 0.00000390, e: -0.00004107, I: -0.0007889, L: 58517.81538729, longPeri: 0.00268329, longNode: -0.27769418 } },
  Marte:    { a: 1.52371034, e: 0.09339410, I: 1.849691, L: -4.55343205, longPeri: -23.94362959, longNode: 49.55953891,
              rates: { a: 0.00001847, e: 0.00007882, I: -0.008131, L: 19140.30268499, longPeri: 0.44441088, longNode: -0.29257343 } },
  Júpiter:  { a: 5.20288700, e: 0.04838624, I: 1.304396, L: 34.39644051, longPeri: 14.72847983, longNode: 100.47390909,
              rates: { a: -0.00011607, e: -0.00013257, I: -0.001837, L: 3034.74612775, longPeri: 0.21252668, longNode: 0.20469106 } },
  Saturno:  { a: 9.53667594, e: 0.05386179, I: 2.485991, L: 49.95424423, longPeri: 92.59887831, longNode: 113.66242448,
              rates: { a: -0.00125060, e: -0.00050991, I: 0.001936, L: 1222.49362201, longPeri: -0.41897216, longNode: -0.28867794 } },
  Urano:    { a: 19.18916464, e: 0.04725744, I: 0.772637, L: 313.23810451, longPeri: 170.95427630, longNode: 74.01692503,
              rates: { a: -0.00196176, e: -0.00004397, I: -0.002429, L: 428.48202785, longPeri: 0.40805280, longNode: 0.04240589 } },
  Neptuno:  { a: 30.06992276, e: 0.00860610, I: 1.770043, L: -55.12002969, longPeri: 44.96476227, longNode: 131.78422574,
              rates: { a: 0.00026291, e: 0.00000813, I: 0.000353, L: 218.45945325, longPeri: -0.32241464, longNode: -0.00508664 } },
  Plutón:   { a: 39.48211675, e: 0.24882730, I: 17.140012, L: 238.92903833, longPeri: 224.06886456, longNode: 110.30393608,
              rates: { a: -0.00031596, e: 0.00005170, I: 0.000048, L: 145.20780515, longPeri: -0.04062942, longNode: -0.01183482 } }
};

class RelojAstrologicoEngine {
  constructor() {
    this.canvas = document.getElementById('reloj-canvas');
    this.ctx = this.canvas.getContext('2d');
    this.container = document.getElementById('reloj-container');
    this.videoBg = document.getElementById('video-bg');

    // Ubicación geográfica (Default: Buenos Aires)
    this.geo = {
      lat: -34.6037,
      lon: -58.3816,
      ciudad: "Buenos Aires, Argentina",
      esExacta: false
    };

    // Estado del Tiempo
    this.timeState = {
      currentDate: new Date(),
      isLive: true,
      timeMultiplier: 1.0, // 1x, 60x, 3600x
      lastFrameTime: performance.now()
    };

    // Radios del Reloj
    this.radii = {
      core: 130,
      aspects: 180,
      housesInner: 190,
      planets: 260,
      housesOuter: 320,
      zodiacInner: 330,
      zodiacOuter: 420,
      degreeRing: 435,
      dialBoundary: 460
    };

    // Datos calculados del instante
    this.calculated = {
      asc: 0,
      mc: 0,
      dsc: 180,
      ic: 180,
      houses: [], // 12 cúspides
      planets: {},
      aspects: [],
      moonPhase: { name: "", frac: 0.5, illumination: "50%" }
    };

    // Efecto partículas de polvo estelar
    this.particles = [];
    this.initParticles(80);

    // Grabador de video para Watermark
    this.mediaRecorder = null;
    this.recordedChunks = [];
    this.isRecording = false;

    // Inicializaciones
    this.initCanvasSize();
    this.detectGeolocation();
    this.initEvents();
    this.calculateAll();
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  initParticles(count) {
    this.particles = [];
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x: (Math.random() - 0.5) * 1200,
        y: (Math.random() - 0.5) * 1200,
        size: Math.random() * 1.8 + 0.3,
        alpha: Math.random() * 0.6 + 0.1,
        speed: (Math.random() * 0.15 + 0.05) * (Math.random() > 0.5 ? 1 : -1)
      });
    }
  }

  initCanvasSize() {
    const dpr = window.devicePixelRatio || 1;
    this.width = this.container.clientWidth;
    this.height = this.container.clientHeight;
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.scale(dpr, dpr);
  }

  detectGeolocation() {
    // Intentar leer caché previo
    const cached = localStorage.getItem('reloj_astro_geo');
    if (cached) {
      try {
        const parsed = JSON.parse(cached);
        this.geo = { ...this.geo, ...parsed };
      } catch (e) {}
    }

    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          this.geo.lat = pos.coords.latitude;
          this.geo.lon = pos.coords.longitude;
          this.geo.ciudad = "Coordenadas Detectadas (GPS)";
          this.geo.esExacta = true;
          localStorage.setItem('reloj_astro_geo', JSON.stringify(this.geo));
          this.updateLocationHUD();
          this.calculateAll();
        },
        (err) => {
          console.warn("Geolocalización declinada o no disponible. Usando fallback:", this.geo.ciudad);
          this.updateLocationHUD();
        },
        { timeout: 7000 }
      );
    } else {
      this.updateLocationHUD();
    }
  }

  updateLocationHUD() {
    const el = document.getElementById('hud-location');
    if (el) {
      const latStr = `${Math.abs(this.geo.lat).toFixed(2)}°${this.geo.lat >= 0 ? 'N' : 'S'}`;
      const lonStr = `${Math.abs(this.geo.lon).toFixed(2)}°${this.geo.lon >= 0 ? 'E' : 'O'}`;
      el.innerHTML = `📍 <span>${this.geo.ciudad}</span> • ${latStr} ${lonStr}`;
    }
  }

  initEvents() {
    window.addEventListener('resize', () => {
      this.initCanvasSize();
      this.calculateAll();
    });

    // Toggle Play/Pause
    const btnPlay = document.getElementById('btn-play-pause');
    if (btnPlay) {
      btnPlay.addEventListener('click', () => {
        this.timeState.isLive = !this.timeState.isLive;
        btnPlay.innerHTML = this.timeState.isLive ? '<span>⏸</span> Pausar' : '<span>▶</span> En Vivo';
        btnPlay.classList.toggle('active', this.timeState.isLive);
      });
    }

    // Botón Ahora (Reset a tiempo actual)
    const btnNow = document.getElementById('btn-now');
    if (btnNow) {
      btnNow.addEventListener('click', () => {
        this.timeState.currentDate = new Date();
        this.timeState.isLive = true;
        this.timeState.timeMultiplier = 1.0;
        if (btnPlay) {
          btnPlay.innerHTML = '<span>⏸</span> Pausar';
          btnPlay.classList.add('active');
        }
        this.calculateAll();
      });
    }

    // Controles de paso de tiempo (-1h, +1h, -1d, +1d)
    const addTimeStep = (id, deltaMs) => {
      const btn = document.getElementById(id);
      if (btn) {
        btn.addEventListener('click', () => {
          this.timeState.isLive = false;
          if (btnPlay) {
            btnPlay.innerHTML = '<span>▶</span> Reanudar';
            btnPlay.classList.remove('active');
          }
          this.timeState.currentDate = new Date(this.timeState.currentDate.getTime() + deltaMs);
          this.calculateAll();
        });
      }
    };
    addTimeStep('btn-time-minus-1h', -3600 * 1000);
    addTimeStep('btn-time-plus-1h', 3600 * 1000);
    addTimeStep('btn-time-minus-1d', -86400 * 1000);
    addTimeStep('btn-time-plus-1d', 86400 * 1000);

    // Multiplicador de velocidad (1x, 60x, 3600x)
    document.querySelectorAll('.speed-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.timeState.timeMultiplier = parseFloat(btn.dataset.speed || "1.0");
      });
    });

    // Selector A/B de Fondo
    document.querySelectorAll('.bg-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.bg-toggle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const bgType = btn.dataset.bg;
        this.cambiarFondo(bgType);
      });
    });

    // Slider de Opacidad del Video
    const sliderOp = document.getElementById('bg-opacity-slider');
    const labelOp = document.getElementById('bg-opacity-label');
    if (sliderOp) {
      sliderOp.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        if (this.videoBg) this.videoBg.style.opacity = val;
        if (labelOp) labelOp.innerText = `${Math.round(val * 100)}%`;
      });
    }

    // Botón Fullscreen (Wallpaper Mode)
    const btnFull = document.getElementById('btn-fullscreen');
    if (btnFull) {
      btnFull.addEventListener('click', () => {
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen().catch(() => {});
        } else {
          document.exitFullscreen().catch(() => {});
        }
      });
    }

    // Grabador de Watermark Video
    const btnRecord = document.getElementById('btn-record-watermark');
    if (btnRecord) {
      btnRecord.addEventListener('click', () => {
        this.toggleRecordWatermark(btnRecord);
      });
    }
  }

  cambiarFondo(bgType) {
    if (!this.videoBg) return;
    const sliderWrapper = document.getElementById('bg-slider-wrapper');

    if (bgType === 'negro') {
      this.videoBg.style.display = 'none';
      if (sliderWrapper) sliderWrapper.style.opacity = '0.3';
    } else {
      this.videoBg.style.display = 'block';
      if (sliderWrapper) sliderWrapper.style.opacity = '1.0';
      if (bgType === 'galaxia') {
        this.videoBg.src = "videos_fondo/07_espacio_galaxias_deep_space_galaxy_pex_v_15562120.mp4";
      } else if (bgType === 'estrellas') {
        this.videoBg.src = "videos_fondo/07_espacio_galaxias_stars_ethereal_glowing_pex_v_35115646.mp4";
      }
      this.videoBg.play().catch(() => {});
    }
  }

  // ── Grabación de Marca de Agua (Watermark Cinemático) ───────────────────────
  toggleRecordWatermark(btn) {
    if (this.isRecording) {
      this.stopRecording(btn);
      return;
    }

    this.isRecording = true;
    btn.innerHTML = '<span>⏹</span> Grabando (5s)...';
    btn.classList.add('recording-pulse');

    const stream = this.canvas.captureStream(30);
    this.recordedChunks = [];
    const mime = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm';
    this.mediaRecorder = new MediaRecorder(stream, { mimeType: mime, videoBitsPerSecond: 10000000 });

    this.mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) this.recordedChunks.push(e.data);
    };

    this.mediaRecorder.onstop = () => {
      const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `watermark_reloj_astrologico_${Date.now()}.webm`;
      a.click();
      URL.revokeObjectURL(url);
      btn.innerHTML = '<span>🎬</span> Capturar Bucle Marca (5s)';
      btn.classList.remove('recording-pulse');
      this.isRecording = false;
    };

    this.mediaRecorder.start();
    // Detener automáticamente a los 5 segundos
    setTimeout(() => {
      if (this.isRecording && this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.stop();
      }
    }, 5000);
  }

  // ── Cálculos Astronómicos en Tiempo Real ───────────────────────────────────

  getJulianDay(date) {
    return (date.getTime() / 86400000) + 2440587.5;
  }

  calculateAll() {
    const d = this.timeState.currentDate;
    const jd = this.getJulianDay(d);
    const T = (jd - 2451545.0) / 36525.0;
    const rad = Math.PI / 180;

    // 1. Tiempo Sideral de Greenwich y Local
    let gst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * T * T - (T * T * T) / 38710000.0;
    gst = ((gst % 360) + 360) % 360;
    let lst = ((gst + this.geo.lon) % 360 + 360) % 360;

    // 2. Ascendente (ASC) y Medio Cielo (MC)
    const eps = (23.4392911 - 0.0130042 * T) * rad;
    const ramc = lst * rad;
    const latRad = this.geo.lat * rad;

    // MC: tan(MC) = tan(RAMC) / cos(eps)
    let mc = Math.atan2(Math.sin(ramc), Math.cos(ramc) * Math.cos(eps)) / rad;
    mc = ((mc % 360) + 360) % 360;

    // ASC: cot(ASC) = -sin(eps)*tan(lat) - cos(eps)*tan(RAMC)
    // Con atan2(y, x):
    const yAsc = -Math.cos(ramc);
    const xAsc = Math.sin(eps) * Math.tan(latRad) + Math.cos(eps) * Math.sin(ramc);
    let asc = Math.atan2(yAsc, xAsc) / rad;
    asc = ((asc % 360) + 360) % 360;

    this.calculated.asc = asc;
    this.calculated.mc = mc;
    this.calculated.dsc = (asc + 180) % 360;
    this.calculated.ic = (mc + 180) % 360;

    // 12 Casas (Placidus / Equal simplificado con orientación ASC en horizonte)
    this.calculated.houses = [];
    for (let h = 0; h < 12; h++) {
      this.calculated.houses.push((asc + h * 30) % 360);
    }

    // 3. Posición del Sol
    const L0 = 280.46646 + 36000.76983 * T;
    const M_sun = (357.52911 + 35999.05029 * T) * rad;
    const C_sun = (1.914602 - 0.004817 * T) * Math.sin(M_sun) + 0.019993 * Math.sin(2 * M_sun);
    const sunLon = ((L0 + C_sun) % 360 + 360) % 360;

    // Coordenadas Tierra para geocéntricas
    const earth_R = 1.00014 - 0.01671 * Math.cos(M_sun);
    const xEarth = earth_R * Math.cos((sunLon + 180) * rad);
    const yEarth = earth_R * Math.sin((sunLon + 180) * rad);

    // 4. Posición de la Luna
    const Lprime = 218.3164477 + 481267.88123421 * T;
    const D = 297.8501921 + 445267.1114034 * T;
    const Mprime = 134.9633964 + 477198.8675055 * T;
    const F = 93.2720950 + 483202.0175233 * T;

    let moonLon = Lprime 
      + 6.288774 * Math.sin(Mprime * rad)
      + 1.274027 * Math.sin((2*D - Mprime) * rad)
      + 0.658314 * Math.sin(2*D * rad)
      + 0.213618 * Math.sin(2*Mprime * rad)
      - 0.185116 * Math.sin(M_sun)
      - 0.114332 * Math.sin(2*F * rad)
      + 0.058793 * Math.sin((2*D - 2*Mprime) * rad)
      + 0.057066 * Math.sin((2*D - M_sun - Mprime) * rad)
      + 0.053320 * Math.sin((2*D + Mprime) * rad)
      + 0.046100 * Math.sin((2*D - M_sun) * rad);
    moonLon = ((moonLon % 360) + 360) % 360;

    // Fase Lunar
    const moonPhaseAngle = ((moonLon - sunLon) % 360 + 360) % 360;
    const illum = Math.round((1 - Math.cos(moonPhaseAngle * rad)) / 2 * 100);
    let phaseName = "Luna Nueva";
    if (moonPhaseAngle > 10 && moonPhaseAngle < 80) phaseName = "Creciente Iluminada";
    else if (moonPhaseAngle >= 80 && moonPhaseAngle <= 100) phaseName = "Cuarto Creciente";
    else if (moonPhaseAngle > 100 && moonPhaseAngle < 170) phaseName = "Gibosa Creciente";
    else if (moonPhaseAngle >= 170 && moonPhaseAngle <= 190) phaseName = "Luna Llena";
    else if (moonPhaseAngle > 190 && moonPhaseAngle < 260) phaseName = "Gibosa Menguante";
    else if (moonPhaseAngle >= 260 && moonPhaseAngle <= 280) phaseName = "Cuarto Menguante";
    else if (moonPhaseAngle > 280 && moonPhaseAngle < 350) phaseName = "Menguante Balsámica";

    this.calculated.moonPhase = {
      name: phaseName,
      angle: moonPhaseAngle,
      illumination: `${illum}%`
    };

    // 5. Planetas Geocéntricos
    const planets = {
      'Sol': { lon: sunLon },
      'Luna': { lon: moonLon }
    };

    for (const [name, p] of Object.entries(KEPLER)) {
      const a = p.a + p.rates.a * T;
      const e = p.e + p.rates.e * T;
      const I = (p.I + p.rates.I * T) * rad;
      const L = (p.L + p.rates.L * T);
      const longPeri = (p.longPeri + p.rates.longPeri * T);
      const longNode = (p.longNode + p.rates.longNode * T) * rad;

      let M = ((L - longPeri) % 360 + 360) % 360;
      let E = M * rad;
      for (let k = 0; k < 5; k++) {
        E = E - (E - e * Math.sin(E) - M * rad) / (1 - e * Math.cos(E));
      }
      const xPrime = a * (Math.cos(E) - e);
      const yPrime = a * Math.sqrt(1 - e * e) * Math.sin(E);
      const r = Math.sqrt(xPrime * xPrime + yPrime * yPrime);
      const v = Math.atan2(yPrime, xPrime);

      const omega = (longPeri - (p.longNode + p.rates.longNode * T)) * rad;
      const u = v + omega;

      const xHelio = r * (Math.cos(longNode) * Math.cos(u) - Math.sin(longNode) * Math.sin(u) * Math.cos(I));
      const yHelio = r * (Math.sin(longNode) * Math.cos(u) + Math.cos(longNode) * Math.sin(u) * Math.cos(I));
      const zHelio = r * Math.sin(u) * Math.sin(I);

      const xGeo = xHelio - xEarth;
      const yGeo = yHelio - yEarth;
      let lonGeo = Math.atan2(yGeo, xGeo) / rad;
      lonGeo = ((lonGeo % 360) + 360) % 360;

      planets[name] = { lon: lonGeo };
    }

    // Nodo Norte medio
    const nodeLon = ((125.04452 - 1934.136261 * T) % 360 + 360) % 360;
    planets['Nodo Norte'] = { lon: nodeLon };

    // Enriquecer cada planeta con signo, grado y casa
    for (const [name, p] of Object.entries(planets)) {
      const signIdx = Math.floor(p.lon / 30);
      const signDeg = p.lon % 30;
      const degInt = Math.floor(signDeg);
      const degMin = Math.floor((signDeg - degInt) * 60);
      const signo = ZODIAC_SIGNS[signIdx];

      // Determinar Casa (relativa al Ascendente)
      let houseRel = ((p.lon - asc) % 360 + 360) % 360;
      let houseNum = Math.floor(houseRel / 30) + 1;

      planets[name] = {
        nombre: name,
        grado_absoluto: p.lon,
        signo_idx: signIdx,
        signo: signo.nombre,
        signo_simbolo: signo.simbolo,
        grado: degInt,
        minutos: degMin,
        casa: houseNum,
        color: PLANET_COLORS[name] || '#ffffff'
      };
    }
    this.calculated.planets = planets;

    // 6. Aspectos Mayores Activos
    const aspectDefs = [
      { nombre: 'Conjunción', angulo: 0, orbe: 7.0, color: ASPECT_COLORS['Conjunción'] },
      { nombre: 'Sextil', angulo: 60, orbe: 5.0, color: ASPECT_COLORS['Sextil'] },
      { nombre: 'Cuadratura', angulo: 90, orbe: 7.0, color: ASPECT_COLORS['Cuadratura'] },
      { nombre: 'Trígono', angulo: 120, orbe: 7.0, color: ASPECT_COLORS['Trígono'] },
      { nombre: 'Quincuncio', angulo: 150, orbe: 3.0, color: ASPECT_COLORS['Quincuncio'] },
      { nombre: 'Oposición', angulo: 180, orbe: 7.0, color: ASPECT_COLORS['Oposición'] }
    ];

    const aspects = [];
    const planetKeys = Object.keys(planets);
    for (let i = 0; i < planetKeys.length; i++) {
      for (let j = i + 1; j < planetKeys.length; j++) {
        const p1 = planets[planetKeys[i]];
        const p2 = planets[planetKeys[j]];
        let diff = Math.abs(p1.grado_absoluto - p2.grado_absoluto);
        if (diff > 180) diff = 360 - diff;

        for (const def of aspectDefs) {
          const orbeActual = Math.abs(diff - def.angulo);
          if (orbeActual <= def.orbe) {
            aspects.push({
              p1: p1.nombre,
              p2: p2.nombre,
              tipo: def.nombre,
              angulo: def.angulo,
              orbe: orbeActual,
              color: def.color
            });
            break;
          }
        }
      }
    }
    this.calculated.aspects = aspects;

    this.updateHUDText();
  }

  updateHUDText() {
    const d = this.timeState.currentDate;
    const timeEl = document.getElementById('hud-time');
    const dateEl = document.getElementById('hud-date');
    const ascEl = document.getElementById('hud-asc');
    const mcEl = document.getElementById('hud-mc');
    const moonEl = document.getElementById('hud-moon');
    const transitEl = document.getElementById('hud-transit');

    if (timeEl) {
      timeEl.innerText = d.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
    if (dateEl) {
      dateEl.innerText = d.toLocaleDateString('es-AR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    }

    if (ascEl) {
      const signIdx = Math.floor(this.calculated.asc / 30);
      const signDeg = Math.floor(this.calculated.asc % 30);
      const signMin = Math.floor(((this.calculated.asc % 30) - signDeg) * 60);
      ascEl.innerHTML = `🌅 <strong>ASC:</strong> ${ZODIAC_SIGNS[signIdx].simbolo} ${ZODIAC_SIGNS[signIdx].nombre} ${signDeg}°${signMin}'`;
    }

    if (mcEl) {
      const signIdx = Math.floor(this.calculated.mc / 30);
      const signDeg = Math.floor(this.calculated.mc % 30);
      mcEl.innerHTML = `👑 <strong>MC:</strong> ${ZODIAC_SIGNS[signIdx].simbolo} ${ZODIAC_SIGNS[signIdx].nombre} ${signDeg}°`;
    }

    if (moonEl) {
      moonEl.innerHTML = `🌙 ${this.calculated.moonPhase.name} • ${this.calculated.moonPhase.illumination}`;
    }

    if (transitEl) {
      // Buscar el aspecto más exacto que involucre al Sol o Luna
      const luminarAspects = this.calculated.aspects.filter(a => a.p1 === 'Sol' || a.p2 === 'Sol' || a.p1 === 'Luna');
      luminarAspects.sort((a, b) => a.orbe - b.orbe);
      if (luminarAspects.length > 0) {
        const top = luminarAspects[0];
        transitEl.innerHTML = `⚡ <strong>Tránsito Clave:</strong> ${top.p1} en ${top.tipo} con ${top.p2} (Orbe ${top.orbe.toFixed(1)}°)`;
      } else {
        transitEl.innerHTML = `⚡ <strong>Cielo Sereno:</strong> Armonía orbital en curso`;
      }
    }
  }

  // ── Renderizado Canvas Vectorial ───────────────────────────────────────────

  degToRad(deg) {
    return (deg * Math.PI) / 180;
  }

  // Convierte un grado del zodíaco a radianes del canvas con el ASC a la izquierda (180° / 9:00 horas)
  coordToAngle(deg) {
    // Carta astral estándar: Ascendente a 180° (izquierda).
    // Ángulo en pantalla = (180 - (deg - asc))
    const rel = (deg - this.calculated.asc);
    const canvasDeg = 180 - rel;
    return this.degToRad((canvasDeg % 360 + 360) % 360);
  }

  animate(now) {
    const deltaMs = now - this.timeState.lastFrameTime;
    this.timeState.lastFrameTime = now;

    if (this.timeState.isLive) {
      const step = deltaMs * this.timeState.timeMultiplier;
      this.timeState.currentDate = new Date(this.timeState.currentDate.getTime() + step);
      this.calculateAll();
    }

    this.render();
    requestAnimationFrame(this.animate);
  }

  render() {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;

    ctx.clearRect(0, 0, w, h);

    const cx = w / 2;
    const cy = h / 2;
    const scale = Math.min(w, h) / 960;

    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(scale, scale);

    // 1. Partículas cósmicas de fondo
    this.renderParticles(ctx);

    // 2. Anillo exterior y esfera de protección
    this.renderDialBoundary(ctx);

    // 3. Rueda de Signos Zodiacales (Los 12 gajos áureos)
    this.renderZodiacWheel(ctx);

    // 4. Las 12 Casas Astrológicas
    this.renderHouses(ctx);

    // 5. Ejes Mayores (Horizonte ASC-DSC y Meridiano MC-IC)
    this.renderCardinals(ctx);

    // 6. Aspectos Euclidianos en el Corazón
    this.renderAspectLines(ctx);

    // 7. Planetas y Agujas Indicadoras
    this.renderPlanets(ctx);

    // 8. Aguja Solar del Tiempo y Corazón Alquímico
    this.renderSunNeedleAndCore(ctx);

    ctx.restore();
  }

  renderParticles(ctx) {
    ctx.save();
    for (const p of this.particles) {
      p.y += p.speed;
      if (p.y > 600) p.y = -600;
      if (p.y < -600) p.y = 600;

      ctx.fillStyle = `rgba(246, 196, 69, ${p.alpha})`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  renderDialBoundary(ctx) {
    const r = this.radii.dialBoundary;
    ctx.save();

    // Viñeta y halo de fondo
    const grad = ctx.createRadialGradient(0, 0, this.radii.core, 0, 0, r + 40);
    grad.addColorStop(0, 'rgba(5, 7, 15, 0.4)');
    grad.addColorStop(0.8, 'rgba(3, 4, 10, 0.85)');
    grad.addColorStop(1, 'rgba(0, 0, 0, 0.98)');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(0, 0, r + 40, 0, Math.PI * 2);
    ctx.fill();

    // Bordes dorados finos
    ctx.strokeStyle = 'rgba(246, 196, 69, 0.35)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(0, 0, r, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = 'rgba(246, 196, 69, 0.15)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(0, 0, r - 6, 0, Math.PI * 2);
    ctx.stroke();

    // Marcas de los 360 grados en el aro exterior
    for (let deg = 0; deg < 360; deg++) {
      const rad = this.coordToAngle(deg);
      const isFive = deg % 5 === 0;
      const isTen = deg % 10 === 0;
      const len = isTen ? 9 : (isFive ? 5 : 2.5);

      const r1 = this.radii.degreeRing;
      const r2 = r1 - len;

      ctx.strokeStyle = isTen ? 'rgba(246, 196, 69, 0.7)' : (isFive ? 'rgba(246, 196, 69, 0.4)' : 'rgba(255, 255, 255, 0.15)');
      ctx.lineWidth = isTen ? 1.2 : 0.7;
      ctx.beginPath();
      ctx.moveTo(Math.cos(rad) * r1, Math.sin(rad) * r1);
      ctx.lineTo(Math.cos(rad) * r2, Math.sin(rad) * r2);
      ctx.stroke();
    }

    ctx.restore();
  }

  renderZodiacWheel(ctx) {
    const rIn = this.radii.zodiacInner;
    const rOut = this.radii.zodiacOuter;
    const rMid = (rIn + rOut) / 2;

    ctx.save();

    for (let i = 0; i < 12; i++) {
      const sign = ZODIAC_SIGNS[i];
      const startDeg = i * 30;
      const endDeg = (i + 1) * 30;
      const midDeg = i * 30 + 15;

      const aStart = this.coordToAngle(startDeg);
      const aEnd = this.coordToAngle(endDeg);
      const aMid = this.coordToAngle(midDeg);

      // Fondo sutil del signo según su elemento
      ctx.beginPath();
      ctx.arc(0, 0, rOut, aStart, aEnd, true); // arco inverso por orientación anti-horaria
      ctx.arc(0, 0, rIn, aEnd, aStart, false);
      ctx.closePath();

      const alpha = (i % 2 === 0) ? 0.08 : 0.03;
      ctx.fillStyle = sign.elemento === 'Fuego' ? `rgba(239, 68, 68, ${alpha})` :
                      sign.elemento === 'Tierra' ? `rgba(16, 185, 129, ${alpha})` :
                      sign.elemento === 'Aire' ? `rgba(245, 158, 11, ${alpha})` :
                      `rgba(56, 189, 248, ${alpha})`;
      ctx.fill();

      // Línea divisoria entre signos
      ctx.strokeStyle = 'rgba(246, 196, 69, 0.35)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(Math.cos(aStart) * rIn, Math.sin(aStart) * rIn);
      ctx.lineTo(Math.cos(aStart) * rOut, Math.sin(aStart) * rOut);
      ctx.stroke();

      // Glifo del Signo Zodiacal
      ctx.fillStyle = '#f6c445';
      ctx.font = '700 24px "Cinzel", "Outfit", serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const gx = Math.cos(aMid) * rMid;
      const gy = Math.sin(aMid) * rMid;
      ctx.fillText(sign.simbolo, gx, gy);

      // Nombre del Signo en el perímetro exterior
      ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
      ctx.font = '500 9px "Outfit", sans-serif';
      const nx = Math.cos(aMid) * (rOut - 14);
      const ny = Math.sin(aMid) * (rOut - 14);
      ctx.fillText(sign.nombre.toUpperCase(), nx, ny);
    }

    // Aros que delimitan los signos
    ctx.strokeStyle = 'rgba(246, 196, 69, 0.6)';
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.arc(0, 0, rIn, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(0, 0, rOut, 0, Math.PI * 2);
    ctx.stroke();

    ctx.restore();
  }

  renderHouses(ctx) {
    const rIn = this.radii.housesInner;
    const rOut = this.radii.housesOuter;
    const rNum = (rIn + rOut) / 2;

    ctx.save();
    for (let h = 0; h < 12; h++) {
      const cuspDeg = this.calculated.houses[h];
      const aCusp = this.coordToAngle(cuspDeg);
      const nextCuspDeg = this.calculated.houses[(h + 1) % 12];
      const aMid = this.coordToAngle((cuspDeg + 15) % 360);

      // Cúspide de la casa
      ctx.strokeStyle = (h % 3 === 0) ? 'rgba(246, 196, 69, 0.5)' : 'rgba(255, 255, 255, 0.12)';
      ctx.lineWidth = (h % 3 === 0) ? 1.5 : 0.8;
      ctx.beginPath();
      ctx.moveTo(Math.cos(aCusp) * this.radii.core, Math.sin(aCusp) * this.radii.core);
      ctx.lineTo(Math.cos(aCusp) * rOut, Math.sin(aCusp) * rOut);
      ctx.stroke();

      // Número romano de la Casa
      const romanos = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"];
      ctx.fillStyle = (h % 3 === 0) ? '#f6c445' : 'rgba(255, 255, 255, 0.35)';
      ctx.font = '600 11px "Outfit", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(romanos[h], Math.cos(aMid) * rNum, Math.sin(aMid) * rNum);
    }
    ctx.restore();
  }

  renderCardinals(ctx) {
    ctx.save();

    // 1. Eje del Horizonte: Ascendente (Izquierda) a Descendente (Derecha)
    const aAsc = this.coordToAngle(this.calculated.asc);
    const aDsc = this.coordToAngle(this.calculated.dsc);
    const rExt = this.radii.dialBoundary + 15;

    ctx.strokeStyle = '#00f2fe';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(Math.cos(aAsc) * rExt, Math.sin(aAsc) * rExt);
    ctx.lineTo(Math.cos(aDsc) * rExt, Math.sin(aDsc) * rExt);
    ctx.stroke();

    // Flecha del Ascendente en el horizonte izquierdo
    ctx.fillStyle = '#00f2fe';
    const ascX = Math.cos(aAsc) * rExt;
    const ascY = Math.sin(aAsc) * rExt;
    ctx.beginPath();
    ctx.arc(ascX, ascY, 5, 0, Math.PI * 2);
    ctx.fill();

    ctx.font = '800 12px "Outfit", sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText('ASC', ascX - 10, ascY);

    ctx.textAlign = 'left';
    ctx.fillText('DSC', Math.cos(aDsc) * rExt + 10, Math.sin(aDsc) * rExt);

    // 2. Eje del Meridiano: Medio Cielo (Arriba) a Fondo de Cielo (Abajo)
    const aMc = this.coordToAngle(this.calculated.mc);
    const aIc = this.coordToAngle(this.calculated.ic);

    ctx.strokeStyle = '#f6c445';
    ctx.lineWidth = 2.0;
    ctx.beginPath();
    ctx.moveTo(Math.cos(aMc) * rExt, Math.sin(aMc) * rExt);
    ctx.lineTo(Math.cos(aIc) * rExt, Math.sin(aIc) * rExt);
    ctx.stroke();

    ctx.fillStyle = '#f6c445';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.fillText('MC', Math.cos(aMc) * rExt, Math.sin(aMc) * rExt - 6);
    ctx.textBaseline = 'top';
    ctx.fillText('IC', Math.cos(aIc) * rExt, Math.sin(aIc) * rExt + 6);

    ctx.restore();
  }

  renderAspectLines(ctx) {
    const r = this.radii.aspects;
    ctx.save();

    for (const asp of this.calculated.aspects) {
      const p1 = this.calculated.planets[asp.p1];
      const p2 = this.calculated.planets[asp.p2];
      if (!p1 || !p2) continue;

      const a1 = this.coordToAngle(p1.grado_absoluto);
      const a2 = this.coordToAngle(p2.grado_absoluto);

      const x1 = Math.cos(a1) * r;
      const y1 = Math.sin(a1) * r;
      const x2 = Math.cos(a2) * r;
      const y2 = Math.sin(a2) * r;

      // Intensidad de la línea inversamente proporcional al orbe
      const alpha = Math.max(0.15, 0.85 - (asp.orbe / 7.0));
      ctx.strokeStyle = asp.color;
      ctx.globalAlpha = alpha;
      ctx.lineWidth = (asp.tipo === 'Conjunción' || asp.tipo === 'Oposición' || asp.tipo === 'Cuadratura') ? 1.8 : 1.2;

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }

    ctx.globalAlpha = 1.0;
    ctx.restore();
  }

  renderPlanets(ctx) {
    const rPlanets = this.radii.planets;
    ctx.save();

    const planetArray = Object.values(this.calculated.planets);

    for (const p of planetArray) {
      const a = this.coordToAngle(p.grado_absoluto);
      const px = Math.cos(a) * rPlanets;
      const py = Math.sin(a) * rPlanets;

      // Aguja indicadora que va desde el círculo de aspectos hacia el astro
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
      ctx.lineWidth = 0.8;
      ctx.beginPath();
      ctx.moveTo(Math.cos(a) * this.radii.aspects, Math.sin(a) * this.radii.aspects);
      ctx.lineTo(Math.cos(a) * (this.radii.zodiacInner - 5), Math.sin(a) * (this.radii.zodiacInner - 5));
      ctx.stroke();

      // Punto orbital en el perímetro del zodíaco
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(Math.cos(a) * this.radii.zodiacInner, Math.sin(a) * this.radii.zodiacInner, 2.5, 0, Math.PI * 2);
      ctx.fill();

      // Cápsula del astro (Aura circular)
      const grad = ctx.createRadialGradient(px, py, 4, px, py, 22);
      grad.addColorStop(0, p.color);
      grad.addColorStop(0.3, 'rgba(15, 23, 42, 0.95)');
      grad.addColorStop(1, 'rgba(0, 0, 0, 0.6)');

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(px, py, 18, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = p.color;
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      ctx.arc(px, py, 16, 0, Math.PI * 2);
      ctx.stroke();

      // Glifo del Planeta
      const glyph = GLYPHS[p.nombre] || '✦';
      ctx.fillStyle = '#ffffff';
      ctx.font = '700 17px "Outfit", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(glyph, px, py - 1);

      // Etiqueta legible (Nombre + Grado)
      ctx.fillStyle = '#f1f5f9';
      ctx.font = '600 9px "Outfit", sans-serif';
      const labelY = py > 0 ? py + 23 : py - 23;
      ctx.fillText(`${p.nombre.slice(0, 3)} ${p.grado}°`, px, labelY);
    }

    ctx.restore();
  }

  renderSunNeedleAndCore(ctx) {
    const sun = this.calculated.planets['Sol'];
    if (!sun) return;

    ctx.save();
    const aSun = this.coordToAngle(sun.grado_absoluto);

    // Aguja Solar Alquímica (Aguja Horaria del Reloj Cósmico)
    const len = this.radii.dialBoundary - 10;
    const gradNeedle = ctx.createLinearGradient(0, 0, Math.cos(aSun) * len, Math.sin(aSun) * len);
    gradNeedle.addColorStop(0, 'rgba(246, 196, 69, 0.9)');
    gradNeedle.addColorStop(0.7, 'rgba(246, 196, 69, 0.7)');
    gradNeedle.addColorStop(1, '#ffffff');

    ctx.strokeStyle = gradNeedle;
    ctx.lineWidth = 2.2;
    ctx.shadowColor = 'rgba(246, 196, 69, 0.8)';
    ctx.shadowBlur = 12;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(aSun) * len, Math.sin(aSun) * len);
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Núcleo Central Alquímico (Sol Negro / Sol Áureo)
    const rCore = this.radii.core;
    const coreGrad = ctx.createRadialGradient(0, 0, 5, 0, 0, rCore);
    coreGrad.addColorStop(0, 'rgba(246, 196, 69, 0.25)');
    coreGrad.addColorStop(0.4, 'rgba(10, 15, 28, 0.85)');
    coreGrad.addColorStop(1, 'rgba(3, 5, 12, 0.98)');

    ctx.fillStyle = coreGrad;
    ctx.beginPath();
    ctx.arc(0, 0, rCore, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = 'rgba(246, 196, 69, 0.5)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(0, 0, rCore, 0, Math.PI * 2);
    ctx.stroke();

    // Sello del Glifo Maestro en el Centro
    ctx.fillStyle = '#f6c445';
    ctx.font = '700 32px "Cinzel", serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('☉', 0, -8);

    ctx.font = '600 10px "Cinzel", sans-serif';
    ctx.fillStyle = 'rgba(246, 196, 69, 0.85)';
    ctx.fillText('EL GLIFO MAESTRO', 0, 22);

    ctx.restore();
  }
}

// Inicializar cuando el DOM esté listo
window.addEventListener('DOMContentLoaded', () => {
  window.relojEngine = new RelojAstrologicoEngine();
});
