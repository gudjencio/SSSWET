(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  let token = "";
  let selectedOrder = "";
  const login = $("login-panel"), ordersPanel = $("orders-panel"), detailPanel = $("detail-panel");
  const money = (minor, currency) => new Intl.NumberFormat(undefined, {style:"currency",currency}).format((minor || 0)/100);
  async function api(path, options = {}) {
    const response = await fetch(path, {
      ...options,
      headers: {"X-SSSWET-Admin-Token": token, ...(options.headers || {})}
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "Request failed (" + response.status + ")");
    return data;
  }
  function node(tag, text, className) {
    const el = document.createElement(tag);
    if (text !== undefined) el.textContent = text;
    if (className) el.className = className;
    return el;
  }
  async function connect() {
    token = $("token").value.trim();
    if (token.length < 32) { $("login-message").textContent = "Enter the administrator token (at least 32 characters)."; return; }
    try {
      await loadOrders();
      login.hidden = true;
      ordersPanel.hidden = false;
      $("token").value = "";
    } catch (error) {
      token = "";
      $("login-message").textContent = error.message;
    }
  }
  async function loadOrders() {
    const data = await api("/api/private/orders");
    $("orders").replaceChildren();
    $("summary").textContent = data.orders.length + " recorded order(s) · personal data stored: no";
    if (!data.orders.length) $("orders").append(node("p","No orders recorded yet."));
    data.orders.forEach(order => {
      const card = node("button", undefined, "order-card");
      card.type = "button";
      const title = node("strong", order.order_id);
      const meta = node("span", order.technology + " · " + order.state);
      const balance = node("span", "Paid " + money(order.paid_minor, order.currency) + " · Remaining " + money(order.balance_minor, order.currency));
      card.append(title, meta, balance);
      card.addEventListener("click", () => showOrder(order.order_id));
      $("orders").append(card);
    });
  }
  async function showOrder(id) {
    selectedOrder = id;
    const data = await api("/api/private/orders/" + encodeURIComponent(id));
    const detail = $("detail");
    detail.replaceChildren();
    detail.append(node("h1", data.order_id), node("p", data.technology + " · " + data.state));
    detail.append(node("p", "Paid: " + money(data.paid_minor,data.currency) + " · Balance: " + money(data.balance_minor,data.currency)));
    detail.append(node("p", "Address stored in this register: no"));
    const list = node("ol");
    data.events.forEach(event => list.append(node("li", new Date(event.created_at).toLocaleString() + " — " + event.event_type)));
    detail.append(node("h2","Audit history"),list);
    const payments = node("ol");
    data.payments.forEach(p => payments.append(node("li", money(p.amount_minor,p.currency) + " · " + p.provider + " · " + p.provider_reference + " · verified by " + p.verified_by)));
    detail.append(node("h2","Verified payments"),payments);
    ordersPanel.hidden = true;
    detailPanel.hidden = false;
  }
  $("connect").addEventListener("click", connect);
  $("token").addEventListener("keydown", e => { if (e.key === "Enter") connect(); });
  $("refresh").addEventListener("click", () => loadOrders().catch(e => $("summary").textContent = e.message));
  $("back").addEventListener("click", () => { detailPanel.hidden = true; ordersPanel.hidden = false; loadOrders().catch(e => $("summary").textContent = e.message); });
  $("payment-form").addEventListener("submit", async e => {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(e.currentTarget));
    try {
      await api("/api/private/orders/" + encodeURIComponent(selectedOrder) + "/payments", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
      $("action-message").textContent = "Payment recorded. Refreshing order…";
      e.currentTarget.reset();
      await showOrder(selectedOrder);
    } catch(error) { $("action-message").textContent = error.message; }
  });
  $("fulfilment-form").addEventListener("submit", async e => {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(e.currentTarget));
    try {
      await api("/api/private/orders/" + encodeURIComponent(selectedOrder) + "/fulfilment", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
      $("action-message").textContent = "Order status updated.";
      await showOrder(selectedOrder);
    } catch(error) { $("action-message").textContent = error.message; }
  });
})();
