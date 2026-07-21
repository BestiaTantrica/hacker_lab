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
    if (!terminal) return;
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
    
    if (tipo.includes("Privilege Escalation")) {
        return `## Title: Vertical Privilege Escalation allows standard users to access Admin endpoint ${url}
## Description:
A Privilege Escalation vulnerability was discovered at the \`${url}\` endpoint. This endpoint is designed to handle administrative functionalities, but fails to properly validate the role of the requesting user. As a result, a low-privileged user (such as a standard agent or user) can successfully make requests to this endpoint and access sensitive administrative data.

## Steps To Reproduce:
1. Log in to the application using a low-privileged account.
2. Make a direct API call to the administrative endpoint \`${url}\`.
3. Observe that the server responds with a 200 OK and returns sensitive administrative data, instead of a 401/403 Forbidden.

## Evidence / Raw Data:
\`\`\`text
${hallazgo.raw ? (hallazgo.raw.split("TEST DE ESCALADA VERTICAL")[1] || hallazgo.raw) : 'Ver consola para datos crudos'}
\`\`\`

## Impact
This is a High/Critical severity vulnerability. A low-privileged user can access administrative endpoints, potentially leading to full platform compromise, unauthorized configuration changes, or exposure of highly sensitive billing/account data.`;
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
            
            // Logica de Cola de Alarmas (Review Queue)
            if (result.data.includes("COLA DE ESPERA:")) {
                const queueBox = document.getElementById('queue-content');
                if (queueBox.textContent.includes("Cola vacía")) queueBox.textContent = "";
                const alarmMatch = result.data.split("COLA DE ESPERA:")[1];
                if (alarmMatch) {
                    queueBox.textContent += `[!] ${new Date().toLocaleTimeString()} - ${alarmMatch}\n`;
                }
            }

            // Lógica de desbloqueo de la cascada
            if (paso === 'mapeo') {
                document.getElementById('step-2').style.opacity = '1';
                document.getElementById('step-2').style.pointerEvents = 'auto';
                document.getElementById('step-3').style.opacity = '1'; // Desbloqueo paso 3 también
                document.getElementById('step-3').style.pointerEvents = 'auto';
                document.getElementById('btn-step-1').classList.replace('btn-primary', 'btn-success');
                document.getElementById('btn-step-1').textContent = "✅ Mapeo Completado";
            } 
            else if (paso === 'ataque') {
                if (result.data.includes("IDOR CONFIRMADO")) {
                    document.getElementById('step-4').style.opacity = '1';
                    document.getElementById('step-4').style.pointerEvents = 'auto';
                    document.getElementById('btn-step-2').classList.replace('btn-secondary', 'btn-success');
                    document.getElementById('btn-step-2').textContent = "✅ Ataque Exitoso";
                    pocActual = result.data; // Guardamos para el reporte
                } else {
                    appendTerminal(`[INFO] No se pudo confirmar IDOR horizontal en este intento.`);
                    document.getElementById('btn-step-2').textContent = "❌ Fallido (Ver Consola)";
                }
            }
            else if (paso === 'escalada') {
                if (result.data.includes("ESCALADA CONFIRMADA")) {
                    document.getElementById('step-4').style.opacity = '1';
                    document.getElementById('step-4').style.pointerEvents = 'auto';
                    document.getElementById('btn-step-3').classList.replace('btn-secondary', 'btn-success');
                    document.getElementById('btn-step-3').textContent = "✅ Escalada Exitosa";
                    pocActual = result.data; // Guardamos para el reporte
                } else {
                    appendTerminal(`[INFO] No se detectó vulnerabilidad vertical evidente.`);
                    document.getElementById('btn-step-3').textContent = "❌ Fallido (Ver Consola)";
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
    
    let tipoBug = "Vulnerabilidad Desconocida";
    let urlBug = "Endpoint Vulnerable";
    
    if (pocActual.includes("ESCALADA CONFIRMADA")) {
        tipoBug = "Privilege Escalation";
        const match = pocActual.match(/ESCALADA CONFIRMADA \[(.+?)\]/);
        if (match) urlBug = match[1];
    } else if (pocActual.includes("IDOR CONFIRMADO")) {
        tipoBug = "IDOR (Cross-Tenant Data Exposure)";
        const match = pocActual.match(/IDOR CONFIRMADO \[(.+?)\]\[(.+?)\]/);
        if (match) urlBug = `/${match[1]}/${match[2]}`;
    }
    
    const hallazgo = {
        tipo: tipoBug,
        url: urlBug,
        raw: pocActual
    };
    
    reportTextarea.value = generarPlantillaH1(hallazgo);
    reportSection.style.display = 'block';
    document.getElementById('inbox-card').scrollIntoView({ behavior: 'smooth' });
}

// LOGS CRUDOS AL ABRIR TERMINAL
document.addEventListener('DOMContentLoaded', () => {
    // Escuchar clics en la tab de Terminal para cargar data cruda
    const terminalTab = document.querySelectorAll('.nav-item')[3];
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

// ═══════════════════════════════════════════════════════════════════
// ═══════════════════════════════════════════════════════════════════
// MOTOR DE DINERO (Resultados Automáticos y Triage)
// ═══════════════════════════════════════════════════════════════════

async function cosecharBugs() {
    const btn = document.getElementById('btn-cosechar');
    const originalText = btn.textContent;
    btn.textContent = '⏳ Descargando de OCI-1...';
    btn.disabled = true;

    try {
        const res = await fetch('/api/get_motor_results');
        const result = await res.json();
        
        if (result.status === 'success') {
            document.getElementById('results-card').style.display = 'block';
            const bugList = document.getElementById('bug-list');
            bugList.innerHTML = ''; // Limpiar lista
            
            let secretos = [];
            let explotador = [];
            try { secretos = JSON.parse(result.secretos); } catch(e) {}
            try { explotador = JSON.parse(result.explotador); } catch(e) {}
            
            const totalBugs = secretos.length + explotador.length;
            
            if (totalBugs === 0) {
                bugList.innerHTML = '<div style="padding: 10px; background: #2a2a35; border-radius: 5px; color: #aaa;">No se encontraron vulnerabilidades en la última ejecución nocturna. OCI-1 seguirá monitoreando.</div>';
            } else {
                // Renderizar secretos JS
                secretos.forEach((bug, index) => renderBugCard(bugList, "Secreto Expuesto en JS", bug, "critical"));
                // Renderizar explotador automático
                explotador.forEach((bug, index) => renderBugCard(bugList, bug.tipo, bug, "high"));
            }
            
            btn.classList.replace('btn-success', 'btn-primary');
            btn.textContent = `✅ Cosecha Completada (${totalBugs} bugs)`;
            appendTerminal(`[OK] Cosecha descargada: ${totalBugs} bugs listos para triage.`);
        } else {
            appendTerminal(`[ERROR] No se pudo descargar la cosecha: ${result.data}`);
            btn.textContent = '❌ Error al descargar';
            setTimeout(() => { btn.textContent = originalText; btn.disabled = false; }, 3000);
        }
    } catch (e) {
        appendTerminal(`[ERROR] Conexión fallida: ${e}`);
        btn.textContent = '❌ Error de red';
        setTimeout(() => { btn.textContent = originalText; btn.disabled = false; }, 3000);
    }
}

function renderBugCard(container, titulo, bugData, severidad) {
    // Generar un ID único para los botones de esta tarjeta
    const cardId = 'bug-' + Math.random().toString(36).substr(2, 9);
    
    const card = document.createElement('div');
    const borderCol = severidad === 'critical' ? '#e74c3c' : '#f29057';
    card.style = `background: #1e1e2e; border: 1px solid #333; border-left: 4px solid ${borderCol}; padding: 12px; border-radius: 5px; margin-bottom: 15px;`;
    
    const rawJson = JSON.stringify(bugData, null, 2);
    // Intentar extraer la URL del bug para verificación (depende del formato)
    const urlStr = bugData.url || bugData.endpoint || (bugData.takeover_url) || "";
    
    let contextoHTML = "";
    if (titulo === "Secreto Expuesto en JS") {
        contextoHTML = `<p style="font-size: 11px; color: #aaa; margin-bottom: 8px;"><strong>Contexto:</strong> Se ha encontrado un token o secreto codificado en el código fuente de un archivo JavaScript. Esto suele ocurrir cuando los desarrolladores compilan el frontend sin ofuscar variables de entorno.</p>`;
    } else if (titulo.includes("subdomain_takeover")) {
        contextoHTML = `<p style="font-size: 11px; color: #aaa; margin-bottom: 8px;"><strong>Contexto:</strong> Un subdominio apunta a un servicio externo (como GitHub Pages o AWS S3) pero la cuenta en ese servicio ya no existe. Un atacante puede registrar esa cuenta y tomar el control del subdominio.</p>`;
    } else {
        contextoHTML = `<p style="font-size: 11px; color: #aaa; margin-bottom: 8px;"><strong>Contexto:</strong> Posible vulnerabilidad detectada automáticamente. Requiere verificación para confirmar impacto.</p>`;
    }
    
    card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h4 style="margin: 0; color: #fff;">${titulo}</h4>
            <span style="font-size: 10px; background: ${borderCol}; padding: 2px 6px; border-radius: 3px; color: #fff;">${severidad.toUpperCase()}</span>
        </div>
        ${contextoHTML}
        <pre style="font-size: 10px; max-height: 100px; overflow-y: auto; background: #000; padding: 8px; border-radius: 3px; color: #a9ff68; margin-bottom: 10px;">${rawJson}</pre>
        
        <div style="display: flex; flex-direction: column; gap: 8px;">
            <button id="btn-verif-${cardId}" class="btn btn-secondary" style="padding: 8px 12px; font-size: 11px; margin-top: 0; display: flex; align-items: center; justify-content: center; gap: 5px;" onclick='verificarBug("${cardId}", "${urlStr}", "${titulo}")'>
                🔍 Verificar Disponibilidad en Vivo
            </button>
            <div id="verif-res-${cardId}" style="font-size: 11px; color: #f1c40f; display: none; padding: 5px; background: rgba(0,0,0,0.3); border-radius: 3px;"></div>
            
            <button id="btn-rep-${cardId}" class="btn btn-primary" style="padding: 8px 12px; font-size: 11px; margin-top: 0; display: none; align-items: center; justify-content: center; gap: 5px; background-color: var(--success);" onclick='mandarAPegaso(${JSON.stringify(rawJson)})'>
                🤖 Redactar Reporte HackerOne (Pegaso)
            </button>
        </div>
    `;
    container.appendChild(card);
}

async function verificarBug(cardId, url, tipo) {
    const btn = document.getElementById(`btn-verif-${cardId}`);
    const resDiv = document.getElementById(`verif-res-${cardId}`);
    const btnRep = document.getElementById(`btn-rep-${cardId}`);
    
    if (!url) {
        resDiv.style.display = 'block';
        resDiv.innerHTML = '⚠️ No se pudo extraer la URL del JSON para verificación automática. Procede con cuidado.';
        btnRep.style.display = 'flex';
        return;
    }
    
    btn.textContent = '⏳ Verificando en OCI-1...';
    btn.disabled = true;
    
    try {
        const res = await fetch('/api/verify_bug', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url, tipo: tipo })
        });
        const result = await res.json();
        
        resDiv.style.display = 'block';
        if (result.status === 'success') {
            resDiv.innerHTML = result.data;
            if (result.data.includes("VERIFICADO EN VIVO")) {
                resDiv.style.color = '#2ecc71';
                btn.classList.replace('btn-secondary', 'btn-success');
                btn.textContent = '✅ Vulnerabilidad Verificada';
                // DESBLOQUEAR ESLABON 3
                btnRep.style.display = 'flex'; 
            } else {
                resDiv.style.color = '#f1c40f';
                btn.textContent = '⚠️ Verificación Dudosa';
                // Lo desbloqueamos igual por si el usuario quiere reportarlo
                btnRep.style.display = 'flex'; 
            }
        } else {
            resDiv.innerHTML = `ERROR: ${result.data}`;
            resDiv.style.color = '#e74c3c';
            btn.textContent = '❌ Error';
            btn.disabled = false;
        }
    } catch(e) {
        resDiv.style.display = 'block';
        resDiv.innerHTML = `Error de red: ${e}`;
        resDiv.style.color = '#e74c3c';
        btn.textContent = '❌ Error';
        btn.disabled = false;
    }
}

function mandarAPegaso(rawJsonStr) {
    // Cambiar a la vista del chat
    const chatTab = document.querySelectorAll('.nav-item')[2]; // Pegaso es el 3er ítem ahora tras borrar eBay
    switchView('chat', chatTab);
    
    // Inyectar el prompt en el input
    const input = document.getElementById('chat-input');
    const prompt = `Por favor, redacta un reporte profesional de HackerOne en inglés para esta vulnerabilidad verificada del Motor de Dinero.\n\nContexto: Tienes que usar el siguiente JSON para armar los pasos de reproducción y el impacto.\n\nData:\n${rawJsonStr}`;
    input.value = prompt;
    
    // Auto enviar
    enviarMensajeChat();
}


// CHAT PEGASO AI
// ═══════════════════════════════════════════════════════════════════

async function enviarMensajeChat() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    const chatBox = document.getElementById('chat-messages');
    
    // Add user message
    const userDiv = document.createElement('div');
    userDiv.className = 'chat-message user';
    userDiv.innerHTML = `<strong>Tú:</strong> ${message}`;
    chatBox.appendChild(userDiv);
    
    input.value = '';
    
    // Add loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message assistant';
    loadingDiv.innerHTML = `<em>Pegaso está pensando...</em>`;
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        
        const result = await res.json();
        chatBox.removeChild(loadingDiv);
        
        const botDiv = document.createElement('div');
        botDiv.className = 'chat-message assistant';
        if (result.status === 'success') {
            botDiv.innerHTML = `<strong>Pegaso:</strong><br>${result.data.replace(/\\n/g, '<br>')}`;
        } else {
            botDiv.innerHTML = `<strong>Error:</strong> No pude conectarme con el cerebro. ${result.data}`;
            botDiv.style.borderLeftColor = 'red';
        }
        chatBox.appendChild(botDiv);
        
    } catch (e) {
        chatBox.removeChild(loadingDiv);
        const botDiv = document.createElement('div');
        botDiv.className = 'chat-message assistant';
        botDiv.innerHTML = `<strong>Error local:</strong> No se pudo enviar el mensaje.`;
        botDiv.style.borderLeftColor = 'red';
        chatBox.appendChild(botDiv);
    }
    
    chatBox.scrollTop = chatBox.scrollHeight;
}

document.getElementById('chat-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        enviarMensajeChat();
    }
});
