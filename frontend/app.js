// Em produção o frontend é servido pelo mesmo app, então a URL é relativa
const API = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';

// ── Storage ──────────────────────────────────────────
const store = {
  get token() { return localStorage.getItem('token'); },
  get user()  { return JSON.parse(localStorage.getItem('user') || 'null'); },
  set token(v){ localStorage.setItem('token', v); },
  set user(v) { localStorage.setItem('user', JSON.stringify(v)); },
  clear()     { localStorage.removeItem('token'); localStorage.removeItem('user'); },
};

// ── API ───────────────────────────────────────────────
const ERROS_PT = {
  'email already registered':        'Email já cadastrado',
  'incorrect email or password':     'Email ou senha incorretos',
  'could not validate credentials':  'Sessão expirada, faça login novamente',
  'not authenticated':               'Você precisa estar logado',
  'task not found':                  'Tarefa não encontrada',
  'value is not a valid email':      'Informe um email válido',
  'string_too_short':                'A senha deve ter pelo menos 6 caracteres',
  'tarefa já está concluída':        'Tarefa já está concluída',
  'tarefa já está cancelada':        'Tarefa já está cancelada',
};

function traduzirErro(msg) {
  if (!msg) return 'Erro desconhecido';
  const lower = msg.toLowerCase();
  for (const [en, pt] of Object.entries(ERROS_PT)) {
    if (lower.includes(en)) return pt;
  }
  return msg;
}

async function api(method, path, body) {
  const headers = { 'Content-Type': 'application/json' };
  if (store.token) headers['Authorization'] = `Bearer ${store.token}`;
  let res;
  try {
    res = await fetch(API + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
  } catch {
    throw new Error('Não foi possível conectar ao servidor. Verifique se o backend está rodando.');
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = Array.isArray(data.detail)
      ? traduzirErro(data.detail[0]?.msg || data.detail[0]?.type || '')
      : traduzirErro(data.detail);
    throw new Error(msg);
  }
  return data;
}

// ── Toast ─────────────────────────────────────────────
function toast(msg, type = 'default') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => el.remove(), 3200);
}

// ── Screens ───────────────────────────────────────────
function showAuth() {
  document.getElementById('auth-screen').style.display = 'flex';
  document.getElementById('app-screen').style.display  = 'none';
}
function showApp() {
  document.getElementById('auth-screen').style.display = 'none';
  document.getElementById('app-screen').style.display  = 'block';
  renderUserInfo();
  loadTasks();
}

// ── Auth tabs ─────────────────────────────────────────
document.getElementById('tab-login').addEventListener('click', () => {
  document.getElementById('tab-login').classList.add('active');
  document.getElementById('tab-register').classList.remove('active');
  document.getElementById('form-login').style.display    = 'block';
  document.getElementById('form-register').style.display = 'none';
  clearAlert();
});
document.getElementById('tab-register').addEventListener('click', () => {
  document.getElementById('tab-register').classList.add('active');
  document.getElementById('tab-login').classList.remove('active');
  document.getElementById('form-register').style.display = 'block';
  document.getElementById('form-login').style.display    = 'none';
  clearAlert();
});

function showAlert(msg, type = 'error') {
  const el = document.getElementById('auth-alert');
  el.textContent = msg; el.className = `alert ${type} show`;
}
function clearAlert() {
  document.getElementById('auth-alert').className = 'alert';
}

// Login
document.getElementById('form-login').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('btn-login');
  btn.disabled = true; btn.textContent = 'Entrando…';
  clearAlert();
  try {
    const email = document.getElementById('login-email').value;
    const senha = document.getElementById('login-senha').value;
    const data  = await api('POST', '/auth/login', { email, senha });
    store.token = data.access_token;
    const payload = JSON.parse(atob(data.access_token.split('.')[1]));
    store.user = { id: payload.sub, email, nome: email.split('@')[0] };
    showApp();
  } catch (err) {
    showAlert(err.message);
  } finally {
    btn.disabled = false; btn.textContent = 'Entrar';
  }
});

// Register
document.getElementById('form-register').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('btn-register');
  btn.disabled = true; btn.textContent = 'Criando conta…';
  clearAlert();
  try {
    const nome  = document.getElementById('reg-nome').value;
    const email = document.getElementById('reg-email').value;
    const senha = document.getElementById('reg-senha').value;
    await api('POST', '/auth/cadastro', { nome, email, senha });
    showAlert('Conta criada! Faça o login.', 'success');
    document.getElementById('tab-login').click();
    document.getElementById('login-email').value = email;
  } catch (err) {
    showAlert(err.message);
  } finally {
    btn.disabled = false; btn.textContent = 'Criar conta';
  }
});

// Logout
document.getElementById('btn-logout').addEventListener('click', () => {
  store.clear(); showAuth();
  document.getElementById('form-login').reset();
  document.getElementById('form-register').reset();
});

// ── User info ─────────────────────────────────────────
function renderUserInfo() {
  const u = store.user;
  if (!u) return;
  document.getElementById('user-avatar').textContent       = (u.nome || u.email || '?')[0].toUpperCase();
  document.getElementById('user-name').textContent         = u.nome  || 'Usuário';
  document.getElementById('user-email-display').textContent= u.email || '';
}

// ── Tasks state ───────────────────────────────────────
let allTasks   = [];
let filterStatus = null; // null = todas

// Sidebar filter nav
document.querySelectorAll('.nav-item[data-filter]').forEach(el => {
  el.addEventListener('click', () => {
    document.querySelectorAll('.nav-item[data-filter]').forEach(x => x.classList.remove('active'));
    el.classList.add('active');
    filterStatus = el.dataset.filter === 'todas' ? null : el.dataset.filter;
    renderTasks();
  });
});

