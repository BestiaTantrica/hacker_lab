/* ==========================================================================
   portal_noticias — TERMÓMETRO SOCIAL AR (v10.0 Client Logic)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

    // 1. FILTRADO POR EJES TEMÁTICOS
    const ejeButtons = document.querySelectorAll('.eje-btn');
    const hubCards = document.querySelectorAll('.card-hub-item');

    ejeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            ejeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const selectedEje = btn.getAttribute('data-eje');

            hubCards.forEach(card => {
                const cardCat = card.getAttribute('data-category');
                if (selectedEje === 'todos' || cardCat === selectedEje) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    });

    // 2. FILTRADO POR CLIC EN PALABRAS DE LA NUBE
    const wordTags = document.querySelectorAll('.word-literal-tag');
    const filterBanner = document.getElementById('word-filter-banner');
    const activeWordText = document.getElementById('active-word-text');
    const btnResetWordFilter = document.getElementById('btn-reset-word-filter');

    wordTags.forEach(tag => {
        tag.addEventListener('click', () => {
            const word = tag.getAttribute('data-word');
            if (!word) return;

            filterBanner.style.display = 'flex';
            activeWordText.textContent = word.toUpperCase();

            hubCards.forEach(card => {
                const title = card.getAttribute('data-title') || '';
                const snippet = card.getAttribute('data-snippet') || '';
                const author = card.getAttribute('data-author') || '';

                if (title.includes(word) || snippet.includes(word) || author.includes(word)) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });

            // Scroll suave hacia los resultados
            document.getElementById('catalogo-contenidos')?.scrollIntoView({ behavior: 'smooth' });
        });
    });

    btnResetWordFilter?.addEventListener('click', () => {
        filterBanner.style.display = 'none';
        hubCards.forEach(card => card.classList.remove('hidden'));
    });

    // 3. VOTACIÓN AJAX EN LA ENCUESTA INTERACTIVA DE CONCEPTOS
    const pollButtons = document.querySelectorAll('.poll-option-btn');

    pollButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const pollId = parseInt(btn.getAttribute('data-poll-id'));
            const optionId = parseInt(btn.getAttribute('data-option-id'));

            if (!pollId || !optionId) return;

            try {
                const res = await fetch('/api/public/vote', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ poll_id: pollId, option_id: optionId })
                });

                const data = await res.json();
                if (data.status === 'success') {
                    // Actualizar porcentajes visuales en vivo
                    const pollContainer = document.getElementById(`poll-options-${pollId}`);
                    if (pollContainer) {
                        data.results.forEach(resOpt => {
                            const optBtn = pollContainer.querySelector(`[data-option-id="${resOpt.id}"]`);
                            if (optBtn) {
                                const fill = optBtn.querySelector('.progress-fill');
                                const pctSpan = optBtn.querySelector('.option-pct');
                                if (fill) fill.style.width = `${resOpt.percentage}%`;
                                if (pctSpan) pctSpan.textContent = `${resOpt.percentage}%`;
                            }
                        });
                    }

                    const counter = document.getElementById(`poll-total-${pollId}`);
                    if (counter) counter.textContent = `${data.total_votes} votos registrados acumulados`;

                    alert('¡Voto registrado exitosamente en el Termómetro Social!');
                }
            } catch (err) {
                console.error('Error registrando voto:', err);
                alert('No se pudo guardar el voto. Intenta nuevamente.');
            }
        });
    });

    // 4. REGISTRO DE PALABRA PERSONALIZADA DEL USUARIO
    const formCustomWord = document.getElementById('form-custom-word');
    const inputCustomWord = document.getElementById('input-custom-word');
    const customWordsList = document.getElementById('custom-words-list');

    formCustomWord?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const word = inputCustomWord.value.trim();
        if (!word) return;

        try {
            const res = await fetch('/api/public/submit_custom_word', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ word: word })
            });

            const data = await res.json();
            if (data.status === 'success') {
                alert(data.message);
                inputCustomWord.value = '';

                // Actualizar la lista de palabras personalizadas visualmente
                if (customWordsList && data.top_custom_words) {
                    customWordsList.innerHTML = data.top_custom_words.map(([w, cnt]) => 
                        `<span class="badge-tag streamers_youtubers" style="font-size: 0.75rem;">${w} (${cnt})</span>`
                    ).join('');
                }
            } else {
                alert(data.detail || 'Error al guardar palabra');
            }
        } catch (err) {
            console.error('Error enviando palabra:', err);
            alert('No se pudo registrar la palabra. Intenta nuevamente.');
        }
    });

    // 5. GENERACIÓN DEL SHORT ANZUELO VISUAL
    const btnGenerateShort = document.getElementById('btn-generate-short');
    const videoPlayer = document.getElementById('short-video-player');

    btnGenerateShort?.addEventListener('click', async () => {
        btnGenerateShort.disabled = true;
        btnGenerateShort.textContent = '⏳ Generando Short Anzuelo Visual...';

        try {
            const res = await fetch('/api/public/generate_short');
            const data = await res.json();

            if (data.status === 'success' && data.download_url) {
                if (videoPlayer) {
                    videoPlayer.src = data.download_url;
                    videoPlayer.load();
                    videoPlayer.play();
                }
                alert('¡Short Anzuelo Visual generado exitosamente!');
            } else {
                alert('No se pudo generar el video short.');
            }
        } catch (err) {
            console.error('Error generando short:', err);
            alert('Ocurrió un error generando el video short.');
        } finally {
            btnGenerateShort.disabled = false;
            btnGenerateShort.textContent = '🎥 Generar / Actualizar Video Short Anzuelo';
        }
    });

    // 6. BOTÓN 1-CLIC COPY DE TEXTO DE COMENTARIOS CON LINK
    const btnCopyCommentText = document.getElementById('btn-copy-comment-text');

    btnCopyCommentText?.addEventListener('click', () => {
        const textToCopy = btnCopyCommentText.getAttribute('data-copy-text');
        if (textToCopy) {
            navigator.clipboard.writeText(textToCopy).then(() => {
                alert('📋 ¡Texto + Link de Comentario copiado al portapapeles! Listo para pegar en TikTok, X o YouTube Shorts.');
            }).catch(err => {
                console.error('Error al copiar:', err);
            });
        }
    });

    // 7. CAPTURA DE BOLETÍN DE LEADS
    const leadForm = document.getElementById('lead-form');
    const leadEmailInput = document.getElementById('lead-email-input');

    leadForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = leadEmailInput.value.trim();
        if (!email) return;

        try {
            const res = await fetch('/api/public/subscribe_lead', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            });
            const data = await res.json();
            if (data.status === 'success') {
                alert('¡Gracias por suscribirte al Termómetro Social!');
                leadEmailInput.value = '';
            }
        } catch (err) {
            console.error('Error al suscribir lead:', err);
        }
    });

});
