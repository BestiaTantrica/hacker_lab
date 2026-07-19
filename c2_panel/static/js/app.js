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

const basePrompts = {
    fase1_recon: `Actúa como mi Mentor y Orquestador Táctico en Bug Bounty.
He obtenido la siguiente telemetría nueva desde mi infraestructura automatizada de reconocimiento (OCI-1):
---
[RAW_DATA]
---
Basado en estos subdominios, explícame brevemente y como si fuera un estudiante:
1. ¿Qué tipo de infraestructura parece ser? (Ej: CDN, plataformas SaaS, etc).
2. De las automatizaciones que tengo listas en mi sistema (Takeovers, CORS, Archivos Expuestos), ¿cuál tiene más sentido ejecutar aquí y por qué?`,

    fase2_triaje: `Actúa como mi Analista de Triaje. He ejecutado el eslabón de automatización en mi infraestructura y ha devuelto los siguientes resultados crudos (PoC):
---
[AUTOMATED_POC_DATA]
---
Por favor, analiza esta salida y enséñame:
1. ¿Hubo algún hallazgo real o son probables falsos positivos? Explícame por qué.
2. Si hay un hallazgo válido, ¿qué paso manual EXACTO (usando Burp Suite o el navegador) debo hacer yo para confirmar visualmente que el bug existe antes de reportarlo?`,

    fase3_reporte: `Actúa como un Bug Bounty Hunter top tier. He seguido tus instrucciones, he verificado manualmente la vulnerabilidad, y el bug es real.
La evidencia técnica capturada originalmente por el sistema es esta:
---
[AUTOMATED_POC_DATA]
---
Quiero que redactes un reporte para HackerOne con esta estructura exacta:
1. Resumen Ejecutivo
2. Descripción Detallada
3. Pasos para Reproducir (Incluyendo la verificación manual que discutimos)
4. Impacto Real
5. Mitigación Recomendada

No inventes datos que no estén en la evidencia. Usa un tono neutro y técnico.`
};

let lastRawData = "Esperando extracción de datos de OCI-1...";
let lastPocData = "Esperando evidencia (PoC) automática de OCI-1...";

async function generarPrompt(tipo) {
    const modal = document.getElementById('prompt-modal');
    const textarea = document.getElementById('prompt-text');
    
    if (tipo === 'fase1_recon') {
        textarea.value = "Extrayendo telemetría resumida de OCI-1 por SSH... Espere...";
        modal.classList.add('show');
        
        try {
            const response = await fetch('/api/raw_data');
            const result = await response.json();
            if (result.status === 'success' && result.data) {
                const dataLines = result.data.split('\\n').slice(-30).join('\\n');
                lastRawData = dataLines || "Sin datos recientes.";
            }
        } catch (error) {
            lastRawData = "Error: OCI-1 no alcanzó a enviar los datos.";
        }
        
        textarea.value = basePrompts[tipo].replace('[RAW_DATA]', lastRawData);
    } else if (tipo === 'fase2_triaje' || tipo === 'fase3_reporte') {
        textarea.value = "Extrayendo resultados/evidencia (PoC) de OCI-1 por SSH... Espere...";
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
