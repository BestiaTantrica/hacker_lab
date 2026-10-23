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
    gemini_api_key: document.getElementById('cfgGeminiKey').value
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

