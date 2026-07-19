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

// LOGICA DE SUPERVISION AUTONOMA
let pocActual = "";

// Función para generar un template base de H1 según el tipo de bug
function generarPlantillaH1(hallazgo) {
    let tipo = hallazgo.tipo || "Vulnerabilidad Desconocida";
    let url = hallazgo.url || "N/A";
    
    if (tipo === "cors") {
        return `## Title: CORS Misconfiguration with Credentials allowed on ${url}
## Description:
The endpoint \`${url}\` is vulnerable to Cross-Origin Resource Sharing (CORS) misconfiguration. It reflects the Origin header back and sets \`Access-Control-Allow-Credentials: true\`. 
This allows an attacker to send an authenticated cross-origin request and read the sensitive response data.

## Steps To Reproduce:
1. Open a browser and navigate to an attacker-controlled domain.
2. Execute the following JavaScript (or use Burp):
\`\`\`javascript
var req = new XMLHttpRequest();
req.onload = req.onerror = function() { console.log(req.responseText); };
req.open('GET', '${url}', true);
req.withCredentials = true;
req.send();
\`\`\`
3. Notice that the sensitive data is successfully returned to the attacker's origin.

## Impact
An attacker can craft a malicious page, trick an authenticated victim into visiting it, and steal their sensitive account information or perform unauthorized actions on their behalf.`;
    }
    
    if (tipo === "exposed_file") {
        return `## Title: Sensitive Information Disclosure via Exposed File at ${url}
## Description:
The application exposes a sensitive file at \`${url}\` which contains internal application data or credentials.

## Steps To Reproduce:
1. Navigate directly to \`${url}\`
2. Observe the following sensitive keywords in the response: ${hallazgo.keywords ? hallazgo.keywords.join(', ') : ''}

## Impact
Information disclosure that can aid an attacker in further exploitation of the system.`;
    }
    
    // Plantilla generica
    return `## Title: ${tipo} on ${url}
## Description:
Automated testing identified a potential vulnerability of type ${tipo}.
Raw data: ${JSON.stringify(hallazgo)}

## Steps To Reproduce:
Please manually verify the provided raw data.`;
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
        const reportSection = document.getElementById('report-section');
        const reportTextarea = document.getElementById('h1-report');
        
        if (result.status === 'success') {
            appendTerminal(`[OK] Eslabón ${tipo} completado con éxito.`);
            
            // Tratamos de parsear si es JSON lo que devuelve el script
            try {
                // El script de Python a veces devuelve texto mezclado. Tratamos de extraer el JSON o buscar patrones
                let raw_data = result.data;
                pocContainer.textContent = raw_data;
                
                // Buscar si hay vulnerabilidades interesantes
                if (raw_data.includes('CORS MISCONFIGURATION') || raw_data.includes('ALTA') || raw_data.includes('MEDIA')) {
                    // Armar un reporte básico (parseo burdo por ahora)
                    let reportType = "cors";
                    let hallazgo = {tipo: "cors", url: "https://vulnerable.com/endpoint"}; // Mock temporal hasta mejorar parseo
                    
                    if(raw_data.includes('ARCHIVO SENSIBLE')) { reportType = "exposed_file"; hallazgo.tipo = reportType; }
                    
                    reportTextarea.value = generarPlantillaH1(hallazgo);
                    reportSection.style.display = 'block';
                } else {
                    reportSection.style.display = 'none';
                }
            } catch(e) {
                pocContainer.textContent = result.data;
                reportSection.style.display = 'none';
            }
            
            inbox.style.display = 'block';
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

function copiarReporte() {
    const textarea = document.getElementById('h1-report');
    textarea.select();
    document.execCommand('copy');
    
    const btn = event.target;
    const oldText = btn.textContent;
    btn.textContent = '¡Copiado!';
    setTimeout(() => { btn.textContent = oldText; }, 2000);
}
