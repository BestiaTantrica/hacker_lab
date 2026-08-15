/**
 * app.js — Escuchatorio Dual, Nubes Emocionales & Multi-Encuestas (v5.0)
 */

document.addEventListener('DOMContentLoaded', () => {
    initViewModeSelector();
    initEmotionTabs();
    initMultiPolls();
    initWordTraceability();
    initLeadForm();
    initShortGenerator();
    initRegionSelector();
    initSocialExportModal();
});

/** CAMBIO DE MODO DE VISTA PRINCIPAL (PESTAÑAS HEADER) **/
function initViewModeSelector() {
    const btns = document.querySelectorAll('.view-mode-btn');
    const sections = document.querySelectorAll('.view-section');

    btns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetView = btn.getAttribute('data-view');
            if (!targetView) return;

            btns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            sections.forEach(sec => {
                if (sec.id === targetView) {
                    sec.classList.add('active');
                } else {
                    sec.classList.remove('active');
                }
            });
        });
    });
}

/** PESTAÑAS DE NUBES DE PALABRAS POR EMOCIÓN **/
function initEmotionTabs() {
    const btns = document.querySelectorAll('.emotion-tab-btn');
    const cloudContainer = document.getElementById('emotion-word-cloud-container');
    const titleDisplay = document.getElementById('emotion-title-display');
    const prensaList = document.getElementById('emotion-prensa-list');
    const redesList = document.getElementById('emotion-redes-list');

    if (!btns.length || !window.INITIAL_DATA) return;

    const emotionalData = window.INITIAL_DATA.emotional_clouds || {};

    btns.forEach(btn => {
        btn.addEventListener('click', () => {
            const emotion = btn.getAttribute('data-emotion');
            if (!emotion || !emotionalData[emotion]) return;

            btns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const data = emotionalData[emotion];

            // 1. Actualizar Título de la Emoción
            if (titleDisplay) {
                titleDisplay.innerText = data.title;
                titleDisplay.style.color = data.color;
            }

            // 2. Renderizar Nube Emocional
            if (cloudContainer) {
                let tagsHTML = '';
                data.word_cloud.forEach(tag => {
                    tagsHTML += `
                        <span class="word-literal-tag" 
                              data-word="${tag.text.toLowerCase()}"
                              style="font-size: ${tag.weight}rem !important; color: ${data.color};">
                            ${tag.text}
                        </span>
                    `;
                });
                cloudContainer.innerHTML = tagsHTML;
                bindCloudTagsTraceability();
            }

            // 3. Renderizar Noticias de Prensa asociadas
            if (prensaList) {
                let prensaHTML = '';
                data.prensa.forEach(item => {
                    prensaHTML += `
                        <div style="padding: 0.75rem; background: rgba(255,255,255,0.03); border-radius: 10px; border-left: 3px solid ${data.color};">
                            <a href="${item.link}" target="_blank" style="color: var(--text-bright); text-decoration: none; font-weight: 600;" rel="noopener">${item.title}</a>
                            <p style="font-size: 0.82rem; color: var(--text-muted); margin-top: 0.3rem;">${item.source} — ${item.snippet}</p>
                        </div>
                    `;
                });
                prensaList.innerHTML = prensaHTML || '<p style="color: var(--text-muted); font-size: 0.85rem;">No hay noticias registradas bajo este espectro en este momento.</p>';
            }

            // 4. Renderizar Posts de Redes Sociales asociados
            if (redesList) {
                let redesHTML = '';
                data.redes.forEach(r => {
                    redesHTML += `
                        <div style="padding: 0.75rem; background: rgba(255,255,255,0.03); border-radius: 10px; border-left: 3px solid ${data.color};">
                            <span style="font-size: 0.75rem; color: var(--accent-purple); font-weight: 700;">${r.network} (${r.author})</span>
                            <p style="font-size: 0.88rem; color: var(--text-main); font-weight: 500; margin-top: 0.2rem;">${r.content}</p>
                            <p style="font-size: 0.8rem; color: var(--accent-blue); margin-top: 0.3rem;">${r.top_comment}</p>
                        </div>
                    `;
                });
                redesList.innerHTML = redesHTML || '<p style="color: var(--text-muted); font-size: 0.85rem;">No hay publicaciones registradas bajo este espectro en este momento.</p>';
            }
        });
    });
}

