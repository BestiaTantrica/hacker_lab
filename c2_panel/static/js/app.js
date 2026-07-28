// app.js — Lógica de Interfaz del C2 Panel (OCI-2) - Rediseño Split-Screen

let current_finding = null;
let current_tab = 'active';

document.addEventListener('DOMContentLoaded', () => {
    checkOciStatus();
    cargarHallazgos();
    setInterval(checkOciStatus, 30000);
});

// NAVEGACIÓN ENTRE VISTAS
function switchView(viewId, navElement) {
    document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
    const targetView = document.getElementById('view-' + viewId);
    if (targetView) targetView.classList.add('active');
    
    if (navElement) {
        document.querySelectorAll('.nav-item').forEach(el => {
            el.classList.remove('active');
            el.style.color = '#888';
            el.style.fontWeight = 'normal';
        });
        navElement.classList.add('active');
        navElement.style.color = '#fff';
        navElement.style.fontWeight = 'bold';
    }
}

// TELEMETRÍA Y ESTADO DEL SISTEMA
async function checkOciStatus() {
    const dot = document.getElementById('oci-status-dot');
    const text = document.getElementById('oci-status-text');
    const deltasCount = document.getElementById('total-deltas-count');
    const findingsCount = document.getElementById('total-findings-count');

    try {
        const response = await fetch(`/api/status?_t=${Date.now()}`);
        const data = await response.json();

        if (data.status === 'online' || data.status === 'degraded') {
            dot.className = data.status === 'online' ? 'dot green' : 'dot yellow';
            text.textContent = data.status === 'online' ? 'OCI-1 ONLINE' : 'MODO LOCAL / OCI-2';
            if (deltasCount) deltasCount.textContent = data.total_deltas || '0';
            if (findingsCount) findingsCount.textContent = data.total_findings || '0';
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
    if (btnElement) {
        document.querySelectorAll('.zone-btn').forEach(b => {
            b.classList.remove('active');
            b.style.background = '#1e293b';
            b.style.color = '#94a3b8';
        });
        btnElement.classList.add('active');
        btnElement.style.background = '#2563eb';
        btnElement.style.color = '#fff';
    }

    const container = document.getElementById('findings-list');
    
    // Si elegimos "Todas", volvemos a mostrar la lista de hallazgos/bugs según la pestaña activa
    if (zone === 'all') {
        cargarHallazgos();
        return;
    }

    container.innerHTML = `<div style="padding: 10px; color: #aaa; font-size: 11px;">Cargando deltas de recolección de zona: ${zone.toUpperCase()}...</div>`;

    try {
        const res = await fetch(`/api/deltas/${zone}?_t=${Date.now()}`);
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
                    <div style="font-size: 10px; color: #888; margin-top: 4px;">Dominio base: ${item.domain} | Origen: ${item.source}</div>
                `;
                container.appendChild(card);
            });
        } else {
            container.innerHTML = `<div style="padding: 10px; color: #888; font-size: 11px;">No hay deltas registrados en OCI-2 para la zona ${zone.toUpperCase()} aún.</div>`;
        }
    } catch (e) {
        container.innerHTML = `<div style="padding: 10px; color: red; font-size: 11px;">Error cargando deltas de zona.</div>`;
    }
}

// PESTAÑAS BUGS ACTIVOS VS HISTORIAL
function cambiarTabFindings(tab, btnElement) {
    current_tab = tab;
    
    document.getElementById('tab-findings-active').style.background = tab === 'active' ? '#2563eb' : '#1e293b';
    document.getElementById('tab-findings-active').style.color = tab === 'active' ? '#fff' : '#94a3b8';
    
    document.getElementById('tab-findings-reported').style.background = tab === 'reported' ? '#2563eb' : '#1e293b';
    document.getElementById('tab-findings-reported').style.color = tab === 'reported' ? '#fff' : '#94a3b8';

    cargarHallazgos();
}

// CARGAR HALLAZGOS VERIFICADOS ($50-$300 USD)
async function cargarHallazgos() {
    const container = document.getElementById('findings-list');
    try {
        const res = await fetch(`/api/findings?status=${current_tab}&_t=${Date.now()}`);
        const data = await res.json();
        
        if (data.status === 'success' && data.findings.length > 0) {
            container.innerHTML = '';
            data.findings.forEach(f => {
                const card = document.createElement('div');
                const borderCol = f.severity === 'Critical' ? '#e74c3c' : (f.severity === 'High' ? '#f39c12' : '#2ecc71');
                card.style = `background: #1e1e2e; border: 1px solid #333; border-left: 4px solid ${borderCol}; padding: 12px; border-radius: 5px; cursor: pointer; transition: transform 0.1s; position: relative;`;
                card.onmouseover = () => card.style.transform = 'scale(1.01)';
                card.onmouseout = () => card.style.transform = 'scale(1)';
                
                let h1Badge = '';
                if (f.reported) {
                    const reportIdStr = f.h1_report_id ? `#${f.h1_report_id.replace(/^#/, '')}` : 'Enviado';
                    const statusStr = f.h1_status || 'Submitted';
                    const bountyStr = f.bounty_paid ? ` | Bounty: $${f.bounty_paid}` : '';
                    h1Badge = `<span style="font-size: 10px; background: #8b5cf6; padding: 2px 6px; border-radius: 3px; color: #fff; margin-left: 6px;">H1: ${reportIdStr} (${statusStr}${bountyStr})</span>`;
                }

                card.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center;" onclick="abrirAreaDeTrabajoFromCard(${f.id})">
                        <h4 style="margin: 0; color: #fff; font-size: 12px;">${f.vuln_type} ${h1Badge}</h4>
                        <span style="font-size: 10px; background: ${borderCol}; padding: 2px 6px; border-radius: 3px; color: #fff;">ESTIMADO: ${f.estimated_bounty}</span>
                    </div>
                    <p style="font-size: 11px; color: #aaa; margin: 6px 0;" onclick="abrirAreaDeTrabajoFromCard(${f.id})"><strong>Target:</strong> ${f.target}</p>
                    <pre style="font-size: 10px; background: #000; color: #a9ff68; padding: 6px; border-radius: 3px; max-height: 80px; overflow-y: auto;" onclick="abrirAreaDeTrabajoFromCard(${f.id})">${f.evidence}</pre>
                `;

                if (f.reported) {
                    const updateBtn = document.createElement('button');
                    updateBtn.className = 'btn btn-secondary';
                    updateBtn.style = 'font-size: 10px; padding: 4px 8px; margin-top: 8px; background: #374151; color: #fff; border: 1px solid #4b5563; border-radius: 4px; cursor: pointer; width: 100%;';
                    updateBtn.innerHTML = '✏️ Actualizar Estado / Bounty HackerOne';
                    updateBtn.onclick = (e) => {
                        e.stopPropagation();
                        actualizarEstadoH1(f.id, f.h1_status, f.h1_report_id, f.bounty_paid);
                    };
                    card.appendChild(updateBtn);
                }

                card._findingData = f;
                container.appendChild(card);
            });
        } else {
            const msg = current_tab === 'active' 
                ? 'Aún no hay hallazgos activos pendientes. OCI-1 enviará deltas automáticamente.' 
                : 'No hay reportes archivados en el historial aún.';
            container.innerHTML = `<div style="padding: 10px; color: #888; font-size: 11px;">${msg}</div>`;
        }
    } catch (e) {
        container.innerHTML = '<div style="padding: 10px; color: red; font-size: 11px;">Error conectando con la BD local de OCI-2.</div>';
    }
}

function abrirAreaDeTrabajoFromCard(findingId) {
    const cards = document.querySelectorAll('#findings-list > div');
    cards.forEach(c => {
        if (c._findingData && c._findingData.id === findingId) {
            abrirAreaDeTrabajo(c._findingData);
        }
    });
}

// NUEVO FLUJO: ÁREA DE TRABAJO (CASCADA INTELIGENTE)
function abrirAreaDeTrabajo(hallazgo) {
    current_finding = hallazgo;
    switchView('workspace', null);
    
    // Limpiar el historial visual del chat para el nuevo contexto aislado
    const chatBox = document.getElementById('chat-messages');
    chatBox.innerHTML = '';
    
    document.getElementById('workspace-vuln-title').textContent = hallazgo.vuln_type;
    document.getElementById('workspace-vuln-target').textContent = `Target: ${hallazgo.target}`;
    
    let skillKey = 'report_h1'; // Default
    
    // Mapeo inteligente (CASCADA)
    const vType = hallazgo.vuln_type.toLowerCase();
    const ev = hallazgo.evidence.toLowerCase();
    
    if (vType.includes('cors')) {
        skillKey = 'cors_analysis';
    } else if (vType.includes('s3') || vType.includes('takeover')) {
        if (ev.includes('404') || ev.includes('nosuchbucket')) {
            skillKey = 'takeover_analysis';
        } else {
            skillKey = 'aws_s3_leak';
        }
    } else if (vType.includes('ssrf')) {
        skillKey = 'ssrf_analysis';
    } else if (vType.includes('jwt')) {
        skillKey = 'jwt_logic_bypass';
    } else if (vType.includes('openapi') || vType.includes('swagger')) {
        skillKey = 'openapi_exposure'; // Use the specific AI skill that prevents hallucination
    } else if (vType.includes('idor') || vType.includes('business logic')) {
        skillKey = 'business_logic_api';
    }
    
    // Anunciar en el Chat Copiloto que empezamos a trabajar
    agregarMensajePegaso(`He detectado que seleccionaste <strong>${hallazgo.vuln_type}</strong> en el target <code>${hallazgo.target}</code>. He activado la skill adecuada y estoy redactando el reporte H1...`);

    // Ejecutar autogeneración
    regenerarReporte(skillKey);
}

async function regenerarReporte(skillKey) {
    if (!current_finding) return;

    const output = document.getElementById('prompt-result-output');
    const badge = document.getElementById('workspace-vuln-badge');
    
    badge.textContent = 'GENERANDO...';
    badge.style.background = '#f39c12';
    output.value = "⏳ Invocando modelo de IA (inyectando URL de target real)...";
    
    document.getElementById('workspace-actions').style.display = 'grid';

    try {
        const res = await fetch('/api/copilot/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                skill_key: skillKey, 
                evidence: current_finding.evidence,
                target: current_finding.target,
                vuln_type: current_finding.vuln_type
            })
        });

        const data = await res.json();
        if (data.status === 'success') {
            output.value = data.result;
            badge.textContent = 'COMPLETADO';
            badge.style.background = '#2ecc71';
            
            agregarMensajePegaso("¡Listo! El reporte está cargado a la izquierda. Revísalo. Si necesitas cambiar el impacto o traducir alguna parte, dímelo por este chat.");
        } else {
            output.value = "❌ Error: " + data.message;
            badge.textContent = 'ERROR';
            badge.style.background = '#e74c3c';
        }
    } catch (e) {
        output.value = "❌ Error de red al invocar el Hub de Prompts.";
        badge.textContent = 'ERROR';
        badge.style.background = '#e74c3c';
    }
}

async function traducirAEspanol() {
    const output = document.getElementById('prompt-result-output');
    const badge = document.getElementById('workspace-vuln-badge');
    const currentText = output.value;
    
    if (!currentText || currentText.trim() === '') return;
    
    badge.textContent = 'TRADUCIENDO...';
    badge.style.background = '#f39c12';
    output.value = "⏳ Traduciendo el reporte al español de forma estricta...";
    
    try {
        const res = await fetch('/api/copilot/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                skill_key: 'traductor_espanol', 
                evidence: currentText,
                target: current_finding ? current_finding.target : ''
            })
        });

        const data = await res.json();
        if (data.status === 'success') {
            output.value = data.result;
            badge.textContent = 'COMPLETADO (ESPAÑOL)';
            badge.style.background = '#2ecc71';
            agregarMensajePegaso("¡El reporte ha sido traducido al español correctamente!");
        } else {
            output.value = "❌ Error en traducción: " + data.message;
            badge.textContent = 'ERROR';
            badge.style.background = '#e74c3c';
        }
    } catch (e) {
        output.value = "❌ Error de red al invocar el Hub de Prompts para traducción.";
        badge.textContent = 'ERROR';
        badge.style.background = '#e74c3c';
    }
}

function copiarReporteGenerado() {
    const output = document.getElementById('prompt-result-output');
    output.select();
    document.execCommand('copy');
    alert("¡Reporte copiado al portapapeles! Listo para enviar a HackerOne.");
}

function abrirHackerOneDirecto() {
    if (!current_finding) return;

    // Deducción inteligente del handle del programa HackerOne
    let target = current_finding.target.toLowerCase();
    let programHandle = "shopify"; // Fallback por defecto

    if (target.includes("shopify")) {
        programHandle = "shopify";
    } else if (target.includes("uber")) {
        programHandle = "uber";
    } else if (target.includes("yahoo")) {
        programHandle = "yahoo";
    } else {
        try {
            let urlStr = target.startsWith('http') ? target : 'http://' + target;
            let urlObj = new URL(urlStr);
            let parts = urlObj.hostname.split('.');
            if (parts.length >= 2) {
                programHandle = parts[parts.length - 2];
            } else if (parts.length === 1) {
                programHandle = parts[0];
            }
        } catch(e) {
            let hostPart = target.replace(/^https?:\/\//, '').split('/')[0];
            let parts = hostPart.split('.');
            if (parts.length >= 2) {
                programHandle = parts[parts.length - 2];
            }
        }
    }

    const h1Url = `https://hackerone.com/${programHandle}/reports/new`;
    
    // Copiar automáticamente el contenido del reporte al portapapeles
    const output = document.getElementById('prompt-result-output');
    if (output && output.value) {
        try {
            navigator.clipboard.writeText(output.value);
        } catch(e) {
            output.select();
            document.execCommand('copy');
        }
    }

    // Intentar abrir la pestaña directamente
    let openedWindow = window.open(h1Url, '_blank');

    // Notificar en el chat con link directo visible y clickeable
    agregarMensajePegaso(`🚀 <strong>¡Enlace Directo a HackerOne Generado!</strong><br><br>Hacer clic aquí para abrir el formulario de <code>${programHandle.toUpperCase()}</code>:<br><a href="${h1Url}" target="_blank" rel="noopener noreferrer" style="display: inline-block; margin-top: 8px; padding: 8px 12px; background: #8b5cf6; color: #fff; text-decoration: none; border-radius: 4px; font-weight: bold;">🔗 Abrir ${h1Url}</a><br><br>📋 <strong>El reporte técnico completo ya fue copiado a tu portapapeles.</strong> Presiona <code>Ctrl+V</code> en HackerOne.`);

    if (!openedWindow || openedWindow.closed || typeof openedWindow.closed == 'undefined') {
        alert(`¡El navegador bloqueó la ventana emergente! Por favor usa el botón que Pegaso acaba de colocar en el chat de la derecha.`);
    }
}

// VERIFICACIÓN EN VIVO DESDE OCI-1
async function verificarBugEnVivo() {
    if (!current_finding) return;
    
    const btn = document.getElementById('btn-verify-live');
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '⏳ Verificando...';
    btn.disabled = true;
    
    agregarMensajePegaso(`Lanzando sonda a OCI-1 para verificar la persistencia de la vulnerabilidad en <code>${current_finding.target}</code>...`);
    
    // Asumimos que los targets vienen sin protocolo, agregamos http:// para el curl
    let url = current_finding.target;
    if (!url.startsWith('http')) url = 'http://' + url;
    
    try {
        const res = await fetch('/api/verify_bug', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                tipo: current_finding.vuln_type
            })
        });
        
        const data = await res.json();
        if (data.status === 'success') {
            agregarMensajePegaso(`<strong>Evidencia Forense Capturada (HackerOne PoC):</strong><br><pre style="background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 6px; font-size: 12px; margin-top: 8px; white-space: pre-wrap; font-family: monospace; max-height: 400px; overflow-y: auto;">${data.data}</pre><br><em>💡 Puedes copiar y pegar este bloque directamente en tu reporte de HackerOne como evidencia técnica.</em>`);
        } else {
            agregarMensajePegaso(`<strong>Error en Verificación (OCI-1):</strong><br><span style="color: red;">${data.data}</span>`);
        }
    } catch (e) {
        agregarMensajePegaso(`<strong>Error Crítico:</strong> No se pudo contactar a OCI-1.`);
    }
    
    btn.innerHTML = originalText;
    btn.disabled = false;
}

