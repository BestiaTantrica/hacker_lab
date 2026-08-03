// app.js — Lógica de Interfaz del C2 Panel (OCI-2) - Rediseño Split-Screen

let current_finding = null;
let current_tab = 'Pendiente';
let _contexto_pegaso_cargado = false; // Flag: contexto inicial solo se carga 1 vez por sesión

// SISTEMA DE NOTIFICACIONES TOAST (sin alert() bloqueante)
function mostrarToast(mensaje, tipo) {
    tipo = tipo || 'success';
    var el = document.createElement('div');
    el.style.cssText = [
        'position:fixed;top:22px;right:22px;z-index:9999;padding:12px 20px;',
        'border-radius:8px;font-size:13px;font-weight:600;max-width:380px;',
        'box-shadow:0 4px 24px rgba(0,0,0,0.55);opacity:1;transition:opacity 0.4s ease;',
        tipo === 'error'
            ? 'background:#3d0d0d;color:#ff8080;border:1px solid #7c2020;'
            : 'background:#0d2d0d;color:#7cfc00;border:1px solid #1d6e1d;'
    ].join('');
    el.textContent = mensaje;
    document.body.appendChild(el);
    setTimeout(function() { el.style.opacity = '0'; }, 3200);
    setTimeout(function() { if (el.parentNode) el.parentNode.removeChild(el); }, 3700);
}

function escapeHtmlModal(s) {
    return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

document.addEventListener('DOMContentLoaded', () => {
    checkOciStatus();
    cargarHallazgos();
    setInterval(checkOciStatus, 30000);
    // Precarga el contexto de sesión en background para que Pegaso esté listo
    iniciarContextoPegaso();
});

// CONTEXTO INTELIGENTE DE PEGASO (Memoria de Sesión)
async function iniciarContextoPegaso() {
    if (_contexto_pegaso_cargado) return;
    _contexto_pegaso_cargado = true;

    try {
        const res = await fetch(`/api/chat/context?_t=${Date.now()}`);
        const data = await res.json();
        if (data.status !== 'success') return;

        const ctx = data.context;
        const stats = ctx.pipeline_stats;
        const findings = ctx.findings_recientes || [];
        const zonas = ctx.zonas_activas || [];
        const historial = ctx.resumen_conversacion_previa || [];

        // Construir el briefing visual de Pegaso
        let msg = `<strong>Briefing de Sesión — Sistema Operativo</strong><br><br>`;

        // Stats del pipeline
        msg += `<strong>📡 Pipeline OCI-1:</strong><br>`;
        msg += `• Deltas recolectados: <code>${stats.total_deltas_recolectados.toLocaleString()}</code><br>`;
        msg += `• Findings verificados: <code>${stats.total_findings_verificados}</code> `;
        msg += `(Pendientes: <code>${stats.pendientes}</code> | Validados: <code>${stats.validados}</code> | Archivados: <code>${stats.archivados}</code>)<br>`;

        // Zonas con heartbeat
        if (zonas.length > 0) {
            msg += `<br><strong>🚦 Zonas Activas:</strong><br>`;
            zonas.forEach(z => {
                msg += `• <code>${z.zone}</code> — último latido: ${z.last_seen}<br>`;
            });
        }

        // Findings recientes
        if (findings.length > 0) {
            msg += `<br><strong>🔍 Hallazgos Recientes:</strong><br>`;
            findings.forEach(f => {
                const col = f.severity === 'Critical' ? '#e74c3c' : (f.severity === 'High' ? '#f39c12' : '#2ecc71');
                msg += `• [<code>#${f.id}</code>] <span style="color:${col};font-weight:bold">${f.severity}</span> — <code>${f.vuln_type}</code> en <code>${f.target}</code> — Estado: <em>${f.status_interno}</em><br>`;
            });
        } else {
            msg += `<br><em>No hay hallazgos verificados todavía. El pipeline sigue pescando.</em><br>`;
        }

        // Resumen del chat previo (contexto de decisiones estrategicas)
        const ultimos = historial.filter(h => h.role === 'assistant').slice(-2);
        if (ultimos.length > 0) {
            msg += `<br><strong>💬 Contexto de Sesión Anterior:</strong><br>`;
            ultimos.forEach(h => {
                const texto = h.message.substring(0, 180).replace(/\n/g, ' ');
                msg += `<em>└ "${texto}..."</em><br>`;
            });
        }

        msg += `<br>Estoy listo. ¿En qué trabajamos hoy?`;

        // Mostrar en el chat del Gurú si existe, sino guardar para cuando se abra
        const chatBox = document.getElementById('chat-messages');
        if (chatBox && chatBox.closest('.view.active')) {
            agregarMensajePegaso(msg);
        } else {
            // Guardar como pendiente para inyectar cuando se abra la vista del chat
            window._pegaso_briefing_pending = msg;
        }
    } catch(e) {
        // Silencioso: si falla el contexto, Pegaso funciona igual sin briefing
        console.warn('Pegaso context load failed:', e);
    }
}

// NAVEGACIÓN ENTRE VISTAS
function switchView(viewId, navElement) {
    document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
    const targetView = document.getElementById('view-' + viewId);
    if (targetView) targetView.classList.add('active');
    
    // Si se navega al chat/gurú y hay un briefing pendiente, inyectarlo ahora
    if ((viewId === 'chat' || viewId === 'guru' || viewId === 'copilot') && window._pegaso_briefing_pending) {
        const chatBox = document.getElementById('chat-messages');
        if (chatBox && chatBox.children.length === 0) {
            agregarMensajePegaso(window._pegaso_briefing_pending);
        }
        window._pegaso_briefing_pending = null;
    }

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
            cargarSaludZonas();
        } else {
            dot.className = 'dot red';
            text.textContent = 'SISTEMA OFFLINE';
        }
    } catch (error) {
        dot.className = 'dot red';
        text.textContent = 'API ERROR';
    }
}

