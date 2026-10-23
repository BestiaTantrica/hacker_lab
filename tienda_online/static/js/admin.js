let currentTab = 'dashboard';

document.addEventListener('DOMContentLoaded', () => {
  if (sessionStorage.getItem('admin_auth') === 'true') {
    showAdmin();
  } else {
    document.getElementById('loginModal').style.display = 'flex';
  }
});

async function handleLogin(e) {
  e.preventDefault();
  const pin = document.getElementById('adminPinInput').value;
  const errEl = document.getElementById('loginError');

  const formData = new FormData();
  formData.append('pin', pin);

  try {
    const res = await fetch('/api/admin/login', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (res.ok && data.success) {
      sessionStorage.setItem('admin_auth', 'true');
      showAdmin();
    } else {
      errEl.innerText = data.detail || 'PIN incorrecto.';
    }
  } catch (err) {
    errEl.innerText = 'Error de conexión con el servidor.';
  }
}

function showAdmin() {
  document.getElementById('loginModal').style.display = 'none';
  document.getElementById('adminApp').style.display = 'flex';
  loadDashboardStats();
}

function logout() {
  sessionStorage.removeItem('admin_auth');
  window.location.reload();
}

function switchTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

  if (tab === 'dashboard') {
    document.getElementById('tabDashboard').classList.add('active');
    document.getElementById('pageTitle').innerText = 'Resumen General';
    loadDashboardStats();
  } else if (tab === 'orders') {
    document.getElementById('tabOrders').classList.add('active');
    document.getElementById('pageTitle').innerText = 'Gestión de Pedidos';
    loadOrders();
  } else if (tab === 'products') {
    document.getElementById('tabProducts').classList.add('active');
    document.getElementById('pageTitle').innerText = 'Catálogo de Productos';
    loadProducts();
  } else if (tab === 'ai_assistant') {
    document.getElementById('tabAiAssistant').classList.add('active');
    document.getElementById('pageTitle').innerText = 'Asistente & Marketing IA';
    loadAiProductsDropdown();
  } else if (tab === 'dropsheable') {
    document.getElementById('tabDropsheable').classList.add('active');
    document.getElementById('pageTitle').innerText = 'Centro de Proveedores Dropsheable';
    loadSettings();
  } else if (tab === 'settings') {
    document.getElementById('tabSettings').classList.add('active');
    document.getElementById('pageTitle').innerText = 'Configuración del Negocio';
    loadSettings();
  }

  // Marcar botón activo
  const activeBtn = Array.from(document.querySelectorAll('.nav-item')).find(b => b.getAttribute('onclick')?.includes(tab));
  if (activeBtn) activeBtn.classList.add('active');
}

// DASHBOARD STATS
async function loadDashboardStats() {
  try {
    const res = await fetch('/api/admin/stats');
    const data = await res.json();
    document.getElementById('statRevenue').innerText = `$${data.total_revenue.toLocaleString('es-AR')}`;
    document.getElementById('statProfit').innerText = `$${data.total_profit.toLocaleString('es-AR')}`;
    document.getElementById('statPending').innerText = data.pending_orders;
    document.getElementById('statTotalOrders').innerText = data.total_orders;
    
    const badge = document.getElementById('badgePendingOrders');
    badge.innerText = data.pending_orders;
    badge.style.display = data.pending_orders > 0 ? 'inline-block' : 'none';
  } catch (e) {
    console.error("Error cargando stats:", e);
  }
}

