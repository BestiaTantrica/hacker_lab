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

const CASA_SIGNIFICADOS = {
  1: "Casa I (Ascendente): Identidad, presencia física, impulso vital y máscara exterior.",
  2: "Casa II: Recursos propios, economía personal, valores y seguridad material.",
  3: "Casa III: Mente concreta, comunicación inmediata, hermanos y entorno cercano.",
  4: "Casa IV (Fondo de Cielo): Raíces, hogar, linaje familiar y mundo íntimo subterráneo.",
  5: "Casa V: Creatividad pura, pasiones, autoexpresión, romances e hijos.",
  6: "Casa VI: Salud somática, disciplina cotidiana, trabajo y orden del cuerpo.",
  7: "Casa VII (Descendente): El espejo del otro, compromisos, socios y vínculos contractuales.",
  8: "Casa VIII: Transformación radical, sexualidad alquímica, crisis y recursos compartidos.",
  9: "Casa IX: Filosofía, viajes lejanos, cosmovisión superior y búsqueda de sentido.",
  10: "Casa X (Medio Cielo): Vocación, destino público, reputación y maestría en el mundo.",
  11: "Casa XI: Redes humanas, proyectos colectivos, ideales comunitarios y futuro.",
  12: "Casa XII: Inconsciente colectivo, lo no resuelto, retiro espiritual y disolución del ego."
};

