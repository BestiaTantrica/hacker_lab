document.addEventListener('DOMContentLoaded', () => {
    checkOciStatus();
    // Re-check every 30 seconds
    setInterval(checkOciStatus, 30000);
});

async function checkOciStatus() {
    const dot = document.getElementById('oci-status-dot');
    const text = document.getElementById('oci-status-text');
    const uptime = document.getElementById('oci-uptime');
    const targets = document.getElementById('targets-count');

    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        if (data.status === 'online') {
            dot.className = 'dot green';
            text.textContent = 'ONLINE';
            uptime.textContent = data.uptime;
            targets.textContent = data.targets;
            appendTerminal(`[INFO] Telemetría recibida de OCI-1 exitosamente. Targets listos: ${data.targets}`);
        } else {
            dot.className = 'dot red';
            text.textContent = 'OFFLINE';
            uptime.textContent = 'Sin conexión SSH';
            appendTerminal(`[ERROR] OCI-1 inalcanzable: ${data.message || 'Error SSH'}`);
        }
    } catch (error) {
        dot.className = 'dot red';
        text.textContent = 'ERROR';
        appendTerminal(`[ERROR] Falló la petición a la API local del panel C2.`);
    }
}

function appendTerminal(msg) {
    const terminal = document.getElementById('terminal-output');
    const time = new Date().toLocaleTimeString();
    terminal.innerHTML += `<br>> [${time}] ${msg}`;
    terminal.scrollTop = terminal.scrollHeight;
}
