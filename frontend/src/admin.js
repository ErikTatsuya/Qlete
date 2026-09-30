const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');

export async function loginAdmin(username, password) {
  const response = await fetch(`${API_BASE}/admin/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || 'Falha ao entrar como admin.');
  }

  return response.json();
}

export async function logoutAdmin() {
  await fetch(`${API_BASE}/admin/logout`, {
    method: 'POST',
    credentials: 'include',
  });
}

export async function getAdminSession() {
  try {
    const response = await fetch(`${API_BASE}/admin/me`, {
      method: 'GET',
      credentials: 'include',
    });
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

export async function fetchAdminTasks() {
  const response = await fetch(`${API_BASE}/admin/tasks`, {
    method: 'GET',
    credentials: 'include',
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || 'Não foi possível carregar as tarefas.');
  }
  return response.json();
}

export async function createAdminTask(task) {
  const response = await fetch(`${API_BASE}/admin/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(task),
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || 'Não foi possível criar a tarefa.');
  }
  return response.json();
}
