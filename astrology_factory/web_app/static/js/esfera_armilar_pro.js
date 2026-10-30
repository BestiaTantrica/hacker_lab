/**
 * esfera_armilar_pro.js — Astrolabio Mecánico Vivo · Esfera Armilar 3D (Three.js r128+)
 * ─────────────────────────────────────────────────────────────────────────────
 * Módulo ES6 autocontenido. 0 % servidor: todo se calcula y se dibuja en el
 * cliente. Sin texturas externas: la pátina, el relieve, la malaquita, los
 * glifos y los números se generan proceduralmente en <canvas> / GLSL.
 *
 * ── USO ──────────────────────────────────────────────────────────────────────
 *   <script src="three.min.js"></script>             <!-- global THREE (r128+) -->
 *   <script type="module">
 *     import { EsferaArmilarPro } from './esfera_armilar_pro.js';
 *     // (con bundler: EsferaArmilarPro.usarTHREE(THREE) antes de instanciar)
 *     const esfera = new EsferaArmilarPro(document.getElementById('esfera'),
 *                                         { latitud: -34.6, longitud: -58.38 });
 *     esfera.iniciar();
 *     // cada vez que el motor astronómico recalcula (p. ej. cada segundo):
 *     esfera.actualizarPosiciones(motor.calculated.planets,
 *                                 motor.calculated.houses, lstEnGrados);
 *   </script>
 *
 * ── FORMATO DE DATOS ─────────────────────────────────────────────────────────
 *   planetas : objeto { Sol:{grado_absoluto|lon|longitud, lat?}, Luna:{…}, … }
 *              o array [{nombre, lon, lat?}, …] (o número = longitud directa).
 *              Longitud/latitud ECLÍPTICAS en grados. `lat` es opcional (0 si falta).
 *              Reconoce (con o sin tildes): Sol, Luna, Mercurio, Venus, Marte, Júpiter,
 *              Saturno, Urano, Neptuno, Plutón, Nodo Norte, Quirón.
 *   casas    : array de 12 longitudes de cúspide en grados [ASC, II, III, … XII]
 *              (formato de `calculated.houses`) u objeto {cuspides:[12], mc?}.
 *   siderealTime : Tiempo Sidéreo Local en GRADOS (0-360). También acepta
 *              {grados}|{horas}|{radianes}. Entre llamadas la esfera lo extrapola
 *              en tiempo real (360.98564736629°/día) → rotación diurna fluida.
 *
 * ── MARCO DE COORDENADAS (observador, mano derecha) ──────────────────────────
 *   +X = Este   +Y = Cenit   +Z = Sur   (Norte = −Z).   Radios (R = 1):
 *   · 0.78  Esfera celeste: aro eclíptico (ε = 23.439°) + ecuador + joyas.
 *   · 0.70  Husos de las 12 casas (lunas esféricas N–S que parten en cada cúspide).
 *   · 0.86–0.96 Horizonte (N·E·S·W)   · 1.00 Meridiano local (escala de altura).
 *   · 1.04  Cristal de zafiro (sólo borde Fresnel)
 *   · 1.10–1.43 Tres aros mecánicos: segundos · minutos · horas.
 *
 * API pública: actualizarPosiciones, setObservador, setHora, setCapa, iniciar,
 *   detener, renderizarUnaVez, resetearCamara, destruir  (+ alias start/stop/dispose).
 */

let THREE = typeof globalThis !== 'undefined' ? globalThis.THREE : undefined;
let REV = THREE ? parseInt(THREE.REVISION, 10) || 150 : 0;

function usarTHREE(lib) {
  THREE = lib;
  REV = parseInt(lib.REVISION, 10) || 150;
}

/* ═══════════════════════════ 1 · CONSTANTES Y MATEMÁTICA ═══════════════════════════ */

const DEG = Math.PI / 180;
const TAU = Math.PI * 2;
const OBLIQUIDAD = 23.439 * DEG;           // ε exacta pedida
const R_ZODIACO = 6.30;                    // Radio del cinturón zodiacal exterior que enmarca el cosmos
const R_HUSOS = 6.10;

const FUENTE_SIMB = '"Noto Sans Symbols","Noto Sans Symbols 2","Segoe UI Symbol","Apple Symbols","DejaVu Sans",serif';
const FUENTE_SERIF = '"Cinzel","Cormorant Garamond","Palatino Linotype",Georgia,"Times New Roman",serif';

const SIGNOS = [
  ['♈', 'ARIES', 0], ['♉', 'TAURO', 1], ['♊', 'GÉMINIS', 2], ['♋', 'CÁNCER', 3],
  ['♌', 'LEO', 0], ['♍', 'VIRGO', 1], ['♎', 'LIBRA', 2], ['♏', 'ESCORPIO', 3],
  ['♐', 'SAGITARIO', 0], ['♑', 'CAPRICORNIO', 1], ['♒', 'ACUARIO', 2], ['♓', 'PISCIS', 3],
];
const ELEMENTO = ['#ff6a3a', '#6fbf73', '#e8d36a', '#58a6ff'];   // fuego, tierra, aire, agua
const ROMANOS = ['XII', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI'];

const ASPECTOS = [
  { ang: 60,  nombre: 'Sextil',     color: 0x19e3ff, orbe: 5 },   // cian
  { ang: 90,  nombre: 'Cuadratura', color: 0xe0103a, orbe: 7 },   // carmesí
  { ang: 120, nombre: 'Trígono',    color: 0xffc53a, orbe: 8 },   // oro
  { ang: 180, nombre: 'Oposición',  color: 0xa03cff, orbe: 8 },   // violeta eléctrico
];
const CUERPOS_ASPECTO = ['sol', 'luna', 'mercurio', 'venus', 'marte', 'jupiter', 'saturno', 'urano', 'neptuno', 'pluton'];

const mod = (a, n) => ((a % n) + n) % n;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const lerp = (a, b, t) => a + (b - a) * t;
const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
/** Diferencia angular más corta b − a en grados (−180, 180]. */
const difAng = (a, b) => mod(b - a + 180, 360) - 180;
/** Diferencia angular más corta en radianes (−π, π]. */
const difRad = (a, b) => mod(b - a + Math.PI, TAU) - Math.PI;
const norm = (s) => String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z]/g, '');

const julianDay = (d) => d.getTime() / 86400000 + 2440587.5;
/** Tiempo Sidéreo Local en grados (lon Este +). */
function tiempoSideralLocal(date, lonDeg) {
  const d = julianDay(date) - 2451545.0;
  return mod(280.46061837 + 360.98564736629 * d + lonDeg, 360);
}

/** Punto sobre la eclíptica en el marco local `eclip` (eje Y = polo eclíptico). */
function posEclip(lonDeg, latDeg, R, out) {
  const l = lonDeg * DEG, b = latDeg * DEG, cb = Math.cos(b);
  return out.set(R * cb * Math.cos(l), R * Math.sin(b), -R * cb * Math.sin(l));
}

/* ═════════════════════════ 2 · PROCEDURALES (canvas) ═════════════════════════ */

const crearCanvas = (w, h) => {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return c;
};

function rng(semilla) {
  let s = semilla >>> 0;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

/** Ruido de valor TILEABLE en [0,1)² (para envolver sin costuras). */
function ruidoTileable(periodo, semilla) {
  const r = rng(semilla);
  const g = new Float32Array(periodo * periodo);
  for (let i = 0; i < g.length; i++) g[i] = r();
  return (x, y) => {
    x *= periodo; y *= periodo;
    const xi = Math.floor(x), yi = Math.floor(y);
    const fx = x - xi, fy = y - yi;
    const sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
    const x0 = mod(xi, periodo), x1 = (x0 + 1) % periodo;
    const y0 = mod(yi, periodo), y1 = (y0 + 1) % periodo;
    const a = g[y0 * periodo + x0], b = g[y0 * periodo + x1];
    const c = g[y1 * periodo + x0], d = g[y1 * periodo + x1];
    return lerp(lerp(a, b, sx), lerp(c, d, sx), sy);
  };
}

function fbm(semilla, octavas = 5, base = 4) {
  const ns = [];
  for (let o = 0; o < octavas; o++) ns.push(ruidoTileable(base << o, semilla * 31 + o * 17 + 3));
  return (x, y) => {
    let a = 0.5, s = 0, n = 0;
    for (let o = 0; o < octavas; o++) { s += a * ns[o](x, y); n += a; a *= 0.5; }
    return s / n;
  };
}

function srgb(t) {
  if ('colorSpace' in t) t.colorSpace = THREE.SRGBColorSpace;
  else t.encoding = THREE.sRGBEncoding;
  return t;
}

/**
 * Pátina PBR procedural: color (metal envejecido + manchas de cardenillo),
 * "ORM" (G = rugosidad, B = metalicidad) y bump. 256² tileable, sin assets.
 */
function crearPatina(size, semilla, cfg) {
  const n1 = fbm(semilla, 4, 4), n2 = fbm(semilla + 11, 4, 3), n3 = fbm(semilla + 29, 3, 12);
  const cc = crearCanvas(size, size), co = crearCanvas(size, size), cb = crearCanvas(size, size);
  const ic = cc.getContext('2d').createImageData(size, size);
  const io = co.getContext('2d').createImageData(size, size);
  const ib = cb.getContext('2d').createImageData(size, size);
  const [br, bg, bb] = cfg.base, [vr, vg, vb] = cfg.cardenillo;
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const u = x / size, v = y / size, i = (y * size + x) * 4;
      const a = n1(u, v), b = n2(u, v), c = n3(u, v);
      const m = smooth(cfg.umbral, cfg.umbral + 0.16, b);          // máscara de cardenillo
      const sh = 0.70 + 0.62 * a;
      const rec = 0.78 + 0.45 * c;                                  // oscurece los huecos
      ic.data[i]     = clamp((br * sh * (1 - m) + vr * rec * m) * rec, 0, 255);
      ic.data[i + 1] = clamp((bg * sh * (1 - m) + vg * rec * m) * rec, 0, 255);
      ic.data[i + 2] = clamp((bb * sh * (1 - m) + vb * rec * m) * rec, 0, 255);
      ic.data[i + 3] = 255;
      io.data[i] = 255;
      io.data[i + 1] = clamp((cfg.rug + 0.42 * m + 0.20 * (c - 0.5)) * 255, 0, 255);
      io.data[i + 2] = clamp(cfg.metal * (1 - 0.55 * m) * 255, 0, 255);
      io.data[i + 3] = 255;
      const h = clamp((0.55 * a + 0.45 * c + 0.18 * m) * 255, 0, 255);
      ib.data[i] = ib.data[i + 1] = ib.data[i + 2] = h; ib.data[i + 3] = 255;
    }
  }
  cc.getContext('2d').putImageData(ic, 0, 0);
  co.getContext('2d').putImageData(io, 0, 0);
  cb.getContext('2d').putImageData(ib, 0, 0);
  const mk = (cv, color) => {
    const t = new THREE.CanvasTexture(cv);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return color ? srgb(t) : t;
  };
  return { map: mk(cc, true), orm: mk(co, false), bump: mk(cb, false) };
}

