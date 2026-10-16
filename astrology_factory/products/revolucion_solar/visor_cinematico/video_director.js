/**
 * video_director.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Director Cinemático y Grabador en Alta Definición (1080p @ 30 FPS).
 * Sincroniza la cámara del navegador y los efectos de luz con el relato de audio
 * del Capítulo 1 de Tomás (121.3s).
 * ─────────────────────────────────────────────────────────────────────────────
 */

const CHOREOGRAPHY_CAPITULO1 = [
  // 00:00 - 00:14: Acto 1 Apertura - Plano General Cósmico (Carta Natal Base)
  {
    time: 0.0,
    run: (nav) => {
      nav.setMode('natal', document.getElementById('btn-mode-natal'));
      nav.flyTo(0, 0, 1.0);
      nav.selectedTarget = null;
      document.getElementById('director-badge').innerText = "ACTO 1: RAÍZ NATAL • PLANO GENERAL";
    }
  },
  // 00:14 - 00:28: Zoom Quirúrgico al Sol y Mercurio en Aries (ADN del Consultante)
  {
    time: 14.0,
    run: (nav) => {
      const sol = nav.natalLayout.find(i => i.nombre === 'Sol');
      if (sol) {
        nav.selectTarget({ type: 'natal', nombre: 'Sol', data: sol.data, x: sol.displayPos.x, y: sol.displayPos.y });
        nav.flyTo(sol.displayPos.x, sol.displayPos.y, 2.3);
      }
      document.getElementById('director-badge').innerText = "ACTO 1: ENFOQUE ☉ SOL EN ARIES (CASA 3)";
    }
  },
  // 00:28 - 00:39.3: Transición hacia Plano General contemplativo
  {
    time: 28.0,
    run: (nav) => {
      nav.selectedTarget = null;
      nav.flyTo(0, 0, 1.15);
      document.getElementById('director-badge').innerText = "ACTO 1: SÍNTESIS DE ILUMINACIÓN Y PENUMBRA";
    }
  },
  // 00:39.3 - 00:48.0: ACTO 2 - Acoplamiento Orbital de la Revolución Solar 2026
  {
    time: 39.3,
    run: (nav) => {
      nav.setMode('transicion', document.getElementById('btn-mode-trans'));
      nav.flyTo(0, 0, 1.25);
      document.getElementById('director-badge').innerText = "ACTO 2: ACOPLAMIENTO ORBITAL RS 2026";
    }
  },
  // 00:48.0 - 00:57.1: Enfoque al Portal del Ascendente RS en Libra 14°21'
  {
    time: 48.0,
    run: (nav) => {
      const ascRS = nav.rs.angulos_rs.Ascendente_RS;
      const pos = nav.polarToXY(nav.degToRad(ascRS.grado_absoluto), nav.radii.rsPlanets);
      nav.flyTo(pos.x, pos.y, 2.0);
      document.getElementById('director-badge').innerText = "ACTO 2: PUERTA DE ENTRADA • LIBRA 14°";
    }
  },
  // 00:57.14 - 00:75.0: ACTO 3 - Contraste con el Ascendente Natal en Acuario
  {
    time: 57.14,
    run: (nav) => {
      const pos = nav.polarToXY(Math.PI, nav.radii.zodiacInner);
      nav.flyTo(pos.x, pos.y, 2.2);
      document.getElementById('director-badge').innerText = "ACTO 3: CONTRASTE CON ASCENDENTE NATAL EN ACUARIO";
    }
  },
  // 00:75.0 - 00:98.0: Vuelo Cinemático al Gran Portal: Casa 9 Natal (Saturno, Plutón, Júpiter y Portal RS)
  {
    time: 75.0,
    run: (nav) => {
      const ascRS = nav.rs.angulos_rs.Ascendente_RS;
      const pos = nav.polarToXY(nav.degToRad(ascRS.grado_absoluto), nav.radii.rsPlanets);
      nav.flyTo(pos.x, pos.y, 2.45);
      document.getElementById('director-badge').innerText = "ACTO 3: PORTAL ANUAL • CASA 9 NATAL (LIBRA 14°)";
    }
  },
  // 00:98.0 - 01:22.0: Inspección de los Nudos Viejos y Pactos (Saturno en Libra)
  {
    time: 98.0,
    run: (nav) => {
      const sat = nav.natalLayout.find(i => i.nombre === 'Saturno');
      if (sat) {
        nav.selectTarget({ type: 'natal', nombre: 'Saturno', data: sat.data, x: sat.displayPos.x, y: sat.displayPos.y });
        nav.flyTo(sat.displayPos.x, sat.displayPos.y, 2.3);
      }
      document.getElementById('director-badge').innerText = "ACTO 3: SATURNO Y PLUTÓN • LÍMITES Y PACTOS";
    }
  },
  // 01:22.0 - 02:26.0: Cierre Triunfal - Plano General Bi-Wheel Completa Resplandeciente
  {
    time: 122.0,
    run: (nav) => {
      nav.selectedTarget = null;
      nav.flyTo(0, 0, 1.0);
      document.getElementById('director-badge').innerText = "ACTO 3: EL HORIZONTE DEL AÑO • BI-WHEEL COMPLETA";
    }
  }
];

class VideoDirector {
  constructor(navigator) {
    this.nav = navigator;
    this.audio = new Audio('audio_capitulo1.mp3');
    this.totalDuration = 146.0; // 2 minutos y 26 segundos sincronizados al relato humano
    this.isRecording = false;
    this.mediaRecorder = null;
    this.recordedChunks = [];
    this.timerInterval = null;
    this.stepIndex = 0;

    this.initControls();
  }

