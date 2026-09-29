<script>
  import { onMount } from 'svelte';
  import { loginAdmin } from './admin.js';

  let username = $state('');
  let password = $state('');
  let error = $state('');
  let saving = $state(false);

  onMount(async () => {
    const apiUrl = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');
    try {
      const response = await fetch(`${apiUrl}/admin/me`, { credentials: 'include' });
      if (response.ok) window.location.replace('/');
    } catch {
      error = 'Não foi possível conectar à API.';
    }
  });

  async function submit(event) {
    event.preventDefault();
    error = '';
    saving = true;
    try {
      await loginAdmin(username, password);
      window.location.assign('/');
    } catch (cause) {
      error = cause instanceof Error ? cause.message : 'Não foi possível entrar no painel.';
    } finally {
      saving = false;
    }
  }
</script>

<main class="login-page">
  <header class="login-header">
    <a class="brand" href="/" aria-label="Qlete, biblioteca de quizzes">
      <strong>Qlete</strong><span>Biblioteca de quizzes</span>
    </a>
    <a class="back-link" href="/">Voltar aos quizzes <span aria-hidden="true">↗</span></a>
  </header>

  <section class="login-content" aria-labelledby="login-title">
    <p class="login-kicker">Área restrita</p>
    <h1 id="login-title">Entrar</h1>
    <p class="login-description">Acesse sua conta para gerenciar e publicar quizzes.</p>
    {#if error}<p class="login-error" role="alert">{error}</p>{/if}
    <form class="login-form" onsubmit={submit}>
      <label class="field">
        <span>Usuário</span>
        <input bind:value={username} autocomplete="username" placeholder="Seu usuário" required />
      </label>
      <label class="field">
        <span>Senha</span>
        <input bind:value={password} type="password" autocomplete="current-password" placeholder="Sua senha" required />
      </label>
      <button class="submit-button" type="submit" disabled={saving}>
        {saving ? 'Entrando...' : 'Entrar'} <span aria-hidden="true">↗</span>
      </button>
    </form>
  </section>
</main>