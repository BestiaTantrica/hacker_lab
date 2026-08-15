/**
 * app.js — Lógica Interactiva (Termómetro, Newsletter, Shorts & Filtro Regional Exacto)
 */

document.addEventListener('DOMContentLoaded', () => {
    initPollSystem();
    initLeadForm();
    initShortGenerator();
    initRegionSelector();
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
        btnGen.innerText = '🎬 Generando Video Short con Voz...';
        btnGen.disabled = true;

        try {
            const res = await fetch('/api/public/generate_short');
            const data = await res.json();

            if (data.status === 'success') {
                alert(`✅ Short con Voz generado exitosamente.\nPuedes descargarlo listo para YouTube Shorts desde:\n${data.download_url}`);
                window.open(data.download_url, '_blank');
            } else {
                alert('No se pudo generar el video short.');
            }
        } catch (err) {
            alert('Error al conectar con la fábrica de shorts.');
        } finally {
            btnGen.innerText = '🎥 Descargar Short en Video con Voz (1080x1920)';
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
