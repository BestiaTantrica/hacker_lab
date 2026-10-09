document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('subscribeForm');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');
    const messageDiv = document.getElementById('formMessage');
    
    let currentUserEmail = "";

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // UI State: Loading
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
        messageDiv.classList.remove('show');
        messageDiv.classList.add('hidden');
        
        const personalResponseDiv = document.getElementById('personalResponse');
        personalResponseDiv.classList.add('hidden');
        personalResponseDiv.innerHTML = '';
        
        messageDiv.textContent = 'Conectando con el cosmos y calculando tránsitos en vivo. Esto tomará unos segundos...';
        messageDiv.className = 'message show';
        
        const formData = new FormData(form);

        try {
            // Suscribir
            const subPromise = fetch('/api/subscribe', { method: 'POST', body: formData });
            
            // Generar lectura en vivo
            const vivoPromise = fetch('/api/transito-vivo', { method: 'POST', body: formData });
            
            const [subRes, vivoRes] = await Promise.all([subPromise, vivoPromise]);
            
            const subResult = await subRes.json();
            const vivoResult = await vivoRes.json();
            
            messageDiv.textContent = subResult.message;
            messageDiv.className = 'message show ' + (subResult.status === 'success' ? 'success' : 'error');
            
            if (vivoResult.status === 'success' && vivoResult.html) {
                personalResponseDiv.innerHTML = vivoResult.html;
                personalResponseDiv.classList.remove('hidden');
                document.getElementById('chatContainer').classList.remove('hidden');
            }
            
            if (subResult.status === 'success') {
                currentUserEmail = formData.get('email');
                form.reset();
            }
            
        } catch (error) {
            messageDiv.textContent = 'Hubo un error de conexión. Inténtalo de nuevo.';
            messageDiv.className = 'message show error';
        } finally {
            // UI State: Reset
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
        }
    });

    const rectifyForm = document.getElementById('rectifyForm');
    if (rectifyForm) {
        rectifyForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(rectifyForm);
            const rMsg = document.getElementById('rectifyMessage');
            rMsg.classList.remove('hidden');
            rMsg.textContent = 'Actualizando hora en Nodriza...';
            rMsg.className = 'message show';

            try {
                const res = await fetch('/api/update-time', { method: 'POST', body: formData });
                const result = await res.json();
                rMsg.textContent = result.message;
                rMsg.className = 'message show ' + (result.status === 'success' ? 'success' : 'error');
                if (result.status === 'success') {
                    rectifyForm.reset();
                    setTimeout(() => rectifyForm.classList.add('hidden'), 3000);
                }
            } catch (error) {
                rMsg.textContent = 'Error de conexión.';
                rMsg.className = 'message show error';
            }
        });
    }

    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatHistory = document.getElementById('chatHistory');
    
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message || !currentUserEmail) return;
            
            // Agregar mensaje del usuario
            chatHistory.innerHTML += `<div style="color: #fff; align-self: flex-end; margin-left: auto;"><strong>Tú:</strong> ${message}</div>`;
            chatInput.value = '';
            
            // Loading state
            const loadingId = 'loading-' + Date.now();
            chatHistory.innerHTML += `<div id="${loadingId}" style="color: #aaa;"><strong>Oráculo:</strong> Pensando...</div>`;
            chatHistory.scrollTop = chatHistory.scrollHeight;
            
            const chatFormData = new FormData();
            chatFormData.append('email', currentUserEmail);
            chatFormData.append('message', message);
            
            try {
                const res = await fetch('/api/chat', { method: 'POST', body: chatFormData });
                const result = await res.json();
                
                document.getElementById(loadingId).remove();
                if (result.status === 'success') {
                    chatHistory.innerHTML += `<div style="color: #4a90e2;"><strong>Oráculo:</strong> ${result.reply}</div>`;
                } else {
                    chatHistory.innerHTML += `<div style="color: #ff3333;"><strong>Error:</strong> ${result.message}</div>`;
                }
            } catch (error) {
                document.getElementById(loadingId).remove();
                chatHistory.innerHTML += `<div style="color: #ff3333;"><strong>Error:</strong> No se pudo conectar con el Oráculo.</div>`;
            }
            chatHistory.scrollTop = chatHistory.scrollHeight;
        });
    }
});
