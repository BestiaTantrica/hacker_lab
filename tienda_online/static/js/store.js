// Estado del Carrito en LocalStorage
let cart = JSON.parse(localStorage.getItem('dropship_cart') || '[]');

document.addEventListener('DOMContentLoaded', () => {
  updateCartBadge();
  setupSearch();
  checkUrlParams();
});

function saveCart() {
  localStorage.setItem('dropship_cart', JSON.stringify(cart));
  updateCartBadge();
  renderCartDrawer();
}

function updateCartBadge() {
  const count = cart.reduce((acc, item) => acc + item.quantity, 0);
  const badge = document.getElementById('cartCount');
  if (badge) badge.innerText = count;
}

function addToCart(id, title, price, image, origin = 'CABA / GBA', supplier = 'Dropsheable Mayorista') {
  const existing = cart.find(item => item.id === id);
  if (existing) {
    existing.quantity += 1;
    if (!existing.origin) existing.origin = origin;
    if (!existing.supplier) existing.supplier = supplier;
  } else {
    cart.push({ id, title, price, image, origin, supplier, quantity: 1 });
  }
  saveCart();
  
  // Abrir carrito y dar feedback
  const drawer = document.getElementById('cartDrawer');
  const overlay = document.getElementById('cartOverlay');
  if (drawer && !drawer.classList.contains('open')) {
    drawer.classList.add('open');
    overlay.classList.add('open');
  }
}

function updateQuantity(id, delta) {
  const item = cart.find(i => i.id === id);
  if (!item) return;
  
  item.quantity += delta;
  if (item.quantity <= 0) {
    cart = cart.filter(i => i.id !== id);
  }
  saveCart();
}

function removeFromCart(id) {
  cart = cart.filter(i => i.id !== id);
  saveCart();
}

function toggleCart() {
  const drawer = document.getElementById('cartDrawer');
  const overlay = document.getElementById('cartOverlay');
  drawer.classList.toggle('open');
  overlay.classList.toggle('open');
  if (drawer.classList.contains('open')) {
    renderCartDrawer();
  }
}

function renderCartDrawer() {
  const list = document.getElementById('cartItemsList');
  const alertEl = document.getElementById('cartLogisticsAlert');
  const subtotalEl = document.getElementById('cartSubtotal');
  const shippingEl = document.getElementById('cartShipping');
  const totalEl = document.getElementById('cartTotal');
  const checkoutBtn = document.getElementById('checkoutBtn');
  
  if (!list) return;

  if (cart.length === 0) {
    if (alertEl) alertEl.innerHTML = '';
    list.innerHTML = `
      <div class="cart-empty">
        <i class="fa-solid fa-basket-shopping"></i>
        <p>Tu carrito está vacío</p>
      </div>
    `;
    subtotalEl.innerText = '$0';
    if (shippingEl) shippingEl.innerText = '$0';
    totalEl.innerText = '$0';
    checkoutBtn.disabled = true;
    return;
  }

  let subtotal = 0;
  list.innerHTML = cart.map(item => {
    const lineTotal = item.price * item.quantity;
    subtotal += lineTotal;
    const itemOrigin = item.origin || 'CABA / GBA';
    return `
      <div class="cart-item">
        <img src="${item.image || 'https://via.placeholder.com/60'}" class="cart-item-img" alt="${item.title}">
        <div class="cart-item-info">
          <div class="cart-item-title">${item.title}</div>
          <div class="cart-item-price">$${item.price.toLocaleString('es-AR')}</div>
          <small style="font-size:0.72rem; color:#64748b;"><i class="fa-solid fa-location-dot"></i> ${itemOrigin}</small>
        </div>
        <div class="cart-item-qty">
          <button class="qty-btn" onclick="updateQuantity(${item.id}, -1)">-</button>
          <span>${item.quantity}</span>
          <button class="qty-btn" onclick="updateQuantity(${item.id}, 1)">+</button>
        </div>
        <button class="cart-item-remove" onclick="removeFromCart(${item.id})"><i class="fa-solid fa-trash-can"></i></button>
      </div>
    `;
  }).join('');

  // Análisis Logístico de Orígenes de Envío
  const cfg = window.STORE_CONFIG || { shippingFlatRate: 0, freeShippingMin: 0 };
  const origins = [...new Set(cart.map(i => i.origin || 'CABA / GBA'))];
  const packageCount = origins.length;

  if (alertEl) {
    if (packageCount === 1) {
      alertEl.innerHTML = `
        <div class="logistics-box unified">
          <i class="fa-solid fa-boxes-packing"></i>
          <div>
            <strong>¡Envío Unificado! (1 solo flete)</strong>
            <p>Todos tus productos salen del depósito <strong>${origins[0]}</strong> en un único paquete.</p>
          </div>
        </div>
      `;
    } else {
      alertEl.innerHTML = `
        <div class="logistics-box multi">
          <i class="fa-solid fa-truck-ramp-box"></i>
          <div>
            <strong>Despacho Multi-Depósito (${packageCount} bultos)</strong>
            <p>Tus productos provienen de orígenes distintos: <strong>${origins.join(', ')}</strong>. Se despacharán en paquetes separados.</p>
          </div>
        </div>
      `;
    }
  }

  // Cálculo automático de costo de envío
  let shippingCost = 0;
  if (cfg.shippingFlatRate > 0) {
    if (cfg.freeShippingMin > 0 && subtotal >= (cfg.freeShippingMin * packageCount)) {
      shippingCost = 0;
    } else {
      shippingCost = cfg.shippingFlatRate * packageCount;
    }
  }

  subtotalEl.innerText = `$${subtotal.toLocaleString('es-AR')}`;
  
  if (shippingEl) {
    if (shippingCost === 0) {
      shippingEl.innerHTML = `<span style="color:#10b981; font-weight:700;">¡Bonificado!</span>`;
    } else {
      shippingEl.innerHTML = `$${shippingCost.toLocaleString('es-AR')} <small style="color:#64748b">(${packageCount} paquete${packageCount > 1 ? 's' : ''})</small>`;
    }
  }

  const finalTotal = subtotal + shippingCost;
  totalEl.innerText = `$${finalTotal.toLocaleString('es-AR')}`;
  checkoutBtn.disabled = false;
}

