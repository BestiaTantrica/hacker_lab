/* ==========================================================================
   portal_noticias — INTELIGENCIA B2B (v12.0 Client Logic)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

    // FILTRADO POR TIPO DE FUENTE
    const ejeButtons = document.querySelectorAll('.eje-btn');
    const hubCards = document.querySelectorAll('.card-hub-item');

    ejeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remover estado activo de todos
            ejeButtons.forEach(b => b.classList.remove('active'));
            // Activar el clickeado
            btn.classList.add('active');

            const selectedEje = btn.getAttribute('data-eje');

            hubCards.forEach(card => {
                const cardCat = card.getAttribute('data-category');
                if (selectedEje === 'todos' || cardCat === selectedEje) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

});
