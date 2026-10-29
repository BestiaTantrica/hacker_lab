/**
 * esfera_armilar_3d.js — Esfera Armilar 3D para el Reloj Astrológico (Three.js)
 *
 * Requisitos: `THREE` global (cualquier build r128+). Sin otras dependencias:
 * incluye su propio control orbital, entorno PBR procedural y selector de modo.
 *
 * Marco de coordenadas del mundo (observador, mano derecha):
 *     +X = Este     +Y = Cenit     +Z = Sur     (Norte = -Z)
 *
 * Geometría (R = 1):
 *   · Meridiano exterior  r=1.00  fijo, plano vertical N–S (normal = Este).
 *   · Horizonte           r=0.92  fijo, horizontal, con N / E / S / W.
 *   · Ecuador celeste     r=0.80  \ solidarios al cielo; el eje polar se eleva
 *   · Eclíptica           r=0.80  / |latitud| sobre el horizonte.
 *       La eclíptica se inclina EXACTAMENTE ε = 23.439° respecto del Ecuador
 *       (matriz de base analítica, sin rotaciones acumuladas) y lleva 12
 *       sectores de 30° con sus glifos + marcas cada 5°.
 *   · Centro ⊕            Tierra con pátina de cardenillo y cruz dorada.
 *
 * La rotación diurna se obtiene construyendo cada frame la matriz que lleva el
 * marco ecuatorial al marco del observador con el Tiempo Sidéreo Local θ:
 *     X_eq (α=0)  → (-sinθ,  cosφ·cosθ,  sinφ·cosθ)
 *     Polo (δ=90) → (   0,   sinφ,       -cosφ    )
 *     Y_eq (α=90) → ( cosθ,  cosφ·sinθ,   sinφ·sinθ)
 * (derivada de sin(alt)=sinφ·sinδ+cosφ·cosδ·cosH, H = θ-α). Es exacta para
 * cualquier latitud, incluida el hemisferio sur (φ = -34.6° Buenos Aires).
 *
 * Uso:
 *     const esfera = new EsferaArmilar3D(document.getElementById('esfera-3d'));
 *     esfera.start();                 // loop con pausa automática si no es visible
 *     esfera.setDate(new Date());     // o null para tiempo real
 *     EsferaArmilar3D.attachModeSelector(host, { canvas2d, container3d, esfera });
 */