// Filtro de categorías
function filterCategory(category) {
  document.querySelectorAll('.cat-pill').forEach(btn => {
    btn.classList.toggle('active', btn.innerText === category || (category === 'Todos' && btn.innerText.includes('Todos')));
  });

  document.querySelectorAll('.product-card').forEach(card => {
    const cardCat = card.getAttribute('data-category');
    if (category === 'Todos' || cardCat === category) {
      card.style.display = 'flex';
    } else {
      card.style.display = 'none';
    }
  });
}

// Búsqueda en vivo
function setupSearch() {
  const input = document.getElementById('searchInput');
  if (!input) return;
  input.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    document.querySelectorAll('.product-card').forEach(card => {
      const title = card.getAttribute('data-title');
      if (title.includes(q)) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    });
  });
}

function openCheckoutModal() {
  if (cart.length === 0) return;
  toggleCart(); // Cierra el drawer
  const subtotal = cart.reduce((acc, it) => acc + (it.price * it.quantity), 0);
  const cfg = window.STORE_CONFIG || { shippingFlatRate: 0, freeShippingMin: 0 };
  const origins = [...new Set(cart.map(i => i.origin || 'CABA / GBA'))];
  const packageCount = origins.length;

  let shippingCost = 0;
  if (cfg.shippingFlatRate > 0) {
    if (cfg.freeShippingMin > 0 && subtotal >= (cfg.freeShippingMin * packageCount)) {
      shippingCost = 0;
    } else {
      shippingCost = cfg.shippingFlatRate * packageCount;
    }
  }

  const finalTotal = subtotal + shippingCost;
  const modalTotalEl = document.getElementById('modalTotal');
  if (modalTotalEl) {
    if (shippingCost > 0) {
      modalTotalEl.innerHTML = `$${finalTotal.toLocaleString('es-AR')} <span style="font-size:0.78rem; font-weight:500; color:#64748b;">(Subtotal: $${subtotal.toLocaleString('es-AR')} + Envío ${packageCount > 1 ? `[${packageCount} paquetes]` : ''}: $${shippingCost.toLocaleString('es-AR')})</span>`;
    } else {
      modalTotalEl.innerHTML = `$${finalTotal.toLocaleString('es-AR')} <span style="font-size:0.78rem; font-weight:600; color:#10b981;">(¡Envío Bonificado!)</span>`;
    }
  }
  document.getElementById('checkoutModal').classList.add('open');
}