async function cargarSaludZonas() {
    try {
        const res = await fetch(`/api/zones_health?_t=${Date.now()}`);
        const data = await res.json();
        if (data.status === 'success' && data.zones) {
            ['americas', 'emea', 'asia'].forEach(z => {
                const el = document.getElementById(`zone-${z}-info`);
                if (el && data.zones[z]) {
                    el.textContent = `Deltas hoy: ${data.zones[z].count_today}`;
                }
            });
        }
    } catch (e) {}
}



function cambiarTabFindings(tab, btnElement) {
    current_tab = tab;
    
    document.querySelectorAll('[id^="tab-findings-"]').forEach(btn => {
        btn.style.background = '#1e293b';
        btn.style.color = '#94a3b8';
    });
    
    if (btnElement) {
        btnElement.style.background = '#2563eb';
        btnElement.style.color = '#fff';
    }

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
                let statusCol = '#3b82f6';
                if (f.status_interno === 'Validado') statusCol = '#10b981';
                else if (f.status_interno === 'Enviado' || f.status_interno === 'Archivado') statusCol = '#8b5cf6';
                else if (f.status_interno === 'FalsoPositivo') statusCol = '#ef4444';

                const severityCol = f.severity === 'Critical' ? '#e74c3c' : (f.severity === 'High' ? '#f39c12' : '#2ecc71');
                
                const card = document.createElement('div');
                card.style = `background: #1e1e2e; border: 1px solid #333; border-left: 4px solid ${statusCol}; padding: 12px; border-radius: 5px; cursor: pointer; transition: transform 0.1s; position: relative;`;
                card.onmouseover = () => card.style.transform = 'scale(1.01)';
                card.onmouseout = () => card.style.transform = 'scale(1)';
                
                let h1Badge = '';
                if (f.reported || f.status_interno === 'Enviado') {
                    const reportIdStr = f.h1_report_id ? `#${f.h1_report_id.replace(/^#/, '')}` : 'Enviado';
                    const statusStr = f.h1_status || 'Submitted';
                    const bountyStr = f.bounty_paid ? ` | Bounty: $${f.bounty_paid}` : '';
                    h1Badge = `<span style="font-size: 10px; background: #8b5cf6; padding: 2px 6px; border-radius: 3px; color: #fff; margin-left: 6px;">H1: ${reportIdStr} (${statusStr}${bountyStr})</span>`;
                }

                let displayBounty = f.estimated_bounty;
                if (!displayBounty || displayBounty === '00-00' || displayBounty === '0' || displayBounty === '$00-00') {
                    if (f.severity === 'Critical') displayBounty = '$1000-$3000+';
                    else if (f.severity === 'High') displayBounty = '$500-$1000';
                    else if (f.severity === 'Medium-High') displayBounty = '$300-$500';
                    else if (f.severity === 'Medium') displayBounty = '$150-$300';
                    else displayBounty = '$50-$100';
                }

                card.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center;" onclick="abrirAreaDeTrabajoFromCard(${f.id})">
                        <h4 style="margin: 0; color: #fff; font-size: 13px;">${f.vuln_type} ${h1Badge}</h4>
                        <span style="font-size: 10px; color: ${severityCol}; font-weight: bold;">ESTIMADO: ${displayBounty}</span>
                    </div>
                    <p style="font-size: 12px; color: #e2e8f0; margin: 6px 0;" onclick="abrirAreaDeTrabajoFromCard(${f.id})"><strong>Target:</strong> <span style="color: #93c5fd;">${f.target}</span></p>
                    <pre style="font-size: 11px; background: #0f172a; color: #94a3b8; border: 1px solid #334155; padding: 8px; border-radius: 4px; max-height: 80px; overflow-y: auto;" onclick="abrirAreaDeTrabajoFromCard(${f.id})">${f.evidence}</pre>
                `;

                if (current_tab === 'Pendiente') {
                    const actionsDiv = document.createElement('div');
                    actionsDiv.style = 'display: flex; gap: 8px; margin-top: 10px;';
                    actionsDiv.innerHTML = `
                        <button class="btn btn-success" style="flex: 1; font-size: 10px; padding: 6px; background: #10B981; color: white; border: none; border-radius: 3px; cursor: pointer;" onclick="event.stopPropagation(); cambiarEstadoInternoDesdeCard(${f.id}, 'Validado')">✅ Validar</button>
                        <button class="btn btn-danger" style="flex: 1; font-size: 10px; padding: 6px; background: #EF4444; color: white; border: none; border-radius: 3px; cursor: pointer;" onclick="event.stopPropagation(); cambiarEstadoInternoDesdeCard(${f.id}, 'FalsoPositivo')">🗑️ Descartar</button>
                    `;
                    card.appendChild(actionsDiv);
                } else if (current_tab === 'Validado') {
                    const actionsDiv = document.createElement('div');
                    actionsDiv.style = 'display: flex; gap: 8px; margin-top: 10px;';
                    actionsDiv.innerHTML = `
                        <button class="btn btn-primary" style="flex: 1; font-size: 10px; padding: 6px; background: #8b5cf6; color: white; border: none; border-radius: 3px; cursor: pointer;" onclick="event.stopPropagation(); abrirAreaDeTrabajoFromCard(${f.id})">Abrir para Reportar</button>
                        <button class="btn btn-secondary" style="flex: 1; font-size: 10px; padding: 6px; background: #1e3a5f; color: #93c5fd; border: 1px solid #2563eb; border-radius: 3px; cursor: pointer;" onclick="event.stopPropagation(); mostrarModalArchivado(${f.id}, '${f.target.replace(/'/g, '\\&apos;')}')">Archivar Directo</button>
                    `;
                    card.appendChild(actionsDiv);
                }

                if (f.reported || f.status_interno === 'Enviado' || f.status_interno === 'Archivado') {
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
                tipo: current_finding.vuln_type,
                evidence: current_finding.evidence
            })
        });
        
        const data = await res.json();
        if (data.status === 'success') {
            let infoMsg = `<strong>Evidencia Forense Capturada (HackerOne PoC):</strong><br><pre style="background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 6px; font-size: 12px; margin-top: 8px; white-space: pre-wrap; font-family: monospace; max-height: 400px; overflow-y: auto;">${data.data}</pre>`;
            
            const area = document.getElementById('prompt-result-output');
            if (area && area.value) {
                let currentText = area.value;
                const marker = "## Supporting Material/References:\n```text\n";
                const endMarker = "\n```";
                
                let markerIndex = currentText.indexOf(marker);
                if (markerIndex !== -1) {
                    let textBefore = currentText.substring(0, markerIndex + marker.length);
                    let rest = currentText.substring(markerIndex + marker.length);
                    let endMarkerIndex = rest.indexOf(endMarker);
                    
                    if (endMarkerIndex !== -1) {
                        let textAfter = rest.substring(endMarkerIndex);
                        area.value = textBefore + data.data + textAfter;
                        infoMsg += `<br><strong style="color: #10B981;">✅ Evidencia inyectada automáticamente en el reporte (se reemplazó el JSON viejo).</strong>`;
                    } else {
                        area.value += "\n\n## Supporting Material/References:\n```text\n" + data.data + "\n```";
                        infoMsg += `<br><strong style="color: #10B981;">✅ Evidencia añadida al final del reporte.</strong>`;
                    }
                } else {
                    area.value += "\n\n## Supporting Material/References:\n```text\n" + data.data + "\n```";
                    infoMsg += `<br><strong style="color: #10B981;">✅ Evidencia añadida al final del reporte.</strong>`;
                }
            } else {
                infoMsg += `<br><em>💡 Puedes copiar y pegar este bloque directamente en tu reporte de HackerOne como evidencia técnica.</em>`;
            }
            
            agregarMensajePegaso(infoMsg);
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

