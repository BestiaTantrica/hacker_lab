/**
 * app.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Motor Cinemático Vectorial Bi-Wheel para Navegación Astrológica Interactiva.
 * Versión 2.0:
 *   - Separación angular y agujas indicadoras para planetas en conjunción estrecha.
 *   - Nombres completos legibles en cápsulas de alto contraste junto a cada astro.
 *   - Ficha y selector lateral con pestañas organizadas (Natales / RS / Casas) sin compresión.
 *   - Hit-testing de precisión al píxel sobre las posiciones desplegadas.
 * ─────────────────────────────────────────────────────────────────────────────
 */

// 1. Constantes Astrológicas y Glifos
const ZODIAC_SIGNS = [
  { nombre: "Aries", simbolo: "♈", elemento: "Fuego", color: "#ef4444" },
  { nombre: "Tauro", simbolo: "♉", elemento: "Tierra", color: "#10b981" },
  { nombre: "Géminis", simbolo: "♊", elemento: "Aire", color: "#f59e0b" },
  { nombre: "Cáncer", simbolo: "♋", elemento: "Agua", color: "#3b82f6" },
  { nombre: "Leo", simbolo: "♌", elemento: "Fuego", color: "#f97316" },
  { nombre: "Virgo", simbolo: "♍", elemento: "Tierra", color: "#059669" },
  { nombre: "Libra", simbolo: "♎", elemento: "Aire", color: "#eab308" },
  { nombre: "Escorpio", simbolo: "♏", elemento: "Agua", color: "#0284c7" },
  { nombre: "Sagitario", simbolo: "♐", elemento: "Fuego", color: "#dc2626" },
  { nombre: "Capricornio", simbolo: "♑", elemento: "Tierra", color: "#047857" },
  { nombre: "Acuario", simbolo: "♒", elemento: "Aire", color: "#d97706" },
  { nombre: "Piscis", simbolo: "♓", elemento: "Agua", color: "#2563eb" }
];

const GLYPHS = {
  'Sol': '☉', 'Luna': '☽', 'Mercurio': '☿', 'Venus': '♀', 'Marte': '♂',
  'Júpiter': '♃', 'Saturno': '♄', 'Urano': '♅', 'Neptuno': '♆', 'Plutón': '♇',
  'Quirón': '⚷', 'Nodo Norte': '☊', 'Lilith': '⚸'
};

const ASPECT_COLORS = {
  'Conjunción': '#f1c40f',
  'Oposición': '#ef4444',
  'Trígono': '#38bdf8',
  'Cuadratura': '#f97316',
  'Sextil': '#34d399'
};

class AstroNavigator {
  constructor() {
    this.canvas = document.getElementById('astro-canvas');
    this.ctx = this.canvas.getContext('2d');
    this.container = document.getElementById('canvas-wrapper');

    // Datos Astrológicos (Cargados desde data_tomas.js)
    this.data = DATOS_ASTRO;
    this.natal = this.data.carta_natal;
    this.rs = this.data.revolucion_solar;
    this.ascDeg = this.natal.angulos.Ascendente.grado_absoluto; // 321.9035° (Acuario 21°54')

    // Modos de visualización: 'natal', 'transicion', 'biwheel'
    this.mode = 'biwheel';
    this.transitionProgress = 1.0;

    // Radios del Mandala (espacio virtual centrado en 0, 0)
    this.radii = {
      core: 150,
      aspects: 210,
      natalPlanets: 275,
      natalHouses: 335,
      zodiacInner: 345,
      zodiacOuter: 435,
      rsHouses: 445,
      rsPlanets: 515,
      boundary: 600
    };

    // Calcular distribución anti-colisión con agujas para natales y RS
    this.natalLayout = this.computePlanetLayout(this.natal.planetas, this.radii.natalPlanets, this.radii.zodiacInner);
    this.rsLayout = this.computePlanetLayout(this.rs.planetas_rs, this.radii.rsPlanets, this.radii.zodiacOuter);

    // Cámara Virtual (x, y en coords virtuales, zoom multiplicador)
    this.camera = { x: 0, y: 0, zoom: 1.0 };
    this.targetCamera = { x: 0, y: 0, zoom: 1.0 };

    // Interacción de Arrastre (Pan)
    this.isDragging = false;
    this.dragStart = { x: 0, y: 0 };
    this.cameraStart = { x: 0, y: 0 };

    // Selección e Inspección
    this.selectedTarget = null;
    this.hoverTarget = null;
    this.tourRunning = false;
    this.tourStep = 0;

    // Inicializaciones
    this.initCanvasSize();
    this.initEvents();
    this.initUI();
    this.animate();
  }

  initCanvasSize() {
    const dpr = window.devicePixelRatio || 1;
    this.width = this.container.clientWidth;
    this.height = this.container.clientHeight;
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.scale(dpr, dpr);
  }

  // Conversión canónica: Ascendente a 180° (izquierda), avance antihorario
  degToRad(deg) {
    const relDeg = (deg - this.ascDeg + 360) % 360;
    return (180 + relDeg) * Math.PI / 180;
  }

  polarToXY(rad, r) {
    return {
      x: r * Math.cos(rad),
      y: -r * Math.sin(rad) // Coordenada Y invertida para avance antihorario
    };
  }

  drawRoundedRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  }

  // Algoritmo de Separación Anti-Colisión y Agujas Indicadoras
  computePlanetLayout(planetsDict, baseRadius, anchorRadius) {
    if (!planetsDict) return [];
    const entries = Object.entries(planetsDict).map(([nombre, p]) => ({
      nombre,
      data: p,
      exactDeg: p.grado_absoluto
    }));

    // Ordenar por grado absoluto
    entries.sort((a, b) => a.exactDeg - b.exactDeg);

    // Agrupar en clusters si la distancia angular es menor a 8.5°
    const clusters = [];
    let currentCluster = [];

    for (let i = 0; i < entries.length; i++) {
      const p = entries[i];
      if (currentCluster.length === 0) {
        currentCluster.push(p);
      } else {
        const prev = currentCluster[currentCluster.length - 1];
        let diff = Math.abs(p.exactDeg - prev.exactDeg);
        if (diff > 180) diff = 360 - diff;
        if (diff < 8.5) {
          currentCluster.push(p);
        } else {
          clusters.push(currentCluster);
          currentCluster = [p];
        }
      }
    }
    if (currentCluster.length > 0) {
      clusters.push(currentCluster);
    }

    const layout = [];
    for (const cluster of clusters) {
      const N = cluster.length;
      if (N === 1) {
        const p = cluster[0];
        const rad = this.degToRad(p.exactDeg);
        const pos = this.polarToXY(rad, baseRadius);
        layout.push({
          nombre: p.nombre,
          data: p.data,
          exactDeg: p.exactDeg,
          dispDeg: p.exactDeg,
          radius: baseRadius,
          displayPos: pos,
          exactPos: pos,
          hasNeedle: false
        });
      } else {
        // Desplazar tangencialmente en abanico
        const step = 7.0; // grados de separación
        for (let k = 0; k < N; k++) {
          const p = cluster[k];
          const offsetAngle = (k - (N - 1) / 2) * step;
          const dispDeg = (p.exactDeg + offsetAngle + 360) % 360;
          // Alternar radio sutilmente para máximo despeje
          const r = (k % 2 === 0) ? baseRadius - 12 : baseRadius + 14;
          const radExact = this.degToRad(p.exactDeg);
          const radDisp = this.degToRad(dispDeg);

          const exactAnchorPos = this.polarToXY(radExact, anchorRadius);
          const displayPos = this.polarToXY(radDisp, r);

          layout.push({
            nombre: p.nombre,
            data: p.data,
            exactDeg: p.exactDeg,
            dispDeg: dispDeg,
            radius: r,
            displayPos: displayPos,
            exactPos: exactAnchorPos,
            hasNeedle: true
          });
        }
      }
    }
    return layout;
  }

  // Conversión entre Coordenadas de Pantalla y Coordenadas Virtuales
  screenToVirtual(screenX, screenY) {
    const cx = this.width / 2;
    const cy = this.height / 2;
    const scale = (Math.min(this.width, this.height) / 1200) * this.camera.zoom;
    return {
      x: (screenX - cx) / scale + this.camera.x,
      y: (screenY - cy) / scale + this.camera.y
    };
  }

  virtualToScreen(vx, vy) {
    const cx = this.width / 2;
    const cy = this.height / 2;
    const scale = (Math.min(this.width, this.height) / 1200) * this.camera.zoom;
    return {
      x: cx + (vx - this.camera.x) * scale,
      y: cy + (vy - this.camera.y) * scale
    };
  }

  flyTo(vx, vy, zoom = 2.2) {
    this.targetCamera.x = vx;
    this.targetCamera.y = vy;
    this.targetCamera.zoom = zoom;
    document.getElementById('zoom-indicator').innerText = zoom.toFixed(1) + 'x';
  }

  resetCamera() {
    this.flyTo(0, 0, 1.0);
  }

  // 3. Manejo de Eventos
  initEvents() {
    window.addEventListener('resize', () => this.initCanvasSize());

    // Mouse Pan
    this.canvas.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      this.dragStart = { x: e.clientX, y: e.clientY };
      this.cameraStart = { x: this.camera.x, y: this.camera.y };
    });

    window.addEventListener('mousemove', (e) => {
      if (this.isDragging) {
        const scale = (Math.min(this.width, this.height) / 1200) * this.camera.zoom;
        const dx = (e.clientX - this.dragStart.x) / scale;
        const dy = (e.clientY - this.dragStart.y) / scale;
        this.targetCamera.x = this.cameraStart.x - dx;
        this.targetCamera.y = this.cameraStart.y - dy;
      } else {
        this.handleHover(e.clientX, e.clientY);
      }
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });

    // Atajos de teclado
    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space') {
        e.preventDefault();
        document.getElementById('btn-nav-tour').click();
      } else if (e.key === 'r' || e.key === 'R') {
        this.resetCamera();
      } else if (e.key === '1') {
        document.getElementById('btn-mode-natal').click();
      } else if (e.key === '2') {
        document.getElementById('btn-mode-trans').click();
      } else if (e.key === '3') {
        document.getElementById('btn-mode-biwheel').click();
      }
    });

    // Zoom con Rueda
    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
      let newZoom = this.targetCamera.zoom * zoomFactor;
      newZoom = Math.max(0.6, Math.min(newZoom, 5.0));
      this.targetCamera.zoom = newZoom;
      document.getElementById('zoom-indicator').innerText = newZoom.toFixed(1) + 'x';
    }, { passive: false });

    // Click para seleccionar e inspeccionar astro
    this.canvas.addEventListener('click', (e) => {
      const vpos = this.screenToVirtual(e.clientX, e.clientY);
      const clicked = this.findAstroAt(vpos.x, vpos.y);
      if (clicked) {
        this.selectTarget(clicked);
        this.flyTo(clicked.x, clicked.y, 2.3);
      }
    });
  }

  // Detección de Colisiones precisa sobre displayPos
  findAstroAt(vx, vy) {
    const hitRadius = 26 / this.camera.zoom;
    const candidates = [];

    // Planetas Natales
    for (const item of this.natalLayout) {
      const dist = Math.hypot(vx - item.displayPos.x, vy - item.displayPos.y);
      if (dist < hitRadius) {
        candidates.push({ type: 'natal', nombre: item.nombre, data: item.data, x: item.displayPos.x, y: item.displayPos.y });
      }
    }

    // Planetas RS (si están activos)
    if (this.mode !== 'natal') {
      for (const item of this.rsLayout) {
        const dist = Math.hypot(vx - item.displayPos.x, vy - item.displayPos.y);
        if (dist < hitRadius) {
          candidates.push({ type: 'rs', nombre: item.nombre, data: item.data, x: item.displayPos.x, y: item.displayPos.y });
        }
      }
    }

    return candidates.length > 0 ? candidates[0] : null;
  }

  handleHover(screenX, screenY) {
    const vpos = this.screenToVirtual(screenX, screenY);
    const hit = this.findAstroAt(vpos.x, vpos.y);
    const tooltip = document.getElementById('hover-tooltip');

    if (hit) {
      this.hoverTarget = hit;
      this.canvas.style.cursor = 'pointer';
      tooltip.style.opacity = '1';
      tooltip.style.left = `${screenX + 16}px`;
      tooltip.style.top = `${screenY + 16}px`;
      const badge = hit.type === 'natal' ? '☉ Natal' : '🌀 Retorno Solar';
      tooltip.innerHTML = `<strong>${GLYPHS[hit.nombre] || '★'} ${hit.nombre}</strong> (${badge})<br>${hit.data.formato}`;
    } else {
      this.hoverTarget = null;
      this.canvas.style.cursor = this.isDragging ? 'grabbing' : 'grab';
      tooltip.style.opacity = '0';
    }
  }

  selectTarget(target) {
    this.selectedTarget = target;
    const panel = document.getElementById('inspector-panel');
    panel.classList.remove('collapsed');

    const icon = document.getElementById('target-icon');
    icon.className = `target-orb ${target.type}`;
    icon.innerText = GLYPHS[target.nombre] || '★';

    document.getElementById('target-name').innerText = `${target.nombre} (${target.type === 'natal' ? 'Natal 1982' : 'Retorno Solar 2026'})`;
    document.getElementById('target-pos').innerText = `${target.data.formato} • Casa ${target.data.casa || target.data.casa_rs}`;
    document.getElementById('det-elem').innerText = `${target.data.elemento} • ${target.data.modalidad}`;
    document.getElementById('det-grado').innerText = `${target.data.grado_absoluto.toFixed(2)}°`;

    const superpRow = document.getElementById('det-superp-row');
    if (target.data.casa_natal) {
      superpRow.style.display = 'flex';
      document.getElementById('det-superp').innerText = `Casa ${target.data.casa_natal} Natal`;
    } else {
      superpRow.style.display = 'none';
    }
  }

  // 4. Inicialización de UI y Controles
  initUI() {
    // Mode Switcher
    document.getElementById('btn-mode-natal').addEventListener('click', (e) => this.setMode('natal', e.target));
    document.getElementById('btn-mode-trans').addEventListener('click', (e) => this.setMode('transicion', e.target));
    document.getElementById('btn-mode-biwheel').addEventListener('click', (e) => this.setMode('biwheel', e.target));

    // Nav Dock Presets
    document.getElementById('btn-nav-general').addEventListener('click', () => this.resetCamera());

    document.getElementById('btn-nav-asc').addEventListener('click', () => {
      const pos = this.polarToXY(this.degToRad(this.ascDeg), this.radii.zodiacInner);
      this.flyTo(pos.x, pos.y, 2.2);
    });

    document.getElementById('btn-nav-sol').addEventListener('click', () => {
      const sol = this.natalLayout.find(i => i.nombre === 'Sol');
      if (sol) {
        this.selectTarget({ type: 'natal', nombre: 'Sol', data: sol.data, x: sol.displayPos.x, y: sol.displayPos.y });
        this.flyTo(sol.displayPos.x, sol.displayPos.y, 2.4);
      }
    });

    document.getElementById('btn-nav-portal-rs').addEventListener('click', () => {
      if (this.mode === 'natal') this.setMode('biwheel', document.getElementById('btn-mode-biwheel'));
      const ascRS = this.rs.angulos_rs.Ascendente_RS;
      const pos = this.polarToXY(this.degToRad(ascRS.grado_absoluto), this.radii.rsPlanets);
      this.flyTo(pos.x, pos.y, 2.4);
    });

    document.getElementById('btn-nav-luna-rs').addEventListener('click', () => {
      if (this.mode === 'natal') this.setMode('biwheel', document.getElementById('btn-mode-biwheel'));
      const luna = this.rsLayout.find(i => i.nombre === 'Luna');
      if (luna) {
        this.selectTarget({ type: 'rs', nombre: 'Luna', data: luna.data, x: luna.displayPos.x, y: luna.displayPos.y });
        this.flyTo(luna.displayPos.x, luna.displayPos.y, 2.4);
      }
    });

    document.getElementById('btn-nav-tour').addEventListener('click', () => this.startCinematicTour());

    // Zoom Controls
    document.getElementById('btn-zoom-in').addEventListener('click', () => {
      this.targetCamera.zoom = Math.min(5.0, this.targetCamera.zoom * 1.3);
      document.getElementById('zoom-indicator').innerText = this.targetCamera.zoom.toFixed(1) + 'x';
    });
    document.getElementById('btn-zoom-out').addEventListener('click', () => {
      this.targetCamera.zoom = Math.max(0.6, this.targetCamera.zoom * 0.77);
      document.getElementById('zoom-indicator').innerText = this.targetCamera.zoom.toFixed(1) + 'x';
    });
    document.getElementById('btn-zoom-reset').addEventListener('click', () => this.resetCamera());

    // Inspector
    const inspector = document.getElementById('inspector-panel');
    document.getElementById('btn-toggle-inspector').addEventListener('click', () => {
      inspector.classList.toggle('collapsed');
    });
    document.getElementById('btn-close-inspector').addEventListener('click', () => {
      inspector.classList.add('collapsed');
    });

    // Category Tabs in Inspector
    const tabBtns = document.querySelectorAll('.cat-tab-btn');
    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const tab = btn.dataset.tab;
        document.querySelectorAll('.cat-tab-pane').forEach(p => p.classList.remove('active'));
        const pane = document.getElementById(`pane-${tab}`);
        if (pane) pane.classList.add('active');
      });
    });

    // Populate Jump Lists as Cards
    this.populateJumpLists();
  }

  setMode(mode, targetBtn) {
    this.mode = mode;
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
    targetBtn.closest('.mode-btn').classList.add('active');

    if (mode === 'transicion') {
      this.transitionProgress = 0.0;
      this.resetCamera();
    } else if (mode === 'natal') {
      this.transitionProgress = 0.0;
      document.getElementById('legend-rs').style.opacity = '0.3';
    } else {
      this.transitionProgress = 1.0;
      document.getElementById('legend-rs').style.opacity = '1.0';
    }
  }

  populateJumpLists() {
    // Jump Natal
    const jumpNatal = document.getElementById('jump-natal-planets');
    jumpNatal.innerHTML = '';
    for (const item of this.natalLayout) {
      const { nombre, data, displayPos } = item;
      const card = document.createElement('div');
      card.className = 'jump-card';
      card.innerHTML = `
        <div class="left-info">
          <span class="glyph" style="color:var(--gold-primary);">${GLYPHS[nombre] || '★'}</span>
          <span>${nombre}</span>
        </div>
        <span class="right-pos">${data.formato} • C${data.casa}</span>
      `;
      card.onclick = () => {
        this.selectTarget({ type: 'natal', nombre, data, x: displayPos.x, y: displayPos.y });
        this.flyTo(displayPos.x, displayPos.y, 2.3);
      };
      jumpNatal.appendChild(card);
    }

    // Jump RS
    const jumpRS = document.getElementById('jump-rs-planets');
    jumpRS.innerHTML = '';
    for (const item of this.rsLayout) {
      const { nombre, data, displayPos } = item;
      const card = document.createElement('div');
      card.className = 'jump-card';
      card.innerHTML = `
        <div class="left-info">
          <span class="glyph" style="color:var(--cyan-primary);">${GLYPHS[nombre] || '★'}</span>
          <span>${nombre}</span>
        </div>
        <span class="right-pos">${data.formato} • C${data.casa_rs || data.casa}</span>
      `;
      card.onclick = () => {
        if (this.mode === 'natal') this.setMode('biwheel', document.getElementById('btn-mode-biwheel'));
        this.selectTarget({ type: 'rs', nombre, data, x: displayPos.x, y: displayPos.y });
        this.flyTo(displayPos.x, displayPos.y, 2.3);
      };
      jumpRS.appendChild(card);
    }

    // Jump Houses
    const jumpHouses = document.getElementById('jump-houses');
    jumpHouses.innerHTML = '';
    for (let h = 1; h <= 12; h++) {
      const c = this.natal.casas[`Casa ${h}`];
      const card = document.createElement('div');
      card.className = 'jump-card';
      card.innerHTML = `
        <div class="left-info">
          <span class="glyph" style="color:#cbd5e1;">🏛️</span>
          <span>Casa ${h}</span>
        </div>
        <span class="right-pos">${c.formato}</span>
      `;
      card.onclick = () => {
        const pos = this.polarToXY(this.degToRad(c.grado_absoluto), (this.radii.natalHouses + this.radii.core) / 2);
        this.flyTo(pos.x, pos.y, 2.1);
      };
      jumpHouses.appendChild(card);
    }
  }

  startCinematicTour() {
    this.tourRunning = true;
    this.tourStep = 0;
    const tourPoints = [
      { name: "Plano General", fn: () => this.resetCamera(), wait: 3500 },
      { name: "Ascendente Natal", fn: () => document.getElementById('btn-nav-asc').click(), wait: 4000 },
      { name: "Sol en Aries", fn: () => document.getElementById('btn-nav-sol').click(), wait: 4000 },
      { name: "Portal RS en Libra", fn: () => document.getElementById('btn-nav-portal-rs').click(), wait: 4500 },
      { name: "Luna RS en Acuario", fn: () => document.getElementById('btn-nav-luna-rs').click(), wait: 4000 },
      { name: "Vuelta a Plano General", fn: () => this.resetCamera(), wait: 3000 }
    ];

    const runNext = () => {
      if (!this.tourRunning) return;
      if (this.tourStep >= tourPoints.length) {
        this.tourRunning = false;
        return;
      }
      const pt = tourPoints[this.tourStep];
      pt.fn();
      this.tourStep++;
      setTimeout(runNext, pt.wait);
    };

    runNext();
  }

  // 5. Motor de Renderizado en Tiempo Real (Canvas 2D @ 60 FPS)
  animate() {
    this.camera.x += (this.targetCamera.x - this.camera.x) * 0.08;
    this.camera.y += (this.targetCamera.y - this.camera.y) * 0.08;
    this.camera.zoom += (this.targetCamera.zoom - this.camera.zoom) * 0.08;

    if (this.mode === 'transicion' && this.transitionProgress < 1.0) {
      this.transitionProgress = Math.min(1.0, this.transitionProgress + 0.008);
    }

    try {
      this.render();
    } catch (err) {
      console.error("Render loop error:", err);
    }
    requestAnimationFrame(() => this.animate());
  }

  render() {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;

    ctx.clearRect(0, 0, w, h);

    // Fondo Cósmico Espacial Limpio
    const bgGrad = ctx.createRadialGradient(w / 2, h / 2, 50, w / 2, h / 2, Math.max(w, h) * 0.7);
    bgGrad.addColorStop(0, '#0a1022');
    bgGrad.addColorStop(0.5, '#050711');
    bgGrad.addColorStop(1, '#020307');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    // Matriz de Transformación Cinemática
    ctx.save();
    const cx = w / 2;
    const cy = h / 2;
    const scale = (Math.min(w, h) / 1200) * this.camera.zoom;

    ctx.translate(cx, cy);
    ctx.scale(scale, scale);
    ctx.translate(-this.camera.x, -this.camera.y);

    // Dibujar capas
    this.drawBackgroundRings(ctx);
    this.drawAspectsEuclidean(ctx);
    this.drawNatalHouses(ctx);
    this.drawZodiacRing(ctx);
    this.drawNatalPlanets(ctx);

    if (this.mode !== 'natal') {
      const alpha = this.mode === 'transicion' ? this.transitionProgress : 1.0;
      this.drawSolarReturnRing(ctx, alpha);
    }

    this.drawMainAxes(ctx);
    this.drawTargetReticle(ctx);

    ctx.restore();
  }

  drawBackgroundRings(ctx) {
    ctx.save();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
    ctx.lineWidth = 1;

    ctx.beginPath();
    ctx.arc(0, 0, this.radii.aspects, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(8, 12, 24, 0.7)';
    ctx.fill();
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(0, 0, this.radii.zodiacOuter, 0, Math.PI * 2);
    ctx.stroke();

    ctx.restore();
  }

  // 1. Aspectos Euclidianos Rectos (Color Base Reforzado y Neón al Seleccionar)
  drawAspectsEuclidean(ctx) {
    const aspectos = this.natal.aspectos;
    if (!aspectos) return;

    ctx.save();

    for (const asp of aspectos) {
      const p1 = this.natal.planetas[asp.cuerpo1];
      const p2 = this.natal.planetas[asp.cuerpo2];
      if (!p1 || !p2) continue;

      const pos1 = this.polarToXY(this.degToRad(p1.grado_absoluto), this.radii.aspects - 6);
      const pos2 = this.polarToXY(this.degToRad(p2.grado_absoluto), this.radii.aspects - 6);

      const isHighlighted = (this.selectedTarget && 
        (this.selectedTarget.nombre === asp.cuerpo1 || this.selectedTarget.nombre === asp.cuerpo2));

      ctx.beginPath();
      ctx.moveTo(pos1.x, pos1.y);
      ctx.lineTo(pos2.x, pos2.y);

      if (isHighlighted) {
        ctx.strokeStyle = ASPECT_COLORS[asp.aspecto] || '#fff';
        ctx.lineWidth = 3.2;
        ctx.shadowColor = ctx.strokeStyle;
        ctx.shadowBlur = 14;
        ctx.globalAlpha = 1.0;
        ctx.stroke();
      } else {
        const color = ASPECT_COLORS[asp.aspecto] || '#94a3b8';
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.6;
        ctx.globalAlpha = 0.40; // Color más fuerte y definido como pidió el usuario
        ctx.stroke();
        ctx.globalAlpha = 1.0;
      }
    }
    ctx.restore();
  }

  // 2. Casas Natales (Números Destacados y Ejes Visibles)
  drawNatalHouses(ctx) {
    ctx.save();
    for (let h = 1; h <= 12; h++) {
      const c = this.natal.casas[`Casa ${h}`];
      if (!c) continue;

      const rad = this.degToRad(c.grado_absoluto);
      const isAngle = (h === 1 || h === 4 || h === 7 || h === 10);

      const pInner = this.polarToXY(rad, this.radii.aspects);
      const pOuter = this.polarToXY(rad, this.radii.zodiacInner);

      ctx.beginPath();
      ctx.moveTo(pInner.x, pInner.y);
      ctx.lineTo(pOuter.x, pOuter.y);

      if (isAngle) {
        ctx.strokeStyle = h === 1 ? '#f6c445' : 'rgba(246, 196, 69, 0.75)';
        ctx.lineWidth = h === 1 ? 2.8 : 1.8;
      } else {
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.16)';
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
      }
      ctx.stroke();
      ctx.setLineDash([]);

      const nextH = h === 12 ? 1 : h + 1;
      const nextC = this.natal.casas[`Casa ${nextH}`];
      if (nextC) {
        let diff = (nextC.grado_absoluto - c.grado_absoluto);
        if (diff < 0) diff += 360;
        const midDeg = c.grado_absoluto + diff / 2;
        const midRad = this.degToRad(midDeg);

        const pNum = this.polarToXY(midRad, (this.radii.aspects + this.radii.natalPlanets) / 2 - 4);

        // Chapa / círculo contenedor para que los números de casas se lean sin problema
        ctx.beginPath();
        ctx.arc(pNum.x, pNum.y, 11, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.lineWidth = 1;
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#f1f5f9';
        ctx.font = '700 12px Outfit, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(h.toString(), pNum.x, pNum.y);
      }
    }
    ctx.restore();
  }

  // 3. Anillo Zodiacal Canónico (Continuo sin bugs de 360°, Glifos + Nombres Completos)
  drawZodiacRing(ctx) {
    ctx.save();
    const rIn = this.radii.zodiacInner;
    const rOut = this.radii.zodiacOuter;
    const rMid = (rIn + rOut) / 2;

    for (let i = 0; i < 12; i++) {
      const sign = ZODIAC_SIGNS[i];
      const degCenter = i * 30 + 15;

      // Ángulo relativo continuo normalizado [-180, +180] para evitar discontinuidades
      let diffCenter = (degCenter - this.ascDeg) % 360;
      if (diffCenter < -180) diffCenter += 360;
      if (diffCenter > 180) diffCenter -= 360;

      const radMid = (180 + diffCenter) * Math.PI / 180;
      const radS = radMid - (15 * Math.PI / 180);
      const radE = radMid + (15 * Math.PI / 180);

      // Sector circular
      ctx.beginPath();
      ctx.arc(0, 0, rOut, -radS, -radE, true);
      ctx.arc(0, 0, rIn, -radE, -radS, false);
      ctx.closePath();
      ctx.fillStyle = (i % 2 === 0) ? 'rgba(15, 23, 42, 0.65)' : 'rgba(10, 16, 32, 0.5)';
      ctx.fill();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Líneas divisorias de signos
      const pDivIn = this.polarToXY(radS, rIn);
      const pDivOut = this.polarToXY(radS, rOut);
      ctx.beginPath();
      ctx.moveTo(pDivIn.x, pDivIn.y);
      ctx.lineTo(pDivOut.x, pDivOut.y);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
      ctx.lineWidth = 1.2;
      ctx.stroke();

      // Ticks de grados dentro del signo
      for (let d = 5; d < 30; d += 5) {
        const radTick = radS + (d * Math.PI / 180);
        const tickLength = (d === 15) ? 11 : 6;
        const p1 = this.polarToXY(radTick, rIn);
        const p2 = this.polarToXY(radTick, rIn + tickLength);
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = (d === 15) ? 'rgba(255, 255, 255, 0.35)' : 'rgba(255, 255, 255, 0.14)';
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      // Símbolo Glifo Zodiacal (Agrandado a 22px con resplandor cromático)
      const pGlyph = this.polarToXY(radMid, rMid - 11);
      ctx.fillStyle = sign.color;
      ctx.font = '700 22px "Segoe UI Symbol", Outfit, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.shadowColor = sign.color;
      ctx.shadowBlur = 10;
      ctx.fillText(sign.simbolo, pGlyph.x, pGlyph.y);
      ctx.shadowBlur = 0;

      // Nombre del Signo en mayúsculas legible
      const pName = this.polarToXY(radMid, rMid + 14);
      ctx.fillStyle = '#f1f5f9';
      ctx.font = '700 11px Outfit, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
      ctx.shadowBlur = 4;
      ctx.fillText(sign.nombre.toUpperCase(), pName.x, pName.y);
      ctx.shadowBlur = 0;
    }
    ctx.restore();
  }

  // 3b. Ejes Cardinales Principales con Badges Destacados (Ascendente, Descendente, MC, IC)
  drawMainAxes(ctx) {
    ctx.save();

    // 1. Eje del Horizonte: Ascendente (180° a la izquierda) y Descendente (0° a la derecha)
    const rStart = this.radii.aspects - 2;
    const rEnd = this.radii.rsPlanets + 25;

    // Línea Ascendente (180°)
    const pAscIn = this.polarToXY(Math.PI, rStart);
    const pAscOut = this.polarToXY(Math.PI, rEnd);
    ctx.beginPath();
    ctx.moveTo(pAscIn.x, pAscIn.y);
    ctx.lineTo(pAscOut.x, pAscOut.y);
    ctx.strokeStyle = '#f6c445';
    ctx.lineWidth = 3.0;
    ctx.shadowColor = '#f6c445';
    ctx.shadowBlur = 12;
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Badge Flotante del Ascendente
    const ascBadgeX = pAscOut.x - 120;
    const ascBadgeY = pAscOut.y;
    ctx.fillStyle = 'rgba(10, 16, 32, 0.95)';
    ctx.strokeStyle = '#f6c445';
    ctx.lineWidth = 2;
    this.drawRoundedRect(ctx, ascBadgeX - 105, ascBadgeY - 14, 210, 28, 6);
    ctx.shadowColor = 'rgba(246, 196, 69, 0.5)';
    ctx.shadowBlur = 10;
    ctx.fill();
    ctx.stroke();
    ctx.shadowBlur = 0;

    ctx.fillStyle = '#ffe270';
    ctx.font = '800 12px Outfit, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('◀ ASC: ♒ ACUARIO 21° 54\'', ascBadgeX, ascBadgeY);

    // Línea Descendente (0° / 360°)
    const pDscIn = this.polarToXY(0, rStart);
    const pDscOut = this.polarToXY(0, rEnd);
    ctx.beginPath();
    ctx.moveTo(pDscIn.x, pDscIn.y);
    ctx.lineTo(pDscOut.x, pDscOut.y);
    ctx.strokeStyle = 'rgba(246, 196, 69, 0.7)';
    ctx.lineWidth = 2.0;
    ctx.stroke();

    // Badge Descendente
    const dscBadgeX = pDscOut.x + 105;
    const dscBadgeY = pDscOut.y;
    ctx.fillStyle = 'rgba(10, 16, 32, 0.92)';
    ctx.strokeStyle = 'rgba(246, 196, 69, 0.6)';
    ctx.lineWidth = 1.5;
    this.drawRoundedRect(ctx, dscBadgeX - 95, dscBadgeY - 13, 190, 26, 6);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#fbbf24';
    ctx.font = '700 11px Outfit, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('DSC: ♌ LEO 21° 54\' ▶', dscBadgeX, dscBadgeY);

    // 2. Eje del Meridiano: Medio Cielo (MC) y Fondo de Cielo (IC)
    const mcDeg = this.natal.angulos["Medio Cielo"].grado_absoluto;
    const radMC = this.degToRad(mcDeg);
    const pMcIn = this.polarToXY(radMC, rStart);
    const pMcOut = this.polarToXY(radMC, rEnd);
    ctx.beginPath();
    ctx.moveTo(pMcIn.x, pMcIn.y);
    ctx.lineTo(pMcOut.x, pMcOut.y);
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2.2;
    ctx.shadowColor = '#38bdf8';
    ctx.shadowBlur = 10;
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Badge MC
    const pMcBadge = this.polarToXY(radMC, rEnd + 26);
    ctx.fillStyle = 'rgba(10, 16, 32, 0.92)';
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 1.5;
    this.drawRoundedRect(ctx, pMcBadge.x - 90, pMcBadge.y - 13, 180, 26, 6);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#38bdf8';
    ctx.font = '700 11px Outfit, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('▲ MC: ♏ ESCORPIO 16° 40\'', pMcBadge.x, pMcBadge.y);

    // IC (Fondo de Cielo)
    const icDeg = this.natal.angulos["Fondo Cielo"].grado_absoluto;
    const radIC = this.degToRad(icDeg);
    const pIcIn = this.polarToXY(radIC, rStart);
    const pIcOut = this.polarToXY(radIC, rEnd);
    ctx.beginPath();
    ctx.moveTo(pIcIn.x, pIcIn.y);
    ctx.lineTo(pIcOut.x, pIcOut.y);
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.6)';
    ctx.lineWidth = 1.8;
    ctx.stroke();

    const pIcBadge = this.polarToXY(radIC, rEnd + 26);
    ctx.fillStyle = 'rgba(10, 16, 32, 0.92)';
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.5)';
    ctx.lineWidth = 1.5;
    this.drawRoundedRect(ctx, pIcBadge.x - 85, pIcBadge.y - 13, 170, 26, 6);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#93c5fd';
    ctx.font = '700 11px Outfit, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('▼ IC: ♉ TAURO 16° 40\'', pIcBadge.x, pIcBadge.y);

    ctx.restore();
  }

  // 4. Planetas Natales (Con Agujas Indicadoras y Nombres Completos Legibles)
  // 4. Planetas Natales (Orbes 22px, Glifos 20px, Badges 12px con Agujas Indicadoras)
  drawNatalPlanets(ctx) {
    ctx.save();
    for (const item of this.natalLayout) {
      const { displayPos, exactPos, hasNeedle, nombre, data, dispDeg } = item;
      const rad = this.degToRad(dispDeg);

      // Si fue separado para evitar superposición, dibujar aguja fina hacia el grado real
      if (hasNeedle) {
        ctx.beginPath();
        ctx.moveTo(exactPos.x, exactPos.y);
        ctx.lineTo(displayPos.x, displayPos.y);
        ctx.strokeStyle = 'rgba(246, 196, 69, 0.6)';
        ctx.lineWidth = 1.2;
        ctx.setLineDash([3, 3]);
        ctx.stroke();
        ctx.setLineDash([]);

        // Punto de referencia en el grado zodiacal exacto
        ctx.beginPath();
        ctx.arc(exactPos.x, exactPos.y, 3, 0, Math.PI * 2);
        ctx.fillStyle = '#f6c445';
        ctx.fill();
      }

      // Orbe cósmico dorado (Agrandado a 22px para máxima legibilidad)
      ctx.beginPath();
      ctx.arc(displayPos.x, displayPos.y, 22, 0, Math.PI * 2);
      const orbGrad = ctx.createRadialGradient(displayPos.x, displayPos.y, 3, displayPos.x, displayPos.y, 22);
      orbGrad.addColorStop(0, '#fff3b0');
      orbGrad.addColorStop(0.5, '#eab308');
      orbGrad.addColorStop(1, '#a16207');
      ctx.fillStyle = orbGrad;
      ctx.shadowColor = 'rgba(246, 196, 69, 0.7)';
      ctx.shadowBlur = 12;
      ctx.fill();
      ctx.shadowBlur = 0;

      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Glifo del Planeta (20px bold)
      ctx.fillStyle = '#0f172a';
      ctx.font = '700 20px "Segoe UI Symbol", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(GLYPHS[nombre] || '★', displayPos.x, displayPos.y);

      // Etiqueta legible con NOMBRE y GRADOS: e.g. "Sol 21°"
      const labelDist = item.radius > this.radii.natalPlanets ? 32 : -32;
      const pLabel = this.polarToXY(rad, item.radius + labelDist);
      const labelText = `${nombre} ${data.grado_en_signo}°`;

      ctx.font = '700 12px Outfit, sans-serif';
      const textWidth = ctx.measureText(labelText).width;

      // Cápsula oscura para legibilidad cristalina
      ctx.fillStyle = 'rgba(5, 8, 20, 0.94)';
      ctx.strokeStyle = 'rgba(246, 196, 69, 0.6)';
      ctx.lineWidth = 1.2;
      this.drawRoundedRect(ctx, pLabel.x - textWidth / 2 - 8, pLabel.y - 10, textWidth + 16, 20, 6);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#fef08a';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(labelText, pLabel.x, pLabel.y);
    }
    ctx.restore();
  }

  // 5. Revolución Solar (Orbes 22px, Glifos 20px, Badges 12px Cian)
  drawSolarReturnRing(ctx, alpha = 1.0) {
    ctx.save();
    ctx.globalAlpha = alpha;

    // Anillo exterior contenedor
    ctx.beginPath();
    ctx.arc(0, 0, this.radii.rsPlanets + 30, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(0, 242, 254, 0.4)';
    ctx.lineWidth = 1.8;
    ctx.stroke();

    // Casas de la Revolución Solar
    if (this.rs.casas_rs) {
      for (let h = 1; h <= 12; h++) {
        const c = this.rs.casas_rs[`Casa ${h}`];
        if (!c) continue;

        const rad = this.degToRad(c.grado_absoluto);
        const p1 = this.polarToXY(rad, this.radii.zodiacOuter);
        const p2 = this.polarToXY(rad, this.radii.rsPlanets + 25);

        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = h === 1 ? '#00f2fe' : 'rgba(0, 242, 254, 0.25)';
        ctx.lineWidth = h === 1 ? 2.8 : 1.2;
        ctx.stroke();
      }
    }

    // Portal Ascendente RS (Libra 14°21' sobre Casa 9)
    const ascRS = this.rs.angulos_rs.Ascendente_RS;
    if (ascRS) {
      const radAscRS = this.degToRad(ascRS.grado_absoluto);
      const posPortal = this.polarToXY(radAscRS, this.radii.rsPlanets);

      ctx.beginPath();
      ctx.arc(posPortal.x, posPortal.y, 34, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(0, 242, 254, 0.6)';
      ctx.lineWidth = 2.2;
      ctx.shadowColor = '#00f2fe';
      ctx.shadowBlur = 20;
      ctx.stroke();
      ctx.shadowBlur = 0;

      const pLabel = this.polarToXY(radAscRS, this.radii.rsPlanets + 48);
      ctx.fillStyle = 'rgba(10, 16, 32, 0.94)';
      ctx.strokeStyle = '#00f2fe';
      ctx.lineWidth = 1.5;
      const portalTxt = 'PORTAL RS: C9 ♎ 14°';
      ctx.font = '800 12px Outfit, sans-serif';
      const pw = ctx.measureText(portalTxt).width;
      this.drawRoundedRect(ctx, pLabel.x - pw / 2 - 8, pLabel.y - 10, pw + 16, 20, 6);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#00f2fe';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(portalTxt, pLabel.x, pLabel.y);
    }

    // Planetas RS
    for (const item of this.rsLayout) {
      const { displayPos, exactPos, hasNeedle, nombre, data, dispDeg } = item;
      const rad = this.degToRad(dispDeg);

      if (hasNeedle) {
        ctx.beginPath();
        ctx.moveTo(exactPos.x, exactPos.y);
        ctx.lineTo(displayPos.x, displayPos.y);
        ctx.strokeStyle = 'rgba(0, 242, 254, 0.6)';
        ctx.lineWidth = 1.2;
        ctx.setLineDash([3, 3]);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.beginPath();
        ctx.arc(exactPos.x, exactPos.y, 3, 0, Math.PI * 2);
        ctx.fillStyle = '#00f2fe';
        ctx.fill();
      }

      // Orbe cian (22px)
      ctx.beginPath();
      ctx.arc(displayPos.x, displayPos.y, 22, 0, Math.PI * 2);
      const orbGrad = ctx.createRadialGradient(displayPos.x, displayPos.y, 3, displayPos.x, displayPos.y, 22);
      orbGrad.addColorStop(0, '#cffafe');
      orbGrad.addColorStop(0.5, '#06b6d4');
      orbGrad.addColorStop(1, '#0e7490');
      ctx.fillStyle = orbGrad;
      ctx.shadowColor = 'rgba(0, 242, 254, 0.7)';
      ctx.shadowBlur = 14;
      ctx.fill();
      ctx.shadowBlur = 0;

      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Glifo RS (20px)
      ctx.fillStyle = '#082f49';
      ctx.font = '700 20px "Segoe UI Symbol", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(GLYPHS[nombre] || '★', displayPos.x, displayPos.y);

      // Etiqueta legible con NOMBRE y GRADOS: e.g. "Marte 1°"
      const labelDist = item.radius > this.radii.rsPlanets ? 32 : -32;
      const pLabel = this.polarToXY(rad, item.radius + labelDist);
      const labelText = `${nombre} ${data.grado_en_signo}°`;

      ctx.font = '700 12px Outfit, sans-serif';
      const textWidth = ctx.measureText(labelText).width;

      ctx.fillStyle = 'rgba(5, 8, 20, 0.94)';
      ctx.strokeStyle = 'rgba(0, 242, 254, 0.6)';
      ctx.lineWidth = 1.2;
      this.drawRoundedRect(ctx, pLabel.x - textWidth / 2 - 8, pLabel.y - 10, textWidth + 16, 20, 6);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#38bdf8';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(labelText, pLabel.x, pLabel.y);
    }
    ctx.restore();
  }

  // 6. Retículo sobre el Astro Seleccionado
  drawTargetReticle(ctx) {
    if (!this.selectedTarget) return;

    ctx.save();
    const t = this.selectedTarget;
    const color = t.type === 'natal' ? '#f6c445' : '#00f2fe';

    ctx.beginPath();
    ctx.arc(t.x, t.y, 32, 0, Math.PI * 2);
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]);
    ctx.stroke();

    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(t.x - 40, t.y);
    ctx.lineTo(t.x - 22, t.y);
    ctx.moveTo(t.x + 22, t.y);
    ctx.lineTo(t.x + 40, t.y);
    ctx.moveTo(t.x, t.y - 40);
    ctx.lineTo(t.x, t.y - 22);
    ctx.moveTo(t.x, t.y + 22);
    ctx.lineTo(t.x, t.y + 40);
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.restore();
  }
}

// Iniciar aplicación
window.addEventListener('DOMContentLoaded', () => {
  window.astroNavigator = new AstroNavigator();
});
