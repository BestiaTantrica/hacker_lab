/**
 * app.js — Lógica Interactiva del Portal Público (Termómetro Social & Encuestas)
 */

document.addEventListener('DOMContentLoaded', () => {
    initPollSystem();
});

function initPollSystem() {
    const pollOptions = document.querySelectorAll('.poll-option-btn');
    if (!pollOptions.length) return;

    pollOptions.forEach(btn => {
        btn.addEventListener('click', async () => {
            const pollId = btn.getAttribute('data-poll-id');
            const optionId = btn.getAttribute('data-option-id');

            // Deshabilitar botones temporalmente para evitar doble clic
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
        totalElem.innerText = `${totalVotes.toLocaleString()} votos registrados`;
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