/** SISTEMA DE VOTO MULTI-ENCUESTAS **/
function initMultiPolls() {
    const pollBtns = document.querySelectorAll('.poll-option-btn');
    if (!pollBtns.length) return;

    pollBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const pollId = btn.getAttribute('data-poll-id');
            const optionId = btn.getAttribute('data-option-id');

            if (!pollId || !optionId) return;

            const container = document.getElementById(`poll-options-${pollId}`);
            if (container) {
                container.querySelectorAll('.poll-option-btn').forEach(b => b.disabled = true);
            }

            try {
                const response = await fetch('/api/public/vote', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ poll_id: parseInt(pollId), option_id: parseInt(optionId) })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    updatePollUI(data.poll_id, data.results, data.total_votes);
                } else {
                    alert(data.detail || 'Error al guardar el voto');
                    if (container) container.querySelectorAll('.poll-option-btn').forEach(b => b.disabled = false);
                }
            } catch (err) {
                console.error('Error enviando voto:', err);
                alert('No se pudo conectar para guardar el voto.');
                if (container) container.querySelectorAll('.poll-option-btn').forEach(b => b.disabled = false);
            }
        });
    });
}

function updatePollUI(pollId, results, totalVotes) {
    const totalCounter = document.getElementById(`poll-total-${pollId}`);
    if (totalCounter) {
        totalCounter.innerText = `${totalVotes.toLocaleString()} votos acumulados en tiempo real`;
    }

    results.forEach(res => {
        const btn = document.querySelector(`.poll-option-btn[data-poll-id="${pollId}"][data-option-id="${res.id}"]`);
        if (btn) {
            const pctElem = btn.querySelector('.option-pct');
            const fillElem = btn.querySelector('.progress-fill');

            if (pctElem) pctElem.innerText = `${res.percentage}%`;
            if (fillElem) fillElem.style.width = `${res.percentage}%`;
        }
    });
}

/** TRAZABILIDAD POR PALABRAS EN AMBAS AGENDAS (PRENSA Y REDES) **/
function initWordTraceability() {
    bindCloudTagsTraceability();

    const btnReset = document.getElementById('btn-reset-word-filter');
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            document.querySelectorAll('.card-news').forEach(c => c.classList.remove('hidden'));
            document.querySelectorAll('.card-social').forEach(s => s.style.display = 'block');
            const banner = document.getElementById('word-filter-banner');
            if (banner) banner.style.display = 'none';
        });
    }
}

function bindCloudTagsTraceability() {
    const tags = document.querySelectorAll('.word-literal-tag');
    const newsCards = document.querySelectorAll('.card-news');
    const socialCards = document.querySelectorAll('.card-social');
    const banner = document.getElementById('word-filter-banner');
    const activeText = document.getElementById('active-word-text');

    tags.forEach(tag => {
        tag.addEventListener('click', () => {
            const word = tag.getAttribute('data-word');
            if (!word) return;

            let matchPrensa = 0;
            newsCards.forEach(card => {
                const title = card.getAttribute('data-title') || '';
                const snippet = card.getAttribute('data-snippet') || '';
                if (title.includes(word) || snippet.includes(word)) {
                    card.classList.remove('hidden');
                    matchPrensa++;
                } else {
                    card.classList.add('hidden');
                }
            });

            let matchRedes = 0;
            socialCards.forEach(card => {
                const content = card.getAttribute('data-content') || '';
                if (content.includes(word)) {
                    card.style.display = 'block';
                    matchRedes++;
                } else {
                    card.style.display = 'none';
                }
            });

            if (banner && activeText) {
                activeText.innerText = `'${word.toUpperCase()}' (${matchPrensa} noticias | ${matchRedes} posts en redes)`;
                banner.style.display = 'flex';
                
                // Activar automáticamente la vista comparativa si estamos filtrando
                document.querySelector('.view-mode-btn[data-view="mode-comparativo"]')?.click();
            }
        });
    });
}