// PEDIDOS (ORDERS)
async function loadOrders() {
  const tbody = document.getElementById('ordersTableBody');
  tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding: 20px;">Cargando pedidos...</td></tr>';

  try {
    const res = await fetch('/api/admin/orders');
    const orders = await res.json();

    if (orders.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding: 30px; color: #64748b;">No hay pedidos registrados aún.</td></tr>';
      return;
    }

    tbody.innerHTML = orders.map(ord => {
      const itemsList = ord.items.map(it => `• ${it.quantity}x ${it.title}`).join('<br>');
      const phoneClean = ord.customer_phone ? ord.customer_phone.replace(/\D/g, '') : '';
      const whatsappBtn = phoneClean ? `
        <a href="https://wa.me/${phoneClean}" target="_blank" class="btn-sm-action btn-whatsapp-sm" title="Escribir por WhatsApp">
          <i class="fa-brands fa-whatsapp"></i> Chat
        </a>
      ` : '';

      return `
        <tr>
          <td><strong>${ord.order_code}</strong></td>
          <td style="font-size:0.8rem; color:#64748b;">${ord.created_at || '-'}</td>
          <td>
            <strong>${ord.customer_name}</strong><br>
            <span style="font-size:0.8rem; color:#64748b;">${ord.customer_phone || ''}</span>
            ${whatsappBtn}
          </td>
          <td style="font-size:0.85rem;">${itemsList}</td>
          <td><strong>$${ord.total.toLocaleString('es-AR')}</strong></td>
          <td class="text-green">+$${ord.estimated_profit.toLocaleString('es-AR')}</td>
          <td>
            <select class="form-group" style="padding:4px 8px; font-size:0.8rem; margin:0;" onchange="updateOrderStatus(${ord.id}, this.value)">
              <option value="nuevo" ${ord.order_status === 'nuevo' ? 'selected' : ''}>Nuevo</option>
              <option value="pagado" ${ord.order_status === 'pagado' ? 'selected' : ''}>Pagado</option>
              <option value="en_proveedor" ${ord.order_status === 'en_proveedor' ? 'selected' : ''}>En Dropsheable</option>
              <option value="enviado" ${ord.order_status === 'enviado' ? 'selected' : ''}>Enviado</option>
              <option value="entregado" ${ord.order_status === 'entregado' ? 'selected' : ''}>Entregado</option>
              <option value="cancelado" ${ord.order_status === 'cancelado' ? 'selected' : ''}>Cancelado</option>
            </select>
          </td>
          <td>
            <input type="text" value="${ord.tracking_code || ''}" placeholder="Guía de Correo" style="width:130px; font-size:0.8rem; padding:4px;" onchange="updateOrderTracking(${ord.id}, this.value)">
          </td>
          <td>
            <span class="status-pill status-${ord.order_status}">${ord.order_status.toUpperCase()}</span>
          </td>
        </tr>
      `;
    }).join('');
  } catch (e) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:red;">Error cargando pedidos.</td></tr>';
  }
}

async function updateOrderStatus(orderId, newStatus) {
  try {
    await fetch(`/api/admin/orders/${orderId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_status: newStatus })
    });
    loadDashboardStats();
  } catch (e) {
    alert("Error actualizando estado del pedido");
  }
}

async function updateOrderTracking(orderId, tracking) {
  try {
    await fetch(`/api/admin/orders/${orderId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tracking_code: tracking })
    });
  } catch (e) {
    alert("Error guardando guía de seguimiento");
  }
}