function closeCheckoutModal() {
  document.getElementById('checkoutModal').classList.remove('open');
}

async function submitOrder(e) {
  e.preventDefault();
  const btn = document.getElementById('submitOrderBtn');
  btn.disabled = true;
  btn.innerText = 'Procesando pedido...';

  const payload = {
    customer_name: document.getElementById('custName').value,
    customer_phone: document.getElementById('custPhone').value,
    customer_email: document.getElementById('custEmail').value,
    shipping_address: document.getElementById('custAddress').value,
    shipping_city: document.getElementById('custCity').value,
    shipping_province: document.getElementById('custProvince').value,
    shipping_postal_code: document.getElementById('custZip').value,
    payment_method: document.querySelector('input[name="payMethod"]:checked').value,
    notes: document.getElementById('orderNotes').value,
    items: cart.map(it => ({ product_id: it.id, quantity: it.quantity }))
  };

  try {
    const res = await fetch('/api/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (!res.ok) {
      alert(data.detail || 'Error procesando la orden.');
      btn.disabled = false;
      btn.innerText = 'Confirmar y Pagar';
      return;
    }

    // Vaciar carrito
    cart = [];
    saveCart();
    closeCheckoutModal();

    // Mostrar modal de éxito según medio de pago
    showSuccessModal(data);
  } catch (err) {
    alert('Error de conexión con el servidor.');
    btn.disabled = false;
    btn.innerText = 'Confirmar y Pagar';
  }
}

function showSuccessModal(data) {
  const modal = document.getElementById('successModal');
  const codeEl = document.getElementById('successCode');
  const titleEl = document.getElementById('successTitle');
  const msgEl = document.getElementById('successMessage');
  const actionEl = document.getElementById('successAction');

  codeEl.innerText = data.order_code;

  if (data.payment_method === 'mercadopago' && data.mp_init_point) {
    titleEl.innerText = '¡Pedido Registrado!';
    msgEl.innerText = 'Haz clic en el botón de abajo para abonar con Mercado Pago de forma segura:';
    actionEl.innerHTML = `
      <a href="${data.mp_init_point}" class="btn-primary-link" target="_blank">
        <i class="fa-solid fa-credit-card"></i> Pagar con Mercado Pago
      </a>
    `;
  } else if (data.payment_method === 'whatsapp' && data.whatsapp_url) {
    titleEl.innerText = '¡Pedido Casi Listo!';
    msgEl.innerText = 'Haz clic para enviar el detalle de tu orden por WhatsApp y coordinar el despacho:';
    actionEl.innerHTML = `
      <a href="${data.whatsapp_url}" class="btn-whatsapp-link" target="_blank">
        <i class="fa-brands fa-whatsapp"></i> Enviar Pedido a WhatsApp
      </a>
    `;
  } else if (data.payment_method === 'transferencia' && data.bank_info) {
    titleEl.innerText = '¡Pedido Registrado con Éxito!';
    msgEl.innerHTML = `
      Por favor transfiere el total a los siguientes datos:<br>
      <strong>Banco/Billetera:</strong> ${data.bank_info.bank_name}<br>
      <strong>Alias:</strong> <code>${data.bank_info.bank_alias}</code><br>
      <strong>CBU:</strong> <code>${data.bank_info.bank_cbu}</code><br>
      <strong>Titular:</strong> ${data.bank_info.bank_holder}<br><br>
      Envíanos el comprobante por WhatsApp indicando el código <strong>${data.order_code}</strong>.
    `;
    actionEl.innerHTML = '';
  } else {
    titleEl.innerText = '¡Pedido Recibido!';
    msgEl.innerText = 'Nos pondremos en contacto contigo a la brevedad para coordinar la entrega.';
    actionEl.innerHTML = '';
  }

  modal.classList.add('open');
}

function closeSuccessModal() {
  document.getElementById('successModal').classList.remove('open');
}

function checkUrlParams() {
  const params = new URLSearchParams(window.location.search);
  const successOrder = params.get('order_success');
  if (successOrder) {
    alert(`¡Gracias por tu pago! Tu orden ${successOrder} fue aprobada con éxito.`);
    window.history.replaceState({}, document.title, "/");
  }
}