// CHAT PEGASO COPILOT
function agregarMensajePegaso(htmlContent, rawData = null) {
    const chatBox = document.getElementById('chat-messages');
    const botDiv = document.createElement('div');
    botDiv.className = 'chat-message assistant';
    
    const textSpan = document.createElement('span');
    textSpan.innerHTML = `<strong>Pegaso:</strong><br>${htmlContent}`;
    botDiv.appendChild(textSpan);
    
    // Si hay rawData y parece un reporte (contiene ## Title o ##), añadimos un botón para aplicarlo
    if (rawData && (rawData.includes('## Title') || rawData.includes('## Severity'))) {
        const br = document.createElement('br');
        const applyBtn = document.createElement('button');
        applyBtn.className = 'btn btn-primary';
        applyBtn.style = 'font-size: 10px; padding: 6px 10px; margin-top: 8px; width: 100%; background: #3b82f6; color: #fff; border: none; cursor: pointer; border-radius: 4px;';
        applyBtn.innerHTML = '📥 Aplicar al Área de Trabajo';
        applyBtn.onclick = () => {
            const area = document.getElementById('prompt-result-output');
            if(area) {
                area.value = rawData;
                applyBtn.innerHTML = '✅ Reporte Aplicado con Éxito';
                applyBtn.style.background = '#10B981';
                setTimeout(() => {
                    applyBtn.innerHTML = '📥 Aplicar al Área de Trabajo';
                    applyBtn.style.background = '#3b82f6';
                }, 2000);
            }
        };
        botDiv.appendChild(br);
        botDiv.appendChild(applyBtn);
    }
    
    chatBox.appendChild(botDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

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
    loadingDiv.innerHTML = `<em>Pegaso procesando...</em>`;
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    // Adjuntar el reporte actual como contexto si existe
    const currentReportContext = current_finding ? `\n[Contexto - Target actual: ${current_finding.target}]\n[Reporte Actual:\n${document.getElementById('prompt-result-output').value}]` : '';

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: message + currentReportContext,
                finding_id: current_finding ? current_finding.id : 0
            })
        });
        
        const result = await res.json();
        chatBox.removeChild(loadingDiv);
        
        if (result.status === 'success') {
            agregarMensajePegaso(result.data.replace(/\n/g, '<br>'), result.data);
        } else {
            const botDiv = document.createElement('div');
            botDiv.className = 'chat-message assistant';
            botDiv.innerHTML = `<strong>Error:</strong> ${result.data}`;
            botDiv.style.borderLeftColor = 'red';
            chatBox.appendChild(botDiv);
        }
        
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