// PRODUCTOS
async function loadProducts() {
  const tbody = document.getElementById('productsTableBody');
  tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">Cargando catálogo...</td></tr>';

  try {
    const res = await fetch('/api/admin/products');
    const prods = await res.json();

    tbody.innerHTML = prods.map(p => {
      const profit = p.sale_price - p.cost_price;
      const margin = p.cost_price > 0 ? Math.round((profit / p.cost_price) * 100) : 100;
      return `
        <tr>
          <td><img src="${p.image_url || 'https://via.placeholder.com/50'}" style="width:45px; height:45px; object-fit:cover; border-radius:6px;"></td>
          <td>
            <strong>${p.title}</strong><br>
            <span style="font-size:0.75rem; color:#64748b;">SKU: ${p.supplier_sku || 'N/A'}</span>
            <span style="font-size:0.75rem; color:#0369a1; margin-left:6px;"><i class="fa-solid fa-location-dot"></i> ${p.shipping_origin || 'CABA / GBA'}</span>
            ${p.supplier_url ? `<a href="${p.supplier_url}" target="_blank" style="font-size:0.75rem; margin-left:6px; color:#0284c7;"><i class="fa-solid fa-arrow-up-right-from-square"></i> Dropsheable</a>` : ''}
          </td>
          <td><span class="status-pill" style="background:#e2e8f0; color:#334155;">${p.category}</span></td>
          <td>$${p.cost_price.toLocaleString('es-AR')}</td>
          <td><strong>$${p.sale_price.toLocaleString('es-AR')}</strong></td>
          <td class="text-green">+$${profit.toLocaleString('es-AR')} (${margin}%)</td>
          <td>${p.stock}</td>
          <td>
            <button class="btn-sm-action" onclick="openAiGenerator(${p.id}, '${p.title.replace(/'/g, "\\'")}')" style="color:#8b5cf6;" title="Generar Publicación Viral con IA"><i class="fa-solid fa-wand-magic-sparkles"></i></button>
            <button class="btn-sm-action" onclick='editProduct(${JSON.stringify(p)})' title="Editar"><i class="fa-solid fa-pen"></i></button>
            <button class="btn-sm-action" onclick="deleteProduct(${p.id})" style="color:red;" title="Eliminar"><i class="fa-solid fa-trash"></i></button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (e) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:red;">Error cargando catálogo.</td></tr>';
  }
}

function calcProfit() {
  const cost = parseFloat(document.getElementById('prodCostPrice').value) || 0;
  const sale = parseFloat(document.getElementById('prodSalePrice').value) || 0;
  const profit = sale - cost;
  const margin = cost > 0 ? Math.round((profit / cost) * 100) : (sale > 0 ? 100 : 0);

  document.getElementById('calcProfitAmount').innerText = `$${profit.toLocaleString('es-AR')}`;
  document.getElementById('calcProfitMargin').innerText = `${margin}%`;
}

function openProductModal() {
  document.getElementById('prodEditId').value = '';
  document.getElementById('productForm').reset();
  document.getElementById('prodSupplierName').value = 'Dropsheable Mayorista';
  document.getElementById('prodShippingOrigin').value = 'CABA / GBA';
  document.getElementById('prodDispatchTime').value = '24-48 hs hábiles';
  document.getElementById('productModalTitle').innerText = 'Nuevo Producto';
  calcProfit();
  document.getElementById('productModal').classList.add('open');
}

function editProduct(p) {
  document.getElementById('prodEditId').value = p.id;
  document.getElementById('prodTitle').value = p.title;
  document.getElementById('prodCategory').value = p.category;
  document.getElementById('prodStock').value = p.stock;
  document.getElementById('prodImageUrl').value = p.image_url;
  document.getElementById('prodDescription').value = p.description;
  document.getElementById('prodCostPrice').value = p.cost_price;
  document.getElementById('prodSalePrice').value = p.sale_price;
  document.getElementById('prodDiscountPrice').value = p.discount_price || 0;
  document.getElementById('prodSupplierSku').value = p.supplier_sku || '';
  document.getElementById('prodSupplierUrl').value = p.supplier_url || '';
  document.getElementById('prodSupplierName').value = p.supplier_name || 'Dropsheable Mayorista';
  document.getElementById('prodShippingOrigin').value = p.shipping_origin || 'CABA / GBA';
  document.getElementById('prodDispatchTime').value = p.dispatch_time || '24-48 hs hábiles';
  document.getElementById('prodFeatured').checked = p.featured === 1;
  document.getElementById('prodActive').checked = p.active === 1;

  document.getElementById('productModalTitle').innerText = 'Editar Producto';
  calcProfit();
  document.getElementById('productModal').classList.add('open');
}

function closeProductModal() {
  document.getElementById('productModal').classList.remove('open');
}

async function saveProduct(e) {
  e.preventDefault();
  const id = document.getElementById('prodEditId').value;
  const payload = {
    title: document.getElementById('prodTitle').value,
    category: document.getElementById('prodCategory').value || 'General',
    stock: parseInt(document.getElementById('prodStock').value) || 0,
    image_url: document.getElementById('prodImageUrl').value,
    description: document.getElementById('prodDescription').value,
    cost_price: parseFloat(document.getElementById('prodCostPrice').value) || 0,
    sale_price: parseFloat(document.getElementById('prodSalePrice').value) || 0,
    discount_price: parseFloat(document.getElementById('prodDiscountPrice').value) || 0,
    supplier_sku: document.getElementById('prodSupplierSku').value,
    supplier_url: document.getElementById('prodSupplierUrl').value,
    supplier_name: document.getElementById('prodSupplierName').value || 'Dropsheable Mayorista',
    shipping_origin: document.getElementById('prodShippingOrigin').value || 'CABA / GBA',
    dispatch_time: document.getElementById('prodDispatchTime').value || '24-48 hs hábiles',
    featured: document.getElementById('prodFeatured').checked ? 1 : 0,
    active: document.getElementById('prodActive').checked ? 1 : 0
  };

  const url = id ? `/api/admin/products/${id}` : '/api/admin/products';
  const method = id ? 'PUT' : 'POST';

  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      closeProductModal();
      loadProducts();
    } else {
      alert("Error guardando producto");
    }
  } catch (err) {
    alert("Error de conexión");
  }
}

async function deleteProduct(id) {
  if (!confirm("¿Seguro que deseas eliminar este producto?")) return;
  try {
    await fetch(`/api/admin/products/${id}`, { method: 'DELETE' });
    loadProducts();
  } catch (e) {
    alert("Error eliminando producto");
  }
}

// CONFIGURACIÓN (SETTINGS)
async function loadSettings() {
  try {
    const res = await fetch('/api/admin/settings');
    const s = await res.json();
    document.getElementById('cfgStoreName').value = s.store_name || '';
    document.getElementById('cfgStoreDesc').value = s.store_description || '';
    document.getElementById('cfgWhatsapp').value = s.whatsapp_phone || '';
    document.getElementById('cfgAdminPin').value = s.admin_pin || '1234';
    document.getElementById('cfgMpToken').value = s.mp_access_token || '';
    document.getElementById('cfgMpKey').value = s.mp_public_key || '';
    document.getElementById('cfgBankName').value = s.bank_name || '';
    document.getElementById('cfgBankHolder').value = s.bank_holder || '';
    document.getElementById('cfgBankAlias').value = s.bank_alias || '';
    document.getElementById('cfgBankCbu').value = s.bank_cbu || '';
    document.getElementById('cfgShippingFlat').value = s.shipping_flat_rate || 0;
    document.getElementById('cfgShippingFreeMin').value = s.free_shipping_min || 0;
    document.getElementById('cfgShippingPolicy').value = s.shipping_policy_text || '';
    document.getElementById('cfgGeminiKey').value = s.gemini_api_key || '';
    if (document.getElementById('cfgGeminiKeyBackup')) {
      document.getElementById('cfgGeminiKeyBackup').value = s.gemini_api_key_backup || '';
    }
    if (document.getElementById('cfgDropsheableKey')) {
      document.getElementById('cfgDropsheableKey').value = s.dropsheable_api_key || s.dropsheable_api_token || '';
    }
    if (document.getElementById('cfgDropsheableSecret')) {
      document.getElementById('cfgDropsheableSecret').value = s.dropsheable_api_secret || '';
    }
    if (document.getElementById('waAutoReplyToggle')) {
      document.getElementById('waAutoReplyToggle').checked = s.whatsapp_auto_reply !== '0';
    }
    checkWhatsAppStatus();
  } catch (e) {
    console.error("Error cargando configuración:", e);
  }
}

async function saveSettings() {
  const payload = {
    store_name: document.getElementById('cfgStoreName').value,
    store_description: document.getElementById('cfgStoreDesc').value,
    whatsapp_phone: document.getElementById('cfgWhatsapp').value,
    admin_pin: document.getElementById('cfgAdminPin').value,
    mp_access_token: document.getElementById('cfgMpToken').value,
    mp_public_key: document.getElementById('cfgMpKey').value,
    bank_name: document.getElementById('cfgBankName').value,
    bank_holder: document.getElementById('cfgBankHolder').value,
    bank_alias: document.getElementById('cfgBankAlias').value,
    bank_cbu: document.getElementById('cfgBankCbu').value,
    shipping_flat_rate: document.getElementById('cfgShippingFlat').value,
    free_shipping_min: document.getElementById('cfgShippingFreeMin').value,
    shipping_policy_text: document.getElementById('cfgShippingPolicy').value,
    gemini_api_key: document.getElementById('cfgGeminiKey').value,
    gemini_api_key_backup: document.getElementById('cfgGeminiKeyBackup') ? document.getElementById('cfgGeminiKeyBackup').value : '',
    dropsheable_api_key: document.getElementById('cfgDropsheableKey') ? document.getElementById('cfgDropsheableKey').value : '',
    dropsheable_api_secret: document.getElementById('cfgDropsheableSecret') ? document.getElementById('cfgDropsheableSecret').value : '',
    dropsheable_api_token: document.getElementById('cfgDropsheableKey') ? document.getElementById('cfgDropsheableKey').value : ''
  };

  try {
    const res = await fetch('/api/admin/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      alert("✅ Configuración guardada correctamente.");
    } else {
      alert("Error guardando cambios.");
    }
  } catch (e) {
    alert("Error de conexión");
  }
}

// GENERADOR DE CONTENIDO VIRAL CON IA (GEMINI)
let currentAiCaption = '';

async function openAiGenerator(productId, productTitle) {
  document.getElementById('aiModalTitle').innerHTML = `<i class="fa-solid fa-wand-magic-sparkles" style="color:#8b5cf6;"></i> Publicación IA: ${productTitle}`;
  document.getElementById('aiLoading').style.display = 'block';
  document.getElementById('aiResults').style.display = 'none';
  document.getElementById('aiModal').classList.add('open');

  try {
    const res = await fetch('/api/admin/generate-content', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error generando contenido');

    document.getElementById('aiHook').innerText = data.tiktok_hook || '-';
    document.getElementById('aiScript').innerText = data.tiktok_script || '-';
    document.getElementById('aiCaption').innerText = data.instagram_caption || '-';
    document.getElementById('aiHashtags').innerText = data.hashtags || '-';
    currentAiCaption = (data.instagram_caption || '') + '\n\n' + (data.hashtags || '');

    document.getElementById('aiLoading').style.display = 'none';
    document.getElementById('aiResults').style.display = 'flex';
  } catch (err) {
    document.getElementById('aiLoading').innerHTML = `<div style="text-align:center; padding:20px; color:#ef4444;"><i class="fa-solid fa-triangle-exclamation" style="font-size:2rem; margin-bottom:10px;"></i><p><strong>Error al generar contenido:</strong> ${err.message}</p></div>`;
  }
}

function closeAiModal() {
  document.getElementById('aiModal').classList.remove('open');
}

function copyInstagramCopy() {
  if (!currentAiCaption) return;
  navigator.clipboard.writeText(currentAiCaption).then(() => {
    alert("¡Texto copiado al portapapeles! Listo para pegar en Instagram / TikTok.");
  }).catch(() => {
    alert("Copia manualmente el texto seleccionado.");
  });
}

// ASISTENTE & MARKETING IA (TAB DEDICADA)
let allProductsCache = [];
let currentAssistantText = '';

async function loadAiProductsDropdown() {
  const select = document.getElementById('aiSocialProductSelect');
  if (!select) return;
  select.innerHTML = '<option value="">Cargando productos...</option>';

  try {
    const res = await fetch('/api/admin/products');
    allProductsCache = await res.json();

    if (allProductsCache.length === 0) {
      select.innerHTML = '<option value="">No hay productos cargados aún</option>';
      return;
    }

    select.innerHTML = allProductsCache.map(p => 
      `<option value="${p.id}">${p.title} - $${p.sale_price.toLocaleString('es-AR')}</option>`
    ).join('');
  } catch (e) {
    select.innerHTML = '<option value="">Error cargando productos</option>';
  }
}

function triggerAiSocialFromTab() {
  const select = document.getElementById('aiSocialProductSelect');
  const prodId = select ? select.value : '';
  if (!prodId) {
    alert("Selecciona un producto del menú desplegable.");
    return;
  }
  const prod = allProductsCache.find(p => p.id == prodId);
  const title = prod ? prod.title : 'Producto';
  openAiGenerator(prodId, title);
}

async function triggerAiWhatsAppReply() {
  const msg = document.getElementById('aiWaCustomerMessage').value.trim();
  const prodTitle = document.getElementById('aiWaProductTitle').value.trim();
  if (!msg) {
    alert("Por favor ingresa la pregunta que te hizo el cliente.");
    return;
  }

  showAssistantResult("Generando respuesta para WhatsApp con IA...", "Cargando...", true);

  try {
    const res = await fetch('/api/admin/ai/whatsapp-reply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer_message: msg, product_title: prodTitle })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error generando respuesta');

    showAssistantResult(data.reply, `Modelo utilizado: ${data.model_used}`);
  } catch (err) {
    showAssistantResult(`Error: ${err.message}`, "Error", false);
  }
}

async function triggerAiAdvisor() {
  const q = document.getElementById('aiAdvisorQuestion').value.trim();
  if (!q) {
    alert("Por favor escribe tu consulta para el asesor de Dropshipping.");
    return;
  }

  showAssistantResult("Consultando al Asesor Estratégico...", "Pensando...", true);

  try {
    const res = await fetch('/api/admin/ai/advisor', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error en la consulta');

    showAssistantResult(data.advice, `Modelo utilizado: ${data.model_used}`);
  } catch (err) {
    showAssistantResult(`Error: ${err.message}`, "Error", false);
  }
}

function showAssistantResult(text, badgeText, isLoading = false) {
  const card = document.getElementById('aiAssistantResultCard');
  const body = document.getElementById('aiAssistantResultBody');
  const badge = document.getElementById('aiModelBadge');
  if (!card || !body) return;

  currentAssistantText = text;
  badge.innerText = badgeText;
  
  if (isLoading) {
    body.innerHTML = `<div style="text-align:center; padding:20px; color:#6366f1;"><i class="fa-solid fa-circle-notch fa-spin" style="font-size:2rem; margin-bottom:10px;"></i><p>${text}</p></div>`;
  } else {
    body.innerText = text;
  }

  card.style.display = 'block';
  card.scrollIntoView({ behavior: 'smooth' });
}

function copyAssistantResult() {
  if (!currentAssistantText) return;
  navigator.clipboard.writeText(currentAssistantText).then(() => {
    alert("¡Copiado al portapapeles con éxito!");
  }).catch(() => {
    alert("Copia manualmente el texto.");
  });
}

// ANALIZADOR INTELIGENTE DROPSHEABLE
let currentDropsheableAnalysisText = '';

async function triggerDropsheableAnalysis() {
  const query = document.getElementById('dropsheableQueryInput').value.trim();
  const mode = document.querySelector('input[name="dropsheableMode"]:checked')?.value || 'producto';

  if (!query) {
    alert("Por favor ingresa un producto o proveedor para analizar.");
    return;
  }

  const resultCard = document.getElementById('dropsheableResultCard');
  const resultBody = document.getElementById('dropsheableResultBody');
  resultCard.style.display = 'block';
  resultBody.innerHTML = '<div style="text-align:center; padding:15px; color:#0284c7;"><i class="fa-solid fa-circle-notch fa-spin" style="font-size:1.8rem; margin-bottom:8px;"></i><p>Analizando catálogo de Dropsheable, fletes y márgenes...</p></div>';

  try {
    const res = await fetch('/api/admin/dropsheable/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode, query })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error en el análisis');

    currentDropsheableAnalysisText = data.analysis;
    resultBody.innerText = data.analysis;
  } catch (err) {
    resultBody.innerHTML = `<p style="color:red;"><i class="fa-solid fa-triangle-exclamation"></i> ${err.message}</p>`;
  }
}

function copyDropsheableAnalysis() {
  if (!currentDropsheableAnalysisText) return;
  navigator.clipboard.writeText(currentDropsheableAnalysisText).then(() => {
    alert("¡Análisis copiado al portapapeles!");
  }).catch(() => {
    alert("Copia manualmente el texto.");
  });
}

// GUARDAR CREDENCIALES DROPSHEABLE
async function saveDropsheableCredentials() {
  const apiKey = document.getElementById('cfgDropsheableKey') ? document.getElementById('cfgDropsheableKey').value.trim() : '';
  const apiSecret = document.getElementById('cfgDropsheableSecret') ? document.getElementById('cfgDropsheableSecret').value.trim() : '';

  if (!apiKey || !apiSecret) {
    alert("Por favor completa tanto la API Key como el API Secret de Dropsheable.");
    return;
  }

  const payload = {
    dropsheable_api_key: apiKey,
    dropsheable_api_secret: apiSecret,
    dropsheable_api_token: apiKey
  };

  try {
    const res = await fetch('/api/admin/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      const fb = document.getElementById('dropsheableSaveFeedback');
      if (fb) {
        fb.style.display = 'block';
        setTimeout(() => fb.style.display = 'none', 6000);
      }
      const badge = document.getElementById('dropsheableStatusBadge');
      if (badge) {
        badge.style.background = '#dcfce7';
        badge.style.color = '#15803d';
        badge.innerHTML = '<i class="fa-solid fa-circle-check"></i> Credenciales Guardadas';
      }
      alert("✅ ¡Credenciales de Dropsheable guardadas y activadas con éxito!");
    } else {
      alert("Error al guardar credenciales en el servidor.");
    }
  } catch (err) {
    alert("Error de conexión al guardar credenciales de Dropsheable.");
  }
}

// GESTIÓN WHATSAPP BOT 24/7 (BAILEYS QR)
let waPollInterval = null;

async function checkWhatsAppStatus() {
  const badge = document.getElementById('waConnectionBadge');
  if (!badge) return;

  try {
    const res = await fetch('/api/admin/whatsapp/status');
    const data = await res.json();

    if (data.connected) {
      badge.style.background = '#dcfce7';
      badge.style.color = '#15803d';
      badge.innerHTML = `<i class="fa-solid fa-circle-check"></i> Conectado: ${data.phone || 'Activo'}`;
      if (waPollInterval) {
        clearInterval(waPollInterval);
        waPollInterval = null;
      }
    } else if (data.has_qr) {
      badge.style.background = '#fef3c7';
      badge.style.color = '#b45309';
      badge.innerHTML = '<i class="fa-solid fa-qrcode"></i> Esperando Escaneo QR';
    } else {
      badge.style.background = '#fee2e2';
      badge.style.color = '#b91c1c';
      badge.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> Desconectado';
    }
  } catch (e) {
    badge.style.background = '#f1f5f9';
    badge.style.color = '#64748b';
    badge.innerHTML = '<i class="fa-solid fa-signal"></i> Servicio en espera';
  }
}

async function openWhatsAppQrModal() {
  document.getElementById('whatsappQrModal').classList.add('open');
  await requestNewQrCode();
  
  // Polling para detectar cuando el usuario escanea el QR
  if (waPollInterval) clearInterval(waPollInterval);
  waPollInterval = setInterval(async () => {
    try {
      const res = await fetch('/api/admin/whatsapp/status');
      const data = await res.json();
      if (data.connected) {
        clearInterval(waPollInterval);
        waPollInterval = null;
        closeWhatsAppQrModal();
        checkWhatsAppStatus();
        alert("🎉 ¡WhatsApp vinculado con éxito! Tu bot responderá automáticamente 24/7.");
      }
    } catch (e) {}
  }, 3000);
}

function closeWhatsAppQrModal() {
  document.getElementById('whatsappQrModal').classList.remove('open');
  if (waPollInterval) {
    clearInterval(waPollInterval);
    waPollInterval = null;
  }
}

async function requestNewQrCode() {
  const loading = document.getElementById('waQrLoading');
  const img = document.getElementById('waQrImage');
  loading.style.display = 'block';
  img.style.display = 'none';

  try {
    const res = await fetch('/api/admin/whatsapp/qr');
    const data = await res.json();
    if (data.qr) {
      img.src = data.qr;
      loading.style.display = 'none';
      img.style.display = 'block';
    } else if (data.connected) {
      loading.innerHTML = '<p style="color:#15803d; font-weight:700;"><i class="fa-solid fa-circle-check"></i> ¡Tu WhatsApp ya está conectado!</p>';
    } else {
      loading.innerHTML = `<p style="color:#b91c1c;">${data.detail || 'Iniciando servicio de WhatsApp... reintenta en unos segundos.'}</p>`;
    }
  } catch (err) {
    loading.innerHTML = '<p style="color:#b91c1c;">Error conectando con el servicio de WhatsApp.</p>';
  }
}

async function toggleWaAutoReply(active) {
  try {
    await fetch('/api/admin/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ whatsapp_auto_reply: active ? '1' : '0' })
    });
  } catch (e) {
    console.error("Error toggling auto-reply", e);
  }
}



