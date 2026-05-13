const DB_NAME = "vinhesque-mobile";
const DB_VERSION = 1;
const STORE_OPS = "operations";
const STORE_DATA = "catalog";

let db;
let mode = "COMPRA";
let clients = [];
let materials = [];
let dashboard = {
  usuario: "Adriel",
  resumo_dia: { compras: 0, vendas: 0, total_vendas: 0 },
  ultima_sincronizacao: "--/--/---- --:--"
};
let syncTimer;
let isSyncing = false;
let stagedItems = [];
let editingOperationId = null;
let editingOriginalCreatedAt = null;
let currentReceiptText = "";
let currentReceiptOperation = null;
let operationsMode = "receipts";
let receiptLogoPromise = null;

const el = (id) => document.getElementById(id);
const money = (value) => `R$ ${Number(value || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const kg = (value) => `${Number(value || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} kg`;
const numberBr = (value) => Number(value || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const parseDecimal = (value) => Number(String(value || "0").replace(/\./g, "").replace(",", ".")) || 0;
const parseWeight = (value) => String(value || "").includes(",,")
  ? String(value).split(/,,+/).reduce((sum, part) => sum + parseDecimal(part), 0)
  : parseDecimal(value);
const nowIso = () => new Date().toISOString();

function openDb() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const database = request.result;
      if (!database.objectStoreNames.contains(STORE_OPS)) {
        database.createObjectStore(STORE_OPS, { keyPath: "mobile_id" });
      }
      if (!database.objectStoreNames.contains(STORE_DATA)) {
        database.createObjectStore(STORE_DATA, { keyPath: "key" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function tx(store, modeName = "readonly") {
  return db.transaction(store, modeName).objectStore(store);
}

function getStoreValue(key) {
  return new Promise((resolve, reject) => {
    const request = tx(STORE_DATA).get(key);
    request.onsuccess = () => resolve(request.result ? request.result.value : null);
    request.onerror = () => reject(request.error);
  });
}

function setStoreValue(key, value) {
  return new Promise((resolve, reject) => {
    const request = tx(STORE_DATA, "readwrite").put({ key, value });
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}

function getOperations() {
  return new Promise((resolve, reject) => {
    const request = tx(STORE_OPS).getAll();
    request.onsuccess = () => resolve(request.result.sort((a, b) => String(b.created_at).localeCompare(String(a.created_at))));
    request.onerror = () => reject(request.error);
  });
}

function saveOperation(operation) {
  return new Promise((resolve, reject) => {
    const request = tx(STORE_OPS, "readwrite").put(operation);
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}

function deleteOperation(id) {
  return new Promise((resolve, reject) => {
    const request = tx(STORE_OPS, "readwrite").delete(id);
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}

function apiBase() {
  const configured = localStorage.getItem("vinhesqueApiUrl");
  if (configured) return configured.replace(/\/+$/, "");
  if (["http:", "https:"].includes(window.location.protocol)) {
    return window.location.origin;
  }
  return "";
}

function hasApiBase() {
  return Boolean(apiBase());
}

function syncHeaders(extra = {}) {
  const token = localStorage.getItem("vinhesqueSyncToken") || "";
  return token ? { ...extra, "X-Vinhesque-Token": token } : extra;
}

function materialByName(name) {
  const typed = String(name || "").trim().toLowerCase();
  return materials.find((item) => String(item.nome).trim().toLowerCase() === typed);
}

function hydrateLists() {
  renderSuggestions(el("clientName"), el("clientSuggestions"), clients, selectClient, formatClientSuggestion);
  renderDashboard();
}

function sameLocalDate(isoValue, date = new Date()) {
  const parsed = new Date(isoValue);
  if (Number.isNaN(parsed.getTime())) return false;
  return parsed.toLocaleDateString("pt-BR") === date.toLocaleDateString("pt-BR");
}

function escapeHtml(value) {
  return String(value || "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[char]);
}

async function loadCachedData() {
  clients = await getStoreValue("clients") || [];
  materials = await getStoreValue("materials") || [];
  dashboard = await getStoreValue("dashboard") || dashboard;
  hydrateLists();
}

async function fetchBootstrap() {
  if (!hasApiBase()) {
    throw new Error("Configure o endereco de sincronizacao para baixar clientes e materiais.");
  }
  const response = await fetch(`${apiBase()}/api/bootstrap`, {
    cache: "no-store",
    headers: syncHeaders()
  });
  if (!response.ok) throw new Error("Nao foi possivel buscar dados.");
  const payload = await response.json();
  clients = payload.clientes || [];
  materials = payload.materiais || [];
  dashboard = {
    usuario: payload.usuario || dashboard.usuario,
    resumo_dia: payload.resumo_dia || dashboard.resumo_dia,
    ultima_sincronizacao: payload.ultima_sincronizacao || dashboard.ultima_sincronizacao
  };
  await setStoreValue("clients", clients);
  await setStoreValue("materials", materials);
  await setStoreValue("dashboard", dashboard);
  hydrateLists();
  return payload;
}

async function renderDashboard() {
  const operations = db ? await getOperations().catch(() => []) : [];
  const todayBuys = operations.filter((op) => op.tipo === "COMPRA" && sameLocalDate(op.created_at));
  const totalToday = todayBuys.reduce((sum, op) => sum + Number(op.total || 0), 0);
  el("userName").textContent = dashboard.usuario || "Administrador";
  el("lastSyncText").textContent = dashboard.ultima_sincronizacao || "--/--/---- --:--";
  el("summaryBuys").textContent = todayBuys.length;
  el("summaryTotal").textContent = Number(totalToday || 0).toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

function setMode(nextMode) {
  mode = "COMPRA";
  document.querySelectorAll(".item-row").forEach(fillItemPrice);
  updateTotal();
}

function addItem() {
  if (document.querySelector(".item-row")) return;
  const node = el("itemTemplate").content.firstElementChild.cloneNode(true);
  const materialInput = node.querySelector(".material-name");
  const suggestions = node.querySelector(".material-suggestions");
  const inputs = node.querySelectorAll("input");
  node.querySelector(".remove-item").addEventListener("click", () => {
    clearCurrentItem();
    updateTotal();
  });
  setupSuggestions(
    materialInput,
    suggestions,
    () => materials,
    (material) => {
      materialInput.value = material.nome;
      fillItemPrice(node);
    },
    formatMaterialSuggestion
  );
  materialInput.addEventListener("change", () => fillItemPrice(node));
  inputs.forEach((input) => input.addEventListener("input", () => updateItem(node)));
  el("itemsList").appendChild(node);
  hydrateLists();
}

function clearCurrentItem() {
  const node = document.querySelector(".item-row");
  if (!node) return;
  node.querySelectorAll("input").forEach((input) => {
    input.value = "";
  });
}

function setupSuggestions(input, box, sourceFn, onSelect, formatFn) {
  input.addEventListener("input", () => renderSuggestions(input, box, sourceFn(), onSelect, formatFn));
  input.addEventListener("focus", () => renderSuggestions(input, box, sourceFn(), onSelect, formatFn));
  input.addEventListener("blur", () => {
    window.setTimeout(() => {
      box.hidden = true;
    }, 160);
  });
}

function renderSuggestions(input, box, rows, onSelect, formatFn) {
  const query = String(input.value || "").trim().toLowerCase();
  if (!query) {
    box.hidden = true;
    box.innerHTML = "";
    return;
  }
  const matches = rows
    .filter((row) => String(row.nome || "").toLowerCase().includes(query))
    .slice(0, 8);
  if (!matches.length) {
    box.hidden = true;
    box.innerHTML = "";
    return;
  }
  box.innerHTML = matches.map((row, index) => {
    const formatted = formatFn(row);
    return `
      <button class="suggestion-item" type="button" data-suggestion-index="${index}">
        <strong>${escapeHtml(formatted.title)}</strong>
        <span>${escapeHtml(formatted.detail)}</span>
      </button>
    `;
  }).join("");
  box.hidden = false;
  box.querySelectorAll(".suggestion-item").forEach((button) => {
    button.addEventListener("pointerdown", (event) => {
      event.preventDefault();
      onSelect(matches[Number(button.dataset.suggestionIndex)]);
      box.hidden = true;
    });
  });
}

function selectClient(client) {
  el("clientName").value = client.nome || "";
  el("clientDoc").value = client.cnpj || "";
  el("clientPhone").value = client.telefone || "";
}

function formatClientSuggestion(client) {
  const pieces = [client.telefone, client.cnpj, client.cidade].filter(Boolean);
  return {
    title: client.nome || "",
    detail: pieces.length ? pieces.join(" - ") : "Cliente cadastrado"
  };
}

function formatMaterialSuggestion(material) {
  const price = mode === "COMPRA" ? material.preco_compra : material.preco_venda;
  return {
    title: material.nome || "",
    detail: `${mode === "COMPRA" ? "Compra" : "Venda"}: ${money(price)} / kg`
  };
}

function fillItemPrice(node) {
  const material = materialByName(node.querySelector(".material-name").value);
  if (!material) return;
  const price = mode === "COMPRA" ? material.preco_compra : material.preco_venda;
  node.querySelector(".price").value = String(Number(price || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 }));
  updateItem(node);
}

function updateItem(node) {
  const gross = parseWeight(node.querySelector(".gross").value);
  const discount = parseDecimal(node.querySelector(".discount").value);
  const price = parseDecimal(node.querySelector(".price").value);
  const liquid = Math.max(gross - discount, 0);
  const subtotal = liquid * price;
  node.querySelector(".subtotal").value = money(subtotal);
  updateTotal();
}

function collectCurrentItem() {
  const node = document.querySelector(".item-row");
  if (!node) return null;
  const materialName = node.querySelector(".material-name").value.trim();
  const grossText = node.querySelector(".gross").value.trim();
  const priceText = node.querySelector(".price").value.trim();
  const hasAnyValue = materialName || grossText || priceText || node.querySelector(".discount").value.trim();
  if (!hasAnyValue) return null;
  const material = materialByName(materialName);
  const pesoBruto = parseWeight(grossText);
  const desconto = parseDecimal(node.querySelector(".discount").value);
  const pesoLiquido = Math.max(pesoBruto - desconto, 0);
  const precoKg = parseDecimal(priceText);
  return {
    material_id: material ? material.id : null,
    material_nome: materialName,
    peso_bruto: pesoBruto,
    desconto,
    peso_liquido: pesoLiquido,
    preco_kg: precoKg,
    subtotal: pesoLiquido * precoKg
  };
}

function collectItems() {
  const current = collectCurrentItem();
  return [
    ...stagedItems,
    ...(current ? [current] : [])
  ];
}

function commitCurrentItem() {
  const current = collectCurrentItem();
  if (!current) {
    alert("Preencha o material para adicionar.");
    return false;
  }
  validateItem(current);
  stagedItems.push(current);
  clearCurrentItem();
  renderStagedItems();
  updateTotal();
  document.querySelector(".material-name")?.focus();
  return true;
}

function renderStagedItems() {
  const list = el("stagedItemsList");
  if (!list) return;
  list.innerHTML = stagedItems.length ? stagedItems.map((item, index) => `
    <article class="staged-item">
      <div>
        <strong>${escapeHtml(item.material_nome)}</strong>
        <span>${kg(item.peso_liquido)} x ${money(item.preco_kg)} = ${money(item.subtotal)}</span>
      </div>
      <button type="button" data-edit-item="${index}">Editar</button>
      <button type="button" data-remove-item="${index}">Excluir</button>
    </article>
  `).join("") : "<p class=\"hint compact-hint\">Nenhum item adicionado.</p>";
  list.querySelectorAll("[data-remove-item]").forEach((button) => {
    button.addEventListener("click", () => {
      stagedItems.splice(Number(button.dataset.removeItem), 1);
      renderStagedItems();
      updateTotal();
    });
  });
  list.querySelectorAll("[data-edit-item]").forEach((button) => {
    button.addEventListener("click", () => {
      const index = Number(button.dataset.editItem);
      const item = stagedItems.splice(index, 1)[0];
      renderStagedItems();
      fillCurrentItem(item);
      updateTotal();
    });
  });
}

function fillCurrentItem(item) {
  addItem();
  const node = document.querySelector(".item-row");
  node.querySelector(".material-name").value = item.material_nome || "";
  node.querySelector(".gross").value = Number(item.peso_bruto || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 });
  node.querySelector(".discount").value = Number(item.desconto || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 });
  node.querySelector(".price").value = Number(item.preco_kg || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 });
  updateItem(node);
}

function collectItemsFromRows() {
  return Array.from(document.querySelectorAll(".item-row")).map((node) => {
    const materialName = node.querySelector(".material-name").value.trim();
    const material = materialByName(materialName);
    const pesoBruto = parseDecimal(node.querySelector(".gross").value);
    const desconto = parseDecimal(node.querySelector(".discount").value);
    const pesoLiquido = Math.max(pesoBruto - desconto, 0);
    const precoKg = parseDecimal(node.querySelector(".price").value);
    return {
      material_id: material ? material.id : null,
      material_nome: materialName,
      peso_bruto: pesoBruto,
      desconto,
      peso_liquido: pesoLiquido,
      preco_kg: precoKg,
      subtotal: pesoLiquido * precoKg
    };
  });
}

function updateTotal() {
  const total = collectItems().reduce((sum, item) => sum + item.subtotal, 0);
  el("totalValue").textContent = money(total);
}

function validateItem(item) {
  if (!item.material_nome || !item.peso_liquido || !item.preco_kg) {
    throw new Error("Confira material, peso e preco dos itens.");
  }
  if (!item.material_id && materials.length) {
    throw new Error(`Material nao encontrado: ${item.material_nome}`);
  }
}

function validateOperation(items) {
  if (!el("clientName").value.trim()) throw new Error("Informe o cliente.");
  if (!items.length) throw new Error("Adicione pelo menos um item.");
  for (const item of items) {
    validateItem(item);
  }
}

function buildReceipt(operation) {
  const date = new Date(operation.created_at);
  const dateText = Number.isNaN(date.getTime()) ? "" : date.toLocaleDateString("pt-BR");
  const timeText = Number.isNaN(date.getTime()) ? "" : date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  const receiptItems = consolidateReceiptItems(operation.itens);
  const totalWeight = receiptItems.reduce((sum, item) => sum + item.peso_liquido, 0);
  const lines = [
    "VR VINHESQUE RECICLAGEM",
    "SUSTENTABILIDADE QUE GERA VALOR",
    "",
    `CONTROLE ${operation.mobile_id}`,
    `DATA     ${dateText} ${timeText}`.trimEnd(),
    "======================================",
    "DADOS DA OPERACAO",
    "TIPO     Compra",
    `CLIENTE  ${String(operation.cliente_nome || "").slice(0, 25)}`,
    "======================================",
    "PRODUTOS",
    "MATERIAL|QTD|DESC|V/KG|TOTAL",
    "--------------------------------------"
  ];
  receiptItems.forEach((item) => {
    lines.push([
      item.material_nome,
      kg(item.peso_liquido).replace(" kg", ""),
      kg(item.desconto).replace(" kg", ""),
      money(item.preco_kg).replace("R$ ", ""),
      money(item.subtotal).replace("R$ ", "")
    ].join("|"));
  });
  lines.push("--------------------------------------");
  lines.push(`PESO TOTAL             ${kg(totalWeight).padStart(13)}`);
  lines.push(`TOTAL                  ${money(operation.total).padStart(13)}`);
  lines.push("");
  lines.push("Obrigado pela preferencia!");
  if (operation.observacao) {
    lines.push("");
    lines.push("OBSERVACOES");
    lines.push(...wrapReceiptLine(operation.observacao, 30));
  }
  return lines.join("\n");
}

function consolidateReceiptItems(items) {
  const map = new Map();
  for (const item of items) {
    const key = item.material_nome;
    if (!map.has(key)) {
      map.set(key, { material_nome: key, peso_liquido: 0, desconto: 0, preco_kg: item.preco_kg, subtotal: 0 });
    }
    const target = map.get(key);
    target.peso_liquido += Number(item.peso_liquido || 0);
    target.desconto += Number(item.desconto || 0);
    target.subtotal += Number(item.subtotal || 0);
    target.preco_kg = target.peso_liquido > 0 ? target.subtotal / target.peso_liquido : Number(item.preco_kg || 0);
  }
  return Array.from(map.values());
}

function wrapReceiptLine(text, maxChars) {
  const words = String(text || "").split(/\s+/).filter(Boolean);
  if (!words.length) return [""];
  const lines = [];
  let current = words.shift();
  for (const word of words) {
    if (`${current} ${word}`.length <= maxChars) {
      current = `${current} ${word}`;
    } else {
      lines.push(current);
      current = word;
    }
  }
  lines.push(current);
  return lines;
}

async function submitOperation(event) {
  event.preventDefault();
  try {
    const itens = collectItems();
    validateOperation(itens);
    const total = itens.reduce((sum, item) => sum + item.subtotal, 0);
    const operation = {
      mobile_id: editingOperationId || `MOB-${Date.now()}`,
      tipo: mode,
      cliente_nome: el("clientName").value.trim(),
      cliente_documento: el("clientDoc").value.trim(),
      cliente_telefone: el("clientPhone").value.trim(),
      destino_compra: mode === "COMPRA" ? "Venda externa" : "",
      observacao: el("note").value.trim(),
      itens,
      total,
      created_at: editingOriginalCreatedAt || nowIso(),
      status: "pending"
    };
    operation.comprovante = buildReceipt(operation);
    await saveOperation(operation);
    showReceipt(operation.comprovante, operation);
    resetForm();
    await refreshOperations();
  } catch (error) {
    alert(error.message);
  }
}

function resetForm() {
  el("operationForm").reset();
  el("itemsList").innerHTML = "";
  stagedItems = [];
  editingOperationId = null;
  editingOriginalCreatedAt = null;
  renderStagedItems();
  addItem();
  setMode(mode);
}

function showReceipt(text, operation = null) {
  currentReceiptText = text;
  currentReceiptOperation = operation;
  el("receiptText").textContent = text;
  drawReceiptPreview(operation, text);
  el("receiptDialog").showModal();
}

function loadReceiptLogo() {
  if (!receiptLogoPromise) {
    receiptLogoPromise = new Promise((resolve) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => resolve(null);
      image.src = "./icons/logo-comprovante-mobile.png?v=15";
    });
  }
  return receiptLogoPromise;
}

function receiptOperationFromText(text) {
  const lines = String(text || "").split("\n");
  const controle = (lines.find((line) => line.startsWith("CONTROLE")) || "").replace("CONTROLE", "").trim();
  const dataLine = (lines.find((line) => line.startsWith("DATA")) || "").replace("DATA", "").trim();
  const cliente = (lines.find((line) => line.startsWith("CLIENTE")) || "").replace("CLIENTE", "").trim();
  const totalLine = [...lines].reverse().find((line) => line.startsWith("TOTAL")) || "";
  return {
    mobile_id: controle || "MOBILE",
    tipo: "COMPRA",
    cliente_nome: cliente || "",
    created_at: dataLine,
    itens: [],
    total: parseDecimal(totalLine.replace("TOTAL", "").replace("R$", "").trim())
  };
}

function fitText(ctx, text, x, y, maxWidth) {
  let safeText = String(text || "");
  if (ctx.measureText(safeText).width <= maxWidth) {
    ctx.fillText(safeText, x, y);
    return;
  }
  while (safeText.length > 1 && ctx.measureText(`${safeText}...`).width > maxWidth) {
    safeText = safeText.slice(0, -1);
  }
  ctx.fillText(`${safeText}...`, x, y);
}

function fitRightText(ctx, text, rightX, y, maxWidth) {
  const value = String(text || "");
  const originalFont = ctx.font;
  const match = originalFont.match(/(\d+)px/);
  let size = match ? Number(match[1]) : 18;
  while (size > 12 && ctx.measureText(value).width > maxWidth) {
    size -= 1;
    ctx.font = originalFont.replace(/\d+px/, `${size}px`);
  }
  ctx.fillText(value, rightX, y);
  ctx.font = originalFont;
}

function drawReceiptImage(canvas, operation, logo) {
  const receiptItems = consolidateReceiptItems(operation.itens || []);
  const totalWeight = receiptItems.reduce((sum, item) => sum + Number(item.peso_liquido || 0), 0);
  const rows = receiptItems.length ? receiptItems : [{ material_nome: "", peso_liquido: 0, desconto: 0, preco_kg: 0, subtotal: 0 }];
  const observationLines = operation.observacao ? wrapReceiptLine(operation.observacao, 46) : [];
  const width = 570;
  const rowHeight = 39;
  const baseHeight = 575;
  const height = baseHeight + rows.length * rowHeight + observationLines.length * 22 + (observationLines.length ? 42 : 0);
  const scale = Math.max(window.devicePixelRatio || 1, 2);
  canvas.width = width * scale;
  canvas.height = height * scale;
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  const ctx = canvas.getContext("2d");
  ctx.scale(scale, scale);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, width, height);
  ctx.textBaseline = "alphabetic";

  let y = 6;
  if (logo) {
    const logoWidth = 240;
    const logoHeight = 158;
    const ratio = Math.min(logoWidth / logo.width, logoHeight / logo.height);
    const drawWidth = logo.width * ratio;
    const drawHeight = logo.height * ratio;
    ctx.drawImage(logo, (width - drawWidth) / 2, y, drawWidth, drawHeight);
  } else {
    ctx.fillStyle = "#111111";
    ctx.textAlign = "center";
    ctx.font = "800 38px Arial, sans-serif";
    ctx.fillText("VR VINHESQUE", width / 2, y + 48);
    ctx.font = "800 22px Arial, sans-serif";
    ctx.fillText("RECICLAGEM", width / 2, y + 82);
  }

  ctx.fillStyle = "#111111";
  ctx.textAlign = "center";
  ctx.font = "16px Consolas, monospace";
  y = 194;
  ctx.fillText("SUSTENTABILIDADE QUE GERA VALOR", width / 2, y);
  y += 34;

  const created = new Date(operation.created_at);
  const dateText = Number.isNaN(created.getTime())
    ? String(operation.created_at || "")
    : `${created.toLocaleDateString("pt-BR")} ${created.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}`;
  const control = operation.numero || operation.mobile_id || "MOBILE";

  ctx.textAlign = "left";
  ctx.font = "20px Consolas, monospace";
  ctx.fillText(`CONTROLE ${control}`, 12, y);
  y += 26;
  ctx.fillText(`DATA    ${dateText}`, 12, y);
  y += 18;

  ctx.strokeStyle = "#111111";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(12, y);
  ctx.lineTo(width - 12, y);
  ctx.stroke();
  y += 22;

  ctx.textAlign = "center";
  ctx.font = "700 20px Consolas, monospace";
  ctx.fillText("DADOS DA OPERACAO", width / 2, y);
  y += 30;
  ctx.textAlign = "left";
  ctx.font = "20px Consolas, monospace";
  ctx.fillText("TIPO", 12, y);
  ctx.fillText("Compra", 120, y);
  y += 26;
  ctx.fillText("CLIENTE", 12, y);
  fitText(ctx, operation.cliente_nome || "", 120, y, width - 132);
  y += 18;

  ctx.beginPath();
  ctx.moveTo(12, y);
  ctx.lineTo(width - 12, y);
  ctx.stroke();
  y += 22;

  ctx.textAlign = "center";
  ctx.font = "700 20px Consolas, monospace";
  ctx.fillText("PRODUTOS", width / 2, y);
  y += 25;

  ctx.textAlign = "left";
  ctx.font = "700 16px Consolas, monospace";
  ctx.fillText("MATERIAL", 12, y);
  ctx.textAlign = "right";
  ctx.fillText("QTD", 250, y);
  ctx.fillText("DESC", 320, y);
  ctx.fillText("V/KG", 405, y);
  ctx.fillText("TOTAL", width - 12, y);
  y += 23;

  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(12, y);
  ctx.lineTo(width - 12, y);
  ctx.stroke();
  y += 24;

  ctx.font = "700 19px Consolas, monospace";
  rows.forEach((item) => {
    ctx.textAlign = "left";
    fitText(ctx, item.material_nome, 12, y, 176);
    ctx.textAlign = "right";
    fitRightText(ctx, numberBr(item.peso_liquido), 250, y, 60);
    fitRightText(ctx, numberBr(item.desconto), 320, y, 58);
    fitRightText(ctx, numberBr(item.preco_kg), 405, y, 58);
    fitRightText(ctx, numberBr(item.subtotal), width - 12, y, 110);
    y += rowHeight;
  });

  ctx.beginPath();
  ctx.moveTo(12, y - 11);
  ctx.lineTo(width - 12, y - 11);
  ctx.stroke();
  y += 11;

  ctx.textAlign = "left";
  ctx.font = "20px Consolas, monospace";
  ctx.fillText("PESO TOTAL", 12, y);
  ctx.textAlign = "right";
  fitRightText(ctx, `${numberBr(totalWeight)} kg`, 410, y, 150);
  y += 32;

  ctx.textAlign = "left";
  ctx.font = "700 26px Consolas, monospace";
  ctx.fillText("TOTAL", 34, y);
  ctx.textAlign = "right";
  fitRightText(ctx, money(operation.total), width - 20, y, 210);
  y += 38;

  if (observationLines.length) {
    ctx.textAlign = "left";
    ctx.font = "16px Consolas, monospace";
    ctx.fillText("OBSERVACOES", 12, y);
    y += 22;
    observationLines.forEach((line) => {
      fitText(ctx, line, 12, y, width - 24);
      y += 22;
    });
    y += 12;
  }

  ctx.textAlign = "center";
  ctx.font = "700 20px Consolas, monospace";
  ctx.fillText("Obrigado pela preferencia!", width / 2, y);
}

async function drawReceiptPreview(operation, text) {
  const canvas = el("receiptCanvas");
  const receiptOperation = operation || receiptOperationFromText(text);
  const logo = await loadReceiptLogo();
  drawReceiptImage(canvas, receiptOperation, logo);
}

function receiptCanvas(text, operation = currentReceiptOperation) {
  const canvas = document.createElement("canvas");
  drawReceiptImage(canvas, operation || receiptOperationFromText(text), null);
  return canvas;
}

async function saveReceiptImage() {
  if (!currentReceiptText) return;
  await drawReceiptPreview(currentReceiptOperation, currentReceiptText);
  const canvas = el("receiptCanvas");
  const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
  const file = new File([blob], `comprovante-${Date.now()}.png`, { type: "image/png" });
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    await navigator.share({ files: [file], title: "Comprovante Vinhesque" });
    return;
  }
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = file.name;
  link.click();
  URL.revokeObjectURL(url);
}

async function refreshOperations() {
  const operations = await getOperations();
  const pending = operations.filter((op) => op.status !== "synced").length;
  el("pendingStatus").textContent = `${pending} pendente${pending === 1 ? "" : "s"}`;
  const isHistory = operationsMode === "history";
  el("operationsTitle").textContent = isHistory ? "Historico" : "Comprovantes";
  el("operationsSubtitle").textContent = isHistory ? "Lancamentos do aparelho" : "Comprovantes salvos";
  el("clearSyncedButton").hidden = !isHistory;
  el("operationsList").innerHTML = operations.length ? operations.map((op) => `
    <article class="operation-row">
      <strong>Compra - ${escapeHtml(op.cliente_nome)}</strong>
      <span>${new Date(op.created_at).toLocaleString("pt-BR")} - ${money(op.total)}</span>
      <span>${op.status === "synced" ? "Sincronizado" : op.status === "error" ? "Erro" : "Pendente"}</span>
      <div class="operation-actions">
        <button type="button" data-receipt="${op.mobile_id}">Comprovante</button>
        ${isHistory ? `<button type="button" data-edit-op="${op.mobile_id}">Editar</button>
        <button type="button" data-delete-op="${op.mobile_id}">Excluir</button>` : ""}
      </div>
    </article>
  `).join("") : "<p class=\"hint\">Nenhum lancamento salvo neste aparelho.</p>";
  document.querySelectorAll("[data-receipt]").forEach((button) => {
    button.addEventListener("click", async () => {
      const op = (await getOperations()).find((item) => item.mobile_id === button.dataset.receipt);
      if (op) showReceipt(op.comprovante || buildReceipt(op), op);
    });
  });
  document.querySelectorAll("[data-edit-op]").forEach((button) => {
    button.addEventListener("click", async () => {
      const op = (await getOperations()).find((item) => item.mobile_id === button.dataset.editOp);
      if (!op) return;
      if (op.status === "synced") {
        alert("Lancamento ja sincronizado. Edite pelo sistema do notebook.");
        return;
      }
      loadOperationForEdit(op);
    });
  });
  document.querySelectorAll("[data-delete-op]").forEach((button) => {
    button.addEventListener("click", async () => {
      const op = (await getOperations()).find((item) => item.mobile_id === button.dataset.deleteOp);
      if (!op) return;
      if (op.status === "synced") {
        alert("Lancamento ja sincronizado. Exclua pelo sistema do notebook.");
        return;
      }
      if (!confirm("Excluir este lancamento deste aparelho?")) return;
      await deleteOperation(op.mobile_id);
      await refreshOperations();
    });
  });
  renderDashboard();
}

function loadOperationForEdit(operation) {
  editingOperationId = operation.mobile_id;
  editingOriginalCreatedAt = operation.created_at;
  el("clientName").value = operation.cliente_nome || "";
  el("clientDoc").value = operation.cliente_documento || "";
  el("clientPhone").value = operation.cliente_telefone || "";
  el("note").value = operation.observacao || "";
  stagedItems = [...(operation.itens || [])];
  clearCurrentItem();
  renderStagedItems();
  updateTotal();
  showView("form");
}

async function syncPending(options = {}) {
  const silent = Boolean(options.silent);
  if (isSyncing) return false;
  if (!hasApiBase()) {
    if (!silent) alert("Configure o endereco de sincronizacao no Menu. O app continua funcionando offline.");
    return false;
  }
  isSyncing = true;
  const operations = (await getOperations()).filter((op) => op.status !== "synced");
  try {
    if (!operations.length) {
      await fetchBootstrap();
      if (!silent) alert("Dados atualizados.");
      return true;
    }
    const response = await fetch(`${apiBase()}/api/sync`, {
      method: "POST",
      headers: syncHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ operations })
    });
    if (!response.ok) throw new Error("Falha ao sincronizar.");
    const payload = await response.json();
    for (const result of payload.results || []) {
      const operation = operations.find((op) => op.mobile_id === result.mobile_id);
      if (!operation) continue;
      operation.status = result.ok ? "synced" : "error";
      operation.sync_message = result.message || "";
      operation.transacao_id = result.transacao_id || null;
      operation.numero = result.numero || null;
      operation.printed = Boolean(result.printed);
      operation.print_message = result.print_message || "";
      operation.synced_at = result.ok ? nowIso() : null;
      await saveOperation(operation);
    }
    await refreshOperations();
    fetchBootstrap().catch(() => null);
    const printedCount = (payload.results || []).filter((result) => result.printed).length;
    if (!silent) {
      alert(printedCount ? "Sincronizado e enviado para a impressora do notebook." : "Sincronizacao concluida. Comprovante salvo no notebook.");
    }
    return true;
  } catch (error) {
    if (!silent) alert(error.message);
    return false;
  } finally {
    isSyncing = false;
  }
}

async function clearSynced() {
  const operations = await getOperations();
  await Promise.all(operations.filter((op) => op.status === "synced").map((op) => deleteOperation(op.mobile_id)));
  await refreshOperations();
  renderDashboard();
}

function showView(name) {
  if (name === "pending" || name === "history") {
    operationsMode = name === "history" ? "history" : "receipts";
    refreshOperations();
  }
  const viewName = name === "history" ? "pending" : name;
  document.querySelectorAll(".view").forEach((item) => item.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
  el(`${viewName}View`).classList.add("active");
  const floatingMenu = document.querySelector(".floating-menu-button");
  if (floatingMenu) floatingMenu.hidden = viewName === "settings";
  document.querySelectorAll(`[data-tab="${name}"]`).forEach((item) => {
    if (item.classList.contains("nav-item")) item.classList.add("active");
  });
  if (name === "history" && !document.querySelector('[data-tab="history"].nav-item')) {
    document.querySelector('[data-tab="pending"].nav-item')?.classList.add("active");
  }
}

function wireTabs() {
  document.querySelectorAll("[data-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      showView(button.dataset.tab);
    });
  });
  document.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", () => {
      setMode("COMPRA");
      showView("form");
    });
  });
}

function scheduleAutoSync() {
  window.clearInterval(syncTimer);
  syncTimer = window.setInterval(() => {
    if (navigator.onLine) syncPending({ silent: true });
  }, 30000);
}

async function init() {
  db = await openDb();
  el("apiUrl").value = apiBase();
  el("syncToken").value = localStorage.getItem("vinhesqueSyncToken") || "";
  wireTabs();
  setupSuggestions(el("clientName"), el("clientSuggestions"), () => clients, selectClient, formatClientSuggestion);
  el("addItemButton").addEventListener("click", () => {
    try {
      commitCurrentItem();
    } catch (error) {
      alert(error.message);
    }
  });
  el("operationForm").addEventListener("submit", submitOperation);
  el("closeReceiptButton").addEventListener("click", () => el("receiptDialog").close());
  el("saveReceiptImageButton").addEventListener("click", () => saveReceiptImage().catch((error) => alert(error.message)));
  el("heroSyncButton").addEventListener("click", () => syncPending());
  el("clearSyncedButton").addEventListener("click", clearSynced);
  el("saveSettingsButton").addEventListener("click", () => {
    const value = el("apiUrl").value.trim().replace(/\/+$/, "");
    if (value) {
      localStorage.setItem("vinhesqueApiUrl", value);
    } else {
      localStorage.removeItem("vinhesqueApiUrl");
    }
    const token = el("syncToken").value.trim();
    if (token) {
      localStorage.setItem("vinhesqueSyncToken", token);
    } else {
      localStorage.removeItem("vinhesqueSyncToken");
    }
    alert("Ajustes salvos.");
    syncPending({ silent: true });
  });
  el("loadDataButton").addEventListener("click", () => fetchBootstrap().then(() => alert("Dados atualizados.")).catch((error) => alert(error.message)));
  window.addEventListener("online", updateConnectionStatus);
  window.addEventListener("offline", updateConnectionStatus);
  window.addEventListener("online", () => syncPending({ silent: true }));
  window.addEventListener("focus", () => {
    if (navigator.onLine) syncPending({ silent: true });
  });
  updateConnectionStatus();
  await loadCachedData();
  if (navigator.onLine && hasApiBase()) {
    fetchBootstrap().catch(() => null);
  }
  addItem();
  renderStagedItems();
  setMode("COMPRA");
  await refreshOperations();
  if ("serviceWorker" in navigator && ["https:", "http:"].includes(location.protocol)) {
    navigator.serviceWorker.register("./sw.js").catch(() => null);
  }
  scheduleAutoSync();
  if (navigator.onLine) syncPending({ silent: true });
}

function updateConnectionStatus() {
  const badge = el("onlineBadge");
  if (navigator.onLine && hasApiBase()) {
    badge.textContent = "Online";
    badge.classList.remove("offline");
  } else if (navigator.onLine) {
    badge.textContent = "Sem sync";
    badge.classList.add("offline");
  } else {
    badge.textContent = "Offline";
    badge.classList.add("offline");
  }
}

init().catch((error) => {
  console.error(error);
  alert("Falha ao iniciar o app mobile.");
});