// ── Load & render ─────────────────────────────────────
async function loadTasks() {
  try {
    allTasks = await api('GET', '/tarefas/');
    renderTasks();
    renderStats();
  } catch (err) {
    if (err.message.includes('Sessão') || err.message.includes('conectar')) {
      store.clear(); showAuth();
    }
  }
}

function renderStats() {
  const p = allTasks.filter(t => t.status === 'Pendente').length;
  const c = allTasks.filter(t => t.status === 'Concluída').length;
  const x = allTasks.filter(t => t.status === 'Cancelada').length;
  document.getElementById('ss-pendente').textContent  = p;
  document.getElementById('ss-concluida').textContent = c;
  document.getElementById('ss-cancelada').textContent = x;
  // nav badges
  document.getElementById('badge-todas').textContent     = allTasks.length;
  document.getElementById('badge-pendente').textContent  = p;
  document.getElementById('badge-concluida').textContent = c;
  document.getElementById('badge-cancelada').textContent = x;
}

function formatDate(str) {
  if (!str) return null;
  const [y, m, d] = str.split('-');
  return `${d}/${m}/${y}`;
}

function isAtrasado(str) {
  if (!str) return false;
  return new Date(str) < new Date(new Date().toDateString());
}

function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function statusClass(s) {
  return { 'Pendente': 'pendente', 'Concluída': 'concluida', 'Cancelada': 'cancelada' }[s] || 'pendente';
}

function renderTasks() {
  const list = document.getElementById('task-list');
  const count = document.getElementById('task-count');

  let tasks = filterStatus
    ? allTasks.filter(t => t.status === filterStatus)
    : allTasks;

  count.textContent = tasks.length;

  if (tasks.length === 0) {
    list.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📋</div>
        <p>${filterStatus ? `Nenhuma tarefa com status "${filterStatus}".` : 'Nenhuma tarefa ainda. Adicione sua primeira tarefa acima!'}</p>
      </div>`;
    return;
  }

  // Sort: pending → concluida → cancelada, then by id desc
  const order = { 'Pendente': 0, 'Concluída': 1, 'Cancelada': 2 };
  tasks = [...tasks].sort((a, b) => (order[a.status] ?? 3) - (order[b.status] ?? 3) || b.id - a.id);

  list.innerHTML = tasks.map(t => {
    const cls      = statusClass(t.status);
    const icon     = t.status === 'Concluída' ? '✓' : t.status === 'Cancelada' ? '✕' : '';
    const desc     = t.descricao ? `<div class="task-desc">${esc(t.descricao)}</div>` : '';
    const atrasado = t.status === 'Pendente' && isAtrasado(t.data_vencimento);
    const dataBadge= t.data_vencimento
      ? `<span class="badge data ${atrasado ? 'atrasado' : ''}">📅 ${formatDate(t.data_vencimento)}${atrasado ? ' · Atrasada' : ''}</span>`
      : '';
    const lembBadge= t.lembrete && t.lembrete !== 'Nenhum'
      ? `<span class="badge lembrete">🔔 ${esc(t.lembrete)}</span>`
      : '';
    const actions  = t.status === 'Pendente' ? `
      <div class="task-actions">
        <button class="btn-action btn-concluir" onclick="concluirTask(${t.id})">✓ Concluir</button>
        <button class="btn-action btn-cancelar" onclick="cancelarTask(${t.id})">✕ Cancelar</button>
      </div>` : '';

    return `
      <div class="task-card ${cls}" id="task-${t.id}">
        <div class="task-check">${icon}</div>
        <div class="task-body">
          <div class="task-title">${esc(t.titulo)}</div>
          ${desc}
          <div class="task-meta">
            <span class="badge ${cls}">${t.status}</span>
            ${dataBadge}
            ${lembBadge}
          </div>
        </div>
        ${actions}
      </div>`;
  }).join('');
}

// ── Add task ──────────────────────────────────────────
document.getElementById('add-task-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const titulo          = document.getElementById('task-titulo').value.trim();
  const descricao       = document.getElementById('task-descricao').value.trim() || null;
  const lembrete        = document.getElementById('task-lembrete').value;
  const data_vencimento = document.getElementById('task-data').value || null;
  if (!titulo) return;

  const btn = document.getElementById('btn-add-task');
  btn.disabled = true;
  try {
    const nova = await api('POST', '/tarefas/', { titulo, descricao, lembrete, data_vencimento });
    allTasks.push(nova);
    renderTasks();
    renderStats();
    document.getElementById('add-task-form').reset();
    toast('Tarefa adicionada!', 'success');
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    btn.disabled = false;
  }
});

// ── Actions ───────────────────────────────────────────
async function concluirTask(id) {
  const card = document.getElementById(`task-${id}`);
  if (card) card.style.opacity = '0.5';
  try {
    const updated = await api('POST', `/tarefas/${id}/concluir`);
    const idx = allTasks.findIndex(t => t.id === id);
    if (idx !== -1) allTasks[idx] = updated;
    renderTasks(); renderStats();
    toast('Tarefa concluída! ✓', 'success');
  } catch (err) {
    if (card) card.style.opacity = '1';
    toast(err.message, 'error');
  }
}

async function cancelarTask(id) {
  const card = document.getElementById(`task-${id}`);
  if (card) card.style.opacity = '0.5';
  try {
    const updated = await api('POST', `/tarefas/${id}/cancelar`);
    const idx = allTasks.findIndex(t => t.id === id);
    if (idx !== -1) allTasks[idx] = updated;
    renderTasks(); renderStats();
    toast('Tarefa cancelada.');
  } catch (err) {
    if (card) card.style.opacity = '1';
    toast(err.message, 'error');
  }
}

// ── Init ──────────────────────────────────────────────
if (store.token) showApp(); else showAuth();
