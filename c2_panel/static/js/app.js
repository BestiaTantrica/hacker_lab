// Lógica Mobile-First y Generadores de Prompts

document.addEventListener('DOMContentLoaded', () => {
    checkOciStatus();
    setInterval(checkOciStatus, 30000);
});

// NAVEGACIÓN ENTRE VISTAS
function switchView(viewId, navElement) {
    // Ocultar todas las vistas
    document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
    // Mostrar la seleccionada
    document.getElementById('view-' + viewId).classList.add('active');
    
    // Actualizar nav bar
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    navElement.classList.add('active');
}

// TELEMETRÍA
async function checkOciStatus() {
    const dot = document.getElementById('oci-status-dot');
    const text = document.getElementById('oci-status-text');
    const targets = document.getElementById('targets-count');

    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        if (data.status === 'online') {
            dot.className = 'dot green';
            text.textContent = 'OCI-1 ONLINE';
            targets.textContent = data.targets;
            appendTerminal(`[INFO] Telemetría OK. Targets listos: ${data.targets}`);
        } else {
            dot.className = 'dot red';
            text.textContent = 'OCI-1 OFFLINE';
            appendTerminal(`[ERROR] Conexión fallida: ${data.message || 'SSH timeout'}`);
        }
    } catch (error) {
        dot.className = 'dot red';
        text.textContent = 'API ERROR';
        appendTerminal(`[ERROR] Panel C2 backend no responde.`);
    }
}

function appendTerminal(msg) {
    const terminal = document.getElementById('terminal-output');
    const time = new Date().toLocaleTimeString();
    terminal.innerHTML += `<br>> [${time}] ${msg}`;
    terminal.scrollTop = terminal.scrollHeight;
}

// GENERADOR DE PROMPTS MAESTROS
const prompts = {
    h1_report: `Actúa como un Bug Bounty Hunter top tier. Voy a pasarte los detalles técnicos de una vulnerabilidad que encontré.
Quiero que redactes un reporte perfecto para HackerOne siguiendo esta estructura exacta:
1. Resumen Ejecutivo
2. Descripción Detallada
3. Pasos para Reproducir (Paso a paso, claros)
4. Impacto Real en el Negocio
5. Mitigación Recomendada

No inventes datos. Usa un tono extremadamente profesional, neutro y técnico.
Datos del Bug:
[PEGAR_AQUI_EVIDENCIA]`,

    js_analysis: `Actúa como un analista de código estático (SAST). 
Te voy a pegar el contenido de un archivo Javascript (app.js) extraído de un target de bug bounty.
Tu trabajo es identificar:
1. Endpoints hardcodeados de APIs internas o versiones antiguas (ej: /api/v1/)
2. Secretos, Tokens o API Keys (AWS, Stripe, etc).
3. Lógica expuesta sobre roles (isAdmin === true)
4. Rutas ocultas no enlazadas en la UI.

Si está ofuscado o minificado, intenta deducir los nombres de variables clave.
Archivo JS:
[PEGAR_JS_AQUI]`
};

function generarPrompt(tipo) {
    const modal = document.getElementById('prompt-modal');
    const textarea = document.getElementById('prompt-text');
    
    textarea.value = prompts[tipo];
    modal.classList.add('show');
}

function cerrarModal() {
    document.getElementById('prompt-modal').classList.remove('show');
}

function copiarPrompt() {
    const textarea = document.getElementById('prompt-text');
    textarea.select();
    document.execCommand('copy');
    
    const btn = document.querySelector('.btn-success');
    const oldText = btn.textContent;
    btn.textContent = '¡Copiado!';
    setTimeout(() => { btn.textContent = oldText; }, 2000);
}
