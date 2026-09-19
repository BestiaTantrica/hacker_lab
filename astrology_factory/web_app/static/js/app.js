document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('subscribeForm');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');
    const messageDiv = document.getElementById('formMessage');

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
            }
            
            if (subResult.status === 'success') {
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
});
