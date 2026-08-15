/**
 * app.js — Lógica Interactiva (Trazabilidad por Palabras, Redes Social Modal, Termómetro & Filtro Regional)
 */

document.addEventListener('DOMContentLoaded', () => {
    initPollSystem();
    initLeadForm();
    initShortGenerator();
    initRegionSelector();
    initWordTraceability();
    initSocialExportModal();
});

function initPollSystem() {
    const pollOptions = document.querySelectorAll('.poll-option-btn');
    if (!pollOptions.length) return;

    pollOptions.forEach(btn => {
        btn.addEventListener('click', async () => {
            const pollId = btn.getAttribute('data-poll-id');
            const optionId = btn.getAttribute('data-option-id');

            pollOptions.forEach(b => b.disabled = true);

            try {
                const response = await fetch('/api/public/vote', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ poll_id: parseInt(pollId), option_id: parseInt(optionId) })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    updatePollUI(data.results, data.total_votes);
                } else {
                    alert(data.detail || 'Error al procesar el voto');
                    pollOptions.forEach(b => b.disabled = false);
                }
            } catch (err) {
                console.error('Error enviando voto:', err);
                alert('No se pudo enviar el voto. Intenta nuevamente.');
                pollOptions.forEach(b => b.disabled = false);
            }
        });
    });
}

function updatePollUI(results, totalVotes) {
    const totalElem = document.getElementById('poll-total-votes');
    if (totalElem) {
        totalElem.innerText = `${totalVotes.toLocaleString()} votos acumulados en tiempo real`;
    }

    results.forEach(res => {
        const btn = document.querySelector(`.poll-option-btn[data-option-id="${res.id}"]`);
        if (btn) {
            const pctElem = btn.querySelector('.option-pct');
            const fillElem = btn.querySelector('.progress-fill');

            if (pctElem) pctElem.innerText = `${res.percentage}%`;
            if (fillElem) fillElem.style.width = `${res.percentage}%`;

            btn.classList.add('voted');
        }
    });
}

/** TRAZABILIDAD POR PALABRAS EN 1-CLIC **/
function initWordTraceability() {
    const tags = document.querySelectorAll('.word-literal-tag');
    const newsCards = document.querySelectorAll('.card-news');
    const banner = document.getElementById('word-filter-banner');
    const activeText = document.getElementById('active-word-text');
    const btnReset = document.getElementById('btn-reset-word-filter');

    if (!tags.length || !newsCards.length) return;

    tags.forEach(tag => {
        tag.addEventListener('click', () => {
            const word = tag.getAttribute('data-word');
            if (!word) return;

            tags.forEach(t => t.classList.remove('active-word'));
            tag.classList.add('active-word');

            let matchCount = 0;
            newsCards.forEach(card => {
                const title = card.getAttribute('data-title') || '';
                const snippet = card.getAttribute('data-snippet') || '';

                if (title.includes(word) || snippet.includes(word)) {
                    card.classList.remove('hidden');
                    matchCount++;
                } else {
                    card.classList.add('hidden');
                }
            });

            if (banner && activeText) {
                activeText.innerText = `'${word.toUpperCase()}' (${matchCount} noticias)`;
                banner.style.display = 'flex';
                document.getElementById('matriz-prensa').scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    if (btnReset) {
        btnReset.addEventListener('click', () => {
            tags.forEach(t => t.classList.remove('active-word'));
            newsCards.forEach(card => card.classList.remove('hidden'));
            if (banner) banner.style.display = 'none';
        });
    }
}

/** MODAL EXPORTADOR DE ENCUESTA A REDES SOCIALES **/
function initSocialExportModal() {
    const btnExport = document.getElementById('btn-export-social');
    const modal = document.getElementById('modal-social');
    const btnClose = document.getElementById('modal-social-close');
    const textContainer = document.getElementById('social-copy-text');
    const btnCopy = document.getElementById('btn-copy-to-clipboard');

    if (!btnExport || !modal) return;

    btnExport.addEventListener('click', () => {
        const question = document.getElementById('poll-question-text')?.innerText || '🔥 Encuesta del día en Argentina';
        const optionsBtns = document.querySelectorAll('.poll-option-btn');

        let optionsText = '';
        optionsBtns.forEach((btn, idx) => {
            const txt = btn.getAttribute('data-option-text') || btn.innerText;
            optionsText += `\n${idx + 1}️⃣ ${txt}`;
        });

        const socialPost = `${question}\n${optionsText}\n\n👇 ¡Sumá tu voto en tiempo real!\n🌐 http://localhost:8001/\n\n#Argentina #TermetroSocial #Noticias #Encuesta`;

        if (textContainer) textContainer.innerText = socialPost;
        modal.classList.add('active');
    });

    if (btnClose) btnClose.addEventListener('click', () => modal.classList.remove('active'));

    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('active');
    });

    if (btnCopy && textContainer) {
        btnCopy.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(textContainer.innerText);
                btnCopy.innerText = '✅ ¡Copiado!';
                setTimeout(() => btnCopy.innerText = '📋 Copiar al Portapapeles', 2000);
            } catch (err) {
                alert('Selecciona y copia el texto manualmente.');
            }
        });
    }
}

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
                alert('🎉 ¡Gracias! Te has suscrito exitosamente al Newsletter Diario.');
                input.value = '';
            } else {
                alert(data.detail || 'No se pudo guardar la suscripción.');
            }
        } catch (err) {
            alert('Error de conexión al guardar el email.');
        }
    });
}

function initShortGenerator() {
    const btnGen = document.getElementById('btn-generate-short');
    if (!btnGen) return;

    btnGen.addEventListener('click', async () => {
        btnGen.innerText = '🎬 Generando Short con Voz Neural...';
        btnGen.disabled = true;

        try {
            const res = await fetch('/api/public/generate_short');
            const data = await res.json();

            if (data.status === 'success') {
                alert(`✅ Short con Voz Neural Argentina generado exitosamente.\nPuedes descargarlo listo para YouTube Shorts desde:\n${data.download_url}`);
                window.open(data.download_url, '_blank');
            } else {
                alert('No se pudo generar el video short.');
            }
        } catch (err) {
            alert('Error al conectar con la fábrica de shorts.');
        } finally {
            btnGen.innerText = '🎥 Short Video con Voz Neural (1080x1920)';
            btnGen.disabled = false;
        }
    });
}

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
                if (selectedRegion === 'nacional') {
                    card.classList.remove('hidden');
                } else if (cardRegion === selectedRegion) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    });
}
