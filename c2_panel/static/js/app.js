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
const basePrompts = {
    h1_report: `Actúa como un Bug Bounty Hunter top tier. Voy a pasarte los detalles técnicos de una vulnerabilidad que encontré.
Quiero que redactes un reporte perfecto para HackerOne siguiendo esta estructura exacta:
1. Resumen Ejecutivo
2. Descripción Detallada
3. Pasos para Reproducir (Paso a paso, claros)
4. Impacto Real en el Negocio
5. Mitigación Recomendada

No inventes datos. Usa un tono extremadamente profesional, neutro y técnico.
Datos del Bug (Extraídos de OCI-1):
[RAW_DATA]`,

    js_analysis: `Actúa como un analista de código estático (SAST). 
Te voy a pegar el contenido crudo de subdominios y activos detectados por OCI-1.
Tu trabajo es identificar:
1. Dominios de alto valor (paneles admin, APIs internas).
2. Patrones inusuales que indiquen vulnerabilidades.
3. Posibles vectores de ataque basados en los nombres de subdominios.

Datos de OCI-1:
[RAW_DATA]`
};

let lastRawData = "Esperando extracción de datos de OCI-1...";

async function generarPrompt(tipo) {
    const modal = document.getElementById('prompt-modal');
    const textarea = document.getElementById('prompt-text');
    
    // Mostramos estado de carga
    textarea.value = "Extrayendo telemetría cruda de OCI-1 por SSH... Espere...";
    modal.classList.add('show');
    
    try {
        const response = await fetch('/api/raw_data');
        const result = await response.json();
        if (result.status === 'success' || result.data) {
            lastRawData = result.data;
        }
    } catch (error) {
        lastRawData = "Error: OCI-1 no alcanzó a enviar los datos.";
    }
    
    let promptFinal = basePrompts[tipo].replace('[RAW_DATA]', lastRawData);
    textarea.value = promptFinal;
}

// LOGS CRUDOS AL ABRIR TERMINAL
document.addEventListener('DOMContentLoaded', () => {
    // Escuchar clics en la tab de Terminal para cargar data cruda
    const terminalTab = document.querySelectorAll('.nav-item')[2];
    terminalTab.addEventListener('click', async () => {
        appendTerminal("[INFO] Solicitando volcado de datos crudos (actual.json)...");
        try {
            const res = await fetch('/api/raw_data');
            const data = await res.json();
            if(data.data) {
                appendTerminal("=== INICIO ACTUAL.JSON ===");
                appendTerminal(data.data.substring(0, 1000) + "... (truncado)");
                appendTerminal("=== FIN ===");
            }
        } catch (e) {
            appendTerminal("[ERROR] Falló extracción de data cruda.");
        }
    });
});

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