/** MODAL EXPORTADOR A REDES SOCIALES **/
function initSocialExportModal() {
    const btnsExport = document.querySelectorAll('.btn-export-poll-social');
    const modal = document.getElementById('modal-social');
    const btnClose = document.getElementById('modal-social-close');
    const textContainer = document.getElementById('social-copy-text');
    const btnCopy = document.getElementById('btn-copy-to-clipboard');

    if (!modal) return;

    btnsExport.forEach(btn => {
        btn.addEventListener('click', () => {
            const pollId = btn.getAttribute('data-poll-id');
            const question = btn.getAttribute('data-poll-question') || '🔥 Encuesta de opinión pública en Argentina';
            
            const optionsBtns = document.querySelectorAll(`.poll-option-btn[data-poll-id="${pollId}"]`);

            let optionsText = '';
            optionsBtns.forEach((b, idx) => {
                const txt = b.getAttribute('data-option-text') || b.innerText;
                optionsText += `\n${idx + 1}️⃣ ${txt}`;
            });

            const socialPost = `📊 ${question}\n${optionsText}\n\n👇 ¡Sumá tu voto anónimo en vivo!\n🌐 http://localhost:8001/\n\n#Argentina #OpinionPublica #RedesVsPrensa #Encuesta`;

            if (textContainer) textContainer.innerText = socialPost;
            modal.classList.add('active');
        });
    });

    if (btnClose) btnClose.addEventListener('click', () => modal.classList.remove('active'));
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.classList.remove('active'); });

    if (btnCopy && textContainer) {
        btnCopy.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(textContainer.innerText);
                btnCopy.innerText = '✅ ¡Copiado!';
                setTimeout(() => btnCopy.innerText = '📋 Copiar al Portapapeles', 2000);
            } catch (err) {
                alert('Copia el texto manualmente.');
            }
        });
    }
}

/** SUSCRIPCIÓN NEWSLETTER **/
function initLeadForm() {
    const form = document.getElementById('lead-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = document.getElementById('lead-email-input');
        if (!input || !input.value) return;

        try {
            const res = await fetch('/api/public/subscribe_lead', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: input.value })
            });

            const data = await res.json();
            if (data.status === 'success') {
                alert('🎉 ¡Gracias! Te has suscrito al Newsletter del Escuchatorio Dual.');
                input.value = '';
            } else {
                alert(data.detail || 'No se pudo registrar.');
            }
        } catch (err) {
            alert('Error de conexión.');
        }
    });
}

/** GENERADOR DE SHORT VIDEO **/
function initShortGenerator() {
    const btnGen = document.getElementById('btn-generate-short');
    if (!btnGen) return;

    btnGen.addEventListener('click', async () => {
        btnGen.innerText = '🎬 Generando Short con Voz Neural... (espera unos segundos)';
        btnGen.disabled = true;

        try {
            const res = await fetch('/api/public/generate_short');
            const data = await res.json();

            if (data.status === 'success') {
                alert(`✅ Short de Video MP4 generado exitosamente.\nPuedes descargarlo o reproducirlo desded:\n${data.download_url}`);
                window.location.reload();
            } else {
                alert('No se pudo generar el video short.');
            }
        } catch (err) {
            alert('Error conectando con el orquestador de video.');
        } finally {
            btnGen.innerText = '🎥 Generar / Actualizar Short MP4 con Voz Neural';
            btnGen.disabled = false;
        }
    });
}

/** SELECTOR REGIONAL **/
function initRegionSelector() {
    const btns = document.querySelectorAll('.region-btn');
    const newsCards = document.querySelectorAll('.card-news');

    btns.forEach(btn => {
        btn.addEventListener('click', () => {
            btns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const selectedRegion = btn.getAttribute('data-region');

            newsCards.forEach(card => {
                const cardRegion = card.getAttribute('data-region');
                if (selectedRegion === 'nacional' || cardRegion === selectedRegion) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    });
}