const ROMAN_HOURS = ['XII', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI'];

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

    // Radios del Reloj Cósmico y Carriles de Tiempo Exteriores
    this.radii = {
      core: 28,            // Reducido a 28px para liberar completamente el centro sagrado y los aspectos
      aspects: 185,
      housesInner: 195,
      planets: 275,
      housesOuter: 330,
      zodiacInner: 340,
      zodiacOuter: 420,
      degreeRing: 432,
      dialBoundary: 450,
      trackHours: 472,     // Carril Exterior 1: Horas (Loading tenebrista y gema de bronce)
      trackMinutes: 494,   // Carril Exterior 2: Minutos (Barra áurea y prisma alquímico)
      trackSeconds: 516    // Carril Exterior 3: Segundos (Barrido fluido y chispa ámbar)
    };

    // Cámara Virtual (Zoom y Paneo Interactivo en el Canvas)
    this.camera = {
      zoom: 1.0,
      minZoom: 0.55,
      maxZoom: 4.5,
      panX: 0,
      panY: 0,
      isDragging: false,
      dragStartX: 0,
      dragStartY: 0
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

    // Efecto partículas de polvo estelar cósmico tenebrista (3 capas de profundidad)
    this.particles = [];
    this.initParticles(160);

    // Grabador de video para Watermark
    this.mediaRecorder = null;
    this.recordedChunks = [];
    this.isRecording = false;

    // Tooltip e Inspector HUD (Proyección en la Esquina para no tapar el orbe)
    this.tooltip = document.getElementById('reloj-tooltip');
    this.inspectorHUD = document.getElementById('astro-inspector-hud');
    this.hoveredItem = null;
    this.inactivityTimer = null;
    this.uiHiddenPinned = false;

    // Detectar Modo Wallpaper por URL (?mode=wallpaper)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('mode') === 'wallpaper' || urlParams.get('clean') === '1') {
      this.uiHiddenPinned = true;
      this.container?.classList.add('clean-wallpaper');
    }

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
      const typeRand = Math.random();
      let type = 'nebula';
      let size = Math.random() * 1.5 + 0.4;
      let alpha = Math.random() * 0.35 + 0.05;
      let speed = (Math.random() * 0.12 + 0.03);
      let color = 'rgba(246, 196, 69,';

      if (typeRand > 0.78) {
        // Capa 3: Chispa alquímica ámbar veloz
        type = 'sparkle';
        size = Math.random() * 2.2 + 0.8;
        alpha = Math.random() * 0.7 + 0.25;
        speed = (Math.random() * 0.28 + 0.08);
        color = Math.random() > 0.5 ? 'rgba(249, 115, 22,' : 'rgba(246, 196, 69,';
      } else if (typeRand > 0.45) {
        // Capa 2: Estrella guía blanca/oro con centelleo
        type = 'star';
        size = Math.random() * 1.9 + 0.6;
        alpha = Math.random() * 0.6 + 0.2;
        speed = (Math.random() * 0.08 + 0.02);
        color = 'rgba(255, 255, 255,';
      }

      this.particles.push({
        x: (Math.random() - 0.5) * 1600,
        y: (Math.random() - 0.5) * 1600,
        type,
        size,
        baseAlpha: alpha,
        alpha,
        speed: speed * (Math.random() > 0.45 ? 1 : -1),
        driftX: (Math.random() - 0.5) * 0.06,
        phase: Math.random() * Math.PI * 2,
        color
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

    // Botón de Reset de Zoom & Paneo
    const btnResetZoom = document.getElementById('btn-reset-zoom');
    if (btnResetZoom) {
      btnResetZoom.addEventListener('click', () => {
        this.resetCamera();
      });
    }

    // ── Zoom y Paneo Interactivo en el Canvas (Cámara Virtual) ───────────
    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      this.resetInactivityTimer();
      const zoomFactor = e.deltaY < 0 ? 1.12 : 0.89;
      const newZoom = Math.min(Math.max(this.camera.zoom * zoomFactor, this.camera.minZoom), this.camera.maxZoom);
      this.camera.zoom = newZoom;
      this.updateZoomHUD();
    }, { passive: false });

    this.canvas.addEventListener('mousedown', (e) => {
      if (e.button === 0) { // Clic izquierdo para arrastrar
        this.camera.isDragging = true;
        this.camera.dragStartX = e.clientX - this.camera.panX;
        this.camera.dragStartY = e.clientY - this.camera.panY;
        this.canvas.style.cursor = 'grabbing';
      }
    });

    window.addEventListener('mouseup', () => {
      if (this.camera.isDragging) {
        this.camera.isDragging = false;
        this.canvas.style.cursor = this.hoveredItem ? 'pointer' : 'default';
      }
    });

    // ── Interacción con Puntero / Touch (Hit Testing & Inspector HUD) ──────
    this.canvas.addEventListener('mousemove', (e) => {
      if (this.camera.isDragging) {
        this.camera.panX = e.clientX - this.camera.dragStartX;
        this.camera.panY = e.clientY - this.camera.dragStartY;
        return;
      }
      this.handlePointerMove(e);
    });

    this.canvas.addEventListener('mouseleave', () => {
      this.camera.isDragging = false;
      this.hoveredItem = null;
      this.updateInspectorHUD(null);
    });

    this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
    this.canvas.addEventListener('touchstart', (e) => {
      if (e.touches.length > 0) {
        this.handlePointerMove(e.touches[0]);
      }
    }, { passive: true });

    // ── Auto-Hide de Interfaz tras 3.8 segundos de inactividad ───────────
    window.addEventListener('mousemove', () => this.resetInactivityTimer());
    window.addEventListener('keydown', (e) => {
      if (e.key === 'h' || e.key === 'H') {
        this.toggleUIVisibility();
      } else if (e.key === '0' || e.key === 'r' || e.key === 'R') {
        this.resetCamera();
      } else {
        this.resetInactivityTimer();
      }
    });

    // Botón Ocultar UI (H)
    const btnToggleUI = document.getElementById('btn-toggle-ui');
    if (btnToggleUI) {
      btnToggleUI.addEventListener('click', () => {
        this.toggleUIVisibility();
      });
    }

    // Doble clic en canvas para alternar UI
    this.canvas.addEventListener('dblclick', () => {
      this.toggleUIVisibility();
    });

    this.resetInactivityTimer();
  }

  // ── Gestión de Inactividad y Modo Inmersivo (Wallpaper Puro) ───────────────
  resetInactivityTimer() {
    if (this.uiHiddenPinned) return;

    this.container?.classList.remove('ui-hidden');

    if (this.inactivityTimer) clearTimeout(this.inactivityTimer);
    this.inactivityTimer = setTimeout(() => {
      this.container?.classList.add('ui-hidden');
    }, 3800);
  }

  toggleUIVisibility() {
    this.uiHiddenPinned = !this.uiHiddenPinned;
    this.container?.classList.toggle('ui-hidden', this.uiHiddenPinned);
    const btn = document.getElementById('btn-toggle-ui');
    if (btn) {
      btn.innerHTML = this.uiHiddenPinned ? '<span>👁‍🗨</span> Mostrar UI (H)' : '<span>👁</span> Ocultar UI (H)';
      btn.classList.toggle('active', this.uiHiddenPinned);
    }
  }

  resetCamera() {
    this.camera.zoom = 1.0;
    this.camera.panX = 0;
    this.camera.panY = 0;
    this.updateZoomHUD();
  }

  updateZoomHUD() {
    const btnReset = document.getElementById('btn-reset-zoom');
    if (btnReset) {
      btnReset.innerHTML = `<span>⟲</span> ${this.camera.zoom.toFixed(1)}x`;
      btnReset.classList.toggle('active', Math.abs(this.camera.zoom - 1.0) > 0.05 || this.camera.panX !== 0 || this.camera.panY !== 0);
    }
  }

  // ── Hit-Testing & Proyección en Esquina (Nada tapa el Orbe) ─────────────────
  handlePointerMove(e) {
    this.resetInactivityTimer();

    const rect = this.canvas.getBoundingClientRect();
    const cx = this.width / 2;
    const cy = this.height / 2;
    const baseScale = Math.min(this.width, this.height) / 1080;
    const currentScale = baseScale * this.camera.zoom;

    const mouseX = (e.clientX - rect.left - (cx + this.camera.panX)) / currentScale;
    const mouseY = (e.clientY - rect.top - (cy + this.camera.panY)) / currentScale;

    let hit = null;

    // 1. Detectar Planetas (Radio 24px)
    const planetArray = Object.values(this.calculated.planets);
    for (const p of planetArray) {
      const a = this.coordToAngle(p.grado_absoluto);
      const px = Math.cos(a) * this.radii.planets;
      const py = Math.sin(a) * this.radii.planets;
      const dist = Math.hypot(mouseX - px, mouseY - py);
      if (dist < 26) {
        hit = { tipo: 'planeta', data: p };
        break;
      }
    }

    // 2. Si no es planeta, detectar si está sobre un Signo Zodiacal
    if (!hit) {
      const distC = Math.hypot(mouseX, mouseY);
      if (distC >= this.radii.zodiacInner && distC <= this.radii.zodiacOuter) {
        let angle = Math.atan2(mouseY, mouseX);
        let relDeg = ((Math.PI - angle) * 180 / Math.PI) % 360;
        if (relDeg < 0) relDeg += 360;
        let eclipticDeg = (relDeg + this.calculated.asc) % 360;
        let signIdx = Math.floor(eclipticDeg / 30);
        let signDeg = Math.floor(eclipticDeg % 30);
        if (ZODIAC_SIGNS[signIdx]) {
          hit = { tipo: 'signo', data: ZODIAC_SIGNS[signIdx], grado: signDeg };
        }
      }
    }

    // 3. Si no es signo, detectar Casa Astrológica
    if (!hit) {
      const distC = Math.hypot(mouseX, mouseY);
      if (distC >= this.radii.housesInner && distC <= this.radii.housesOuter) {
        let angle = Math.atan2(mouseY, mouseX);
        let relDeg = ((Math.PI - angle) * 180 / Math.PI) % 360;
        if (relDeg < 0) relDeg += 360;
        let houseNum = Math.floor(relDeg / 30) + 1;
        if (houseNum >= 1 && houseNum <= 12) {
          hit = { tipo: 'casa', num: houseNum };
        }
      }
    }

    this.hoveredItem = hit;
    this.canvas.style.cursor = hit ? 'pointer' : (this.camera.isDragging ? 'grabbing' : 'default');

    // Proyectar siempre a la esquina inferior izquierda (sin tapar el orbe)
    this.updateInspectorHUD(hit);
  }

  handleCanvasClick(e) {
    if (this.hoveredItem) {
      const p = this.hoveredItem.data;
      if (this.hoveredItem.tipo === 'planeta') {
        console.log(`[Glifo Maestro] Astro Seleccionado: ${p.nombre} en ${p.signo} ${p.grado}°${p.minutos}' (Casa ${p.casa})`);
      }
    }
  }

  // ── Proyección al Inspector HUD (Esquina Inferior Izquierda Limpia) ────────
  updateInspectorHUD(hit) {
    const hud = this.inspectorHUD || document.getElementById('astro-inspector-hud');
    if (!hud) return;

    if (!hit) {
      // Estado de reposo: Tránsito y Luminarias en vivo
      const ascSign = ZODIAC_SIGNS[Math.floor(this.calculated.asc / 30)] || ZODIAC_SIGNS[0];
      const ascDeg = Math.floor(this.calculated.asc % 30);
      const mcSign = ZODIAC_SIGNS[Math.floor(this.calculated.mc / 30)] || ZODIAC_SIGNS[9];
      const mcDeg = Math.floor(this.calculated.mc % 30);

      const topAspect = this.calculated.aspects.find(a => a.p1 === 'Sol' || a.p2 === 'Sol') || this.calculated.aspects[0];
      const aspectStr = topAspect ? `${topAspect.p1} en ${topAspect.tipo} con ${topAspect.p2} (Orbe ${topAspect.orbe.toFixed(1)}°)` : 'Armonía celeste activa';

      hud.innerHTML = `
        <div class="inspector-badge">🔭 INSPECTOR CÓSMICO</div>
        <div class="inspector-title" style="color: #f6c445;">Bóveda Celeste en Vivo</div>
        <div class="inspector-grid">
          <div><span>🌅 ASC:</span> <strong>${ascSign.simbolo} ${ascSign.nombre} ${ascDeg}°</strong></div>
          <div><span>👑 MC:</span> <strong>${mcSign.simbolo} ${mcSign.nombre} ${mcDeg}°</strong></div>
          <div><span>🌙 LUNA:</span> <strong>${this.calculated.moonPhase.name}</strong></div>
          <div><span>⚡ TRÁNSITO:</span> <strong>${aspectStr}</strong></div>
        </div>
        <div class="inspector-hint">Pasa el cursor sobre un planeta o casa para inspeccionar sin tapar el mandala.</div>
      `;
      hud.classList.remove('active-hover');
      return;
    }

    hud.classList.add('active-hover');

    if (hit.tipo === 'planeta') {
      const p = hit.data;
      const glyph = GLYPHS[p.nombre] || '★';
      const casaDesc = CASA_SIGNIFICADOS[p.casa] || `Casa ${p.casa}`;

      // Filtrar aspectos activos del planeta
      const planetAspects = this.calculated.aspects.filter(a => a.p1 === p.nombre || a.p2 === p.nombre);
      let aspectsHtml = '';
      if (planetAspects.length > 0) {
        aspectsHtml = '<div class="inspector-aspects-list">' +
          planetAspects.slice(0, 4).map(a => {
            const otro = a.p1 === p.nombre ? a.p2 : a.p1;
            return `<div class="aspect-pill" style="border-left: 2px solid ${a.color};">
              <span style="color:${a.color}">⚡ ${a.tipo}</span> con <strong>${GLYPHS[otro]||''} ${otro}</strong> (orbe ${a.orbe.toFixed(1)}°)
            </div>`;
          }).join('') + '</div>';
      } else {
        aspectsHtml = '<div style="color: #94a3b8; font-size: 10px; margin-top: 4px;">Sin aspectos mayores tensos en este orbe.</div>';
      }

      hud.innerHTML = `
        <div class="inspector-badge" style="color:${p.color}; border-color:${p.color};">✦ PLANETA EN TRÁNSITO</div>
        <div class="inspector-title">
          <span style="font-size: 20px; color:${p.color}; margin-right: 6px;">${glyph}</span>
          <strong>${p.nombre}</strong> en ${p.signo_simbolo} ${p.signo} ${p.grado}°${p.minutos}'
        </div>
        <div class="inspector-meta">
          <div><strong>Emplazamiento:</strong> ${casaDesc}</div>
        </div>
        ${aspectsHtml}
      `;
    } else if (hit.tipo === 'signo') {
      const s = hit.data;
      hud.innerHTML = `
        <div class="inspector-badge" style="color:${s.color}; border-color:${s.color};">✦ SECTOR ZODIACAL</div>
        <div class="inspector-title">
          <span style="font-size: 20px; color:${s.color}; margin-right: 6px;">${s.simbolo}</span>
          Signo de ${s.nombre} (${hit.grado}°)
        </div>
        <div class="inspector-meta">
          <div><strong>Elemento:</strong> ${s.elemento} • <strong>Planeta Regente:</strong> ${s.regente}</div>
        </div>
      `;
    } else if (hit.tipo === 'casa') {
      const casaDesc = CASA_SIGNIFICADOS[hit.num] || `Casa ${hit.num}`;
      const partes = casaDesc.split(':');
      hud.innerHTML = `
        <div class="inspector-badge">🏛️ CASA ASTROLÓGICA</div>
        <div class="inspector-title">${partes[0]}</div>
        <div class="inspector-meta">
          <div>${partes[1] || ''}</div>
        </div>
      `;
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
        this.videoBg.src = "/videos_fondo/07_espacio_galaxias_deep_space_galaxy_pex_v_15562120.mp4";
      } else if (bgType === 'estrellas') {
        this.videoBg.src = "/videos_fondo/07_espacio_galaxias_stars_ethereal_glowing_pex_v_35115646.mp4";
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
    // Escala base: 1080 da el espacio perfecto para los 3 carriles exteriores y margen de respiración
    const baseScale = Math.min(w, h) / 1080;
    const currentScale = baseScale * this.camera.zoom;

    ctx.save();
    ctx.translate(cx + this.camera.panX, cy + this.camera.panY);
    ctx.scale(currentScale, currentScale);

    // 1. Partículas cósmicas tenebristas en 3 capas de profundidad
    this.renderParticles(ctx, performance.now());

    // 2. Hilos / Rayos Etéreos por debajo de todo (conectan el centro antiguo con los marcadores exteriores)
    this.renderTimeRaysUnderlay(ctx);

    // 3. Bisel tenebrista y aro de protección del astrolabio
    this.renderDialBoundary(ctx);

    // 4. Los Tres Carriles Exteriores de Horas, Minutos y Segundos (Loading Continuo Tenebrista)
    this.renderOuterTimeTracks(ctx);

    // 5. Rueda de Signos Zodiacales (Los 12 gajos áureos)
    this.renderZodiacWheel(ctx);

    // 6. Las 12 Casas Astrológicas (convergen limpiamente en el centro de 28px)
    this.renderHouses(ctx);

    // 7. Ejes Mayores (Horizonte ASC-DSC y Meridiano MC-IC)
    this.renderCardinals(ctx);

    // 8. Aspectos Euclidianos en el Corazón (100% Visibles y Libres de Obstrucción)
    this.renderAspectLines(ctx);

    // 9. Planetas en Tránsito y Agujas Indicadoras
    this.renderPlanets(ctx);

    // 10. Núcleo Alquímico Sagrado (El Observador / Punto Cero Tierra ⊕ de 28px)
    this.renderAlchemicalCore(ctx);

    ctx.restore();
  }

  // ── Polvo Cósmico y Viaje Estelar Tenebrista (3 Capas) ─────────────────────
  renderParticles(ctx, now = performance.now()) {
    ctx.save();
    for (const p of this.particles) {
      p.y += p.speed;
      p.x += p.driftX;
      if (p.y > 750) p.y = -750;
      if (p.y < -750) p.y = 750;
      if (p.x > 750) p.x = -750;
      if (p.x < -750) p.x = 750;

      let alpha = p.baseAlpha;
      if (p.type === 'star') {
        alpha = p.baseAlpha * (0.65 + 0.35 * Math.sin(now * 0.0025 + p.phase));
      } else if (p.type === 'sparkle') {
        alpha = p.baseAlpha * (0.7 + 0.3 * Math.sin(now * 0.005 + p.phase));
      }

      ctx.fillStyle = `${p.color} ${alpha})`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();

      // Cruz de difracción óptica para estrellas más intensas
      if (p.type === 'sparkle' && p.size > 1.8) {
        ctx.strokeStyle = `rgba(255, 255, 255, ${alpha * 0.45})`;
        ctx.lineWidth = 0.6;
        ctx.beginPath();
        ctx.moveTo(p.x - 3.5, p.y);
        ctx.lineTo(p.x + 3.5, p.y);
        ctx.moveTo(p.x, p.y - 3.5);
        ctx.lineTo(p.x, p.y + 3.5);
        ctx.stroke();
      }
    }
    ctx.restore();
  }

  // ── Rayos Etéreos que conectan el Centro Alquímico con los Carriles Exteriores ──
  renderTimeRaysUnderlay(ctx) {
    const d = this.timeState.currentDate;
    const ms = d.getMilliseconds();
    const s = d.getSeconds() + ms / 1000;
    const m = d.getMinutes() + s / 60;
    const h = (d.getHours() % 24) + m / 60;

    const angH = -Math.PI / 2 + (h / 24) * Math.PI * 2;
    const angM = -Math.PI / 2 + (m / 60) * Math.PI * 2;
    const angS = -Math.PI / 2 + (s / 60) * Math.PI * 2;

    const rH = this.radii.trackHours;
    const rM = this.radii.trackMinutes;
    const rS = this.radii.trackSeconds;

    ctx.save();

    // 1. Rayo de Horas: Bronce sagrado etéreo
    const gradH = ctx.createLinearGradient(0, 0, Math.cos(angH) * rH, Math.sin(angH) * rH);
    gradH.addColorStop(0, 'rgba(212, 175, 55, 0.02)');
    gradH.addColorStop(0.5, 'rgba(212, 175, 55, 0.08)');
    gradH.addColorStop(1, 'rgba(246, 196, 69, 0.45)');
    ctx.strokeStyle = gradH;
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(angH) * rH, Math.sin(angH) * rH);
    ctx.stroke();

    // 2. Rayo de Minutos: Oro filigrana tenue
    const gradM = ctx.createLinearGradient(0, 0, Math.cos(angM) * rM, Math.sin(angM) * rM);
    gradM.addColorStop(0, 'rgba(246, 196, 69, 0.02)');
    gradM.addColorStop(0.6, 'rgba(246, 196, 69, 0.12)');
    gradM.addColorStop(1, 'rgba(246, 196, 69, 0.55)');
    ctx.strokeStyle = gradM;
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(angM) * rM, Math.sin(angM) * rM);
    ctx.stroke();

    // 3. Rayo de Segundos: Haz áureo cometa
    const gradS = ctx.createLinearGradient(0, 0, Math.cos(angS) * rS, Math.sin(angS) * rS);
    gradS.addColorStop(0, 'rgba(255, 255, 255, 0.02)');
    gradS.addColorStop(0.7, 'rgba(246, 196, 69, 0.15)');
    gradS.addColorStop(1, 'rgba(255, 255, 255, 0.7)');
    ctx.strokeStyle = gradS;
    ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(angS) * rS, Math.sin(angS) * rS);
    ctx.stroke();

    ctx.restore();
  }

  // ── Los 3 Carriles Exteriores de Horas, Minutos y Segundos (Loading Tenebrista) ──
  renderOuterTimeTracks(ctx) {
    const d = this.timeState.currentDate;
    const ms = d.getMilliseconds();
    const s = d.getSeconds() + ms / 1000;
    const m = d.getMinutes() + s / 60;
    const h = (d.getHours() % 24) + m / 60;

    const angStart = -Math.PI / 2; // Las 12 en punto (cenit)
    const angH = angStart + (h / 24) * Math.PI * 2;
    const angM = angStart + (m / 60) * Math.PI * 2;
    const angS = angStart + (s / 60) * Math.PI * 2;

    const rH = this.radii.trackHours;
    const rM = this.radii.trackMinutes;
    const rS = this.radii.trackSeconds;

    ctx.save();

    // ─────────────────────────────────────────────────────────────────────────
    // CARRIL 1: HORAS (24h — Pista de Bronce con Arco de Carga Áureo)
    // ─────────────────────────────────────────────────────────────────────────
    ctx.strokeStyle = 'rgba(78, 55, 15, 0.22)';
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.arc(0, 0, rH, 0, Math.PI * 2);
    ctx.stroke();

    // Bordes concéntricos de filigrana
    ctx.strokeStyle = 'rgba(246, 196, 69, 0.25)';
    ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.arc(0, 0, rH - 4.5, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(0, 0, rH + 4.5, 0, Math.PI * 2);
    ctx.stroke();

    // Arco de carga/progreso de Horas
    const gradHourArc = ctx.createLinearGradient(0, -rH, 0, rH);
    gradHourArc.addColorStop(0, '#d4af37');
    gradHourArc.addColorStop(0.5, '#78550f');
    gradHourArc.addColorStop(1, '#f6c445');
    ctx.strokeStyle = gradHourArc;
    ctx.lineWidth = 5.0;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.arc(0, 0, rH, angStart, angH, false);
    ctx.stroke();
    ctx.lineCap = 'butt';

    // Marcador de Hora: Medallón Alquímico de Bronce y Oro
    const hx = Math.cos(angH) * rH;
    const hy = Math.sin(angH) * rH;
    ctx.save();
    ctx.shadowColor = 'rgba(246, 196, 69, 0.9)';
    ctx.shadowBlur = 10;
    ctx.fillStyle = '#1c1305';
    ctx.strokeStyle = '#f6c445';
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    ctx.arc(hx, hy, 6.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = '#fef08a';
    ctx.beginPath();
    ctx.arc(hx, hy, 2.8, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // ─────────────────────────────────────────────────────────────────────────
    // CARRIL 2: MINUTOS (60 Minutos — Barra Áurea Bruñida)
    // ─────────────────────────────────────────────────────────────────────────
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.16)';
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.arc(0, 0, rM, 0, Math.PI * 2);
    ctx.stroke();

    // Arco de progreso de Minutos
    ctx.strokeStyle = '#f6c445';
    ctx.lineWidth = 3.8;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.arc(0, 0, rM, angStart, angM, false);
    ctx.stroke();
    ctx.lineCap = 'butt';

    // Marcador de Minuto: Prisma / Rombo Alquímico
    const mx = Math.cos(angM) * rM;
    const my = Math.sin(angM) * rM;
    ctx.save();
    ctx.translate(mx, my);
    ctx.rotate(angM + Math.PI / 4);
    ctx.shadowColor = 'rgba(246, 196, 69, 0.85)';
    ctx.shadowBlur = 8;
    ctx.fillStyle = '#ffffff';
    ctx.strokeStyle = '#d97706';
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.rect(-3.5, -3.5, 7, 7);
    ctx.fill();
    ctx.stroke();
    ctx.restore();

    // ─────────────────────────────────────────────────────────────────────────
    // CARRIL 3: SEGUNDOS (60s — Barrido Continuo Fluido y Chispa Ámbar)
    // ─────────────────────────────────────────────────────────────────────────
    ctx.strokeStyle = 'rgba(246, 196, 69, 0.08)';
    ctx.lineWidth = 3.5;
    ctx.beginPath();
    ctx.arc(0, 0, rS, 0, Math.PI * 2);
    ctx.stroke();

    // Estela de Cometa fluida para los segundos (últimos 45 grados de recorrido)
    const tailSpan = Math.PI / 3;
    const tailStart = angS - tailSpan;
    const gradSecTail = ctx.createLinearGradient(
      Math.cos(tailStart) * rS, Math.sin(tailStart) * rS,
      Math.cos(angS) * rS, Math.sin(angS) * rS
    );
    gradSecTail.addColorStop(0, 'rgba(246, 196, 69, 0.0)');
    gradSecTail.addColorStop(0.6, 'rgba(246, 196, 69, 0.35)');
    gradSecTail.addColorStop(1, 'rgba(255, 255, 255, 0.95)');

    ctx.strokeStyle = gradSecTail;
    ctx.lineWidth = 2.6;
    ctx.beginPath();
    ctx.arc(0, 0, rS, tailStart, angS, false);
    ctx.stroke();

    // Marcador de Segundo: Chispa Estelar Ámbar Resplandeciente
    const sx = Math.cos(angS) * rS;
    const sy = Math.sin(angS) * rS;
    ctx.save();
    ctx.shadowColor = 'rgba(246, 196, 69, 1.0)';
    ctx.shadowBlur = 12;
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(sx, sy, 3.2, 0, Math.PI * 2);
    ctx.fill();

    // Cruz de difracción óptica del segundero
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(sx - 5, sy);
    ctx.lineTo(sx + 5, sy);
    ctx.moveTo(sx, sy - 5);
    ctx.lineTo(sx, sy + 5);
    ctx.stroke();
    ctx.restore();

    // ─────────────────────────────────────────────────────────────────────────
    // ESCALA HORARIA EXTERIOR (24 Números Romanos en el Perímetro Exterior)
    // ─────────────────────────────────────────────────────────────────────────
    const rOuterNums = rS + 18;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    for (let hIndex = 0; hIndex < 24; hIndex++) {
      const aTick = -Math.PI / 2 + (hIndex / 24) * Math.PI * 2;
      const romText = ROMAN_HOURS[hIndex % ROMAN_HOURS.length];
      const isCard = (hIndex % 6 === 0);

      ctx.save();
      ctx.translate(Math.cos(aTick) * rOuterNums, Math.sin(aTick) * rOuterNums);
      ctx.rotate(aTick + Math.PI / 2);
      ctx.fillStyle = isCard ? '#f6c445' : 'rgba(246, 196, 69, 0.5)';
      ctx.font = isCard ? '700 8.5px "Cinzel", serif' : '600 7px "Cinzel", serif';
      ctx.fillText(romText, 0, 0);
      ctx.restore();

      // Muesca exterior sutil
      const tick1 = rS + 4;
      const tick2 = rS + (isCard ? 10 : 7);
      ctx.strokeStyle = isCard ? 'rgba(246, 196, 69, 0.8)' : 'rgba(246, 196, 69, 0.25)';
      ctx.lineWidth = isCard ? 1.4 : 0.7;
      ctx.beginPath();
      ctx.moveTo(Math.cos(aTick) * tick1, Math.sin(aTick) * tick1);
      ctx.lineTo(Math.cos(aTick) * tick2, Math.sin(aTick) * tick2);
      ctx.stroke();
    }

    ctx.restore();
  }

  renderDialBoundary(ctx) {
    const r = this.radii.dialBoundary;
    ctx.save();

    // 1. Viñeta profunda tenebrista (Efecto cuenco cóncavo de astrolabio)
    const grad = ctx.createRadialGradient(0, 0, this.radii.core * 0.8, 0, 0, r + 70);
    grad.addColorStop(0, 'rgba(5, 7, 16, 0.2)');
    grad.addColorStop(0.65, 'rgba(4, 6, 14, 0.75)');
    grad.addColorStop(0.9, 'rgba(2, 3, 7, 0.95)');
    grad.addColorStop(1, 'rgba(0, 0, 0, 1.0)');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(0, 0, r + 70, 0, Math.PI * 2);
    ctx.fill();

    // 2. Anillo de Bronce y Oro Envejecido (Bisel Horológico Astrolabio)
    const rOuterBezel = r + 12;
    const bezelGrad = ctx.createRadialGradient(0, 0, r - 4, 0, 0, rOuterBezel);
    bezelGrad.addColorStop(0, '#1c1305');
    bezelGrad.addColorStop(0.3, '#78550f');
    bezelGrad.addColorStop(0.65, '#d4af37');
    bezelGrad.addColorStop(0.85, '#fff3b0');
    bezelGrad.addColorStop(1, '#2c1e09');

    ctx.strokeStyle = bezelGrad;
    ctx.lineWidth = 10;
    ctx.beginPath();
    ctx.arc(0, 0, r + 6, 0, Math.PI * 2);
    ctx.stroke();

    // 3. Biseles tallados dorados
    ctx.strokeStyle = 'rgba(246, 196, 69, 0.85)';
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.arc(0, 0, rOuterBezel, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = 'rgba(246, 196, 69, 0.5)';
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    ctx.arc(0, 0, r, 0, Math.PI * 2);
    ctx.stroke();

    // 4. Marcas de los 360 grados en el aro interior
    for (let deg = 0; deg < 360; deg++) {
      const rad = this.coordToAngle(deg);
      const isFive = deg % 5 === 0;
      const isTen = deg % 10 === 0;
      const len = isTen ? 9 : (isFive ? 5 : 2.5);

      const r1 = this.radii.degreeRing;
      const r2 = r1 - len;

      ctx.strokeStyle = isTen ? 'rgba(246, 196, 69, 0.8)' : (isFive ? 'rgba(246, 196, 69, 0.45)' : 'rgba(255, 255, 255, 0.15)');
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

      const isHighlight = this.hoveredItem && this.hoveredItem.tipo === 'planeta' &&
                          (this.hoveredItem.data.nombre === asp.p1 || this.hoveredItem.data.nombre === asp.p2);

      // Intensidad de la línea inversamente proporcional al orbe
      const baseAlpha = Math.max(0.2, 0.85 - (asp.orbe / 7.0));
      ctx.strokeStyle = asp.color;
      ctx.globalAlpha = isHighlight ? 1.0 : (this.hoveredItem ? 0.15 : baseAlpha);
      ctx.lineWidth = isHighlight ? 3.0 : ((asp.tipo === 'Conjunción' || asp.tipo === 'Oposición' || asp.tipo === 'Cuadratura') ? 1.8 : 1.2);

      if (isHighlight) {
        ctx.shadowColor = asp.color;
        ctx.shadowBlur = 12;
      } else {
        ctx.shadowBlur = 0;
      }

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }

    ctx.globalAlpha = 1.0;
    ctx.shadowBlur = 0;
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
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
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

      const isHovered = (this.hoveredItem && this.hoveredItem.tipo === 'planeta' && this.hoveredItem.data.nombre === p.nombre);

      // RETÍCULA DE BLOQUEO / HOVER ÁUREA PULSANTE
      if (isHovered) {
        ctx.save();
        const pulse = 1.0 + Math.sin(performance.now() * 0.006) * 0.12;
        ctx.strokeStyle = '#f6c445';
        ctx.lineWidth = 1.8;
        ctx.shadowColor = 'rgba(246, 196, 69, 0.9)';
        ctx.shadowBlur = 15;

        // Círculo exterior retícula
        ctx.beginPath();
        ctx.arc(px, py, 26 * pulse, 0, Math.PI * 2);
        ctx.stroke();

        // 4 Muescas tipo mira telescópica
        const tLen = 6;
        const rT = 26 * pulse;
        for (let i = 0; i < 4; i++) {
          const tAng = (i * Math.PI / 2) + (performance.now() * 0.001);
          ctx.beginPath();
          ctx.moveTo(px + Math.cos(tAng) * (rT - tLen), py + Math.sin(tAng) * (rT - tLen));
          ctx.lineTo(px + Math.cos(tAng) * (rT + tLen), py + Math.sin(tAng) * (rT + tLen));
          ctx.stroke();
        }
        ctx.restore();
      }

      // ── RENDERIZADO 3D TENEBRISTA DEL ORBE PLANETARIO ──────────────────────
      ctx.save();
      // 1. Sombra arrojada de profundidad
      ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
      ctx.shadowBlur = 12;
      ctx.shadowOffsetX = 3;
      ctx.shadowOffsetY = 5;

      // 2. Corona Atmosférica exterior
      const haloGrad = ctx.createRadialGradient(px, py, 14, px, py, isHovered ? 32 : 24);
      haloGrad.addColorStop(0, p.color);
      haloGrad.addColorStop(0.4, p.color + '44');
      haloGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = haloGrad;
      ctx.beginPath();
      ctx.arc(px, py, isHovered ? 32 : 24, 0, Math.PI * 2);
      ctx.fill();

      // 3. Esfera Metálica Sólida (Iluminada desde arriba a la izquierda: 3D Lit Sphere)
      const sphereGrad = ctx.createRadialGradient(px - 5, py - 5, 2, px, py, 17);
      sphereGrad.addColorStop(0, '#ffffff'); // Brillo especular
      sphereGrad.addColorStop(0.25, p.color); // Color vivo del astro
      sphereGrad.addColorStop(0.7, '#1e2029'); // Penumbra tenebrista
      sphereGrad.addColorStop(1, '#05060a'); // Sombra de oclusión

      ctx.fillStyle = sphereGrad;
      ctx.beginPath();
      ctx.arc(px, py, 16, 0, Math.PI * 2);
      ctx.fill();

      // Borde tallado metálico
      ctx.strokeStyle = isHovered ? '#ffffff' : p.color;
      ctx.lineWidth = isHovered ? 2.0 : 1.2;
      ctx.beginPath();
      ctx.arc(px, py, 16, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();

      // 4. Glifo del Planeta
      const glyph = GLYPHS[p.nombre] || '✦';
      ctx.fillStyle = '#ffffff';
      ctx.font = '800 16px "Outfit", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.shadowColor = '#000000';
      ctx.shadowBlur = 4;
      ctx.fillText(glyph, px, py - 0.5);
      ctx.shadowBlur = 0;

      // 5. Etiqueta nítida (Nombre + Grado)
      ctx.fillStyle = isHovered ? '#f6c445' : '#f1f5f9';
      ctx.font = isHovered ? '700 10.5px "Outfit", sans-serif' : '600 9px "Outfit", sans-serif';
      const labelY = py > 0 ? py + 24 : py - 24;
      ctx.fillText(`${p.nombre.slice(0, 3)} ${p.grado}°`, px, labelY);
    }

    ctx.restore();
  }

  renderAlchemicalCore(ctx) {
    const sun = this.calculated.planets['Sol'];
    ctx.save();

    // 1. Haz Solar Alquímico (Luz hacia el grado eclíptico donde transita el Sol)
    if (sun) {
      const aSun = this.coordToAngle(sun.grado_absoluto);
      const len = this.radii.planets - 18;
      const gradNeedle = ctx.createLinearGradient(0, 0, Math.cos(aSun) * len, Math.sin(aSun) * len);
      gradNeedle.addColorStop(0, 'rgba(246, 196, 69, 0.85)');
      gradNeedle.addColorStop(0.7, 'rgba(246, 196, 69, 0.35)');
      gradNeedle.addColorStop(1, 'rgba(255, 255, 255, 0.85)');

      ctx.strokeStyle = gradNeedle;
      ctx.lineWidth = 1.6;
      ctx.shadowColor = 'rgba(246, 196, 69, 0.6)';
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(Math.cos(aSun) * len, Math.sin(aSun) * len);
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    // 2. Núcleo Sagrado Alquímico (El Centro de la Carta Astral = La Tierra / El Observador Encarnado)
    // Radio reducido a 28px y semi-traslúcido para liberar el 100% de los aspectos euclidianos
    const rCore = this.radii.core;
    const coreGrad = ctx.createRadialGradient(0, 0, 2, 0, 0, rCore);
    coreGrad.addColorStop(0, 'rgba(246, 196, 69, 0.3)');
    coreGrad.addColorStop(0.55, 'rgba(10, 15, 28, 0.65)');
    coreGrad.addColorStop(1, 'rgba(3, 5, 12, 0.85)');

    ctx.fillStyle = coreGrad;
    ctx.beginPath();
    ctx.arc(0, 0, rCore, 0, Math.PI * 2);
    ctx.fill();

    // Anillo de filigrana áurea
    ctx.strokeStyle = 'rgba(246, 196, 69, 0.8)';
    ctx.lineWidth = 1.2;
    ctx.shadowColor = 'rgba(246, 196, 69, 0.5)';
    ctx.shadowBlur = 6;
    ctx.beginPath();
    ctx.arc(0, 0, rCore, 0, Math.PI * 2);
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Glifo Sagrado de la Tierra (El Observador / Punto Cero Alquímico ⊕)
    ctx.fillStyle = '#f6c445';
    ctx.font = '700 13px "Cinzel", serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('⊕', 0, 0);

    ctx.restore();
  }
}

// Inicializar cuando el DOM esté listo
window.addEventListener('DOMContentLoaded', () => {
  window.relojEngine = new RelojAstrologicoEngine();
});