// ARCHIVADO DE REPORTES CON REGISTRO DE ID HACKERONE REAL
async function archivarHallazgoActual() {
    if (!current_finding) {
        alert("Primero selecciona un hallazgo del panel.");
        return;
    }

    const reportId = prompt(`Ingresa el número de reporte REAL otorgado por HackerOne para ${current_finding.target} (Ej: 3892352):`, current_finding.h1_report_id || "");
    
    if (reportId === null) return; // Cancelado por usuario

    try {
        const res = await fetch(`/api/findings/${current_finding.id}/archive`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ h1_report_id: reportId.trim() })
        });
        
        const data = await res.json();
        if (data.status === 'success') {
            alert(`✅ Hallazgo #${current_finding.id} (${current_finding.target}) archivado correctamente y vinculado al reporte H1 #${reportId || 'N/A'}.`);
            switchView('dashboard', document.querySelectorAll('.nav-item')[0]);
            cambiarTabFindings('reported', document.getElementById('tab-findings-reported'));
        } else {
            alert(`❌ Error al archivar: ${data.message}`);
        }
    } catch (e) {
        alert("❌ Error de red al intentar archivar el reporte.");
    }
}

// ACTUALIZACIÓN DE ESTADO / RECOMPENSA DESDE EL HISTORIAL
async function actualizarEstadoH1(findingId, currentStatus, currentReportId, currentBounty) {
    const reportId = prompt("Número de Reporte en HackerOne:", currentReportId || "");
    if (reportId === null) return;

    const newStatus = prompt("Estado del reporte en HackerOne (Submitted, Triaged, Resolved, Duplicate, Informative, Bounty Paid):", currentStatus || "Submitted");
    if (newStatus === null) return;

    const bounty = prompt("Monto cobrado en USD (ingresar 0 si aún no fue pagado o fue duplicado):", currentBounty || "");
    if (bounty === null) return;

    try {
        const res = await fetch(`/api/findings/${findingId}/update_status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                h1_status: newStatus.trim(),
                h1_report_id: reportId.trim(),
                bounty_paid: bounty.trim()
            })
        });

        const data = await res.json();
        if (data.status === 'success') {
            alert(`✅ Estado del reporte #${findingId} actualizado a '${newStatus}'.`);
            cargarHallazgos();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (e) {
        alert("❌ Error de red al actualizar estado del reporte.");
    }
}

