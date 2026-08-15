/**
 * app.js — RADAR 360 Lógica Comercial Simple & Directa (v6.0)
 */

document.addEventListener('DOMContentLoaded', () => {
    initPollSystem();
    initWordTraceability();
    initPdfExporter();
    initLeadForm();
    initShortGenerator();
    initRegionSelector();
    initSocialExportModal();
});

/** VOTACIÓN DE ENCUESTA PRINCIPAL **/
function initPollSystem() {
    const pollOptions = document.querySelectorAll('.poll-option-btn');
    if (!pollOptions.length) return;

    pollOptions.forEach(btn => {
        btn.addEventListener('click', async () => {
            const pollId = btn.getAttribute('data-poll-id');
            const optionId = btn.getAttribute('data-option-id');
            if (!pollId || !optionId) return;

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
                    alert(data.detail || 'Error registrando voto');
                    pollOptions.forEach(b => b.disabled = false);
                }
            } catch (err) {
                alert('Error al conectar con la base de datos de encuestas.');
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
        }
    });
}

/** TRAZABILIDAD 1-CLIC EN LA NUBE DE TENDENCIAS **/
function initWordTraceability() {
    const tags = document.querySelectorAll('.word-literal-tag');
    const newsCards = document.querySelectorAll('.card-news');
    const socialCards = document.querySelectorAll('.card-social');
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

            let matchNews = 0;
            newsCards.forEach(card => {
                const title = card.getAttribute('data-title') || '';
                const snippet = card.getAttribute('data-snippet') || '';
                if (title.includes(word) || snippet.includes(word)) {
                    card.classList.remove('hidden');
                    matchNews++;
                } else {
                    card.classList.add('hidden');
                }
            });

            let matchSocial = 0;
            socialCards.forEach(card => {
                const content = card.getAttribute('data-content') || '';
                if (content.includes(word)) {
                    card.style.display = 'block';
                    matchSocial++;
                } else {
                    card.style.display = 'none';
                }
            });

            if (banner && activeText) {
                activeText.innerText = `'${word.toUpperCase()}' (${matchNews} noticias | ${matchSocial} en redes)`;
                banner.style.display = 'flex';
                document.getElementById('seccion-comparativa').scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    if (btnReset) {
        btnReset.addEventListener('click', () => {
            tags.forEach(t => t.style.opacity = '1.0');
            newsCards.forEach(c => c.classList.remove('hidden'));
            socialCards.forEach(s => s.style.display = 'block');
            if (banner) banner.style.display = 'none';
        });
    }
}

/** BOTÓN REPORTE PDF PARA CLIENTES **/
function initPdfExporter() {
    const btnPdf = document.getElementById('btn-export-pdf');
    if (!btnPdf) return;

    btnPdf.addEventListener('click', () => {
        alert('📄 Generando Reporte Ejecutivo de Opinión Pública & Cobertura Mediática en PDF...\n\n(Ideal para vender como informe semanal a marcas y consultoras).');
        window.print();
    });
}

/** MODAL EXPORTADOR A REDES SOCIALES **/
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

        const socialPost = `📊 ${question}\n${optionsText}\n\n👇 ¡Sumá tu voto en tiempo real!\n🌐 http://localhost:8001/\n\n#Argentina #Radar360 #Encuesta`;

        if (textContainer) textContainer.innerText = socialPost;
        modal.classList.add('active');
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
                alert('Selecciona y copia el texto manualmente.');
            }
        });
    }
}

/** SUSCRIPCIÓN AL NEWSLETTER **/
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
                alert('🎉 ¡Gracias por suscribirte al Pulso Diario de Argentina!');
                input.value = '';
            } else {
                alert(data.detail || 'No se pudo guardar la suscripción.');
            }
        } catch (err) {
            alert('Error de conexión.');
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
                alert(`✅ Video Short MP4 generado exitosamente.\nPuedes descargarlo o verlo en:\n${data.download_url}`);
                window.location.reload();
            } else {
                alert('No se pudo generar el video short.');
            }
        } catch (err) {
            alert('Error de conexión con la fábrica de shorts.');
        } finally {
            btnGen.innerText = '🎥 Video Short con Voz Neural';
            btnGen.disabled = false;
        }
    });
}

/** FILTRO REGIONAL **/
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
