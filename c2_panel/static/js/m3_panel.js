/**
 * m3_panel.js -- Módulo 3: UI Forense Anti-Falso Positivo
 * =========================================================
 * Extiende app.js sin modificarlo. Se carga como script adicional en index.html.
 * Agrega: badge de scope, botón PoC, WAF Probe, auto-block submit si UNVERIFIABLE.
 */

(function () {
    'use strict';

    // -------------------------------------------------------------------------
    // CONFIG
    // -------------------------------------------------------------------------
    const API_BASE = '';
    const QUALITY_COLORS = {
        HIGH: { bg: '#0d6e0d', text: '#7cfc00', label: '✅ HIGH' },
        MEDIUM: { bg: '#5a4a00', text: '#ffd700', label: '⚠️ MEDIUM' },
        UNVERIFIABLE: { bg: '#6e0d0d', text: '#ff6b6b', label: '❌ UNVERIFIABLE' },
    };

    // -------------------------------------------------------------------------
    // UTILIDADES
    // -------------------------------------------------------------------------
    function apiPost(path) {
        return fetch(API_BASE + path, { method: 'POST', headers: { 'Content-Type': 'application/json' } })
            .then(r => r.json());
    }

    function notify(msg, type) {
        const el = document.createElement('div');
        el.style.cssText = [
            'position:fixed;top:20px;right:20px;z-index:9999;padding:12px 20px;',
            'border-radius:8px;font-size:13px;font-weight:600;max-width:420px;',
            'box-shadow:0 4px 20px rgba(0,0,0,0.4);animation:fadeIn .3s ease;',
            type === 'error'
                ? 'background:#3d0d0d;color:#ff6b6b;border:1px solid #7c1d1d;'
                : 'background:#0d2d0d;color:#7cfc00;border:1px solid #1d6e1d;'
        ].join('');
        el.textContent = msg;
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 4000);
    }

    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(
            () => notify('✅ PoC copiado al portapapeles'),
            () => {
                const ta = document.createElement('textarea');
                ta.value = text;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                ta.remove();
                notify('✅ PoC copiado al portapapeles');
            }
        );
    }

    // -------------------------------------------------------------------------
    // MODAL REUTILIZABLE
    // -------------------------------------------------------------------------
    function showModal(title, content) {
        document.getElementById('m3-modal')?.remove();
        const modal = document.createElement('div');
        modal.id = 'm3-modal';
        modal.style.cssText = [
            'position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;',
            'background:rgba(0,0,0,0.75);backdrop-filter:blur(4px);'
        ].join('');
        modal.innerHTML = `
            <div style="background:#1a1a2e;border:1px solid #00ff9540;border-radius:14px;
                        padding:24px;max-width:780px;width:92%;max-height:85vh;overflow-y:auto;
                        box-shadow:0 20px 60px rgba(0,255,149,0.1);">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                    <h3 style="color:#00ff95;margin:0;font-size:15px;">${title}</h3>
                    <button id="m3-modal-close" style="background:#ffffff18;border:none;color:#aaa;
                        border-radius:6px;padding:4px 10px;cursor:pointer;font-size:16px;">✕</button>
                </div>
                <div id="m3-modal-body">${content}</div>
            </div>`;
        document.body.appendChild(modal);
        document.getElementById('m3-modal-close').onclick = () => modal.remove();
        modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
        return modal;
    }

    // -------------------------------------------------------------------------
    // BADGE DE SCOPE
    // -------------------------------------------------------------------------
    function renderScopeBadge(finding) {
        const scopeProg = finding.scope_program || '';
        const pocQuality = finding.poc_quality || 'MEDIUM';
        const qConf = QUALITY_COLORS[pocQuality] || QUALITY_COLORS.MEDIUM;

        const scopeHtml = scopeProg
            ? `<span style="background:#0d2d0d;color:#7cfc00;border:1px solid #1d6e1d;
                border-radius:4px;padding:2px 8px;font-size:11px;font-weight:700;">
                ✅ ${scopeProg.toUpperCase()}</span>`
            : `<span style="background:#2d1a0d;color:#ffa500;border:1px solid #6e3d0d;
                border-radius:4px;padding:2px 8px;font-size:11px;font-weight:700;">
                ⚠️ SCOPE UNKNOWN</span>`;

        const qualityHtml = `<span style="background:${qConf.bg};color:${qConf.text};
            border-radius:4px;padding:2px 8px;font-size:11px;font-weight:700;margin-left:6px;">
            ${qConf.label}</span>`;

        return `<div style="margin:6px 0;display:flex;gap:4px;flex-wrap:wrap;">
            ${scopeHtml}${qualityHtml}
        </div>`;
    }

    // -------------------------------------------------------------------------
    // BOTONES M3 en cada finding card
    // -------------------------------------------------------------------------
    function buildM3Buttons(findingId, pocQuality) {
        const isUnverifiable = pocQuality === 'UNVERIFIABLE';
        return `
        <div class="m3-controls" style="display:flex;gap:6px;margin-top:8px;flex-wrap:wrap;">
            <button class="btn-m3-scope" data-id="${findingId}"
                style="background:#1a2a1a;border:1px solid #00ff9540;color:#7cfc00;
                border-radius:6px;padding:5px 10px;font-size:11px;cursor:pointer;">
                🔭 Validar Scope
            </button>
            <button class="btn-m3-poc" data-id="${findingId}"
                style="background:#1a1a2a;border:1px solid #4444ff40;color:#99aaff;
                border-radius:6px;padding:5px 10px;font-size:11px;cursor:pointer;">
                🔬 Generar PoC
            </button>
            <button class="btn-m3-waf" data-id="${findingId}"
                style="background:#2a1a1a;border:1px solid #ff444440;color:#ffaaaa;
                border-radius:6px;padding:5px 10px;font-size:11px;cursor:pointer;">
                🛡️ WAF Probe
            </button>
            ${isUnverifiable ? `<span style="background:#3d0d0d;color:#ff6b6b;border:1px solid #7c1d1d;
                border-radius:6px;padding:5px 10px;font-size:11px;">
                ⛔ PoC Unverifiable — Ejecutar WAF Probe primero</span>` : ''}
        </div>`;
    }

    // -------------------------------------------------------------------------
    // HANDLERS DE BOTONES M3
    // -------------------------------------------------------------------------
    function handleValidateScope(findingId) {
        notify('🔭 Validando scope H1...', 'info');
        apiPost(`/api/findings/${findingId}/validate_scope`)
            .then(r => {
                if (r.valid) {
                    notify(`✅ IN SCOPE: ${r.program_slug} | ${r.reason}`, 'success');
                } else {
                    notify(`⛔ OUT OF SCOPE: ${r.reason}`, 'error');
                }
                refreshFindingsIfPossible();
            })
            .catch(() => notify('Error al validar scope', 'error'));
    }

    function handleGeneratePoc(findingId) {
        notify('🔬 Generando PoC...', 'info');
        apiPost(`/api/findings/${findingId}/generate_poc`)
            .then(r => {
                if (r.status !== 'success') {
                    notify('Error generando PoC: ' + (r.message || ''), 'error');
                    return;
                }
                const qConf = QUALITY_COLORS[r.poc_quality] || QUALITY_COLORS.MEDIUM;
                const content = `
                    <div style="margin-bottom:12px;">
                        <span style="background:${qConf.bg};color:${qConf.text};
                            border-radius:4px;padding:3px 10px;font-weight:700;">
                            ${qConf.label} | Source: ${r.poc_source || 'N/A'}
                        </span>
                    </div>
                    <pre style="background:#0a0a1a;color:#e0e0ff;padding:14px;border-radius:8px;
                        font-size:12px;overflow-x:auto;white-space:pre-wrap;word-break:break-all;
                        border:1px solid #ffffff15;">${escapeHtml(r.triager_poc || 'No PoC generado')}</pre>
                    <button onclick="navigator.clipboard.writeText(${JSON.stringify(r.triager_poc || '')})"
                        style="margin-top:10px;background:#0d2d0d;border:1px solid #00ff9540;
                        color:#7cfc00;border-radius:6px;padding:7px 16px;cursor:pointer;font-size:12px;">
                        📋 Copiar PoC
                    </button>`;
                showModal('🔬 PoC Forense — Finding #' + findingId, content);
                refreshFindingsIfPossible();
            })
            .catch(() => notify('Error al generar PoC', 'error'));
    }

    function handleWafProbe(findingId) {
        notify('🛡️ Ejecutando WAF Probe (hasta 2 intentos)...', 'info');
        apiPost(`/api/findings/${findingId}/waf_probe`)
            .then(r => {
                if (r.status === 'error') {
                    notify('WAF Probe error: ' + (r.data || ''), 'error');
                    return;
                }
                const bypassLabel = r.waf_bypassed
                    ? '<span style="color:#7cfc00;">✅ WAF BYPASS EXITOSO (intento 2)</span>'
                    : '<span style="color:#ffd700;">⚠️ Sin bypass necesario (intento 1 suficiente)</span>';

                let attemptsHtml = (r.attempts || []).map(a => `
                    <div style="background:#0d0d1a;border:1px solid #ffffff15;border-radius:8px;
                        padding:12px;margin-bottom:10px;">
                        <strong style="color:#aaa;">Intento ${a.attempt}</strong>
                        — Status: <strong style="color:${a.status_code === 200 ? '#7cfc00' : '#ff6b6b'};">
                            ${a.status_code || 'N/A'}</strong><br>
                        <small style="color:#666;">UA: ${(a.headers_used?.['User-Agent'] || '').slice(0, 60)}...</small>
                        <pre style="background:#060610;color:#d0d0ff;padding:10px;border-radius:6px;
                            font-size:11px;margin-top:8px;overflow-x:auto;white-space:pre-wrap;">
${escapeHtml((a.triager_curl || '') + '\n\n' + (a.response_preview || '').slice(0, 400))}</pre>
                    </div>`).join('');

                const finalCurlBlock = r.final_triager_curl
                    ? `<div style="margin-top:12px;">
                        <strong style="color:#00ff95;">Curl final para el reporte H1:</strong>
                        <pre style="background:#0a0a1a;color:#7cfc00;padding:12px;border-radius:8px;
                            font-size:12px;margin-top:6px;overflow-x:auto;white-space:pre-wrap;">
${escapeHtml(r.final_triager_curl)}</pre>
                        <button onclick="navigator.clipboard.writeText(${JSON.stringify(r.final_triager_curl)})"
                            style="background:#0d2d0d;border:1px solid #00ff9540;color:#7cfc00;
                            border-radius:6px;padding:7px 16px;cursor:pointer;font-size:12px;margin-top:8px;">
                            📋 Copiar Curl
                        </button>
                      </div>` : '';

                showModal('🛡️ WAF Probe — Finding #' + findingId,
                    `<div style="margin-bottom:12px;">${bypassLabel}</div>${attemptsHtml}${finalCurlBlock}`);
                refreshFindingsIfPossible();
            })
            .catch(() => notify('Error en WAF Probe', 'error'));
    }

    function escapeHtml(s) {
        return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    // -------------------------------------------------------------------------
    // INYECCIÓN EN FINDINGS CARDS (delegación de eventos en el DOM)
    // -------------------------------------------------------------------------
    function injectM3IntoFindings() {
        const cards = document.querySelectorAll('[data-finding-id]:not([data-m3-injected])');
        cards.forEach(card => {
            const findingId = card.getAttribute('data-finding-id');
            const pocQuality = card.getAttribute('data-poc-quality') || 'MEDIUM';
            const scopeProg = card.getAttribute('data-scope-program') || '';

            // Insertar badge de scope antes del primer elemento de contenido
            const badgeTarget = card.querySelector('.finding-header, .finding-title, h3, h4') || card.firstElementChild;
            if (badgeTarget) {
                const badgeEl = document.createElement('div');
                badgeEl.innerHTML = renderScopeBadge({ scope_program: scopeProg, poc_quality: pocQuality });
                badgeTarget.insertAdjacentElement('afterend', badgeEl);
            }

            // Agregar botones M3 al final de la card
            const btnContainer = document.createElement('div');
            btnContainer.innerHTML = buildM3Buttons(findingId, pocQuality);
            card.appendChild(btnContainer);

            // Auto-deshabilitar botón H1 si UNVERIFIABLE
            if (pocQuality === 'UNVERIFIABLE') {
                const h1Btn = card.querySelector('[data-action="open-h1"], .btn-h1, [id*="h1-btn"]');
                if (h1Btn) {
                    h1Btn.disabled = true;
                    h1Btn.style.opacity = '0.3';
                    h1Btn.title = 'PoC no verificado — Ejecutar WAF Probe primero';
                }
            }

            card.setAttribute('data-m3-injected', '1');
        });
    }

    // Delegación global de clics para botones M3
    document.addEventListener('click', function (e) {
        const scopeBtn = e.target.closest('.btn-m3-scope');
        if (scopeBtn) { handleValidateScope(scopeBtn.dataset.id); return; }

        const pocBtn = e.target.closest('.btn-m3-poc');
        if (pocBtn) { handleGeneratePoc(pocBtn.dataset.id); return; }

        const wafBtn = e.target.closest('.btn-m3-waf');
        if (wafBtn) { handleWafProbe(wafBtn.dataset.id); return; }
    });

    // -------------------------------------------------------------------------
    // FUNCIÓN PARA REFRESCAR FINDINGS (compatibilidad con app.js)
    // -------------------------------------------------------------------------
    function refreshFindingsIfPossible() {
        // Si app.js expone una función de refresh, llamarla
        if (typeof window.loadFindings === 'function') window.loadFindings();
        else if (typeof window.refreshFindings === 'function') window.refreshFindings();
        else if (typeof window.renderFindings === 'function') window.renderFindings();
    }

    // -------------------------------------------------------------------------
    // OBSERVER: inyectar M3 cada vez que el DOM cambie (findings se recargan)
    // -------------------------------------------------------------------------
    const observer = new MutationObserver(function () {
        injectM3IntoFindings();
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Inyección inicial
    document.addEventListener('DOMContentLoaded', function () {
        injectM3IntoFindings();
        addM3Styles();
        console.log('[M3] Módulo de Validación Forense cargado ✅');
    });

    // -------------------------------------------------------------------------
    // ESTILOS GLOBALES M3
    // -------------------------------------------------------------------------
    function addM3Styles() {
        const style = document.createElement('style');
        style.textContent = `
            .btn-m3-scope:hover { background: #1a3a1a !important; border-color: #00ff95 !important; }
            .btn-m3-poc:hover   { background: #1a1a3a !important; border-color: #6688ff !important; }
            .btn-m3-waf:hover   { background: #3a1a1a !important; border-color: #ff6666 !important; }
            @keyframes fadeIn   { from { opacity:0; transform:translateY(-8px); } to { opacity:1; transform:none; } }
            #m3-modal pre       { font-family: 'Fira Code', 'Courier New', monospace; }
        `;
        document.head.appendChild(style);
    }

    // Exponer API pública para testing desde consola
    window.M3 = {
        validateScope: handleValidateScope,
        generatePoc:   handleGeneratePoc,
        wafProbe:      handleWafProbe,
        refresh:       injectM3IntoFindings,
    };

})();
