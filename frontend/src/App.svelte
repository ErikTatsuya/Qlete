<script>
  import { onMount } from 'svelte';

  const apiUrl = (
    import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '')
  ).replace(/\/+$/, '');
  const emptyQuestion = () => ({ text: '', alternatives: ['', '', '', ''], correct_alternative: 1 });

  let quizzes = $state([]);
  let loading = $state(true);
  let saving = $state(false);
  let formOpen = $state(false);
  let error = $state('');
  let title = $state('');
  let description = $state('');
  let adminUser = $state('');
  let adminPassword = $state('');
  let adminSession = $state(null);
  let adminTasks = $state([]);
  let adminTaskTitle = $state('');
  let adminTaskDescription = $state('');
  let adminTaskSaving = $state(false);
  let questions = $state([emptyQuestion()]);
  let answerResults = $state({});
  let answering = $state({});

  onMount(async () => {
    await loadQuizzes();
    await checkAdminSession();
  });

  async function loadQuizzes() {
    loading = true;
    error = '';
    try {
      const response = await fetch(`${apiUrl}/api/quizzes`);
      if (!response.ok) throw new Error('Não foi possível carregar os quizzes.');
      quizzes = await response.json();
    } catch {
      error = 'Não foi possível conectar à API. Confira se ela está rodando.';
    } finally {
      loading = false;
    }
  }

  async function checkAdminSession() {
    try {
      const response = await fetch(`${apiUrl}/admin/me`, { credentials: 'include' });
      if (!response.ok) {
        adminSession = null;
        return;
      }
      adminSession = await response.json();
      await loadAdminTasks();
    } catch {
      adminSession = null;
    }
  }

  async function loginAdmin(event) {
    event.preventDefault();
    error = '';

    try {
      const response = await fetch(`${apiUrl}/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username: adminUser, password: adminPassword }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail || 'Usuário ou senha do admin incorretos.');
      }

      adminSession = await response.json();
      adminUser = '';
      adminPassword = '';
      await loadAdminTasks();
    } catch (cause) {
      error = cause instanceof Error ? cause.message : 'Não foi possível entrar no painel admin.';
    }
  }

  async function logoutAdmin() {
    try {
      await fetch(`${apiUrl}/admin/logout`, {
        method: 'POST',
        credentials: 'include',
      });
    } finally {
      adminSession = null;
      adminTasks = [];
      error = '';
    }
  }

  async function loadAdminTasks() {
    if (!adminSession) return;

    try {
      const response = await fetch(`${apiUrl}/admin/tasks`, {
        method: 'GET',
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Não foi possível carregar as tarefas do admin.');
      adminTasks = await response.json();
    } catch (cause) {
      error = cause instanceof Error ? cause.message : 'Erro ao carregar tarefas do admin.';
    }
  }

  async function createAdminTask(event) {
    event.preventDefault();
    if (!adminSession || !adminTaskTitle.trim()) return;

    adminTaskSaving = true;
    try {
      const response = await fetch(`${apiUrl}/admin/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title: adminTaskTitle.trim(),
          description: adminTaskDescription.trim() || null,
          completed: false,
        }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail || 'Não foi possível criar a tarefa.');
      }

      adminTaskTitle = '';
      adminTaskDescription = '';
      await loadAdminTasks();
    } catch (cause) {
      error = cause instanceof Error ? cause.message : 'Não foi possível criar a tarefa.';
    } finally {
      adminTaskSaving = false;
    }
  }

  function addQuestion() {
    if (questions.length < 10) questions.push(emptyQuestion());
  }

  function removeQuestion(index) {
    if (questions.length > 1) questions.splice(index, 1);
  }

  async function chooseAnswer(quiz, question, alternativeIndex) {
    const key = `${quiz.id}:${question.id}`;
    if (answerResults[key] || answering[key]) return;

    answering[key] = true;
    try {
      const response = await fetch(`${apiUrl}/api/quizzes/${quiz.id}/questions/${question.id}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alternative: alternativeIndex + 1 }),
      });
      if (!response.ok) throw new Error('Não foi possível verificar a resposta. Tente novamente.');
      answerResults[key] = await response.json();
    } catch {
      error = 'Não foi possível verificar a resposta. Confira a conexão com a API.';
    } finally {
      answering[key] = false;
    }
  }

  function resetForm() {
    title = '';
    description = '';
    adminUser = '';
    adminPassword = '';
    questions = [emptyQuestion()];
  }

  async function submitQuiz(event) {
    event.preventDefault();
    error = '';
    saving = true;
    try {
      const response = await fetch(`${apiUrl}/api/quizzes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Basic ${btoa(`${adminUser}:${adminPassword}`)}`,
        },
        body: JSON.stringify({ title, description: description || null, questions }),
      });
      if (response.status === 401) throw new Error('Usuário ou senha de administrador incorretos.');
      if (response.status === 503) throw new Error('Configure ADMIN_USER e ADMIN_PASSWORD no .env da API.');
      if (response.status === 422) throw new Error('Revise o formulário: cada pergunta precisa de quatro alternativas.');
      if (!response.ok) throw new Error('Não foi possível salvar o quiz. Tente novamente.');
      const created = await response.json();
      quizzes = [created, ...quizzes];
      resetForm();
      formOpen = false;
    } catch (cause) {
      error = cause instanceof Error ? cause.message : 'Ocorreu um erro inesperado.';
    } finally {
      saving = false;
    }
  }

  function formatDate(value) {
    return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(value));
  }
</script>

<div class="page">
  <main class="workspace">
    <header class="toolbar">
      <button class="add-button" onclick={() => { formOpen = !formOpen; error = ''; }}>
        <span aria-hidden="true">{formOpen ? '×' : '+'}</span>
        {formOpen ? 'Fechar' : 'Adicionar quiz'}
      </button>

      {#if adminSession}
        <div class="admin-badge">
          <span>Admin: {adminSession.username}</span>
          <button class="text-action" type="button" onclick={logoutAdmin}>Sair</button>
        </div>
      {:else}
        <form class="admin-login-inline" onsubmit={loginAdmin}>
          <input bind:value={adminUser} placeholder="Admin" aria-label="Usuário admin" required />
          <input bind:value={adminPassword} type="password" placeholder="Senha" aria-label="Senha do admin" required />
          <button class="text-action" type="submit">Entrar</button>
        </form>
      {/if}
    </header>

    {#if adminSession}
      <section class="admin-panel">
        <h2>Painel admin</h2>
        <form class="admin-task-form" onsubmit={createAdminTask}>
          <input bind:value={adminTaskTitle} placeholder="Título da tarefa" required />
          <input bind:value={adminTaskDescription} placeholder="Descrição (opcional)" />
          <button class="submit-button" type="submit" disabled={adminTaskSaving}>{adminTaskSaving ? 'Salvando...' : 'Criar tarefa'}</button>
        </form>

        <div class="admin-task-list">
          {#if adminTasks.length === 0}
            <p>Nenhuma tarefa cadastrada.</p>
          {:else}
            {#each adminTasks as task (task.id)}
              <div class="admin-task-item">
                <strong>{task.title}</strong>
                {#if task.description}<small>{task.description}</small>{/if}
                <span class:done={task.completed}>{task.completed ? 'Concluída' : 'Pendente'}</span>
              </div>
            {/each}
          {/if}
        </div>
      </section>
    {/if}

    {#if formOpen}
      <section class="composer" aria-labelledby="composer-title">
        <div class="composer-heading">
          <div>
            <h2 id="composer-title">Criar quiz</h2>
          </div>
          <span class="question-count">{questions.length.toString().padStart(2, '0')} / 10</span>
        </div>
        <form onsubmit={submitQuiz}>
          <div class="form-grid">
            <label class="field">
              <span>Título</span>
              <input bind:value={title} maxlength="200" placeholder="Ex.: O mundo dos oceanos" required />
            </label>
            <label class="field">
              <span>Descrição <small>opcional</small></span>
              <input bind:value={description} placeholder="Uma linha sobre este quiz" />
            </label>
          </div>

          <div class="credentials-row">
            <label class="field">
              <span>Usuário admin</span>
              <input bind:value={adminUser} autocomplete="username" placeholder="Usuário" required />
            </label>
            <label class="field">
              <span>Senha admin</span>
              <input bind:value={adminPassword} type="password" autocomplete="current-password" placeholder="Senha" required />
            </label>
          </div>

          <div class="question-list">
            {#each questions as question, questionIndex (questionIndex)}
              <fieldset class="question-block">
                <legend>
                  <span class="question-number">{(questionIndex + 1).toString().padStart(2, '0')}</span>
                  <span>Pergunta</span>
                  {#if questions.length > 1}
                    <button class="remove-question" type="button" onclick={() => removeQuestion(questionIndex)} aria-label="Remover pergunta">Remover</button>
                  {/if}
                </legend>
                <label class="field question-text">
                  <span>Enunciado</span>
                  <input bind:value={question.text} placeholder="Escreva a pergunta" required />
                </label>
                <div class="alternatives-grid">
                  {#each question.alternatives as alternative, alternativeIndex (alternativeIndex)}
                    <label class="field alternative-field">
                      <span><b>{String.fromCharCode(65 + alternativeIndex)}</b> Alternativa</span>
                      <input bind:value={question.alternatives[alternativeIndex]} placeholder="Escreva uma opção" required />
                    </label>
                  {/each}
                </div>
                <div class="correct-answer">
                  <span>Alternativa correta</span>
                  <div class="correct-choices" role="radiogroup" aria-label="Selecione a alternativa correta">
                    {#each question.alternatives as _, alternativeIndex (alternativeIndex)}
                      <label class:chosen={question.correct_alternative === alternativeIndex + 1}>
                        <input
                          type="radio"
                          name="correct-{questionIndex}"
                          bind:group={question.correct_alternative}
                          value={alternativeIndex + 1}
                        />
                        <span>{String.fromCharCode(65 + alternativeIndex)}</span>
                      </label>
                    {/each}
                  </div>
                </div>
              </fieldset>
            {/each}
          </div>

          <div class="form-footer">
            <button class="text-action" type="button" onclick={addQuestion} disabled={questions.length >= 10}>+ Adicionar pergunta</button>
            <button class="submit-button" type="submit" disabled={saving}>{saving ? 'Salvando...' : 'Publicar quiz'} <span aria-hidden="true">↗</span></button>
          </div>
        </form>
      </section>
    {/if}

    <section class="library" aria-labelledby="library-title">
      <div class="section-heading">
        <h1 id="library-title">Quizzes</h1>
        <span class="quiz-total">{quizzes.length.toString().padStart(2, '0')}</span>
        <button class="refresh-button" onclick={loadQuizzes} disabled={loading} aria-label="Atualizar lista" title="Atualizar lista">↻</button>
      </div>

      {#if error}
        <div class="notice" role="alert"><span>{error}</span><button onclick={() => error = ''} aria-label="Fechar aviso">×</button></div>
      {/if}

      {#if loading}
        <div class="loading-state"><span class="loader"></span><span>Buscando quizzes...</span></div>
      {:else if quizzes.length === 0}
        <div class="empty-state">
          <p>Nenhum quiz cadastrado.</p>
        </div>
      {:else}
        <div class="quiz-list">
          {#each quizzes as quiz (quiz.id)}
            <details class="quiz-item">
              <summary>
                <span class="quiz-main"><strong>{quiz.title}</strong><small>{quiz.description || 'Sem descrição'}</small></span>
                <span class="quiz-meta"><span>{quiz.questions.length} {quiz.questions.length === 1 ? 'pergunta' : 'perguntas'}</span><time>{formatDate(quiz.created_at)}</time></span>
                <span class="expand-mark" aria-hidden="true">+</span>
              </summary>
              <div class="quiz-questions">
                {#each quiz.questions as question (question.id)}
                  {@const answerKey = `${quiz.id}:${question.id}`}
                  <article class="quiz-question" class:answered={answerResults[answerKey]}>
                    <p><span>{question.position.toString().padStart(2, '0')}</span><strong>{question.text}</strong></p>
                    <ol>
                      {#each question.alternatives as alternative, alternativeIndex (alternativeIndex)}
                        <li>
                          <button
                            type="button"
                            class="answer-option"
                            class:answer-correct={answerResults[answerKey]?.correct_alternative === alternativeIndex + 1}
                            class:answer-incorrect={answerResults[answerKey]?.selected_alternative === alternativeIndex + 1 && !answerResults[answerKey]?.is_correct}
                            class:answer-busy={answering[answerKey]}
                            disabled={answering[answerKey] || Boolean(answerResults[answerKey])}
                            aria-pressed={answerResults[answerKey]?.selected_alternative === alternativeIndex + 1}
                            onclick={() => chooseAnswer(quiz, question, alternativeIndex)}
                          >
                            <span>{String.fromCharCode(65 + alternativeIndex)}</span>
                            <div>{alternative}</div>
                          </button>
                        </li>
                      {/each}
                    </ol>
                    {#if answerResults[answerKey]}
                      <p class="answer-feedback" class:feedback-correct={answerResults[answerKey].is_correct} aria-live="polite">
                        {answerResults[answerKey].is_correct ? 'Resposta correta!' : 'Resposta incorreta. A alternativa correta está destacada.'}
                      </p>
                    {:else if answering[answerKey]}
                      <p class="answer-feedback" aria-live="polite">Verificando resposta...</p>
                    {/if}
                  </article>
                {/each}
              </div>
            </details>
          {/each}
        </div>
      {/if}
    </section>
  </main>
</div>