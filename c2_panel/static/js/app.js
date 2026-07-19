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
    
    if (tipo.includes("IDOR")) {
        return `## Title: Insecure Direct Object Reference (IDOR) allows Cross-Tenant Data Exposure on ${url}
## Description:
An Insecure Direct Object Reference (IDOR) vulnerability was discovered in the \`${url}\` endpoint. The application fails to properly validate authorization when fetching resources by their ID. This allows an authenticated user from one tenant (Attacker) to access sensitive data belonging to a completely different tenant (Victim) by simply changing the ID parameter in the request.

## Steps To Reproduce:
1. Log in to the application as Tenant A (Attacker).
2. Make a direct API call to the vulnerable endpoint requesting an ID that belongs to Tenant B.
3. Observe that the server responds with a 200 OK and returns the sensitive data of Tenant B, completely bypassing tenant isolation.

## Evidence / Raw Data:
\`\`\`text
${hallazgo.raw ? hallazgo.raw.split("TEST CROSS-TENANT IDOR")[1] || hallazgo.raw : 'Ver consola para datos crudos'}
\`\`\`

## Impact
This is a High/Critical severity vulnerability. Any authenticated user can enumerate IDs and systematically steal sensitive information (such as private support tickets, PII, or configurations) from all other companies/tenants using the platform.`;
    }
    
    // Plantilla generica
    return `## Title: ${tipo} on ${url}
## Description:
Automated testing identified a potential vulnerability of type ${tipo}.
Raw data: ${JSON.stringify(hallazgo)}

## Steps To Reproduce:
Please manually verify the provided raw data.`;
}

// FLUJO DE CASCADA DE IDOR
async function ejecutarPasoCascada(paso) {
    const btn = event.target;
    const originalText = btn.textContent;
    const inbox = document.getElementById('inbox-card');
    const pocContainer = document.getElementById('poc-content');
    const reportSection = document.getElementById('report-section');
    
    btn.textContent = "Ejecutando en OCI-1...";
    btn.disabled = true;
    appendTerminal(`[CASCADA] Iniciando Paso: ${paso.toUpperCase()}`);
    
    inbox.style.display = 'block';
    reportSection.style.display = 'none';
    pocContainer.textContent = "Procesando...";
    inbox.scrollIntoView({ behavior: 'smooth' });
    
    try {
        // Ejecutamos el eslabón correspondiente a este paso
        const response = await fetch('/api/execute_exploit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo: paso }) 
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            appendTerminal(`[OK] Paso ${paso} completado.`);
            pocContainer.textContent = result.data;
            
            // Lógica de desbloqueo de la cascada
            if (paso === 'mapeo') {
                document.getElementById('step-2').style.opacity = '1';
                document.getElementById('step-2').style.pointerEvents = 'auto';
                document.getElementById('btn-step-1').classList.replace('btn-primary', 'btn-success');
                document.getElementById('btn-step-1').textContent = "✅ Mapeo Completado";
            } 
            else if (paso === 'ataque') {
                if (result.data.includes("IDOR CONFIRMADO")) {
                    document.getElementById('step-3').style.opacity = '1';
                    document.getElementById('step-3').style.pointerEvents = 'auto';
                    document.getElementById('btn-step-2').classList.replace('btn-secondary', 'btn-success');
                    document.getElementById('btn-step-2').textContent = "✅ Ataque Exitoso";
                    pocActual = result.data; // Guardamos para el reporte
                } else {
                    appendTerminal(`[INFO] No se pudo confirmar IDOR en este intento.`);
                }
            }
        } else {
            appendTerminal(`[ERROR] Falló paso ${paso}: ${result.data}`);
            pocContainer.textContent = `ERROR: ${result.data}`;
        }
    } catch (error) {
        appendTerminal(`[ERROR] Falló la conexión: ${error}`);
        pocContainer.textContent = "Error de conexión con el servidor.";
    } finally {
        if(btn.textContent === "Ejecutando en OCI-1...") {
            btn.textContent = originalText;
        }
        btn.disabled = false;
    }
}

function generarReporteCascada() {
    const reportSection = document.getElementById('report-section');
    const reportTextarea = document.getElementById('h1-report');
    
    const hallazgo = {
        tipo: "IDOR (Cross-Tenant Data Exposure)",
        url: "API Freshdesk",
        raw: pocActual
    };
    
    reportTextarea.value = generarPlantillaH1(hallazgo);
    reportSection.style.display = 'block';
    document.getElementById('inbox-card').scrollIntoView({ behavior: 'smooth' });
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
