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

// LOGICA DE SUPERVISION AUTONOMA
let pocActual = "";

// La lógica ahora es interactiva por botón, no periódica
// Quitamos el checkTriaje del ciclo de status
const originalCheck = checkOciStatus;
checkOciStatus = async function() {
    await originalCheck();
}

function verificarManual() {
    const modal = document.getElementById('prompt-modal');
    const textarea = document.getElementById('prompt-text');
    
    // Le pasamos el POC a la IA con un prompt duro de "Skill"
    const promptSkill = `Soy el Auditor de un pipeline autónomo de Bug Bounty. El sistema reportó este posible hallazgo mediante su eslabón automático:
---
${pocActual}
---
Necesito verificar si esto es un falso positivo. Dime exactamente los pasos que debo realizar manualmente (por ejemplo, con Burp Suite o el navegador) para confirmar que la vulnerabilidad es real.`;

    textarea.value = promptSkill;
    modal.classList.add('show');
}

function generarReporteFinal() {
    const modal = document.getElementById('prompt-modal');
    const textarea = document.getElementById('prompt-text');
    
    const promptReporte = `Actúa como Bug Bounty Hunter. He verificado manualmente que este bug es real siguiendo tus pasos.
Datos técnicos del sistema:
---
${pocActual}
---
Redacta el reporte H1 final (Resumen, Descripción, Impacto, Pasos para Reproducir y Mitigación). No inventes datos.`;

    textarea.value = promptReporte;
    modal.classList.add('show');
}

// LANZAR ATAQUE (ESLABON)

async function ejecutarEslabon(tipo) {
    const btn = event.target;
    const originalText = btn.textContent;
    
    btn.textContent = "Ejecutando en OCI-1... (Puede demorar mins)";
    btn.disabled = true;
    appendTerminal(`[INFO] Disparando eslabón de explotación: ${tipo}`);
    
    const inbox = document.getElementById('inbox-card');
    inbox.style.display = 'none'; // Ocultar resultados anteriores
    
    try {
        const response = await fetch('/api/execute_exploit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo: tipo })
        });
        
        const result = await response.json();
        const pocContainer = document.getElementById('poc-content');
        
        if (result.status === 'success') {
            appendTerminal(`[OK] Eslabón ${tipo} completado con éxito.`);
            pocActual = result.data;
            pocContainer.textContent = result.data;
            inbox.style.display = 'block'; // Mostrar la caja de triaje con los resultados
            
            // Scrollear hacia abajo suavemente para que el usuario vea el resultado
            inbox.scrollIntoView({ behavior: 'smooth' });
        } else {
            appendTerminal(`[ERROR] Falló la ejecución del eslabón: ${result.data}`);
            alert(`Error ejecutando eslabón: ${result.data}`);
        }
    } catch (error) {
        appendTerminal("[ERROR] Falló la conexión con el panel para ejecutar el ataque.");
        alert("Error de red intentando lanzar el ataque.");
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
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
