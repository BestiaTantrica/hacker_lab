/**
 * app.js — Lógica Interactiva para el Hub de Batalla Cultural (v7.0)
 */

document.addEventListener('DOMContentLoaded', () => {
    initEjesFilter();
    initCopyQuotes();
    initPollSystem();
    initWordTraceability();
    initLeadForm();
    initShortGenerator();
    initSocialExportModal();
});

/** FILTRADO POR EJES TEMÁTICOS **/
function initEjesFilter() {
    const btns = document.querySelectorAll('.eje-btn');
    const items = document.querySelectorAll('.card-hub-item');

    if (!btns.length || !items.length) return;

    btns.forEach(btn => {
        btn.addEventListener('click', () => {
            const selectedEje = btn.getAttribute('data-eje');
            if (!selectedEje) return;

            btns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            items.forEach(item => {
                const itemCat = item.getAttribute('data-category');
                if (selectedEje === 'todos' || itemCat === selectedEje) {
                    item.classList.remove('hidden');
                } else {
                    item.classList.add('hidden');
                }
            });
        });
    });
}

/** COPIAR FRASES BOMBA AL PORTAPAPELES **/
function initCopyQuotes() {
    const copyBtns = document.querySelectorAll('.btn-copy-quote');
    if (!copyBtns.length) return;

    copyBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const quoteText = btn.getAttribute('data-quote');
            if (!quoteText) return;

            try {
                await navigator.clipboard.writeText(quoteText);
                const originalText = btn.innerText;
                btn.innerText = '✅ ¡Copiada!';
                setTimeout(() => btn.innerText = originalText, 2000);
            } catch (err) {
                alert('Selecciona y copia la frase manualmente.');
            }
        });
    });
}

/** VOTO EN ENCUESTAS DE BATALLA CULTURAL **/
function initPollSystem() {
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
                alert('Error al conectar para guardar el voto.');
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

/** TRAZABILIDAD EN 1-CLIC DE CONCEPTOS CLAVE **/
function initWordTraceability() {
    const tags = document.querySelectorAll('.word-literal-tag');
    const items = document.querySelectorAll('.card-hub-item');
    const banner = document.getElementById('word-filter-banner');
    const activeText = document.getElementById('active-word-text');
    const btnReset = document.getElementById('btn-reset-word-filter');

    if (!tags.length) return;

    tags.forEach(tag => {
        tag.addEventListener('click', () => {
            const word = tag.getAttribute('data-word');
            if (!word) return;

            tags.forEach(t => t.style.opacity = '0.35');
            tag.style.opacity = '1.0';

            let matchCount = 0;
            items.forEach(item => {
                const author = item.getAttribute('data-author') || '';
                const title = item.getAttribute('data-title') || '';
                const snippet = item.getAttribute('data-snippet') || '';

                if (author.includes(word) || title.includes(word) || snippet.includes(word)) {
                    item.classList.remove('hidden');
                    matchCount++;
                } else {
                    item.classList.add('hidden');
                }
            });

            if (banner && activeText) {
                activeText.innerText = `'${word.toUpperCase()}' (${matchCount} análisis e intervenciones encontradas)`;
                banner.style.display = 'flex';
                document.getElementById('catalogo-contenidos').scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    if (btnReset) {
        btnReset.addEventListener('click', () => {
            tags.forEach(t => t.style.opacity = '1.0');
            items.forEach(item => item.classList.remove('hidden'));
            if (banner) banner.style.display = 'none';
        });
    }
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
            const question = btn.getAttribute('data-poll-question') || '🔥 Encuesta de Batalla Cultural';
            const optionsBtns = document.querySelectorAll(`.poll-option-btn[data-poll-id="${pollId}"]`);

            let optionsText = '';
            optionsBtns.forEach((b, idx) => {
                const txt = b.getAttribute('data-option-text') || b.innerText;
                optionsText += `\n${idx + 1}️⃣ ${txt}`;
            });

            const socialPost = `🦁 BATALLA CULTURAL | ${question}\n${optionsText}\n\n👇 ¡Sumá tu voto en vivo!\n🌐 http://localhost:8001/\n\n#BatallaCultural #AgustinLaje #Rucauf #Milei #Libertad`;

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
                alert('🎉 ¡Gracias por suscribirte al Boletín de Batalla Cultural!');
                input.value = '';
            } else {
                alert(data.detail || 'No se pudo registrar la suscripción.');
            }
        } catch (err) {
            alert('Error al conectar.');
        }
    });
}

/** GENERADOR DE SHORT VIDEO CON VOZ NEURAL **/
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
                alert(`✅ Short de Video MP4 generado exitosamente.\nPuedes descargarlo o verlo en:\n${data.download_url}`);
                window.location.reload();
            } else {
                alert('No se pudo generar el video short.');
            }
        } catch (err) {
            alert('Error conectando con el generador de video.');
        } finally {
            btnGen.innerText = '🎥 Generar / Actualizar Video Short con Voz Neural';
            btnGen.disabled = false;
        }
    });
}