/** Textura de bandas atmosféricas (gigantes gaseosos). */
function texturaBandas(semilla, paleta, w = 256, h = 128, nBandas = 9) {
  const n = fbm(semilla, 4, 3);
  const c = crearCanvas(w, h), g = c.getContext('2d'), img = g.createImageData(w, h);
  const col = paleta.map((p) => ({ r: ((p >> 16) & 255) / 255, g: ((p >> 8) & 255) / 255, b: (p & 255) / 255 }));
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const u = x / w, v = y / h;
      const b = v * nBandas + (n(u, v) - 0.5) * 1.6;
      const s1 = 0.5 + 0.5 * Math.sin(b * 3.1), s2 = 0.5 + 0.5 * Math.sin(b * 1.3 + 2.0);
      const i = (y * w + x) * 4;
      const r = lerp(lerp(col[0].r, col[1].r, s1), col[2].r, s2 * 0.5);
      const gg = lerp(lerp(col[0].g, col[1].g, s1), col[2].g, s2 * 0.5);
      const bl = lerp(lerp(col[0].b, col[1].b, s1), col[2].b, s2 * 0.5);
      img.data[i] = r * 255; img.data[i + 1] = gg * 255; img.data[i + 2] = bl * 255; img.data[i + 3] = 255;
    }
  }
  g.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = THREE.RepeatWrapping;
  return srgb(t);
}

/** Tierra Tenebrista: Continentes en pergamino/bronce antiguo y océanos en azul noche abisal */
function texturaTierraTenebrista(w = 512, h = 256) {
  const n1 = fbm(12, 5, 4), n2 = fbm(42, 4, 8);
  const c = crearCanvas(w, h), g = c.getContext('2d'), img = g.createImageData(w, h);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const u = x / w, v = y / h;
      const val = n1(u, v) * 0.72 + n2(u * 2, v * 2) * 0.28;
      const esTierra = val > 0.50;
      const i = (y * w + x) * 4;
      if (esTierra) {
        const costa = clamp((val - 0.50) * 6.0, 0, 1);
        const r = lerp(85, 175, costa);
        const gg = lerp(70, 145, costa);
        const b = lerp(45, 90, costa);
        img.data[i] = r; img.data[i + 1] = gg; img.data[i + 2] = b; img.data[i + 3] = 255;
      } else {
        const prof = clamp((0.50 - val) * 5.0, 0, 1);
        const r = lerp(10, 4, prof);
        const gg = lerp(18, 7, prof);
        const b = lerp(38, 16, prof);
        img.data[i] = r; img.data[i + 1] = gg; img.data[i + 2] = b; img.data[i + 3] = 255;
      }
    }
  }
  g.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = THREE.RepeatWrapping;
  return srgb(t);
}

/** Badge flotante para planetas: [ ♂ Marte · 12° ♌ ] */
function texturaBadgeAstro(glifo, nombre, gradoStr, signoSimbolo, colorHex) {
  const w = 340, h = 82;
  const c = crearCanvas(w, h), g = c.getContext('2d');
  
  // Fondo píldora translúcido oscuro de alto contraste
  g.fillStyle = 'rgba(5, 4, 8, 0.94)';
  g.strokeStyle = colorHex || '#ffd070';
  g.lineWidth = 3.2;
  
  const r = 24;
  g.beginPath();
  g.moveTo(r, 4);
  g.lineTo(w - r, 4);
  g.arcTo(w - 4, 4, w - 4, h - 4, r);
  g.arcTo(w - 4, h - 4, 4, h - 4, r);
  g.arcTo(4, h - 4, 4, 4, r);
  g.arcTo(4, 4, w - r, 4, r);
  g.closePath();
  g.fill();
  g.stroke();

  // Glifo grande a la izquierda con brillo cósmico
  g.textAlign = 'left';
  g.textBaseline = 'middle';
  g.font = `bold 42px ${FUENTE_SIMB}`;
  g.fillStyle = colorHex || '#ffd070';
  g.shadowColor = 'rgba(0,0,0,0.98)';
  g.shadowBlur = 10;
  g.fillText(glifo, 18, h / 2 + 1);
  
  // Nombre del astro en marfil sacro
  g.font = `bold 25px ${FUENTE_SERIF}`;
  g.fillStyle = '#fff4dc';
  g.fillText(nombre, 68, h / 2 + 1);

  // Separador y Grado + Signo a la derecha en color de la joya
  const detalle = `· ${gradoStr} ${signoSimbolo}`;
  g.font = `bold 24px ${FUENTE_SIMB}`;
  g.fillStyle = colorHex || '#ffd070';
  g.textAlign = 'right';
  g.fillText(detalle, w - 18, h / 2 + 1);

  const t = srgb(new THREE.CanvasTexture(c));
  t.anisotropy = 4;
  return t;
}

function texturaHalo() {
  const c = crearCanvas(128, 128), g = c.getContext('2d');
  const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, 'rgba(255,255,255,1)');
  gr.addColorStop(0.18, 'rgba(255,255,255,0.55)');
  gr.addColorStop(0.5, 'rgba(255,255,255,0.12)');
  gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
}

function texturaRayos() {
  const S = 256, c = crearCanvas(S, S), g = c.getContext('2d');
  g.translate(S / 2, S / 2);
  const r = rng(77);
  for (let i = 0; i < 28; i++) {
    const L = S * (0.28 + 0.22 * r()), w = 0.03 + 0.05 * r();
    g.save(); g.rotate((i / 28) * TAU + r() * 0.1);
    const gr = g.createLinearGradient(0, 0, L, 0);
    gr.addColorStop(0, 'rgba(255,220,140,0.55)'); gr.addColorStop(1, 'rgba(255,170,60,0)');
    g.fillStyle = gr;
    g.beginPath(); g.moveTo(0, -L * w * 0.25); g.lineTo(L, 0); g.lineTo(0, L * w * 0.25); g.fill();
    g.restore();
  }
  const t = new THREE.CanvasTexture(c);
  return t;
}

function texturaGlifo(texto, color, { size = 128, fuente = FUENTE_SIMB, peso = 'bold', escala = 0.62 } = {}) {
  const c = crearCanvas(size, size), g = c.getContext('2d');
  g.font = `${peso} ${Math.floor(size * escala)}px ${fuente}`;
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.shadowColor = 'rgba(0,0,0,0.95)'; g.shadowBlur = size * 0.09;
  g.fillStyle = color;
  g.fillText(texto, size / 2, size / 2 + size * 0.03);
  g.fillText(texto, size / 2, size / 2 + size * 0.03);
  const t = srgb(new THREE.CanvasTexture(c));
  t.anisotropy = 4;
  return t;
}

/** Texto repetido ±W para que los rótulos que cruzan la costura (t=0/1) cierren. */
function textoWrap(ctx, txt, x, y, W) {
  for (const dx of [-W, 0, W]) ctx.fillText(txt, x + dx, y);
}

