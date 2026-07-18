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

// GENERADOR DE PROMPTS MAESTROS (Con Eslabones Integrados)
const basePrompts = {
    orquestador_ia: `Actúa como el Orquestador Táctico de mi laboratorio de Bug Bounty.
El servidor de reconocimiento (OCI-1) detectó la siguiente telemetría reciente:
---
[RAW_DATA]
---

Para explotar o profundizar, disponemos de los siguientes "Eslabones" (Scripts) en el servidor:
1. [IDOR Cross-Tenant]: \`python3 LAB/api/idor_cross_tenant.py --target <URL>\` (Para plataformas SaaS/Multi-tenant)
2. [Scanner de APIs]: \`python3 LAB/api/auditor_freshdesk.py\` (Específico para Freshworks/CRM)
3. [Explotador Masivo]: \`python3 LAB/api/explotador_automatico.py\` (Takeovers y CORS)

Tu tarea: Analiza la telemetría, identifica el activo más prometedor, y respóndeme ÚNICAMENTE con el comando exacto que debo ejecutar basado en nuestros Eslabones. No alucines comandos que no existen.`,

    h1_report: `Actúa como un Bug Bounty Hunter top tier. He confirmado una vulnerabilidad usando nuestro eslabón automatizado.
Quiero que redactes un reporte para HackerOne con esta estructura exacta:
1. Resumen Ejecutivo
2. Descripción Detallada
3. Pasos para Reproducir (Mencionando herramientas estándar como Burp Suite o cURL)
4. Impacto Real
5. Mitigación Recomendada

No inventes datos. Usa un tono neutro y técnico.
Datos confirmados del Bug (Generado automáticamente por el Eslabón):
[AUTOMATED_POC_DATA]`
};

let lastRawData = "Esperando extracción de datos de OCI-1...";
let lastPocData = "Esperando evidencia (PoC) automática de OCI-1...";

async function generarPrompt(tipo) {
    const modal = document.getElementById('prompt-modal');
    const textarea = document.getElementById('prompt-text');
    
    // Mostramos estado de carga solo si requiere data cruda
    if (tipo === 'orquestador_ia') {
        textarea.value = "Extrayendo telemetría resumida de OCI-1 por SSH... Espere...";
        modal.classList.add('show');
        
        try {
            const response = await fetch('/api/raw_data');
            const result = await response.json();
            if (result.status === 'success' && result.data) {
                // Truncar para no saturar a la IA (Evitar exceso de contexto)
                const dataLines = result.data.split('\\n').slice(-30).join('\\n');
                lastRawData = dataLines || "Sin datos recientes.";
            }
        } catch (error) {
            lastRawData = "Error: OCI-1 no alcanzó a enviar los datos.";
        }
        
        textarea.value = basePrompts[tipo].replace('[RAW_DATA]', lastRawData);
    } else if (tipo === 'h1_report') {
        textarea.value = "Extrayendo Evidencia Automática (PoC) de OCI-1 por SSH... Espere...";
        modal.classList.add('show');
        
        try {
            const response = await fetch('/api/get_poc');
            const result = await response.json();
            if (result.status === 'success' && result.data) {
                lastPocData = result.data;
            }
        } catch (error) {
            lastPocData = "Error: Falló la comunicación con OCI-1 para extraer el PoC.";
        }
        
        textarea.value = basePrompts[tipo].replace('[AUTOMATED_POC_DATA]', lastPocData);
    } else {
        textarea.value = basePrompts[tipo];
        modal.classList.add('show');
    }
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
