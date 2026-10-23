const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const QRCode = require('qrcode');
const http = require('http');
const path = require('path');
const fs = require('fs');
const pino = require('pino');

const PORT = 3001;
const AUTH_DIR = path.join(__dirname, 'auth_info');
const API_URL = 'http://127.0.0.1:8000/api/admin/ai/whatsapp-reply';

let sock = null;
let lastQr = null;
let isConnected = false;
let connectedPhone = null;

async function startWhatsApp() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);

  sock = makeWASocket({
    auth: state,
    printQRInTerminal: true,
    logger: pino({ level: 'silent' }),
    browser: ['EcoMarvex Tienda', 'Chrome', '120.0.0']
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      try {
        lastQr = await QRCode.toDataURL(qr, { width: 300, margin: 2 });
        isConnected = false;
        console.log('[WhatsApp] Nuevo código QR generado.');
      } catch (err) {
        console.error('[WhatsApp] Error convirtiendo QR a data URL:', err);
      }
    }

    if (connection === 'close') {
      const statusCode = lastDisconnect?.error?.output?.statusCode;
      const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
      isConnected = false;
      connectedPhone = null;
      console.log(`[WhatsApp] Conexión cerrada. Razón/Código: ${statusCode}. Reconectando: ${shouldReconnect}`);

      if (shouldReconnect) {
        setTimeout(startWhatsApp, 3000);
      } else {
        console.log('[WhatsApp] Sesión cerrada permanentemente. Limpiando credenciales...');
        fs.rmSync(AUTH_DIR, { recursive: true, force: true });
        lastQr = null;
        setTimeout(startWhatsApp, 3000);
      }
    } else if (connection === 'open') {
      isConnected = true;
      lastQr = null;
      connectedPhone = sock.user?.id ? sock.user.id.split(':')[0] : 'Conectado';
      console.log(`[WhatsApp] ¡Conexión establecida con éxito! Número: ${connectedPhone}`);
    }
  });

  // Escuchar mensajes entrantes para responder automáticamente 24/7
  sock.ev.on('messages.upsert', async (m) => {
    if (m.type !== 'notify') return;

    for (const msg of m.messages) {
      if (msg.key.fromMe) continue; // Ignorar mis propios mensajes
      const remoteJid = msg.key.remoteJid;
      if (!remoteJid || remoteJid.includes('@g.us') || remoteJid.includes('status@broadcast')) {
        continue; // Ignorar grupos y estados de WhatsApp
      }

      const text = msg.message?.conversation ||
                   msg.message?.extendedTextMessage?.text ||
                   msg.message?.imageMessage?.caption;

      if (!text || text.trim().length === 0) continue;

      console.log(`[WhatsApp] Mensaje recibido de ${remoteJid}: "${text}"`);

      // Procesar respuesta con el cerebro Gemini
      try {
        // Enviar presencia "escribiendo..."
        await sock.sendPresenceUpdate('composing', remoteJid);

        // Llamar al endpoint local de FastAPI
        const response = await fetch(API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ customer_message: text })
        });

        if (!response.ok) {
          console.error('[WhatsApp] Error desde FastAPI /api/admin/ai/whatsapp-reply');
          await sock.sendPresenceUpdate('paused', remoteJid);
          continue;
        }

        const data = await response.json();
        const replyText = data.reply;

        if (replyText) {
          // Simular delay de tipeo humano (3.5 a 5.5 segundos)
          const delayMs = Math.floor(Math.random() * 2000) + 3500;
          console.log(`[WhatsApp] Esperando delay humano de ${delayMs}ms antes de enviar...`);
          await new Promise((resolve) => setTimeout(resolve, delayMs));

          await sock.sendMessage(remoteJid, { text: replyText }, { quoted: msg });
          console.log(`[WhatsApp] Respuesta enviada con éxito a ${remoteJid}`);
        }

        await sock.sendPresenceUpdate('paused', remoteJid);
      } catch (err) {
        console.error('[WhatsApp] Error respondiendo mensaje:', err);
      }
    }
  });
}

// Servidor HTTP interno para el Panel de Control
const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  if (req.url === '/status' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      connected: isConnected,
      phone: connectedPhone,
      has_qr: !!lastQr
    }));
  } else if (req.url === '/qr' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      connected: isConnected,
      qr: lastQr
    }));
  } else if (req.url === '/disconnect' && req.method === 'POST') {
    try {
      isConnected = false;
      connectedPhone = null;
      lastQr = null;
      if (sock) {
        sock.logout();
      }
      fs.rmSync(AUTH_DIR, { recursive: true, force: true });
      setTimeout(startWhatsApp, 2000);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true }));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: err.message }));
    }
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[WhatsApp Bridge] Servidor interno escuchando en http://127.0.0.1:${PORT}`);
  startWhatsApp();
});