/** Anillo plano con UV polares (u = ángulo 0..1, v = radio 0 interior … 1 exterior). */
function franjaGeo(inner, outer, segs, inicio, dir) {
  const pos = [], nor = [], uv = [], idx = [];
  for (let i = 0; i <= segs; i++) {
    const t = i / segs, a = inicio + dir * t * TAU, c = Math.cos(a), s = Math.sin(a);
    pos.push(inner * c, inner * s, 0, outer * c, outer * s, 0);
    nor.push(0, 0, 1, 0, 0, 1);
    uv.push(t, 0, t, 1);
  }
  for (let i = 0; i < segs; i++) {
    const a = i * 2, b = a + 1, c = a + 2, d = a + 3;
    idx.push(a, c, b, b, c, d);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  return g;
}

/**
 * Borde Fresnel (rim lighting) sobre un MeshStandard/Physical: suma una emisión
 * pow(1 − N·V, p) para que los cantos dorados "enciendan" contra el vacío.
 */
function conBorde(mat, color, potencia = 3, fuerza = 0.6) {
  const c = new THREE.Color(color);
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uRimColor = { value: c };
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', '#include <common>\nuniform vec3 uRimColor;')
      .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
        { float rimF = pow(1.0 - saturate(dot(normalize(vViewPosition), normal)), ${potencia.toFixed(2)});
          totalEmissiveRadiance += uRimColor * rimF * ${fuerza.toFixed(3)}; }`);
  };
  mat.customProgramCacheKey = () => `rim${color}-${potencia}-${fuerza}`;
  return mat;
}

const COLA_SHADER = () => (REV >= 152
  ? '#include <tonemapping_fragment>\n#include <colorspace_fragment>'
  : '#include <tonemapping_fragment>\n#include <encodings_fragment>');

const GLSL_RUIDO = /* glsl */`
  float hash3(vec3 p){ p=fract(p*0.3183099+.1); p*=17.0; return fract(p.x*p.y*p.z*(p.x+p.y+p.z)); }
  float noise3(vec3 x){
    vec3 i=floor(x), f=fract(x); f=f*f*(3.0-2.0*f);
    return mix(mix(mix(hash3(i),hash3(i+vec3(1,0,0)),f.x), mix(hash3(i+vec3(0,1,0)),hash3(i+vec3(1,1,0)),f.x),f.y),
               mix(mix(hash3(i+vec3(0,0,1)),hash3(i+vec3(1,0,1)),f.x), mix(hash3(i+vec3(0,1,1)),hash3(i+vec3(1,1,1)),f.x),f.y), f.z);
  }
  float fbm3(vec3 p){ float a=.5,s=0.; for(int i=0;i<4;i++){ s+=a*noise3(p); p*=2.03; a*=.5; } return s; }
`;

/* ══════════════════ 3 · CATÁLOGO DE JOYAS (los astros) ══════════════════ */

/*  Planetas reales con órbitas escaladas: profundidad astronómica 3D real  */
const ASTROS = {
  luna:      { nombre: 'Luna', glifo: '☽', rOrb: 0.44, r: 0.038, geo: 'esfera', color: 0xd6dae0, emis: 0x181e26, rug: 0.60, metal: 0.05, cc: 0.2, borde: 0xd8e4f5, halo: 0xc4d4e8, bump: 0.8 },
  nodonorte: { nombre: 'Nodo Norte', glifo: '☊', rOrb: 0.54, r: 0.024, geo: 'octa', color: 0x1fc87a, emis: 0x064a2c, rug: 0.10, metal: 0.40, cc: 1, borde: 0x40ffa0, halo: 0x30ffa0 },
  mercurio:  { nombre: 'Mercurio', glifo: '☿', rOrb: 0.95, r: 0.034, geo: 'esfera', color: 0x7e8794, emis: 0x14181f, rug: 0.50, metal: 0.65, cc: 0.2, borde: 0xa8bccf, halo: 0x8494a4, bump: 0.6 },
  venus:     { nombre: 'Venus', glifo: '♀', rOrb: 1.45, r: 0.046, geo: 'esfera', color: 0xe5c98d, emis: 0x362712, rug: 0.25, metal: 0.25, cc: 0.8, borde: 0xffe2a4, halo: 0xffd988 },
  sol:       { nombre: 'Sol', glifo: '☉', rOrb: 2.05, r: 0.095, tipo: 'sol', halo: 0xffb830 },
  marte:     { nombre: 'Marte', glifo: '♂', rOrb: 2.70, r: 0.042, geo: 'esfera', color: 0xb83a22, emis: 0x481006, rug: 0.45, metal: 0.15, cc: 0.3, borde: 0xff6640, halo: 0xff4828, bump: 0.8 },
  quiron:    { nombre: 'Quirón', glifo: '⚷', rOrb: 3.30, r: 0.026, geo: 'octa', color: 0x60b0a8, emis: 0x123a36, rug: 0.15, metal: 0.50, cc: 1, borde: 0x98ffec, halo: 0x78e8dc },
  jupiter:   { nombre: 'Júpiter', glifo: '♃', rOrb: 3.95, r: 0.088, geo: 'esfera', bandas: [0xd6a468, 0x824b26, 0xf0dfbc], emis: 0x221308, rug: 0.32, metal: 0.05, cc: 0.5, borde: 0xffc070, halo: 0xffaa50 },
  saturno:   { nombre: 'Saturno', glifo: '♄', rOrb: 4.65, r: 0.072, geo: 'esfera', bandas: [0xd4be88, 0xa38548, 0xfaeec8], emis: 0x1f180a, rug: 0.35, metal: 0.05, cc: 0.5, borde: 0xffdba0, halo: 0xffd27a, anillos: true },
  urano:     { nombre: 'Urano', glifo: '♅', rOrb: 5.25, r: 0.048, geo: 'esfera', color: 0x44bdb6, emis: 0x083836, rug: 0.20, metal: 0.15, cc: 0.7, borde: 0x70fff6, halo: 0x50f0e8 },
  neptuno:   { nombre: 'Neptuno', glifo: '♆', rOrb: 5.70, r: 0.048, geo: 'esfera', color: 0x224ec0, emis: 0x0a1e64, rug: 0.18, metal: 0.20, cc: 0.7, borde: 0x6a96ff, halo: 0x4080ff },
  pluton:    { nombre: 'Plutón', glifo: '♇', rOrb: 6.05, r: 0.028, geo: 'esfera', color: 0x725b7a, emis: 0x201626, rug: 0.55, metal: 0.25, cc: 0.2, borde: 0xb08ec0, halo: 0x9070a8, bump: 0.7 },
};
const GENERICO = { nombre: '?', glifo: '✦', rOrb: 3.0, r: 0.024, geo: 'octa', color: 0xd0d0d0, emis: 0x303030, rug: 0.2, metal: 0.5, borde: 0xffffff, halo: 0xffffff };

/* ═══════════════════════════ 4 · CLASE PRINCIPAL ═══════════════════════════ */

export class EsferaArmilarPro {
  /** Inyección de THREE cuando no existe como global (bundlers / import map). */
  static usarTHREE(lib) { usarTHREE(lib); }

  /**
   * @param {HTMLElement} contenedor
   * @param {{latitud?:number, longitud?:number, fpsMax?:number, autoRotar?:boolean,
   *          autoAvanzar?:boolean, etiquetas?:boolean, fondo?:'espacio'|'transparente',
   *          calidad?:'auto'|'alta'|'baja', THREE?:object}} [opciones]
   */
  constructor(contenedor, opciones = {}) {
    if (opciones.THREE) usarTHREE(opciones.THREE);
    if (!THREE) throw new Error('[EsferaArmilarPro] THREE no está disponible (global o EsferaArmilarPro.usarTHREE).');
    this.contenedor = contenedor;
    this.opts = Object.assign({
      latitud: -34.6, longitud: -58.38, fpsMax: 60, autoRotar: true,
      autoAvanzar: true, etiquetas: true, fondo: 'espacio', calidad: 'auto',
    }, opciones);
    this._lat = this.opts.latitud * DEG;
    this._lon = this.opts.longitud;

    const gruesa = typeof matchMedia !== 'undefined' && matchMedia('(pointer:coarse)').matches;
    const pocos = (navigator.hardwareConcurrency || 4) <= 4;
    this._lite = this.opts.calidad === 'baja' || (this.opts.calidad === 'auto' && (gruesa || pocos));

    this._astros = {};
    this._cuspides = null;
    this._mcLon = null;
    this._lstRef = null; this._lstRefEpoch = 0;
    this._horaFija = null;
    this._repintar = [];
    this._disp = [];
    this._listeners = [];
    this._capas = { aspectos: true, casas: false, etiquetas: !!this.opts.etiquetas, reloj: false };
    this._t = 0; this._lastTs = 0; this._lastFrame = 0;
    this._corriendo = false; this._visible = true;
    this._tmp = { v: new THREE.Vector3(), v2: new THREE.Vector3(), m: new THREE.Matrix4(), q: new THREE.Quaternion() };

    this._initRenderer();
    this._initEscena();
    this._initControles();
    this._initObservadores();
    this._resize();
    this.renderizarUnaVez();
  }

  /* ─────────────────────────────── Renderer ─────────────────────────────── */

  _initRenderer() {
    const r = (this.renderer = new THREE.WebGLRenderer({
      antialias: true, alpha: this.opts.fondo === 'transparente', powerPreference: 'high-performance',
    }));
    r.setPixelRatio(Math.min(window.devicePixelRatio || 1, this._lite ? 1.5 : 2));
    if ('outputColorSpace' in r) r.outputColorSpace = THREE.SRGBColorSpace;
    else r.outputEncoding = THREE.sRGBEncoding;
    r.toneMapping = THREE.ACESFilmicToneMapping;
    r.toneMappingExposure = 1.15;
    r.setClearColor(0x010103, this.opts.fondo === 'transparente' ? 0 : 1);
    r.domElement.style.cssText = 'display:block;width:100%;height:100%;touch-action:none;cursor:grab;outline:none;';
    r.domElement.setAttribute('role', 'img');
    r.domElement.setAttribute('aria-label', 'Astrolabio mecánico: esfera armilar 3D interactiva con planetas, aspectos y casas en tiempo real');
    this.contenedor.appendChild(r.domElement);
    this._aniso = Math.min(8, r.capabilities.getMaxAnisotropy ? r.capabilities.getMaxAnisotropy() : 4);
    this._maxTex = r.capabilities.maxTextureSize || 4096;
  }

  /* ─────────────────────────────── Escena ─────────────────────────────── */

  _initEscena() {
    const scene = (this.scene = new THREE.Scene());
    this.camera = new THREE.PerspectiveCamera(36, 1, 0.1, 120);
    this._phys = REV >= 155;                       // luces en unidades físicas

    this._env = this._crearEntorno();
    this._crearMateriales();
    this._crearFondo();
    this._crearLuces();

    const root = (this.root = new THREE.Group());
    scene.add(root);
    this.seg = this._lite ? { rad: 10, tub: 128 } : { rad: 16, tub: 256 };

    this._crearMarcosFijos();
    this._crearCielo();
    this._crearTierra();
    this._crearReloj();
    this._crearCristal();
    this._crearPolvo();

    this._cam = {
      az: 0.75, el: 0.52, dist: 14.2, tDist: 14.2, vAz: 0, vEl: 0,
      target: new THREE.Vector3(), tTarget: new THREE.Vector3(),
      arrastrando: false, modoPan: false, ultimo: performance.now()
    };
    this._aplicarCamara(16);

    // Los glifos usan fuentes web: repintar las franjas cuando estén listas.
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => { this._repintar.forEach((f) => f()); });
    }
  }

  /** Entorno claroscuro procedural (PMREM): una sala negra con un panel cálido tipo vela. */
  _crearEntorno() {
    const env = new THREE.Scene();
    env.add(new THREE.Mesh(new THREE.SphereGeometry(10, 24, 16), new THREE.MeshBasicMaterial({ color: 0x040302, side: THREE.BackSide })));
    const panel = (color, k, w, h, pos) => {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h),
        new THREE.MeshBasicMaterial({ color: new THREE.Color(color).multiplyScalar(k), side: THREE.DoubleSide }));
      m.position.set(...pos); m.lookAt(0, 0, 0); env.add(m);
    };
    panel(0xffa24a, 9.0, 6, 5, [-6, 3, 5]);        // vela cálida lateral
    panel(0xffe2b0, 3.5, 3, 8, [6, 1, -4]);        // contraluz dorada estrecha (rim)
    panel(0x8fa8ff, 2.0, 8, 8, [0, 9, 0]);         // cenital etérea
    panel(0x3a2412, 1.4, 10, 3, [5, -2, -6]);      // rebote tenue
    const pm = new THREE.PMREMGenerator(this.renderer);
    const rt = pm.fromScene(env, 0.04);
    pm.dispose();
    env.traverse((o) => { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); });
    this._disp.push(rt.texture);
    return rt.texture;
  }

  _crearMateriales() {
    const tam = this._lite ? 128 : 256;
    const envI = (m, k) => { m.envMap = this._env; m.envMapIntensity = k; return m; };
    const std = (patina, k, extra = {}) => {
      this._disp.push(patina.map, patina.orm, patina.bump);
      const m = new THREE.MeshStandardMaterial({
        map: patina.map, roughnessMap: patina.orm, metalnessMap: patina.orm,
        bumpMap: patina.bump, bumpScale: 1.4, roughness: 1, metalness: 1, ...extra,
      });
      this._disp.push(m);
      return envI(m, k);
    };
    // Oro bruñido envejecido (olivo en los huecos), bronce renacentista, bronce oscuro y cardenillo.
    this.mat = {
      oro: conBorde(std(crearPatina(tam, 3, { base: [232, 170, 40], cardenillo: [110, 118, 54], umbral: 0.70, metal: 1.0, rug: 0.22 }), 1.45), 0xffc860, 3.0, 0.38),
      bronce: conBorde(std(crearPatina(tam, 7, { base: [158, 98, 48], cardenillo: [62, 134, 108], umbral: 0.46, metal: 0.92, rug: 0.34 }), 1.25), 0xffa860, 3.2, 0.30),
      bronceOsc: conBorde(std(crearPatina(tam, 13, { base: [84, 54, 30], cardenillo: [58, 122, 98], umbral: 0.40, metal: 0.9, rug: 0.38 }), 1.15), 0xd89a50, 3.5, 0.22),
      verdigris: std(crearPatina(tam, 21, { base: [72, 118, 98], cardenillo: [112, 170, 140], umbral: 0.30, metal: 0.55, rug: 0.52 }), 0.95),
    };
    this._texHalo = texturaHalo(); this._disp.push(this._texHalo);
    this._texRuidoPlaneta = crearPatina(128, 41, { base: [128, 128, 128], cardenillo: [128, 128, 128], umbral: 0.5, metal: 0.1, rug: 0.5 }).bump;
    this._disp.push(this._texRuidoPlaneta);
  }

  /* ── Fondo espacial profundo: nebulosa GLSL + campo de estrellas titilantes ── */
  _crearFondo() {
    if (this.opts.fondo === 'transparente') return;
    const nebulosa = new THREE.Mesh(
      new THREE.SphereGeometry(60, 32, 24),
      new THREE.ShaderMaterial({
        side: THREE.BackSide, depthWrite: false, depthTest: false, fog: false,
        uniforms: { uTime: { value: 0 } },
        vertexShader: 'varying vec3 vDir; void main(){ vDir=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }',
        fragmentShader: `
          uniform float uTime; varying vec3 vDir;
          ${GLSL_RUIDO}
          void main(){
            vec3 d=normalize(vDir);
            float n=fbm3(d*2.4+vec3(0.0,uTime*0.004,0.0));
            float m=fbm3(d*5.2+7.0);
            vec3 col=vec3(0.005,0.004,0.009);
            col+=vec3(0.065,0.028,0.115)*pow(n,2.7)*1.7;                 // violeta profundo
            col+=vec3(0.140,0.070,0.020)*pow(m*n,3.0)*2.6;               // polvo cálido
            col+=vec3(0.015,0.035,0.085)*smoothstep(0.2,1.0,d.y*0.5+0.5)*0.55;
            gl_FragColor=vec4(col,1.0);
            ${COLA_SHADER()}
          }`,
      }));
    nebulosa.renderOrder = -10;
    nebulosa.frustumCulled = false;
    this.scene.add(nebulosa);
    this._fondoMat = nebulosa.material;
    this._disp.push(nebulosa.geometry, nebulosa.material);

    const N = this._lite ? 1400 : 3200, r = rng(99);
    const pos = new Float32Array(N * 3), sem = new Float32Array(N), tin = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) {
      const u = r() * 2 - 1, a = r() * TAU, s = Math.sqrt(1 - u * u), R = 40;
      pos.set([R * s * Math.cos(a), R * u, R * s * Math.sin(a)], i * 3);
      sem[i] = r();
      const c = r();
      tin.set(c < 0.25 ? [1, 0.82, 0.6] : c < 0.45 ? [0.7, 0.8, 1] : [1, 1, 1], i * 3);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    g.setAttribute('aSeed', new THREE.BufferAttribute(sem, 1));
    g.setAttribute('aTint', new THREE.BufferAttribute(tin, 3));
    const px = Math.min(window.devicePixelRatio || 1, this._lite ? 1.5 : 2);
    const m = new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      uniforms: { uTime: { value: 0 }, uPx: { value: px } },
      vertexShader: `
        attribute float aSeed; attribute vec3 aTint; uniform float uTime; uniform float uPx;
        varying float vA; varying vec3 vC;
        void main(){
          gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);
          float tw=0.65+0.35*sin(uTime*(0.8+aSeed*2.6)+aSeed*60.0);
          vA=(0.35+0.65*aSeed*aSeed)*tw; vC=aTint;
          gl_PointSize=uPx*(0.9+aSeed*aSeed*2.6);
        }`,
      fragmentShader: `
        varying float vA; varying vec3 vC;
        void main(){
          float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.0,d)*vA;
          gl_FragColor=vec4(vC*1.4,a);
          ${COLA_SHADER()}
        }`,
    });
    const estrellas = new THREE.Points(g, m);
    estrellas.frustumCulled = false; estrellas.renderOrder = -9;
    this.scene.add(estrellas);
    this._estrellasMat = m;
    this._disp.push(g, m);
  }

  _crearLuces() {
    const P = this._phys, s = this.scene;
    s.add(new THREE.AmbientLight(0x241a12, P ? 0.9 : 0.6));
    // Vela cálida lateral baja: el claroscuro tenebrista.
    const vela = new THREE.PointLight(0xffa860, P ? 110 : 1.7, 0, 2);
    vela.position.set(-3.4, 1.9, 3.2);
    // Contraluz fría/dorada desde atrás: dibuja los cantos de los aros (rim lighting).
    const contra = new THREE.DirectionalLight(0xffd9a0, P ? 1.6 : 0.8);
    contra.position.set(3.5, 2.5, -4.5);
    const cenit = new THREE.DirectionalLight(0xa9bcff, P ? 0.7 : 0.3);
    cenit.position.set(0.5, 5, -0.5);
    s.add(vela, contra, cenit);
    this._vela = vela;
    // Luz del Sol (se monta en el grupo eclíptico: viaja con la joya solar).
    this._luzSol = new THREE.PointLight(0xffd9a0, P ? 5.5 : 1.7, P ? 0 : 4.8, P ? 2 : 1.2);
  }

  /* ── Franjas grabadas: textura (color + luminancia) ↔ MeshStandard con relieve y brillo ── */
  _franja({ inner, outer, inicio = 0, dir = 1, W = 8192, dibujar, emisivo = 0xffc860, intens = 0.9, metal = 0.8, rug = 0.36, bump = 1.8, doble = true }) {
    W = Math.min(W, this._maxTex, this._lite ? 4096 : 8192);
    const rmid = (inner + outer) / 2;
    const ppu = W / (TAU * rmid);
    const H = Math.max(48, Math.round((outer - inner) * ppu));
    const cm = crearCanvas(W, H), cl = crearCanvas(W, H);
    const g = { c: cm.getContext('2d'), l: cl.getContext('2d'), W, H, ppu };
    const tm = srgb(new THREE.CanvasTexture(cm)), tl = srgb(new THREE.CanvasTexture(cl));
    for (const t of [tm, tl]) { t.wrapS = THREE.RepeatWrapping; t.anisotropy = this._aniso; }
    const pintar = () => { dibujar(g); tm.needsUpdate = true; tl.needsUpdate = true; };
    pintar();
    this._repintar.push(pintar);
    const mat = new THREE.MeshStandardMaterial({
      map: tm, emissiveMap: tl, emissive: new THREE.Color(emisivo), emissiveIntensity: intens,
      bumpMap: tl, bumpScale: bump, metalness: metal, roughness: rug,
      envMap: this._env, envMapIntensity: 1.1, side: doble ? THREE.DoubleSide : THREE.FrontSide,
    });
    const geo = franjaGeo(inner, outer, this._lite ? 192 : 384, inicio, dir);
    this._disp.push(tm, tl, mat, geo);
    return new THREE.Mesh(geo, mat);
  }

  _torus(radio, tubo, mat, padre) {
    const g = new THREE.TorusGeometry(radio, tubo, this.seg.rad, this.seg.tub);
    const uv = g.attributes.uv, nu = Math.max(2, Math.round(radio * 16));
    for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * nu, uv.getY(i) * 2);
    this._disp.push(g);
    const m = new THREE.Mesh(g, mat);
    padre.add(m);
    return m;
  }

  /* ═══════ Horizonte exterior etéreo (despeja el interior para las órbitas 3D) ═══════ */
  _crearMarcosFijos() {
    const root = this.root;
    // Anillo exterior etéreo en el plano horizontal a distancia del zodíaco
    const gHor = new THREE.BufferGeometry();
    const pts = [];
    for (let i = 0; i <= 128; i++) {
      const a = (i / 128) * TAU;
      pts.push(new THREE.Vector3(R_ZODIACO * Math.cos(a), 0, -R_ZODIACO * Math.sin(a)));
    }
    gHor.setFromPoints(pts);
    const mHor = new THREE.LineBasicMaterial({
      color: 0x3d4a40, transparent: true, opacity: 0.25, blending: THREE.AdditiveBlending, depthWrite: false
    });
    const linHor = new THREE.Line(gHor, mHor);
    root.add(linHor);
    this._disp.push(gHor, mHor);

    // 4 Puntos cardinales etéreos en el perímetro exterior
    const cards = [
      { t: 'N', a: -Math.PI / 2, c: '#ff7040' },
      { t: 'E', a: 0, c: '#ffd070' },
      { t: 'S', a: Math.PI / 2, c: '#ffd070' },
      { t: 'W', a: Math.PI, c: '#ffd070' }
    ];
    for (const cd of cards) {
      const s = this._etiqueta(cd.t, cd.c, 0.22, { fuente: FUENTE_SERIF, escala: 0.6 });
      s.position.set(R_ZODIACO * 1.05 * Math.cos(cd.a), 0, R_ZODIACO * 1.05 * Math.sin(cd.a));
      s.material.opacity = 0.55;
      root.add(s);
    }
  }

  /** Material de gema (físico, con clearcoat) reutilizable. */
  _matGema(color, emis, rug, extra = {}) {
    const m = new THREE.MeshPhysicalMaterial({
      color, emissive: emis, roughness: rug, metalness: 0.2, clearcoat: 1, clearcoatRoughness: 0.05,
      envMap: this._env, envMapIntensity: 1.6, flatShading: true, ...extra,
    });
    this._disp.push(m);
    return m;
  }

  _sprite(map, color, escala, opacidad = 1, aditivo = true) {
    const mt = new THREE.SpriteMaterial({
      map, color, transparent: true, opacity: opacidad, depthWrite: false,
      blending: aditivo ? THREE.AdditiveBlending : THREE.NormalBlending,
    });
    this._disp.push(mt);
    const s = new THREE.Sprite(mt);
    s.scale.set(escala, escala, 1);
    return s;
  }

  _etiqueta(texto, color, escala, opts) {
    const map = texturaGlifo(texto, color, opts);
    this._disp.push(map);
    return this._sprite(map, 0xffffff, escala, 1, false);
  }

  /* ═══════ Cielo: eclíptica con zodíaco exterior, órbitas, joyas 3D, aspectos ═══════ */
  _crearCielo() {
    const { oro } = this.mat, root = this.root;
    const cielo = (this.cielo = new THREE.Group());
    cielo.matrixAutoUpdate = false;
    root.add(cielo);

    // Eclíptica inclinada EXACTAMENTE ε = 23.439°: base analítica
    const eclip = (this.eclip = new THREE.Group());
    const e1 = new THREE.Vector3(1, 0, 0);
    const e2 = new THREE.Vector3(0, Math.sin(OBLIQUIDAD), -Math.cos(OBLIQUIDAD));
    const nP = new THREE.Vector3().crossVectors(e1, e2);
    eclip.matrixAutoUpdate = false;
    eclip.matrix.makeBasis(e1, nP, e2.clone().negate());
    cielo.add(eclip);

    // Cinturón del Zodíaco exterior: corona celestial que enmarca todo el cosmos
    const zod = this._franja({
      inner: 5.95, outer: 6.55, inicio: 0, dir: 1, emisivo: 0xffc860, intens: 1.15, metal: 0.78, rug: 0.34, bump: 2.4,
      dibujar: (g) => this._dibujarZodiaco(g),
    });
    zod.rotation.x = -Math.PI / 2;
    eclip.add(zod);
    this._torus(6.55, 0.014, this.mat.oro, eclip).rotation.x = Math.PI / 2;
    this._torus(5.95, 0.010, this.mat.oro, eclip).rotation.x = Math.PI / 2;

    // Órbitas astronómicas concéntricas en el plano eclíptico
    this._crearOrbitas();

    // Luz del Sol dentro del sistema
    eclip.add(this._luzSol);

    // Husos de las casas (desactivado por defecto)
    this._crearHusos();

    // Marcadores angulares sobre el cinturón del zodíaco
    this._angulares = ['AC', 'DC', 'MC', 'IC'].map((t) => {
      const s = this._etiqueta(t, '#ffe08a', 0.22, { fuente: FUENTE_SERIF, escala: 0.55 });
      s.visible = false; eclip.add(s);
      return s;
    });

    // Los astros (joyas 3D a sus distancias reales) y la red de aspectos
    this._crearAstros();
    this._crearAspectos();
  }

  _crearOrbitas() {
    const eclip = this.eclip;
    const gOrbitas = new THREE.Group();
    eclip.add(gOrbitas);

    for (const [k, def] of Object.entries(ASTROS)) {
      const r = def.rOrb;
      if (!r) continue;
      const pts = [];
      const segs = 128;
      for (let i = 0; i <= segs; i++) {
        const a = (i / segs) * TAU;
        pts.push(new THREE.Vector3(r * Math.cos(a), 0, -r * Math.sin(a)));
      }
      const geo = new THREE.BufferGeometry().setFromPoints(pts);
      const col = def.halo || 0xffd070;
      const mat = new THREE.LineBasicMaterial({
        color: col,
        transparent: true,
        opacity: k === 'sol' ? 0.38 : (k === 'luna' ? 0.32 : 0.20),
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      });
      const linea = new THREE.Line(geo, mat);
      gOrbitas.add(linea);
      this._disp.push(geo, mat);
    }
  }

  _dibujarZodiaco({ c, l, W, H, ppu }) {
    const gr = c.createLinearGradient(0, 0, 0, H);
    gr.addColorStop(0, '#2c1d0c'); gr.addColorStop(1, '#130c05');
    c.fillStyle = gr; c.fillRect(0, 0, W, H);
    l.fillStyle = '#000'; l.fillRect(0, 0, W, H);
    const wS = W / 12;
    for (let k = 0; k < 12; k++) {
      const x0 = k * wS;
      c.globalAlpha = 0.20; c.fillStyle = ELEMENTO[SIGNOS[k][2]]; c.fillRect(x0, H * 0.17, wS, H * 0.80); c.globalAlpha = 1;
      c.fillStyle = '#e0aa28'; c.fillRect(x0 - 2.5, 0, 5, H);
      l.fillStyle = '#fff'; l.fillRect(x0 - 2.5, 0, 5, H);
    }
    c.fillStyle = '#e0aa28'; c.fillRect(0, H * 0.155, W, 3); c.fillRect(0, H - 4, W, 4);
    l.fillStyle = '#bbb'; l.fillRect(0, H * 0.155, W, 3); l.fillRect(0, H - 4, W, 4);
    // Marcas de grado: 1°, 5°, 10°
    for (let d = 0; d < 360; d++) {
      const x = (d / 360) * W, len = (d % 10 === 0 ? 0.15 : d % 5 === 0 ? 0.11 : 0.06) * H;
      c.fillStyle = '#f0c860'; c.fillRect(x - 1, 0, 2, len);
      l.fillStyle = '#fff'; l.fillRect(x - 1, 0, 2, len);
    }
    c.textAlign = l.textAlign = 'center'; c.textBaseline = l.textBaseline = 'middle';
    for (let k = 0; k < 12; k++) {
      const xc = (k + 0.5) * wS;
      c.font = l.font = `bold ${Math.round(H * 0.46)}px ${FUENTE_SIMB}`;
      c.fillStyle = '#f4cf72'; l.fillStyle = '#fff';
      c.fillText(SIGNOS[k][0] + '\uFE0E', xc, H * 0.50); l.fillText(SIGNOS[k][0] + '\uFE0E', xc, H * 0.50);
      c.font = l.font = `${Math.round(H * 0.095)}px ${FUENTE_SERIF}`;
      c.fillStyle = '#d8b060'; l.fillStyle = '#bbb';
      c.fillText(SIGNOS[k][1], xc, H * 0.83); l.fillText(SIGNOS[k][1], xc, H * 0.83);
    }
  }

  /* ── Husos de las casas: un único shader sobre una esfera; cada fragmento calcula su casa ── */
  _crearHusos() {
    this._husosU = {
      uStart: { value: new Float32Array(12) },
      uSpan: { value: new Float32Array(12) },
      uTime: { value: 0 },
      uOp: { value: 1 },
    };
    const mat = new THREE.ShaderMaterial({
      uniforms: this._husosU, transparent: true, depthWrite: false, side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending,
      vertexShader: `
        varying vec3 vP; varying vec3 vN; varying vec3 vV;
        void main(){
          vP=position; vN=normalize(normalMatrix*normal);
          vec4 mv=modelViewMatrix*vec4(position,1.0); vV=-mv.xyz;
          gl_Position=projectionMatrix*mv;
        }`,
      fragmentShader: `
        uniform float uStart[12]; uniform float uSpan[12]; uniform float uTime; uniform float uOp;
        varying vec3 vP; varying vec3 vN; varying vec3 vV;
        const float TAU=6.2831853;
        void main(){
          vec3 p=normalize(vP);
          float psi=atan(p.y,p.x);            // acimut alrededor del eje N–S (Z); 0 = Este, +90° = Cenit
          float rho=length(p.xy);             // 1 en el plano vertical primario, 0 en los polos N/S
          float casa=-1.0, local=0.0, borde=0.0;
          for(int i=0;i<12;i++){
            float sg=uSpan[i]>=0.0?1.0:-1.0;
            float d=mod((psi-uStart[i])*sg,TAU);
            float w=abs(uSpan[i]);
            if(d<w){ casa=float(i); local=d/max(w,1e-4); }
            float de=min(d,TAU-d);
            borde=max(borde,exp(-de*de*1100.0));
          }
          bool angular=(casa==0.0||casa==3.0||casa==6.0||casa==9.0);
          vec3 cA=vec3(1.00,0.72,0.26);       // angulares: ámbar
          vec3 cB=(mod(casa,2.0)<0.5)?vec3(0.30,0.34,0.95):vec3(0.14,0.62,0.78);
          vec3 base=angular?cA:cB;
          float fr=pow(1.0-abs(dot(normalize(vN),normalize(vV))),2.0);
          float shimmer=0.80+0.20*sin(uTime*0.7+local*9.4+casa*1.7);
          float polos=smoothstep(0.10,0.55,rho);
          float a=((angular?0.075:0.040)*shimmer+fr*0.07)*polos;
          vec3 col=base*a;
          col+=vec3(1.0,0.86,0.5)*borde*0.55*smoothstep(0.08,0.45,rho);
          col*=uOp;
          gl_FragColor=vec4(col,1.0);
          ${COLA_SHADER()}
        }`,
    });
    const huso = new THREE.Mesh(new THREE.SphereGeometry(R_HUSOS, this._lite ? 64 : 112, this._lite ? 40 : 72), mat);
    huso.renderOrder = 3;
    this.root.add(huso);
    this._husos = huso;
    this._disp.push(huso.geometry, mat);
    huso.visible = false;

    // Números romanos de las casas, en el plano vertical primario
    this._numCasas = ROMANOS.map((_, i) => {
      const txt = ROMANOS[(i + 1) % 12];
      const s = this._etiqueta(txt, '#f1d58a', 0.075, { fuente: FUENTE_SERIF, escala: 0.40 });
      s.material.opacity = 0.8; s.visible = false;
      this.root.add(s);
      return s;
    });
  }

  /* ── Joyas: los 12 astros como esferas/gemas 3D emisivas ── */
  _crearAstros() {
    for (const k of Object.keys(ASTROS)) this._astro(k, ASTROS[k]);
  }

  _astro(clave, def) {
    if (this._astros[clave]) return this._astros[clave];
    const g = new THREE.Group();
    const a = {
      clave, def, g, lon: 0, lat: 0, lonT: 0, latT: 0, nuevo: true, visible: false,
      semilla: Math.random() * 10, spin: [], halo: null, etiqueta: null,
    };
    g.visible = false;
    const r = def.r;
    let cuerpo;
    if (def.tipo === 'sol') {
      cuerpo = this._crearSol(a, r);
    } else {
      let geo;
      if (def.geo === 'gema') geo = new THREE.IcosahedronGeometry(r, 1);
      else if (def.geo === 'octa') { geo = new THREE.OctahedronGeometry(r * 1.15, 0); }
      else geo = new THREE.SphereGeometry(r, 36, 28);
      this._disp.push(geo);
      const facetado = def.geo === 'gema' || def.geo === 'octa';
      const p = {
        roughness: def.rug, metalness: def.metal, emissive: def.emis, flatShading: facetado,
        envMap: this._env, envMapIntensity: facetado ? 1.8 : 1.3,
        clearcoat: def.cc || 0, clearcoatRoughness: 0.08,
      };
      if (def.bandas) { p.map = texturaBandas(Math.round(a.semilla * 7) + 1, def.bandas); this._disp.push(p.map); }
      else p.color = def.color;
      if (def.bump) { p.bumpMap = this._texRuidoPlaneta; p.bumpScale = def.bump; }
      const mat = conBorde(new THREE.MeshPhysicalMaterial(p), def.borde, 2.6, 0.55);
      this._disp.push(mat);
      cuerpo = new THREE.Mesh(geo, mat);
      a.spin.push(cuerpo);
      if (def.anillos) this._anillosSaturno(g, r);
      if (clave === 'urano') this._anilloFino(g, r * 1.9, 0xa0fff4, true);
    }
    g.add(cuerpo);

    // Halo aditivo radiante
    const halo = this._sprite(this._texHalo, def.halo, r * 7.5, 0.55);
    halo.renderOrder = 6; g.add(halo); a.halo = halo;

    // Badge flotante tipo reliquia [ ♂ Marte · 12° ♌ ]
    const colHex = '#' + new THREE.Color(def.halo).getHexString();
    const mapBadge = texturaBadgeAstro(def.glifo, def.nombre, '0°', '♈', colHex);
    this._disp.push(mapBadge);
    const et = this._sprite(mapBadge, 0xffffff, 0.34, 0.95, false);
    et.scale.set(0.34, 0.082, 1);
    et.material.opacity = 0.95; et.material.depthTest = false; et.renderOrder = 9;
    et.visible = this._capas.etiquetas; a.etiqueta = et;
    a.badgeColor = colHex;
    a.badgeKey = '';
    this.eclip.add(et);

    // Rayo proyector radial hacia el cinturón exterior del zodíaco
    const rayPts = new Float32Array(6);
    const rayGeo = new THREE.BufferGeometry();
    rayGeo.setAttribute('position', new THREE.BufferAttribute(rayPts, 3));
    const rayMat = new THREE.LineBasicMaterial({
      color: new THREE.Color(def.halo || 0xffd070),
      transparent: true,
      opacity: 0.24,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    const rayLine = new THREE.Line(rayGeo, rayMat);
    rayLine.frustumCulled = false;
    rayLine.visible = false;
    this.eclip.add(rayLine);
    a.rayoZod = rayLine;
    this._disp.push(rayGeo, rayMat);

    this.eclip.add(g);
    this._astros[clave] = a;
    return a;
  }

  _crearSol(a, r) {
    const sol = new THREE.Mesh(new THREE.SphereGeometry(r, 48, 36), new THREE.ShaderMaterial({
      uniforms: { uTime: { value: 0 } },
      vertexShader: `
        varying vec3 vPos; varying vec3 vN; varying vec3 vV;
        void main(){ vPos=position; vN=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.0); vV=-mv.xyz; gl_Position=projectionMatrix*mv; }`,
      fragmentShader: `
        uniform float uTime; varying vec3 vPos; varying vec3 vN; varying vec3 vV;
        ${GLSL_RUIDO}
        void main(){
          vec3 p=normalize(vPos);
          float n=fbm3(p*3.0+vec3(uTime*0.15,uTime*0.10,-uTime*0.12));
          float m=fbm3(p*7.5-vec3(uTime*0.22));
          float f=pow(1.0-abs(dot(normalize(vN),normalize(vV))),2.0);
          vec3 col=mix(vec3(1.0,0.46,0.07),vec3(1.0,0.86,0.42),n);
          col=mix(col,vec3(1.0,0.97,0.82),m*m*0.85);
          col*=1.55-0.55*f; col+=vec3(1.0,0.5,0.1)*f*0.7;
          gl_FragColor=vec4(col,1.0);
          ${COLA_SHADER()}
        }`,
    }));
    this._disp.push(sol.geometry, sol.material);
    this._solMat = sol.material;
    // Corona aditiva
    const corona = new THREE.Mesh(new THREE.SphereGeometry(r * 1.9, 32, 24), new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      uniforms: { uTime: { value: 0 } },
      vertexShader: `varying vec3 vN; varying vec3 vV; void main(){ vN=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.0); vV=-mv.xyz; gl_Position=projectionMatrix*mv; }`,
      fragmentShader: `
        uniform float uTime; varying vec3 vN; varying vec3 vV;
        void main(){
          float f=abs(dot(normalize(vN),normalize(vV)));
          float a=pow(f,3.2)*0.55*(0.88+0.12*sin(uTime*2.3));
          gl_FragColor=vec4(vec3(1.0,0.72,0.26)*a*1.6,a);
          ${COLA_SHADER()}
        }`,
    }));
    corona.renderOrder = 5;
    a.g.add(corona);
    this._coronaMat = corona.material;
    this._disp.push(corona.geometry, corona.material);
    // Rayos
    const tr = texturaRayos(); this._disp.push(tr);
    const rayos = this._sprite(tr, 0xffd890, r * 11, 0.75);
    rayos.renderOrder = 6; a.g.add(rayos); a.rayos = rayos;
    return sol;
  }

  _anillosSaturno(grupo, r) {
    const c = crearCanvas(8, 256), g = c.getContext('2d');
    const H = 256;
    const bandas = [[0.00, 0.17, 0.18, '#8a7048'], [0.17, 0.54, 0.86, '#e2c88e'], [0.54, 0.60, 0.05, '#40301c'],
                    [0.60, 0.80, 0.70, '#cdb07a'], [0.80, 0.82, 0.12, '#40301c'], [0.82, 1.00, 0.55, '#bda06a']];
    for (const [a, b, op, col] of bandas) {
      g.globalAlpha = op; g.fillStyle = col;
      g.fillRect(0, (1 - b) * H, 8, (b - a) * H);
    }
    const t = srgb(new THREE.CanvasTexture(c));
    const geo = franjaGeo(r * 1.38, r * 2.55, 96, 0, 1);
    const mat = new THREE.MeshStandardMaterial({
      map: t, transparent: true, side: THREE.DoubleSide, depthWrite: false, roughness: 0.55, metalness: 0.35,
      emissive: 0x2a2010, envMap: this._env, envMapIntensity: 1.0,
    });
    this._disp.push(t, geo, mat);
    const anillo = new THREE.Mesh(geo, mat);
    const pivote = new THREE.Group();
    pivote.rotation.set(-Math.PI / 2 + 0.466, 0, 0.35);       // 26.7° de inclinación
    pivote.add(anillo);
    grupo.add(pivote);
  }

  _anilloFino(grupo, radio, color, vertical) {
    const geo = new THREE.TorusGeometry(radio, radio * 0.008, 6, 64);
    const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.55, blending: THREE.AdditiveBlending });
    this._disp.push(geo, mat);
    const m = new THREE.Mesh(geo, mat);
    if (vertical) m.rotation.set(0.3, 0, 1.45);
    grupo.add(m);
  }

  /* ── Red de aspectos: hilos de plasma (cilindros aditivos con shader de flujo) ── */
  _crearAspectos() {
    this._aspGeo = new THREE.CylinderGeometry(1, 1, 1, 10, 1, true);
    this._disp.push(this._aspGeo);
    this._aspKeys = CUERPOS_ASPECTO;
    this._aspPool = [];
    const n = (CUERPOS_ASPECTO.length * (CUERPOS_ASPECTO.length - 1)) / 2;
    const vs = `
      varying vec3 vN; varying vec3 vV; varying vec2 vUv;
      void main(){ vUv=uv; vN=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.0); vV=-mv.xyz; gl_Position=projectionMatrix*mv; }`;
    const fs = `
      uniform vec3 uColor; uniform float uTime; uniform float uStr; uniform float uLen; uniform float uSeed;
      varying vec3 vN; varying vec3 vV; varying vec2 vUv;
      void main(){
        float f=abs(dot(normalize(vN),normalize(vV)));
        float core=pow(f,1.7), hot=pow(f,9.0);
        float y=vUv.y*uLen;
        float pk=pow(0.5+0.5*sin(y*15.0-uTime*3.4+uSeed),5.0);
        float tr=0.75+0.25*sin(y*46.0-uTime*8.0+uSeed*2.0);
        float ends=smoothstep(0.0,0.07,vUv.y)*smoothstep(0.0,0.07,1.0-vUv.y);
        float a=(core*0.50+hot*0.95)*(0.50+0.50*pk)*tr*uStr*ends;
        vec3 col=uColor*(1.15+pk*1.5)+vec3(hot)*0.65;
        gl_FragColor=vec4(col,a);
        ${COLA_SHADER()}
      }`;
    for (let i = 0; i < n; i++) {
      const mat = new THREE.ShaderMaterial({
        transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
        uniforms: {
          uColor: { value: new THREE.Color(0xffffff) }, uTime: { value: 0 }, uStr: { value: 1 },
          uLen: { value: 1 }, uSeed: { value: Math.random() * 6.28 },
        },
        vertexShader: vs, fragmentShader: fs,
      });
      const m = new THREE.Mesh(this._aspGeo, mat);
      m.visible = false; m.renderOrder = 4; m.frustumCulled = false;
      this.eclip.add(m);
      this._disp.push(mat);
      this._aspPool.push(m);
    }
  }

  /* ═══════ Tierra ⊕: orbe geocéntrico noble en el centro ═══════ */
  _crearTierra() {
    const R = 0.132, oro = this.mat.oro, root = this.root;
    const mapa = texturaTierraTenebrista(); this._disp.push(mapa);
    const mat = new THREE.MeshStandardMaterial({
      map: mapa, roughness: 0.42, metalness: 0.18,
      bumpMap: mapa, bumpScale: 0.008, envMap: this._env, envMapIntensity: 0.9,
    });
    conBorde(mat, 0xffd070, 3.2, 0.40);
    const orbe = new THREE.Mesh(new THREE.SphereGeometry(R, 48, 36), mat);
    this._disp.push(orbe.geometry, mat);

    // Grupo orientado: eje local Y = polo celeste (marco geocéntrico del observador).
    const tierra = (this.tierra = new THREE.Group());
    tierra.add(orbe);
    const rg = this._lite ? 48 : 96;
    const linea = (geo) => { this._disp.push(geo); return new THREE.Mesh(geo, oro); };
    for (let k = 0; k < 6; k++) {                                     // meridianos cada 30°
      const m = linea(new THREE.TorusGeometry(R * 1.003, 0.0011, 5, rg));
      m.rotation.y = (k * 30) * DEG;
      tierra.add(m);
    }
    const ecu = linea(new THREE.TorusGeometry(R * 1.003, 0.0018, 5, rg)); ecu.rotation.x = Math.PI / 2; tierra.add(ecu);

    // Eje polar fino en oro
    const ejeGeo = new THREE.CylinderGeometry(0.0016, 0.0016, R * 2.3, 12);
    const eje = new THREE.Mesh(ejeGeo, oro);
    tierra.add(eje);
    this._disp.push(ejeGeo);

    // Pasador dorado: ubicación del observador
    const pin = new THREE.Mesh(new THREE.SphereGeometry(0.009, 12, 10), oro);
    const haloP = this._sprite(this._texHalo, 0xffd070, 0.07, 0.85);
    this._pinTierra = { pin, haloP, R };
    tierra.add(pin, haloP);
    this._disp.push(pin.geometry);
    root.add(tierra);
    this._orientarTierra();
  }

  _orientarTierra() {
    const phi = this._lat, cp = Math.cos(phi), sp = Math.sin(phi);
    const polo = new THREE.Vector3(0, sp, -cp);
    const ex = new THREE.Vector3(0, cp, sp);                  // en el plano meridiano, ⟂ al polo
    const ez = new THREE.Vector3().crossVectors(ex, polo);
    const m = new THREE.Matrix4().makeBasis(ex, polo, ez);
    this.tierra.quaternion.setFromRotationMatrix(m);
    // En el marco local de la Tierra el observador está en (cosφ, sinφ, 0)·R
    const { pin, haloP, R } = this._pinTierra;
    pin.position.set(cp * R, sp * R, 0);
    haloP.position.copy(pin.position).multiplyScalar(1.04);
  }

  /* ═══════ Aros mecánicos exteriores (Desactivados en favor del Cosmograma 3D puro) ═══════ */
  _crearReloj() {
    this.reloj = new THREE.Group();
    this.reloj.visible = false;
    this.root.add(this.reloj);
    this._anillos = { seg: new THREE.Group(), min: new THREE.Group(), hor: new THREE.Group() };
    this._joyasReloj = [];
    this._escape = new THREE.Group();
    this._volante = new THREE.Group();
    this._ancora = new THREE.Group();
  }

  /* ═══════ Cristal de zafiro (Desactivado para preservar tenebrismo abisal puro) ═══════ */
  _crearCristal() {
    this._cristal = new THREE.Group();
  }

  /* ═══════ Polvo volumétrico: motas que se encienden cerca del Sol ═══════ */
  _crearPolvo() {
    const N = this._lite ? 220 : 520, r = rng(1234);
    const pos = new Float32Array(N * 3), sem = new Float32Array(N);
    for (let i = 0; i < N; i++) {
      let x, y, z;
      do { x = r() * 2 - 1; y = r() * 2 - 1; z = r() * 2 - 1; } while (x * x + y * y + z * z > 1);
      const k = 1.5;
      pos.set([x * k, y * k, z * k], i * 3); sem[i] = r();
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    g.setAttribute('aSeed', new THREE.BufferAttribute(sem, 1));
    const px = Math.min(window.devicePixelRatio || 1, this._lite ? 1.5 : 2);
    this._polvoU = { uTime: { value: 0 }, uSun: { value: new THREE.Vector3() }, uPx: { value: px } };
    const m = new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: this._polvoU,
      vertexShader: `
        attribute float aSeed; uniform float uTime; uniform vec3 uSun; uniform float uPx; varying float vA;
        void main(){
          vec3 p=position+0.035*vec3(sin(uTime*0.21+aSeed*10.0),cos(uTime*0.17+aSeed*7.0),sin(uTime*0.13+aSeed*5.0));
          vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=projectionMatrix*mv;
          float d=distance(p,uSun);
          vA=0.07+1.5/(1.0+d*d*7.0);
          gl_PointSize=uPx*(1.6+aSeed*3.2)*clamp(3.2/(-mv.z),0.5,2.0);
        }`,
      fragmentShader: `
        varying float vA;
        void main(){
          float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.0,d)*vA*0.30;
          gl_FragColor=vec4(vec3(1.0,0.78,0.42)*1.5,a);
          ${COLA_SHADER()}
        }`,
    });
    const p = new THREE.Points(g, m);
    p.frustumCulled = false; p.renderOrder = 7;
    this.root.add(p);
    this._polvo = p;
    this._disp.push(g, m);
  }

  /* ═══════════════════════ Controles orbitales con inercia ═══════════════════════ */

  _on(target, tipo, fn, opts) {
    target.addEventListener(tipo, fn, opts);
    this._listeners.push(() => target.removeEventListener(tipo, fn, opts));
  }

  _initControles() {
    const el = this.renderer.domElement, c = this._cam;
    const pts = new Map();
    let pinch = 0, tPrev = 0;
    const SENS = 0.0055;
    this._on(el, 'contextmenu', (e) => e.preventDefault());
    this._on(el, 'pointerdown', (e) => {
      el.setPointerCapture(e.pointerId);
      const esPan = e.button === 2 || e.button === 1 || e.shiftKey;
      pts.set(e.pointerId, { x: e.clientX, y: e.clientY, pan: esPan });
      c.arrastrando = true; c.vAz = c.vEl = 0; c.ultimo = performance.now(); tPrev = e.timeStamp;
      el.style.cursor = esPan ? 'move' : 'grabbing';
    });
    this._on(el, 'pointermove', (e) => {
      const p = pts.get(e.pointerId);
      if (!p) return;
      const dx = e.clientX - p.x, dy = e.clientY - p.y;
      p.x = e.clientX; p.y = e.clientY;
      c.ultimo = performance.now();
      if (pts.size === 1) {
        if (p.pan) {
          // Paneo libre en el plano de vista de la cámara
          const right = new THREE.Vector3(1, 0, 0).applyQuaternion(this.camera.quaternion);
          const up = new THREE.Vector3(0, 1, 0).applyQuaternion(this.camera.quaternion);
          const panFactor = Math.max(0.001, c.dist * 0.0014);
          c.tTarget.addScaledVector(right, -dx * panFactor);
          c.tTarget.addScaledVector(up, dy * panFactor);
        } else {
          const dt = Math.max(6, e.timeStamp - tPrev); tPrev = e.timeStamp;
          const dAz = -dx * SENS, dEl = dy * SENS;
          c.az += dAz; c.el = clamp(c.el + dEl, -1.35, 1.45);
          c.vAz = lerp(c.vAz, dAz / dt, 0.5); c.vEl = lerp(c.vEl, dEl / dt, 0.5);    // rad/ms
        }
      } else if (pts.size === 2) {
        const [a, b] = [...pts.values()];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        if (pinch) c.tDist = clamp(c.tDist * (pinch / d), this._zMin, this._zMax);
        pinch = d;
      }
    });
    const soltar = (e) => {
      pts.delete(e.pointerId); pinch = 0;
      if (!pts.size) { c.arrastrando = false; el.style.cursor = 'grab'; if (performance.now() - c.ultimo > 90) c.vAz = c.vEl = 0; }
    };
    this._on(el, 'pointerup', soltar);
    this._on(el, 'pointercancel', soltar);
    this._on(el, 'wheel', (e) => {
      e.preventDefault();
      c.tDist = clamp(c.tDist * Math.exp(e.deltaY * 0.0012), this._zMin, this._zMax);
      c.ultimo = performance.now();
    }, { passive: false });
    this._on(el, 'dblclick', () => this.resetearCamara());
    this._zMin = 0.5; this._zMax = 28.0;
  }

  resetearCamara() {
    const c = this._cam;
    c.vAz = c.vEl = 0; c.tDist = 14.2; c.ultimo = performance.now();
    c.tTarget.set(0, 0, 0);
    this._reset = { az: 0.75, el: 0.52 };
  }

  _aplicarCamara(dt) {
    const c = this._cam;
    if (this._reset) {
      c.az += difRad(c.az, this._reset.az) * 0.10; c.el += (this._reset.el - c.el) * 0.10;
      if (Math.abs(difRad(c.az, this._reset.az)) + Math.abs(c.el - this._reset.el) < 1e-3) this._reset = null;
    } else if (!c.arrastrando) {
      c.az += c.vAz * dt; c.el = clamp(c.el + c.vEl * dt, -1.35, 1.45);
      const f = Math.exp(-dt * 0.0048);                        // amortiguación inercial (~145 ms de vida media)
      c.vAz *= f; c.vEl *= f;
      if (Math.abs(c.vAz) < 1e-6) c.vAz = 0;
      if (Math.abs(c.vEl) < 1e-6) c.vEl = 0;
      // Giro lento de contemplación tras 6 s sin interacción
      if (this.opts.autoRotar && performance.now() - c.ultimo > 6000) c.az += 0.00011 * dt;
    }
    c.dist += (c.tDist - c.dist) * (1 - Math.exp(-dt * 0.011));
    c.target.lerp(c.tTarget, 1 - Math.exp(-dt * 0.018));
    this.camera.position.set(
      c.target.x + c.dist * Math.sin(c.az) * Math.cos(c.el),
      c.target.y + c.dist * Math.sin(c.el),
      c.target.z + c.dist * Math.cos(c.az) * Math.cos(c.el)
    );
    this.camera.lookAt(c.target);
  }

  /* ═══════════════════════════ Observadores / tamaño ═══════════════════════════ */

  _initObservadores() {
    this._ro = new ResizeObserver(() => this._resize());
    this._ro.observe(this.contenedor);
    this._io = new IntersectionObserver((es) => { this._visible = es[0].isIntersecting && !document.hidden; });
    this._io.observe(this.contenedor);
    this._on(document, 'visibilitychange', () => { this._visible = !document.hidden; });
    this._on(this.renderer.domElement, 'webglcontextlost', (e) => e.preventDefault());
  }

  _resize() {
    const w = this.contenedor.clientWidth || 1, h = this.contenedor.clientHeight || 1;
    this.renderer.setSize(w, h, false);
    const asp = w / h;
    this.camera.aspect = asp;
    this.camera.fov = asp < 1 ? 36 / Math.max(asp, 0.55) : 36;     // en vertical, la esfera sigue cabiendo
    this.camera.updateProjectionMatrix();
  }

  /* ═══════════════════════════ API de actualización ═══════════════════════════ */

  /** Actualiza la posición del observador (grados; lon Este +). */
  setObservador(latitud, longitud) {
    this._lat = latitud * DEG;
    if (typeof longitud === 'number') this._lon = longitud;
    this._orientarTierra();
  }

  /** Fija la hora de los aros mecánicos (Date) o `null` para el reloj del dispositivo. */
  setHora(fecha) { this._horaFija = fecha ? new Date(fecha) : null; }

  /** Muestra/oculta capas: 'aspectos' | 'casas' | 'etiquetas' | 'reloj'. */
  setCapa(nombre, visible) {
    this._capas[nombre] = !!visible;
    if (nombre === 'etiquetas') for (const a of Object.values(this._astros)) a.etiqueta.visible = !!visible && a.visible;
    if (nombre === 'reloj') this.reloj.visible = !!visible;
  }

  /**
   * Alimenta la esfera con los datos del motor astronómico.
   * @param {Object|Array} planetas  ver cabecera (longitud/latitud eclípticas en grados)
   * @param {Array|{cuspides:number[], mc?:number}} casas  12 longitudes de cúspide
   * @param {number|{grados?:number,horas?:number,radianes?:number}} siderealTime  TSL en grados
   */
  actualizarPosiciones(planetas, casas, siderealTime) {
    // — Planetas —
    const lista = [];
    if (Array.isArray(planetas)) {
      for (const p of planetas) lista.push([p.nombre ?? p.name ?? p.nombreAstro, p]);
    } else if (planetas && typeof planetas === 'object') {
      for (const [k, v] of Object.entries(planetas)) lista.push([v && v.nombre ? v.nombre : k, v]);
    }
    const vistos = new Set();
    for (const [nombre, v] of lista) {
      if (nombre == null || v == null) continue;
      const lon = typeof v === 'number' ? v : (v.lon ?? v.longitud ?? v.grado_absoluto ?? v.longitude);
      if (typeof lon !== 'number' || !isFinite(lon)) continue;
      const lat = typeof v === 'object' ? (v.lat ?? v.latitud ?? v.latitude ?? v.beta ?? 0) : 0;
      const clave = norm(nombre);
      const a = this._astro(clave, ASTROS[clave] || { ...GENERICO, nombre, glifo: GENERICO.glifo });
      a.lonT = mod(lon, 360); a.latT = lat;
      if (a.nuevo) { a.lon = a.lonT; a.lat = a.latT; a.nuevo = false; }
      a.visible = true; a.g.visible = true; a.etiqueta.visible = this._capas.etiquetas;
      if (a.rayoZod) a.rayoZod.visible = true;
      vistos.add(clave);

      // Actualizar badge con grado y signo zodiacal exactos [ ♂ Marte · 12° ♌ ]
      const sIdx = Math.floor(a.lonT / 30) % 12;
      const deg = Math.floor(a.lonT % 30);
      const sigGlifo = (SIGNOS[sIdx] && SIGNOS[sIdx][0]) || '';
      const bKey = `${deg}°_${sigGlifo}`;
      if (a.badgeKey !== bKey) {
        a.badgeKey = bKey;
        const nuevoMap = texturaBadgeAstro(a.def.glifo, a.def.nombre, `${deg}°`, sigGlifo, a.badgeColor);
        this._disp.push(nuevoMap);
        a.etiqueta.material.map = nuevoMap;
        a.etiqueta.material.needsUpdate = true;
      }
    }
    for (const [k, a] of Object.entries(this._astros)) {
      if (!vistos.has(k)) { a.visible = false; a.g.visible = false; a.etiqueta.visible = false; if (a.rayoZod) a.rayoZod.visible = false; }
    }

    // — Casas —
    const cus = Array.isArray(casas) ? casas : casas && casas.cuspides;
    if (Array.isArray(cus) && cus.length >= 12 && cus.every((x) => typeof x === 'number' && isFinite(x))) {
      this._cuspides = cus.slice(0, 12).map((x) => mod(x, 360));
      this._mcLon = !Array.isArray(casas) && typeof casas.mc === 'number' ? mod(casas.mc, 360) : this._cuspides[9];
    } else if (casas === null) {
      this._cuspides = null;
    }

    // — Tiempo sidéreo (grados); se extrapola en tiempo real entre actualizaciones —
    let lst = null;
    if (typeof siderealTime === 'number') lst = siderealTime;
    else if (siderealTime && typeof siderealTime === 'object') {
      if (typeof siderealTime.grados === 'number') lst = siderealTime.grados;
      else if (typeof siderealTime.horas === 'number') lst = siderealTime.horas * 15;
      else if (typeof siderealTime.radianes === 'number') lst = siderealTime.radianes / DEG;
    }
    if (lst !== null && isFinite(lst)) { this._lstRef = mod(lst, 360); this._lstRefEpoch = Date.now(); }
  }

  /* ═══════════════════════════ Bucle de render ═══════════════════════════ */

  iniciar() {
    if (this._corriendo) return;
    this._corriendo = true;
    this.renderer.setAnimationLoop((t) => this._frame(t));
  }
  detener() { this._corriendo = false; this.renderer.setAnimationLoop(null); }
  start() { this.iniciar(); }
  stop() { this.detener(); }

  _frame(ts) {
    if (!this._visible) { this._lastTs = ts; return; }
    const minDt = 1000 / this.opts.fpsMax - 1.5;
    if (ts - this._lastFrame < minDt) return;
    this._lastFrame = ts;
    const dt = this._lastTs ? Math.min(100, ts - this._lastTs) : 16;
    this._lastTs = ts;
    this._avanzar(dt);
    this.renderer.render(this.scene, this.camera);
  }

  renderizarUnaVez() {
    this._avanzar(16);
    this.renderer.render(this.scene, this.camera);
  }

  _lstActual() {
    if (this._lstRef === null) return tiempoSideralLocal(this._horaFija || new Date(), this._lon);
    if (!this.opts.autoAvanzar) return this._lstRef;
    return mod(this._lstRef + ((Date.now() - this._lstRefEpoch) / 86400000) * 360.98564736629, 360);
  }

  _avanzar(dtMs) {
    const t = (this._t += dtMs / 1000);
    this._aplicarCamara(dtMs);
    this._actualizarCielo(this._lstActual());
    this._actualizarAstros(t, dtMs);
    if (this._capas.casas) this._actualizarCasas(); else { this._husos.visible = false; this._numCasas.forEach((s) => (s.visible = false)); }
    this._actualizarAspectos(t);
    if (this._capas.reloj) this._actualizarReloj(t);

    // Uniformes de tiempo / luz
    this._husosU.uTime.value = t;
    this._polvoU.uTime.value = t;
    const sol = this._astros.sol;
    if (sol && sol.visible) {
      sol.g.getWorldPosition(this._tmp.v);
      this.root.worldToLocal(this._tmp.v);
      this._polvoU.uSun.value.copy(this._tmp.v);
      this._luzSol.visible = true;
      this._luzSol.position.copy(sol.g.position);
    } else {
      this._luzSol.visible = false;
      this._polvoU.uSun.value.set(0, 0, 0);
    }
    if (this._solMat) this._solMat.uniforms.uTime.value = t;
    if (this._coronaMat) this._coronaMat.uniforms.uTime.value = t;
    if (this._fondoMat) this._fondoMat.uniforms.uTime.value = t;
    if (this._estrellasMat) this._estrellasMat.uniforms.uTime.value = t;
    if (this._haloZenit) this._haloZenit.material.opacity = 0.75 + 0.2 * Math.sin(t * 1.6);
    this._vela.intensity = (this._phys ? 110 : 1.7) * (1 + 0.035 * Math.sin(t * 7.3) * Math.sin(t * 3.1)); // parpadeo de vela
  }

  /**
   * Rotación diurna: matriz marco ecuatorial → marco del observador con el TSL θ.
   *   X_eq (α=0)  → (−sinθ,  cosφ·cosθ,  sinφ·cosθ)
   *   Polo        → (   0,   sinφ,       −cosφ    )
   *   Y_eq (α=90) → ( cosθ,  cosφ·sinθ,   sinφ·sinθ)
   * Exacta para cualquier latitud (también hemisferio sur).
   */
  _actualizarCielo(lstDeg) {
    const th = lstDeg * DEG, ph = this._lat;
    const sT = Math.sin(th), cT = Math.cos(th), sP = Math.sin(ph), cP = Math.cos(ph);
    const xEq = this._tmp.v.set(-sT, cP * cT, sP * cT);
    const polo = this._tmp.v2.set(0, sP, -cP);
    const yEq = new THREE.Vector3(cT, cP * sT, sP * sT).negate();      // base local: Z = −Y_eq
    this.cielo.matrix.makeBasis(xEq, polo, yEq);
    this.cielo.matrixWorldNeedsUpdate = true;
    this.eclip.matrixWorldNeedsUpdate = true;
  }

  _actualizarAstros(t, dtMs) {
    const k = 1 - Math.exp(-dtMs * 0.006);                              // suavizado de transiciones
    for (const a of Object.values(this._astros)) {
      if (!a.visible) continue;
      a.lon = mod(a.lon + difAng(a.lon, a.lonT) * k, 360);
      a.lat += (a.latT - a.lat) * k;
      const r = a.def.rOrb || 2.5;
      posEclip(a.lon, a.lat, r, a.g.position);
      a.etiqueta.position.set(a.g.position.x, a.g.position.y + a.def.r + 0.16, a.g.position.z);
      const pulso = 1 + 0.10 * Math.sin(t * 1.7 + a.semilla);
      a.halo.scale.setScalar(a.def.r * 7.5 * pulso);
      a.halo.material.opacity = 0.42 + 0.16 * Math.sin(t * 2.1 + a.semilla);
      for (const m of a.spin) m.rotation.y += dtMs * 0.0004;
      if (a.rayos) { a.rayos.material.rotation += dtMs * 0.00012; a.rayos.scale.setScalar(a.def.r * 11 * (1 + 0.06 * Math.sin(t * 1.3))); }
      if (a.clave === 'sol' && this._luzSol) {
        this._luzSol.position.copy(a.g.position);
      }
      if (a.rayoZod) {
        const pa = a.rayoZod.geometry.attributes.position.array;
        pa[0] = a.g.position.x; pa[1] = a.g.position.y; pa[2] = a.g.position.z;
        const l = a.lon * DEG;
        pa[3] = R_ZODIACO * Math.cos(l); pa[4] = 0; pa[5] = -R_ZODIACO * Math.sin(l);
        a.rayoZod.geometry.attributes.position.needsUpdate = true;
      }
    }
  }

  _actualizarAspectos(t) {
    const pool = this._aspPool, K = this._aspKeys;
    let n = 0;
    if (this._capas.aspectos) {
      const UP = this._tmp.v2.set(0, 1, 0);
      for (let i = 0; i < K.length; i++) {
        const A = this._astros[K[i]];
        if (!A || !A.visible) continue;
        for (let j = i + 1; j < K.length; j++) {
          const B = this._astros[K[j]];
          if (!B || !B.visible) continue;
          const sep = Math.abs(difAng(A.lon, B.lon));
          for (const asp of ASPECTOS) {
            const orbe = asp.orbe + (i < 2 || j < 2 ? 1.5 : 0);        // luminares: orbe ampliado
            const dev = Math.abs(sep - asp.ang);
            if (dev >= orbe) continue;
            const s = 1 - dev / orbe;                                  // 1 = exacto
            const m = pool[n++];
            const u = m.material.uniforms;
            const dir = this._tmp.v.copy(B.g.position).sub(A.g.position);
            const len = dir.length();
            m.position.copy(A.g.position).addScaledVector(dir, 0.5);
            dir.multiplyScalar(1 / len);
            m.quaternion.setFromUnitVectors(UP, dir);
            const pulso = 0.80 + 0.20 * Math.sin(t * 2.1 + u.uSeed.value);
            const w = (0.007 + 0.015 * s) * (1 + 0.28 * Math.sin(t * 3.0 + u.uSeed.value));
            m.scale.set(w, len, w);
            u.uColor.value.setHex(asp.color);
            u.uStr.value = (0.35 + 0.65 * s) * pulso;
            u.uLen.value = len; u.uTime.value = t;
            m.visible = true;
            break;
          }
        }
      }
    }
    for (let i = n; i < pool.length; i++) pool[i].visible = false;
  }

  _actualizarCasas() {
    const cus = this._cuspides;
    if (!cus) { this._husos.visible = false; this._numCasas.forEach((s) => (s.visible = false)); return; }
    this._husos.visible = true;
    // Cúspide → dirección en el marco del observador → acimut ψ alrededor del eje N–S.
    const M = this._tmp.m.multiplyMatrices(this.cielo.matrix, this.eclip.matrix);
    const v = this._tmp.v;
    const psi = new Array(12);
    for (let i = 0; i < 12; i++) {
      const l = cus[i] * DEG;
      v.set(Math.cos(l), 0, -Math.sin(l)).applyMatrix4(M);
      psi[i] = Math.atan2(v.y, v.x);
    }
    const st = this._husosU.uStart.value, sp = this._husosU.uSpan.value;
    for (let i = 0; i < 12; i++) {
      st[i] = psi[i];
      sp[i] = difRad(psi[i], psi[(i + 1) % 12]);
      const mid = psi[i] + sp[i] / 2;
      const s = this._numCasas[i];
      s.position.set(Math.cos(mid), Math.sin(mid), 0).multiplyScalar(R_HUSOS * 0.93);
      s.visible = this._capas.etiquetas;
    }
    // Puntos angulares sobre la eclíptica (AC, DC, MC, IC)
    const ang = [cus[0], mod(cus[0] + 180, 360), this._mcLon ?? cus[9], mod((this._mcLon ?? cus[9]) + 180, 360)];
    this._angulares.forEach((s, i) => { posEclip(ang[i], 0, R_ZODIACO * 1.04, s.position); s.visible = true; });
  }

  /** Aros mecánicos: horas (1 rev/12 h), minutos (1 rev/h), segundos con paso de escape. */
  _actualizarReloj(t) {
    const d = this._horaFija || new Date();
    const ms = d.getMilliseconds(), s = d.getSeconds(), m = d.getMinutes(), h = d.getHours() % 12;
    // Paso de escape suizo: el aro de segundos avanza a saltos con un leve rebote.
    const f = ms / 1000;
    const x = f < 0.14 ? f / 0.14 : 1;
    const paso = f < 0.14 ? 1 + 2.2 * Math.pow(x - 1, 3) + 1.2 * Math.pow(x - 1, 2) : 1;
    const segTot = s + clamp(paso, 0, 1.08);
    this._anillos.seg.rotation.y = (segTot / 60) * TAU;
    this._anillos.min.rotation.y = ((m + (s + f) / 60) / 60) * TAU;
    this._anillos.hor.rotation.y = ((h + (m + (s + f) / 60) / 60) / 12) * TAU;
    // Escape: volante a 2.5 Hz (18 000 alternancias/h) y áncora que bascula con cada impulso.
    const fase = Math.sin(TAU * 2.5 * t);
    this._volante.rotation.y = 1.35 * fase;
    this._ancora.rotation.y = 0.20 * Math.tanh(5 * fase);
    const br = 0.45 + 0.25 * Math.sin(t * 2.2);
    for (let i = 0; i < this._joyasReloj.length; i++) {
      const o = this._joyasReloj[i];
      if (o.isSprite) o.material.opacity = 0.55 + br * 0.5;
    }
  }

  /* ═══════════════════════════ Liberación de recursos ═══════════════════════════ */

  destruir() {
    this.detener();
    this._ro && this._ro.disconnect();
    this._io && this._io.disconnect();
    this._listeners.forEach((off) => off());
    this.scene.traverse((o) => {
      if (o.geometry) o.geometry.dispose();
      if (o.material) (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => m.dispose());
    });
    this._disp.forEach((d) => d && d.dispose && d.dispose());
    this.renderer.dispose();
    this.renderer.domElement.remove();
  }
  dispose() { this.destruir(); }
}

EsferaArmilarPro.math = { tiempoSideralLocal, posEclip, OBLIQUIDAD };

if (typeof window !== 'undefined') window.EsferaArmilarPro = EsferaArmilarPro;

export default EsferaArmilarPro;