// ARCHIVADO DE REPORTES — llama al modal premium sin prompt() bloqueante
function archivarHallazgoActual() {
    if (!current_finding) {
        mostrarToast('Primero selecciona un hallazgo del panel', 'error');
        return;
    }
    mostrarModalArchivado(current_finding.id, current_finding.target);
}

function actualizarEstadoH1(findingId, currentStatus, currentReportId, currentBounty) {
    mostrarModalActualizacionH1(findingId, currentStatus, currentReportId, currentBounty);
}

// ACTUALIZACIÓN DE ESTADO INTERNO (TAXONOMÍA) — sin alert() bloqueante
async function cambiarEstadoInterno(nuevoEstado) {
    if (!current_finding) return;

    try {
        const res = await fetch(`/api/findings/${current_finding.id}/internal_status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status_interno: nuevoEstado })
        });

        const data = await res.json();
        if (data.status === 'success') {
            mostrarToast('Estado actualizado a: ' + nuevoEstado);
            switchView('dashboard', document.querySelectorAll('.nav-item')[0]);
            const tabBtn = document.getElementById('tab-findings-' + nuevoEstado);
            if (tabBtn) {
                cambiarTabFindings(nuevoEstado, tabBtn);
            } else {
                cargarHallazgos();
            }
        } else {
            mostrarToast('Error al cambiar estado: ' + (data.message || ''), 'error');
        }
    } catch (e) {
        mostrarToast('Error de red al intentar cambiar el estado interno', 'error');
    }
}

// ACTUALIZACIÓN DE ESTADO INTERNO DESDE LA TARJETA DIRECTAMENTE
async function cambiarEstadoInternoDesdeCard(findingId, nuevoEstado) {
    try {
        const res = await fetch(`/api/findings/${findingId}/internal_status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status_interno: nuevoEstado })
        });
        const data = await res.json();
        if (data.status === 'success') {
            // Cambiar automáticamente a la pestaña del nuevo estado para que el usuario no se pierda
            const tabBtn = document.getElementById(`tab-findings-${nuevoEstado}`);
            if(tabBtn) {
                cambiarTabFindings(nuevoEstado, tabBtn);
            } else {
                cargarHallazgos(); 
            }
        }
    } catch(e) {
        alert("Error de red al actualizar estado");
    }
}