(function (global) {
  'use strict';

  const THREE = global.THREE;
  if (!THREE) {
    console.error('[EsferaArmilar3D] THREE no está cargado.');
    return;
  }

  const DEG = Math.PI / 180;
  const OBLIQUITY = 23.439 * DEG;          // oblicuidad de la eclíptica (J2000)
  const REV = parseInt(THREE.REVISION, 10) || 150;
  const PHYSICAL_LIGHTS = REV >= 155;      // unidades de luz físicas (candela)

  const ZODIAC = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
    .map((g) => g + '\uFE0E');             // \uFE0E fuerza glifo de texto (no emoji)

  /* ───────────────────────── Astronomía mínima ───────────────────────── */

  const julianDay = (d) => d.getTime() / 86400000 + 2440587.5;

  /** Tiempo Sidéreo Local en radianes. lonDeg: Este positivo. */
  function localSiderealTime(date, lonDeg) {
    const d = julianDay(date) - 2451545.0;
    const gmst = 280.46061837 + 360.98564736629 * d;
    return ((((gmst + lonDeg) % 360) + 360) % 360) * DEG;
  }

  /** Longitud eclíptica aparente del Sol (±0.01°). */
  function sunLongitude(date) {
    const n = julianDay(date) - 2451545.0;
    const L = 280.460 + 0.9856474 * n;
    const g = (357.528 + 0.9856003 * n) * DEG;
    return (((L + 1.915 * Math.sin(g) + 0.020 * Math.sin(2 * g)) % 360) + 360) % 360 * DEG;
  }

  /* ───────────────────────── Utilidades visuales ───────────────────────── */

  function glyphTexture(text, color, size) {
    const c = document.createElement('canvas');
    c.width = c.height = size || 128;
    const g = c.getContext('2d');
    g.font = `bold ${Math.floor(c.width * 0.66)}px "Segoe UI Symbol","Noto Sans Symbols","DejaVu Sans",serif`;
    g.textAlign = 'center';
    g.textBaseline = 'middle';
    g.shadowColor = 'rgba(0,0,0,0.9)';
    g.shadowBlur = c.width * 0.08;
    g.fillStyle = color;
    g.fillText(text, c.width / 2, c.height / 2 + c.width * 0.03);
    const t = new THREE.CanvasTexture(c);
    t.anisotropy = 4;
    return t;
  }

  function makeSprite(text, color, scale, disposables) {
    const map = glyphTexture(text, color);
    const mat = new THREE.SpriteMaterial({ map, transparent: true, depthWrite: false });
    disposables.push(map, mat);
    const s = new THREE.Sprite(mat);
    s.scale.set(scale, scale, 1);
    return s;
  }

  /** Ruido procedural para bump/rugosidad de la pátina (sin assets externos). */
  function noiseTexture(size, seed) {
    const c = document.createElement('canvas');
    c.width = c.height = size;
    const g = c.getContext('2d');
    const img = g.createImageData(size, size);
    let s = seed >>> 0;
    const rnd = () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
    for (let i = 0; i < size * size; i++) {
      const v = 90 + rnd() * 120;
      img.data[i * 4] = img.data[i * 4 + 1] = img.data[i * 4 + 2] = v;
      img.data[i * 4 + 3] = 255;
    }
    g.putImageData(img, 0, 0);
    g.globalAlpha = 0.5;
    g.filter = 'blur(2px)';
    g.drawImage(c, 0, 0);
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return t;
  }

  /**
   * Entorno claroscuro procedural: una "habitación" negra con un panel cálido
   * (vela) y un tenue panel cenital frío. Los metales necesitan reflejar algo
   * para no verse planos; esto da el brillo tenebrista sin cargar HDRIs.
   */
  function buildEnvironment(renderer) {
    const env = new THREE.Scene();
    const room = new THREE.Mesh(
      new THREE.SphereGeometry(10, 24, 16),
      new THREE.MeshBasicMaterial({ color: 0x050403, side: THREE.BackSide })
    );
    env.add(room);
    const panel = (color, intensity, w, h, pos) => {
      const m = new THREE.Mesh(
        new THREE.PlaneGeometry(w, h),
        new THREE.MeshBasicMaterial({ color: new THREE.Color(color).multiplyScalar(intensity), side: THREE.DoubleSide })
      );
      m.position.set(...pos);
      m.lookAt(0, 0, 0);
      env.add(m);
    };
    panel(0xffa24a, 7.0, 6, 5, [-6, 3, 5]);      // luz cálida lateral (claroscuro)
    panel(0x9db4ff, 1.6, 8, 8, [0, 9, 0]);       // cenital etérea
    panel(0x3a2412, 1.2, 10, 3, [5, -2, -6]);    // rebote tenue
    const pmrem = new THREE.PMREMGenerator(renderer);
    const rt = pmrem.fromScene(env, 0.04);
    pmrem.dispose();
    env.traverse((o) => { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); });
    return rt.texture;
  }

  /* ───────────────────────────── Clase principal ───────────────────────────── */

  class EsferaArmilar3D {
    /**
     * @param {HTMLElement} container
     * @param {{latitude?:number, longitude?:number, maxFps?:number, timeScale?:number}} [opts]
     */
    constructor(container, opts = {}) {
      this.container = container;
      this.lat = (opts.latitude ?? -34.6) * DEG;     // Buenos Aires
      this.lon = opts.longitude ?? -58.38;           // grados, Este +
      this.maxFps = opts.maxFps ?? 60;
      this.timeScale = opts.timeScale ?? 1;
      this.fixedDate = null;
      this._simStart = performance.now();
      this._simBase = Date.now();
      this._disposables = [];
      this._running = false;
      this._visible = true;
      this._lastFrame = 0;
      this._needsRender = true;

      const coarse = global.matchMedia && matchMedia('(pointer:coarse)').matches;
      const lowEnd = (navigator.hardwareConcurrency || 4) <= 4;
      this._lite = coarse || lowEnd;                 // menos segmentos / DPR en móviles

      this._initRenderer();
      this._initScene();
      this._initControls();
      this._initObservers();
      this._resize();
    }

    /* ── Renderer / escena ── */
    _initRenderer() {
      const r = (this.renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: 'high-performance',
      }));
      r.setPixelRatio(Math.min(global.devicePixelRatio || 1, this._lite ? 1.5 : 2));
      if ('outputColorSpace' in r) r.outputColorSpace = THREE.SRGBColorSpace;
      else r.outputEncoding = THREE.sRGBEncoding;
      r.toneMapping = THREE.ACESFilmicToneMapping;
      r.toneMappingExposure = 1.05;
      r.domElement.style.cssText = 'display:block;width:100%;height:100%;touch-action:none;cursor:grab;';
      r.domElement.setAttribute('aria-label', 'Esfera armilar 3D interactiva');
      this.container.appendChild(r.domElement);
    }

    _initScene() {
      const scene = (this.scene = new THREE.Scene());
      this.camera = new THREE.PerspectiveCamera(38, 1, 0.1, 50);

      const envTex = buildEnvironment(this.renderer);
      this._disposables.push(envTex);

      // ── Materiales PBR tenebristas ──
      const patina = noiseTexture(256, 7);
      this._disposables.push(patina);
      const mk = (p) => { const m = new THREE.MeshStandardMaterial({ envMap: envTex, ...p }); this._disposables.push(m); return m; };
      const oro = mk({ color: 0xd9a21b, metalness: 0.90, roughness: 0.26, envMapIntensity: 1.25 });   // oro bruñido
      const bronce = mk({ color: 0x8a5a2b, metalness: 0.86, roughness: 0.34, envMapIntensity: 1.1 }); // bronce antiguo
      const bronceOscuro = mk({ color: 0x4e3218, metalness: 0.85, roughness: 0.35, envMapIntensity: 1.0 });
      const cardenillo = mk({
        color: 0x4f7d68, metalness: 0.55, roughness: 0.62, bumpMap: patina, bumpScale: 1.4,
        roughnessMap: patina, envMapIntensity: 0.9,
      });
      const solMat = new THREE.MeshBasicMaterial({ color: 0xffd36a });
      this._disposables.push(solMat);

      // ── Luces: claroscuro ──
      scene.add(new THREE.AmbientLight(0x1a1410, PHYSICAL_LIGHTS ? 0.6 : 0.5));
      const vela = new THREE.PointLight(0xffa860, PHYSICAL_LIGHTS ? 95 : 1.7, 0, 2);
      vela.position.set(-3.2, 1.8, 3.0);                        // cálida, lateral baja
      const cenit = new THREE.DirectionalLight(0xa9bcff, PHYSICAL_LIGHTS ? 0.9 : 0.35);
      cenit.position.set(0.5, 5, -0.5);                         // etérea, desde arriba
      scene.add(vela, cenit);

      const seg = this._lite ? { rad: 12, tub: 96 } : { rad: 20, tub: 192 };
      const torus = (r, tube, mat, parent) => {
        const g = new THREE.TorusGeometry(r, tube, seg.rad, seg.tub);  // normal = +Z
        this._disposables.push(g);
        const m = new THREE.Mesh(g, mat);
        parent.add(m);
        return m;
      };

      /* Raíz del instrumento. */
      const root = (this.root = new THREE.Group());
      scene.add(root);

      /* ① Meridiano exterior — fijo, vertical, plano N–S (normal = Este). */
      const meridiano = torus(1.0, 0.026, bronce, root);
      meridiano.rotation.y = Math.PI / 2;

      /* ② Horizonte — fijo, nivelado (normal = cenit), con puntos cardinales. */
      const horizonte = torus(0.92, 0.018, bronceOscuro, root);
      horizonte.rotation.x = Math.PI / 2;
      const cardinales = [['N', 0, -1], ['E', 1, 0], ['S', 0, 1], ['W', -1, 0]];
      for (const [t, x, z] of cardinales) {
        const s = makeSprite(t, t === 'N' ? '#ffd36a' : '#d8b878', 0.16, this._disposables);
        s.position.set(x * 1.06, 0, z * 1.06);
        root.add(s);
        const tick = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.03, 0.14), oro);
        this._disposables.push(tick.geometry);
        tick.position.set(x * 0.92, 0, z * 0.92);
        if (x !== 0) tick.rotation.y = Math.PI / 2;
        root.add(tick);
      }

      /* ③ Cielo (marco ecuatorial): matriz recalculada con el TSL cada frame. */
      const cielo = (this.cielo = new THREE.Group());
      cielo.matrixAutoUpdate = false;
      root.add(cielo);

      //   Eje polar (local +Y = polo norte celeste) y casquetes.
      const eje = new THREE.Mesh(new THREE.CylinderGeometry(0.007, 0.007, 2.3, 8), oro);
      this._disposables.push(eje.geometry);
      cielo.add(eje);
      for (const sgn of [1, -1]) {
        const cap = new THREE.Mesh(new THREE.ConeGeometry(0.03, 0.08, 12), oro);
        this._disposables.push(cap.geometry);
        cap.position.y = sgn * 1.19;
        if (sgn < 0) cap.rotation.x = Math.PI;
        cielo.add(cap);
      }

      //   Ecuador celeste (normal = eje polar = local Y).
      const ecuador = torus(0.80, 0.012, bronce, cielo);
      ecuador.rotation.x = Math.PI / 2;

      //   Eclíptica: base analítica exacta. En el marco local del cielo
      //   (X=α0, Y=polo, Z=-Y_eq): e1=(1,0,0), e2(λ=90°)=(0,sinε,-cosε),
      //   polo eclíptico n = e1×e2 = (0,cosε,sinε). Base (e1, n, -e2) es
      //   mano derecha y un punto de longitud λ queda en (cosλ, 0, -sinλ).
      const eclip = (this.eclip = new THREE.Group());
      const e1 = new THREE.Vector3(1, 0, 0);
      const e2 = new THREE.Vector3(0, Math.sin(OBLIQUITY), -Math.cos(OBLIQUITY));
      const n = new THREE.Vector3().crossVectors(e1, e2);
      eclip.matrixAutoUpdate = false;
      eclip.matrix.makeBasis(e1, n, e2.clone().negate());
      cielo.add(eclip);

      const aro = torus(0.80, 0.020, oro, eclip);
      aro.rotation.x = Math.PI / 2;

      //   Banda zodiacal (anillo plano grabado) bajo el aro.
      const banda = new THREE.Mesh(
        new THREE.RingGeometry(0.80 - 0.10, 0.80 - 0.02, this._lite ? 96 : 192),
        mk({ color: 0x2a1b0d, metalness: 0.8, roughness: 0.45, side: THREE.DoubleSide, envMapIntensity: 0.8 })
      );
      this._disposables.push(banda.geometry);
      banda.rotation.x = -Math.PI / 2;
      eclip.add(banda);

      //   Marcas cada 5° (mayores cada 30° = límites de signo) — InstancedMesh.
      const tickGeo = new THREE.BoxGeometry(1, 0.008, 0.008);   // largo en X (radial)
      this._disposables.push(tickGeo);
      const ticks = new THREE.InstancedMesh(tickGeo, oro, 72);
      const dummy = new THREE.Object3D();
      for (let i = 0; i < 72; i++) {
        const lam = i * 5 * DEG;
        const major = i % 6 === 0;
        const len = major ? 0.11 : 0.045;
        const r = 0.80 - 0.02 - len / 2 + (major ? 0.0 : -0.0);
        dummy.position.set(r * Math.cos(lam), 0, -r * Math.sin(lam));
        dummy.rotation.set(0, lam, 0);          // rot Y(λ): X → (cosλ, 0, -sinλ)
        dummy.scale.set(len, major ? 1.8 : 1, major ? 1.8 : 1);
        dummy.updateMatrix();
        ticks.setMatrixAt(i, dummy.matrix);
      }
      eclip.add(ticks);

      //   12 sectores zodiacales: glifo en el centro de cada sector de 30°.
      for (let k = 0; k < 12; k++) {
        const lam = (k * 30 + 15) * DEG;
        const rg = 0.80 - 0.062;
        const s = makeSprite(ZODIAC[k], '#f0c860', 0.105, this._disposables);
        s.position.set(rg * Math.cos(lam), 0, -rg * Math.sin(lam));
        eclip.add(s);
      }

      //   Marcador del Sol sobre la eclíptica.
      const sol = (this.sol = new THREE.Mesh(new THREE.SphereGeometry(0.035, 20, 14), solMat));
      this._disposables.push(sol.geometry);
      eclip.add(sol);
      const halo = makeSprite('●', 'rgba(255,200,90,0.35)', 0.22, this._disposables);
      sol.add(halo);

      /* ④ Centro ⊕ — la Tierra. */
      const tierra = new THREE.Mesh(new THREE.SphereGeometry(0.075, 32, 24), cardenillo);
      this._disposables.push(tierra.geometry);
      root.add(tierra);
      const crossR = 0.0765;
      const c1 = torus(crossR, 0.003, oro, root); c1.rotation.x = Math.PI / 2;  // ecuador terrestre
      const c2 = torus(crossR, 0.003, oro, root); c2.rotation.y = Math.PI / 2;  // meridiano terrestre
      this.tierra = tierra;

      // Encuadre: el hemisferio sur mira "hacia arriba" cómodo desde el sur-este.
      this._cam = { az: 0.55, el: 0.28, dist: 3.3, tAz: 0.55, tEl: 0.28, tDist: 3.3 };
      this._applyCamera();
    }

    /* ── Control orbital propio (arrastrar / rueda / pellizco) ── */
    _initControls() {
      const el = this.renderer.domElement;
      const c = this._cam;
      const pts = new Map();
      let pinch = 0;
      const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

      this._on(el, 'pointerdown', (e) => {
        el.setPointerCapture(e.pointerId);
        pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
        el.style.cursor = 'grabbing';
        this._userActive();
      });
      this._on(el, 'pointermove', (e) => {
        const p = pts.get(e.pointerId);
        if (!p) return;
        const dx = e.clientX - p.x, dy = e.clientY - p.y;
        p.x = e.clientX; p.y = e.clientY;
        if (pts.size === 1) {
          c.tAz -= dx * 0.006;
          c.tEl = clamp(c.tEl + dy * 0.006, -1.2, 1.35);
        } else if (pts.size === 2) {
          const [a, b] = [...pts.values()];
          const d = Math.hypot(a.x - b.x, a.y - b.y);
          if (pinch) c.tDist = clamp(c.tDist * (pinch / d), 1.9, 6);
          pinch = d;
        }
        this._needsRender = true;
      });
      const up = (e) => { pts.delete(e.pointerId); pinch = 0; if (!pts.size) el.style.cursor = 'grab'; };
      this._on(el, 'pointerup', up);
      this._on(el, 'pointercancel', up);
      this._on(el, 'wheel', (e) => {
        e.preventDefault();
        c.tDist = clamp(c.tDist * (1 + Math.sign(e.deltaY) * 0.08), 1.9, 6);
        this._needsRender = true;
      }, { passive: false });
    }

    _userActive() { this._needsRender = true; }

    _applyCamera() {
      const c = this._cam;
      c.az += (c.tAz - c.az) * 0.14;
      c.el += (c.tEl - c.el) * 0.14;
      c.dist += (c.tDist - c.dist) * 0.14;
      this.camera.position.set(
        c.dist * Math.sin(c.az) * Math.cos(c.el),
        c.dist * Math.sin(c.el),
        c.dist * Math.cos(c.az) * Math.cos(c.el)
      );
      this.camera.lookAt(0, 0, 0);
      return Math.abs(c.tAz - c.az) + Math.abs(c.tEl - c.el) + Math.abs(c.tDist - c.dist) > 1e-4;
    }

    /* ── Observadores: resize, visibilidad (ahorro de batería) ── */
    _on(target, type, fn, opts) {
      target.addEventListener(type, fn, opts);
      (this._listeners = this._listeners || []).push(() => target.removeEventListener(type, fn, opts));
    }

    _initObservers() {
      this._ro = new ResizeObserver(() => this._resize());
      this._ro.observe(this.container);
      this._io = new IntersectionObserver((es) => { this._visible = es[0].isIntersecting; });
      this._io.observe(this.container);
      this._on(document, 'visibilitychange', () => { this._visible = !document.hidden; });
      // Pérdida de contexto WebGL (móviles): restaurar sin recargar la página.
      this._on(this.renderer.domElement, 'webglcontextlost', (e) => e.preventDefault());
      this._on(this.renderer.domElement, 'webglcontextrestored', () => { this._needsRender = true; });
    }

    _resize() {
      const w = this.container.clientWidth || 1;
      const h = this.container.clientHeight || 1;
      this.renderer.setSize(w, h, false);
      this.camera.aspect = w / h;
      // En pantallas verticales, alejar para que la esfera completa quepa.
      this.camera.fov = w / h < 1 ? 38 / Math.max(w / h, 0.6) : 38;
      this.camera.updateProjectionMatrix();
      this._needsRender = true;
    }

    /* ── Tiempo ── */

    /** Fija una fecha concreta; null = tiempo real (× timeScale). */
    setDate(date) {
      this.fixedDate = date ? new Date(date) : null;
      this._simStart = performance.now();
      this._simBase = Date.now();
      this._needsRender = true;
    }

    _now() {
      if (this.fixedDate) return this.fixedDate;
      return new Date(this._simBase + (performance.now() - this._simStart) * this.timeScale);
    }

    _updateSky(date) {
      const th = localSiderealTime(date, this.lon);
      const phi = this.lat;
      const sT = Math.sin(th), cT = Math.cos(th), sP = Math.sin(phi), cP = Math.cos(phi);
      const xEq = new THREE.Vector3(-sT, cP * cT, sP * cT);
      const polo = new THREE.Vector3(0, sP, -cP);
      const yEq = new THREE.Vector3(cT, cP * sT, sP * sT);
      // Base local del cielo: X=α0, Y=polo, Z=-Y_eq  (mano derecha, verificada).
      this.cielo.matrix.makeBasis(xEq, polo, yEq.negate());
      this.cielo.matrixWorldNeedsUpdate = true;

      const lam = sunLongitude(date);
      const r = 0.80;
      this.sol.position.set(r * Math.cos(lam), 0, -r * Math.sin(lam));
    }

    /* ── Loop ── */
    start() {
      if (this._running) return;
      this._running = true;
      this.renderer.setAnimationLoop((t) => this._frame(t));
    }

    stop() {
      this._running = false;
      this.renderer.setAnimationLoop(null);
    }

    _frame(t) {
      if (!this._visible) return;                          // 0 % GPU fuera de pantalla
      const minDt = 1000 / this.maxFps - 1.5;
      if (t - this._lastFrame < minDt) return;
      this._lastFrame = t;
      this._updateSky(this._now());
      this._applyCamera();
      this.renderer.render(this.scene, this.camera);
    }

    /** Un render puntual (útil si no se llama a start()). */
    renderOnce() {
      this._updateSky(this._now());
      this._applyCamera();
      this.renderer.render(this.scene, this.camera);
    }

    dispose() {
      this.stop();
      this._ro && this._ro.disconnect();
      this._io && this._io.disconnect();
      (this._listeners || []).forEach((off) => off());
      this.scene.traverse((o) => {
        if (o.geometry) o.geometry.dispose();
      });
      this._disposables.forEach((d) => d.dispose && d.dispose());
      this.renderer.dispose();
      this.renderer.domElement.remove();
    }

    /* ── Selector [ 2D Clásico | 3D Esfera Armilar ] ── */

    /**
     * @param {HTMLElement} host   dónde insertar el selector
     * @param {{canvas2d:HTMLElement, container3d:HTMLElement, esfera?:EsferaArmilar3D,
     *          create?:()=>EsferaArmilar3D, onChange?:(mode:'2d'|'3d')=>void}} cfg
     *   `create` permite instanciar la esfera de forma perezosa (solo al elegir 3D).
     */
    static attachModeSelector(host, cfg) {
      let esfera = cfg.esfera || null;
      const wrap = document.createElement('div');
      wrap.setAttribute('role', 'tablist');
      wrap.style.cssText =
        'display:inline-flex;gap:2px;padding:3px;border:1px solid rgba(217,162,27,.45);' +
        'border-radius:999px;background:rgba(10,7,4,.72);backdrop-filter:blur(6px);font:600 12px/1 system-ui,sans-serif;';
      const mk = (id, label) => {
        const b = document.createElement('button');
        b.type = 'button'; b.id = id; b.textContent = label;
        b.setAttribute('role', 'tab');
        b.style.cssText = 'all:unset;cursor:pointer;padding:8px 14px;border-radius:999px;color:#d8b878;transition:background .2s,color .2s;';
        return b;
      };
      const b2 = mk('modo-2d', '2D Clásico');
      const b3 = mk('modo-3d', '3D Esfera Armilar');
      wrap.append(b2, b3);
      host.appendChild(wrap);

      const set = (mode) => {
        const is3d = mode === '3d';
        if (is3d && !esfera && cfg.create) esfera = cfg.create();
        cfg.canvas2d.style.display = is3d ? 'none' : '';
        cfg.container3d.style.display = is3d ? 'block' : 'none';
        if (esfera) { if (is3d) { esfera._resize(); esfera.start(); } else esfera.stop(); }
        for (const [b, on] of [[b2, !is3d], [b3, is3d]]) {
          b.setAttribute('aria-selected', String(on));
          b.style.background = on ? 'linear-gradient(135deg,#d9a21b,#8a5a2b)' : 'transparent';
          b.style.color = on ? '#120c05' : '#d8b878';
        }
        cfg.onChange && cfg.onChange(mode);
      };
      b2.onclick = () => set('2d');
      b3.onclick = () => set('3d');
      set('2d');
      return { set, get esfera() { return esfera; } };
    }
  }

  EsferaArmilar3D.math = { localSiderealTime, sunLongitude, OBLIQUITY };
  global.EsferaArmilar3D = EsferaArmilar3D;
})(typeof window !== 'undefined' ? window : globalThis);
