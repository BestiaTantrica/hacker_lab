// app.js — Lógica de Interfaz del C2 Panel (OCI-2)

document.addEventListener('DOMContentLoaded', () => {
    checkOciStatus();
    cargarHallazgos();
    setInterval(checkOciStatus, 30000);
});

// NAVEGACIÓN ENTRE VISTAS
function switchView(viewId, navElement) {
    document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
    document.getElementById('view-' + viewId).classList.add('active');
    
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    navElement.classList.add('active');
}

// TELEMETRÍA Y ESTADO DEL SISTEMA
async function checkOciStatus() {
    const dot = document.getElementById('oci-status-dot');
    const text = document.getElementById('oci-status-text');
    const deltasCount = document.getElementById('total-deltas-count');
    const findingsCount = document.getElementById('total-findings-count');

    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        if (data.status === 'online' || data.status === 'degraded') {
            dot.className = data.status === 'online' ? 'dot green' : 'dot yellow';
            text.textContent = data.status === 'online' ? 'OCI-1 ONLINE' : 'MODO LOCAL / OCI-2';
            deltasCount.textContent = data.total_deltas || '0';
            findingsCount.textContent = data.total_findings || '0';
        } else {
            dot.className = 'dot red';
            text.textContent = 'SISTEMA OFFLINE';
        }
    } catch (error) {
        dot.className = 'dot red';
        text.textContent = 'API ERROR';
    }
}

// FILTRADO POR ZONA HORARIA
async function filtrarZona(zone, btnElement) {
    document.querySelectorAll('.zone-btn').forEach(b => b.classList.remove('active'));
    btnElement.classList.add('active');

    const container = document.getElementById('findings-list');
    container.innerHTML = `<div style="padding: 10px; color: #aaa; font-size: 11px;">Cargando targets de zona: ${zone.toUpperCase()}...</div>`;

    try {
        const res = await fetch(`/api/deltas/${zone}`);
        const data = await res.json();
        
        if (data.status === 'success' && data.deltas.length > 0) {
            container.innerHTML = '';
            data.deltas.forEach(item => {
                const card = document.createElement('div');
                card.style = 'background: #1e1e2e; border: 1px solid #333; padding: 10px; border-radius: 4px; font-size: 11px; color: #fff; border-left: 3px solid var(--primary);';
                card.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>${item.subdomain}</strong>
                        <span style="font-size: 9px; background: #333; padding: 2px 5px; border-radius: 3px; color: #2ecc71;">${item.zone.toUpperCase()}</span>
                    </div>
                    <div style="font-size: 10px; color: #888; margin-top: 4px;">Dominio base: ${item.domain}</div>
                `;
                container.appendChild(card);
            });
        } else {
            container.innerHTML = `<div style="padding: 10px; color: #888; font-size: 11px;">No hay deltas registrados para la zona ${zone.toUpperCase()}.</div>`;
        }
    } catch (e) {
        container.innerHTML = `<div style="padding: 10px; color: red; font-size: 11px;">Error cargando deltas.</div>`;
    }
}

// CARGAR HALLAZGOS VERIFICADOS ($50-$300 USD)
async function cargarHallazgos() {
    const container = document.getElementById('findings-list');
    try {
        const res = await fetch('/api/findings');
        const data = await res.json();
        
        if (data.status === 'success' && data.findings.length > 0) {
            container.innerHTML = '';
            data.findings.forEach(f => {
                const card = document.createElement('div');
                const borderCol = f.severity === 'Critical' ? '#e74c3c' : (f.severity === 'High' ? '#f39c12' : '#2ecc71');
                card.style = `background: #1e1e2e; border: 1px solid #333; border-left: 4px solid ${borderCol}; padding: 12px; border-radius: 5px;`;
                
                card.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #fff; font-size: 12px;">${f.vuln_type}</h4>
                        <span style="font-size: 10px; background: ${borderCol}; padding: 2px 6px; border-radius: 3px; color: #fff;">ESTIMADO: ${f.estimated_bounty}</span>
                    </div>
                    <p style="font-size: 11px; color: #aaa; margin: 6px 0;"><strong>Target:</strong> ${f.target}</p>
                    <pre style="font-size: 10px; background: #000; color: #a9ff68; padding: 6px; border-radius: 3px; max-height: 80px; overflow-y: auto;">${f.evidence}</pre>
                    <button class="btn btn-primary" style="font-size: 10px; padding: 5px 10px; margin-top: 6px;" onclick='enviarAPrompts(${JSON.stringify(f.evidence)})'>🚀 Generar Reporte H1</button>
                `;
                container.appendChild(card);
            });
        } else {
            container.innerHTML = '<div style="padding: 10px; color: #888; font-size: 11px;">Aún no hay hallazgos persistidos. OCI-1 enviará deltas automáticamente.</div>';
        }
    } catch (e) {
        container.innerHTML = '<div style="padding: 10px; color: red; font-size: 11px;">Error conectando con la BD local de OCI-2.</div>';
    }
}

// HUB DE PROMPTS SKILLS
async function ejecutarPromptSkill(skillKey) {
    const evidence = document.getElementById('prompt-evidence-input').value.trim();
    if (!evidence) {
        alert("Por favor ingresa evidencia cruda (request, response o URL) para formatear.");
        return;
    }

    const container = document.getElementById('prompt-result-container');
    const output = document.getElementById('prompt-result-output');
    container.style.display = 'block';
    output.value = "⏳ Invocando modelo de IA con plantilla de Skill...";

    try {
        const res = await fetch('/api/copilot/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ skill_key: skillKey, evidence: evidence })
        });

        const data = await res.json();
        if (data.status === 'success') {
            output.value = data.result;
        } else {
            output.value = "❌ Error: " + data.message;
        }
    } catch (e) {
        output.value = "❌ Error de red al invocar el Hub de Prompts.";
    }
}

function enviarAPrompts(evidenceText) {
    switchView('prompts', document.querySelectorAll('.nav-item')[1]);
    document.getElementById('prompt-evidence-input').value = typeof evidenceText === 'object' ? JSON.stringify(evidenceText, null, 2) : evidenceText;
    ejecutarPromptSkill('report_h1');
}

function copiarReporteGenerado() {
    const output = document.getElementById('prompt-result-output');
    output.select();
    document.execCommand('copy');
    alert("¡Reporte copiado al portapapeles! Listo para enviar a HackerOne.");
}

// CHAT PEGASO COPILOT
async function enviarMensajeChat() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    const chatBox = document.getElementById('chat-messages');
    
    const userDiv = document.createElement('div');
    userDiv.className = 'chat-message user';
    userDiv.innerHTML = `<strong>Tú:</strong> ${message}`;
    chatBox.appendChild(userDiv);
    
    input.value = '';
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message assistant';
    loadingDiv.innerHTML = `<em>Pegaso consultando OCI-2 DB...</em>`;
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
            botDiv.innerHTML = `<strong>Pegaso:</strong><br>${result.data.replace(/\n/g, '<br>')}`;
        } else {
            botDiv.innerHTML = `<strong>Error:</strong> ${result.data}`;
            botDiv.style.borderLeftColor = 'red';
        }
        chatBox.appendChild(botDiv);
        
    } catch (e) {
        chatBox.removeChild(loadingDiv);
        const botDiv = document.createElement('div');
        botDiv.className = 'chat-message assistant';
        botDiv.innerHTML = `<strong>Error:</strong> Fallo de conexión.`;
        botDiv.style.borderLeftColor = 'red';
        chatBox.appendChild(botDiv);
    }
    
    chatBox.scrollTop = chatBox.scrollHeight;
}