// M4-B: EXPORTACIÓN FORMAL DE REPORTES
function descargarReporteMD() {
    if (!current_finding) return;
    const output = document.getElementById('prompt-result-output').value;
    if (!output || output.trim() === "") {
        alert("El reporte está vacío. Genera uno primero.");
        return;
    }
    
    const dateStr = new Date().toISOString().split('T')[0];
    const targetClean = current_finding.target.replace(/[^a-zA-Z0-9]/g, '_');
    const filename = `H1_Report_${targetClean}_${dateStr}.md`;
    
    const blob = new Blob([output], { type: 'text/markdown' });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    agregarMensajePegaso("✅ Se ha descargado el reporte en formato Markdown (.md).");
}

function imprimirPDF() {
    if (!current_finding) return;
    const output = document.getElementById('prompt-result-output').value;
    if (!output || output.trim() === "") {
        alert("El reporte está vacío. Genera uno primero.");
        return;
    }
    
    const targetClean = current_finding.target;
    const dateStr = new Date().toISOString().split('T')[0];
    
    // Crear una ventana temporal para la impresión nativa sin afectar la interfaz C2
    const printWindow = window.open('', '_blank', 'width=800,height=900');
    if(!printWindow) {
        alert("El navegador bloqueó la ventana emergente. Por favor permítelas e intenta de nuevo.");
        return;
    }
    
    printWindow.document.write(`
        <html>
        <head>
            <title>Vulnerability Report - ${targetClean}</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                pre {
                    background-color: #f6f8fa;
                    border-radius: 6px;
                    padding: 16px;
                    overflow: auto;
                    font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;
                    font-size: 85%;
                    border: 1px solid #e1e4e8;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }
                code {
                    font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;
                    background-color: rgba(27,31,35,0.05);
                    padding: .2em .4em;
                    border-radius: 6px;
                }
                h1, h2, h3 {
                    border-bottom: 1px solid #eaecef;
                    padding-bottom: .3em;
                    margin-top: 24px;
                    margin-bottom: 16px;
                }
                .header {
                    border-bottom: 2px solid #0366d6;
                    margin-bottom: 30px;
                    padding-bottom: 10px;
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-end;
                }
                @media print {
                    .no-print { display: none; }
                }
            </style>
        </head>
        <body>
            <div class="no-print" style="margin-bottom: 20px; text-align: right;">
                <button onclick="window.print()" style="padding: 10px 20px; background: #0366d6; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">Imprimir a PDF</button>
            </div>
            
            <div class="header">
                <div>
                    <h2 style="margin: 0; border: none;">Reporte de Seguridad Forense</h2>
                    <p style="margin: 5px 0 0 0; color: #586069;">Target: <strong>${targetClean}</strong></p>
                </div>
                <div style="text-align: right; color: #586069; font-size: 14px;">
                    Generado el: ${dateStr}<br>
                    C2 Copilot Hub
                </div>
            </div>
            
            <!-- Renderizamos el contenido crudo, pero conservando los saltos de línea y formateo base -->
            <div style="white-space: pre-wrap;">${output
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/## (.*?)\n/g, '<h2>$1</h2>')
                .replace(/```[a-z]*\n([\s\S]*?)```/g, '<pre>$1</pre>')
                .replace(/`(.*?)`/g, '<code>$1</code>')
            }</div>
            
            <script>
                // Auto-print al cargar
                setTimeout(() => {
                    window.print();
                }, 500);
            </script>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    agregarMensajePegaso("Se ha abierto una ventana limpia para Imprimir a PDF. Puedes guardar el reporte nativamente.");
}

// =============================================================================
// MODAL: ARCHIVADO PREMIUM (reemplaza prompt() bloqueante)
// =============================================================================
function mostrarModalArchivado(findingId, targetLabel) {
    if (!findingId) { mostrarToast('Primero selecciona un hallazgo', 'error'); return; }
    var existing = document.getElementById('c2-modal-archive');
    if (existing) existing.parentNode.removeChild(existing);

    var prefilledId = '';
    if (current_finding && current_finding.id === findingId) {
        prefilledId = current_finding.h1_report_id || '';
    }

    var overlay = document.createElement('div');
    overlay.id = 'c2-modal-archive';
    overlay.style.cssText = 'position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.82);backdrop-filter:blur(4px);';

    overlay.innerHTML = '<div id="c2-modal-archive-inner" style="background:#1a1a2e;border:1px solid #334155;border-radius:14px;padding:28px;max-width:480px;width:92%;box-shadow:0 20px 60px rgba(0,0,0,0.6);transform:translateY(-18px);transition:transform 0.22s ease;">'
        + '<h3 style="color:#e2e8f0;margin:0 0 6px 0;font-size:16px;">Archivar Hallazgo</h3>'
        + '<p style="color:#94a3b8;font-size:12px;margin:0 0 20px 0;">Target: <strong style="color:#93c5fd;">' + escapeHtmlModal(targetLabel) + '</strong></p>'
        + '<label style="display:block;font-size:12px;color:#94a3b8;margin-bottom:6px;">Numero de Reporte HackerOne (opcional)</label>'
        + '<input id="modal-arch-h1id" type="text" value="' + escapeHtmlModal(prefilledId) + '" placeholder="Ej: 3892352" style="width:100%;padding:10px 12px;background:#0f172a;border:1px solid #334155;color:#e2e8f0;border-radius:8px;font-size:13px;box-sizing:border-box;font-family:Monospace;">'
        + '<p style="font-size:11px;color:#64748b;margin:8px 0 20px 0;">El numero lo asigna HackerOne cuando enviás el bug. Si todavia no lo envias, dejalo vacio y archiva igual.</p>'
        + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">'
        + '<button id="modal-arch-confirm" style="padding:11px;background:#2563eb;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:13px;font-weight:600;">Confirmar Archivado</button>'
        + '<button id="modal-arch-fp" style="padding:11px;background:#1e293b;color:#f87171;border:1px solid #ef4444;border-radius:8px;cursor:pointer;font-size:13px;">Marcar Falso Positivo</button>'
        + '</div>'
        + '<button id="modal-arch-cancel" style="width:100%;padding:9px;background:transparent;color:#64748b;border:1px solid #334155;border-radius:8px;cursor:pointer;font-size:12px;">Cancelar</button>'
        + '</div>';

    document.body.appendChild(overlay);
    setTimeout(function() {
        var inner = document.getElementById('c2-modal-archive-inner');
        if (inner) inner.style.transform = 'translateY(0)';
    }, 10);

    var inp = document.getElementById('modal-arch-h1id');
    if (inp) inp.focus();

    document.getElementById('modal-arch-confirm').onclick = function() {
        var reportId = (document.getElementById('modal-arch-h1id').value || '').trim();
        fetch('/api/findings/' + findingId + '/archive', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ h1_report_id: reportId })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
            if (data.status === 'success') {
                mostrarToast('Hallazgo #' + findingId + ' archivado correctamente');
                if (current_finding && current_finding.id === findingId) {
                    switchView('dashboard', document.querySelectorAll('.nav-item')[0]);
                }
                var tabBtn = document.getElementById('tab-findings-Historico');
                cambiarTabFindings('Historico', tabBtn);
            } else {
                mostrarToast('Error al archivar: ' + (data.message || ''), 'error');
            }
        })
        .catch(function() { mostrarToast('Error de red al archivar', 'error'); });
    };

    document.getElementById('modal-arch-fp').onclick = function() {
        fetch('/api/findings/' + findingId + '/internal_status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status_interno: 'FalsoPositivo' })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
            if (data.status === 'success') {
                mostrarToast('Hallazgo marcado como Falso Positivo');
                if (current_finding && current_finding.id === findingId) {
                    switchView('dashboard', document.querySelectorAll('.nav-item')[0]);
                }
                var tabBtn = document.getElementById('tab-findings-Historico');
                cambiarTabFindings('Historico', tabBtn);
            } else {
                mostrarToast('Error: ' + (data.message || ''), 'error');
            }
        })
        .catch(function() { mostrarToast('Error de red', 'error'); });
    };

    document.getElementById('modal-arch-cancel').onclick = function() {
        if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
    };
    overlay.onclick = function(e) {
        if (e.target === overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
    };
    function onEscArch(e) {
        if (e.key === 'Escape') {
            if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
            document.removeEventListener('keydown', onEscArch);
        }
    }
    document.addEventListener('keydown', onEscArch);
}

// =============================================================================
// MODAL: ACTUALIZACION DE ESTADO H1 (reemplaza triple prompt() bloqueante)
// =============================================================================
function mostrarModalActualizacionH1(findingId, currentStatus, currentReportId, currentBounty) {
    var existing = document.getElementById('c2-modal-h1upd');
    if (existing) existing.parentNode.removeChild(existing);

    var statusOptions = ['Submitted', 'Triaged', 'Resolved', 'Bounty Paid', 'Duplicate', 'Informative', 'N/A'];
    var optionsHtml = statusOptions.map(function(s) {
        return '<option value="' + s + '"' + (s === currentStatus ? ' selected' : '') + '>' + s + '</option>';
    }).join('');

    var overlay = document.createElement('div');
    overlay.id = 'c2-modal-h1upd';
    overlay.style.cssText = 'position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.82);backdrop-filter:blur(4px);';

    overlay.innerHTML = '<div id="c2-modal-h1upd-inner" style="background:#1a1a2e;border:1px solid #334155;border-radius:14px;padding:28px;max-width:480px;width:92%;box-shadow:0 20px 60px rgba(0,0,0,0.6);transform:translateY(-18px);transition:transform 0.22s ease;">'
        + '<h3 style="color:#e2e8f0;margin:0 0 20px 0;font-size:16px;">Actualizar Estado HackerOne — #' + findingId + '</h3>'
        + '<label style="display:block;font-size:12px;color:#94a3b8;margin-bottom:6px;">Numero de Reporte H1</label>'
        + '<input id="modal-upd-id" type="text" value="' + escapeHtmlModal(currentReportId || '') + '" placeholder="Ej: 3892352" style="width:100%;padding:10px 12px;background:#0f172a;border:1px solid #334155;color:#e2e8f0;border-radius:8px;font-size:13px;box-sizing:border-box;font-family:Monospace;margin-bottom:14px;">'
        + '<label style="display:block;font-size:12px;color:#94a3b8;margin-bottom:6px;">Estado del Reporte en HackerOne</label>'
        + '<select id="modal-upd-status" style="width:100%;padding:10px 12px;background:#0f172a;border:1px solid #334155;color:#e2e8f0;border-radius:8px;font-size:13px;box-sizing:border-box;margin-bottom:14px;">' + optionsHtml + '</select>'
        + '<label style="display:block;font-size:12px;color:#94a3b8;margin-bottom:6px;">Bounty cobrado en USD (0 si no fue pagado aun)</label>'
        + '<input id="modal-upd-bounty" type="text" value="' + escapeHtmlModal(currentBounty || '') + '" placeholder="Ej: 150" style="width:100%;padding:10px 12px;background:#0f172a;border:1px solid #334155;color:#e2e8f0;border-radius:8px;font-size:13px;box-sizing:border-box;margin-bottom:20px;font-family:Monospace;">'
        + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">'
        + '<button id="modal-upd-confirm" style="padding:11px;background:#2563eb;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:13px;font-weight:600;">Guardar Cambios</button>'
        + '<button id="modal-upd-cancel" style="padding:11px;background:transparent;color:#64748b;border:1px solid #334155;border-radius:8px;cursor:pointer;font-size:13px;">Cancelar</button>'
        + '</div>'
        + '</div>';

    document.body.appendChild(overlay);
    setTimeout(function() {
        var inner = document.getElementById('c2-modal-h1upd-inner');
        if (inner) inner.style.transform = 'translateY(0)';
    }, 10);

    document.getElementById('modal-upd-confirm').onclick = function() {
        var reportId = (document.getElementById('modal-upd-id').value || '').trim();
        var newStatus = (document.getElementById('modal-upd-status').value || '').trim();
        var bounty = (document.getElementById('modal-upd-bounty').value || '').trim();

        // Auto-taxonomia: mover a la tab correcta segun el resultado de H1
        var finalStatusLower = newStatus.toLowerCase();
        var autoInternalStatus = null;
        if (['informative', 'duplicate', 'n/a'].indexOf(finalStatusLower) !== -1) {
            autoInternalStatus = 'FalsoPositivo';
        } else if (['submitted', 'triaged', 'resolved', 'bounty paid'].indexOf(finalStatusLower) !== -1) {
            autoInternalStatus = 'Archivado';
        }

        fetch('/api/findings/' + findingId + '/update_status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ h1_status: newStatus, h1_report_id: reportId, bounty_paid: bounty })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.status !== 'success') {
                mostrarToast('Error: ' + (data.message || ''), 'error');
                return;
            }
            if (autoInternalStatus) {
                fetch('/api/findings/' + findingId + '/internal_status', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status_interno: autoInternalStatus })
                })
                .then(function() {
                    if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
                    mostrarToast('Estado actualizado a: ' + newStatus);
                    var tabBtn = document.getElementById('tab-findings-Historico');
                    cambiarTabFindings('Historico', tabBtn);
                });
            } else {
                if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
                mostrarToast('Estado actualizado a: ' + newStatus);
                cargarHallazgos();
            }
        })
        .catch(function() { mostrarToast('Error de red', 'error'); });
    };

    document.getElementById('modal-upd-cancel').onclick = function() {
        if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
    };
    overlay.onclick = function(e) {
        if (e.target === overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
    };
    function onEscUpd(e) {
        if (e.key === 'Escape') {
            if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
            document.removeEventListener('keydown', onEscUpd);
        }
    }
    document.addEventListener('keydown', onEscUpd);
}