  initControls() {
    const btnRecord = document.getElementById('btn-record-capitulo1');
    if (btnRecord) {
      btnRecord.addEventListener('click', () => {
        if (!this.isRecording) {
          this.startDirector({ record: true });
        } else {
          this.stopDirector();
        }
      });
    }

    // Comprobar parámetro de URL ?autorecord=1 para ejecución headless automática
    const params = new URLSearchParams(window.location.search);
    if (params.get('autorecord') === '1') {
      console.log("Iniciando auto-grabación headless...");
      setTimeout(() => this.startDirector({ record: true, headless: true }), 1500);
    }
  }

  startDirector({ record = true, headless = false }) {
    this.isRecording = true;
    this.stepIndex = 0;
    this.recordedChunks = [];

    const overlay = document.getElementById('recording-overlay');
    if (overlay) overlay.style.display = 'flex';

    const btnRecord = document.getElementById('btn-record-capitulo1');
    if (btnRecord) {
      btnRecord.classList.add('recording-pulse');
      btnRecord.innerHTML = '<span>⏹️</span> Detener Render';
    }

    // Configurar MediaRecorder sobre el Canvas a 1920x1080 @ 30 FPS
    if (record) {
      const stream = this.nav.canvas.captureStream(30);
      const options = {
        mimeType: 'video/webm; codecs=vp9',
        videoBitsPerSecond: 12000000 // 12 Mbps broadcast quality
      };

      try {
        this.mediaRecorder = new MediaRecorder(stream, options);
      } catch (e) {
        console.warn("VP9 no soportado, intentando VP8/default", e);
        this.mediaRecorder = new MediaRecorder(stream);
      }

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          this.recordedChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        this.finishRecording(headless);
      };

      this.mediaRecorder.start(250); // Emitir chunks cada 250ms
      console.log("MediaRecorder iniciado a 30 FPS.");
    }

    // Iniciar Audio y Reloj de Dirección
    this.audio.currentTime = 0;
    if (!headless) {
      this.audio.play().catch(e => console.log("Audio autoplay bloqueado, continuando en modo silencioso:", e));
    }

    const startTime = performance.now();
    this.timerInterval = setInterval(() => {
      const elapsed = (performance.now() - startTime) / 1000;
      this.updateProgress(elapsed);

      // Ejecutar pasos de la coreografía cuando corresponda
      while (this.stepIndex < CHOREOGRAPHY_CAPITULO1.length &&
             elapsed >= CHOREOGRAPHY_CAPITULO1[this.stepIndex].time) {
        CHOREOGRAPHY_CAPITULO1[this.stepIndex].run(this.nav);
        this.stepIndex++;
      }

      // Finalizar al cumplir la duración
      if (elapsed >= this.totalDuration) {
        this.stopDirector();
      }
    }, 100);
  }

  updateProgress(elapsed) {
    const recTimer = document.getElementById('rec-timer');
    if (recTimer) {
      const m = Math.floor(elapsed / 60).toString().padStart(2, '0');
      const s = Math.floor(elapsed % 60).toString().padStart(2, '0');
      recTimer.innerText = `${m}:${s} / 02:01`;
    }

    const progressBar = document.getElementById('rec-progress-fill');
    if (progressBar) {
      const pct = Math.min(100, (elapsed / this.totalDuration) * 100);
      progressBar.style.width = `${pct}%`;
    }
  }

  stopDirector() {
    this.isRecording = false;
    clearInterval(this.timerInterval);
    this.audio.pause();

    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
    }

    const btnRecord = document.getElementById('btn-record-capitulo1');
    if (btnRecord) {
      btnRecord.classList.remove('recording-pulse');
      btnRecord.innerHTML = '<span>🎬</span> Renderizar Video (MP4)';
    }
  }

  async finishRecording(headless) {
    console.log("Grabación finalizada. Generando blob WebM...");
    const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
    console.log(`Blob WebM creado: ${(blob.size / (1024 * 1024)).toFixed(2)} MB`);

    const overlayMsg = document.getElementById('recording-status-msg');
    if (overlayMsg) overlayMsg.innerText = "Transfiriendo y ensamblando con FFmpeg a 1080p...";

    try {
      // Enviar el video al servidor backend local para ensamble con FFmpeg
      const response = await fetch('/api/save_render', {
        method: 'POST',
        headers: { 'Content-Type': 'video/webm' },
        body: blob
      });

      const resJson = await response.json();
      console.log("Respuesta del servidor:", resJson);

      if (overlayMsg) {
        overlayMsg.innerHTML = `✅ <strong>¡Video 1080p generado con éxito!</strong><br><small>${resJson.output_file || 'Guardado en disco'}</small>`;
      }

      setTimeout(() => {
        const overlay = document.getElementById('recording-overlay');
        if (overlay) overlay.style.display = 'none';
      }, 5000);

    } catch (err) {
      console.error("Error al transferir video al servidor:", err);
      // Fallback: Descarga local en navegador
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'capitulo1_render_vectorial.webm';
      a.click();
      if (overlayMsg) overlayMsg.innerText = "Descarga local completada.";
    }
  }
}

// Iniciar Director cuando el AstroNavigator esté listo
window.addEventListener('DOMContentLoaded', () => {
  const checkInterval = setInterval(() => {
    if (window.astroNavigator) {
      clearInterval(checkInterval);
      window.videoDirector = new VideoDirector(window.astroNavigator);
    }
  }, 100);
});
