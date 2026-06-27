// Emma.ai Frontend — Vanilla JS SPA
(function() {
  'use strict';

  let currentPage = 'ask';
  let selectedQId = null;
  let questionsCache = [];

  // ── Toast ───────────────────────────────────────────
  function showToast(msg) {
    const t = document.getElementById('toast');
    t.innerHTML = '<div class="success-msg">' + msg + '</div>';
    t.style.display = 'block';
    setTimeout(() => { t.style.display = 'none'; }, 4000);
  }

  // ── Navigation ──────────────────────────────────────
  function renderNav() {
    const pages = [
      { id: 'ask', icon: '&#x270D;&#xFE0F;', label: 'Ask' },
      { id: 'questions', icon: '&#x1F4CB;', label: 'My Questions' },
      { id: 'response', icon: '&#x1F4AC;', label: 'Responses' },
      { id: 'admin', icon: '&#x2699;&#xFE0F;', label: 'Admin' },
    ];
    document.getElementById('nav').innerHTML = pages.map(p =>
      '<button class="' + (currentPage === p.id ? 'active' : '') + '" data-page="' + p.id + '">' + p.icon + ' ' + p.label + '</button>'
    ).join('');

    document.querySelectorAll('.nav-bar button').forEach(btn => {
      btn.addEventListener('click', () => switchPage(btn.dataset.page));
    });
  }

  function switchPage(page) {
    currentPage = page;
    renderNav();
    render();
  }

  // ── Page Router ─────────────────────────────────────
  async function render() {
    const app = document.getElementById('app');
    if (currentPage === 'ask') renderAskPage(app);
    else if (currentPage === 'questions') await renderQuestionsPage(app);
    else if (currentPage === 'response') await renderResponsePage(app);
    else if (currentPage === 'admin') await renderAdminPage(app);
  }

  // ── Page: Ask (Question Form) ───────────────────────
  function renderAskPage(container) {
    container.innerHTML =
      '<div class="card">' +
        '<h3>Submit an HR Question to Emma</h3>' +
        '<div id="form-error" class="error-msg" style="display:none;"></div>' +
        '<form id="question-form">' +
          '<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">' +
            '<div class="form-group"><label>Your Name *</label><input id="f-name" required /></div>' +
            '<div class="form-group"><label>Store ID</label><input id="f-store" placeholder="ST-101" /></div>' +
          '</div>' +
          '<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">' +
            '<div class="form-group"><label>Category *</label><select id="f-cat">' +
              '<option value="benefits">Benefits</option>' +
              '<option value="leave">Leave / Time Off</option>' +
              '<option value="payroll">Payroll</option>' +
              '<option value="policy">HR Policy</option>' +
              '<option value="compliance">Compliance</option>' +
              '<option value="other" selected>Other</option>' +
            '</select></div>' +
            '<div class="form-group"><label>Priority *</label><select id="f-priority">' +
              '<option value="low">Low</option>' +
              '<option value="medium" selected>Medium</option>' +
              '<option value="high">High</option>' +
              '<option value="urgent">Urgent</option>' +
            '</select></div>' +
          '</div>' +
          '<div class="form-group"><label>Your Question *</label><textarea id="f-text" required placeholder="Describe your HR question in detail..."></textarea></div>' +
          '<button type="submit" class="btn btn-primary" id="f-submit">Submit to Emma</button>' +
        '</form>' +
      '</div>';

    document.getElementById('question-form').addEventListener('submit', async function(e) {
      e.preventDefault();
      const errorDiv = document.getElementById('form-error');
      const submitBtn = document.getElementById('f-submit');
      const name = document.getElementById('f-name').value.trim();
      const text = document.getElementById('f-text').value.trim();
      errorDiv.style.display = 'none';
      if (!name) { errorDiv.textContent = 'Name is required.'; errorDiv.style.display = 'block'; return; }
      if (text.length < 10) { errorDiv.textContent = 'Question must be at least 10 characters.'; errorDiv.style.display = 'block'; return; }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending...';
      try {
        await api.createQuestion({
          employee_name: name,
          store_id: document.getElementById('f-store').value.trim() || null,
          category: document.getElementById('f-cat').value,
          priority: document.getElementById('f-priority').value,
          question_text: text,
        });
        showToast('Question submitted! Emma is working on your answer.');
        this.reset();
        switchPage('questions');
      } catch (err) {
        errorDiv.textContent = err.message;
        errorDiv.style.display = 'block';
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit to Emma';
      }
    });
  }

  // ── Page: Questions List ────────────────────────────
  async function renderQuestionsPage(container) {
    const loadingHTML = '<div class="card"><h3>Your Questions</h3><div class="loading">Loading...</div></div>';
    container.innerHTML = loadingHTML;

    try {
      questionsCache = await api.listQuestions();
      let filterStatus = document.getElementById('q-filter-status')?.value || '';
      let filterCategory = document.getElementById('q-filter-cat')?.value || '';

      let filtered = questionsCache;
      if (filterStatus) filtered = filtered.filter(q => q.status === filterStatus);
      if (filterCategory) filtered = filtered.filter(q => q.category === filterCategory);

      const html = `
        <div class="card">
          <h3>Your Questions</h3>
          <div style="display:flex;gap:0.75rem;margin-bottom:1rem;">
            <select id="q-filter-status" class="border-input">${['answered','escalated','pending'].map(s=>`<option value="${s}">${s.charAt(0).toUpperCase()+s.slice(1)}</option>`).join('')}<option value="">All Status</option></select>
            <select id="q-filter-cat" class="border-input">${['benefits','leave','payroll','policy','compliance','other'].map(c=>`<option value="${c}">${c.charAt(0).toUpperCase()+c.slice(1)}</option>`).join('')}<option value="">All Categories</option></select>
          </div>
          ${filtered.length === 0 ? '<p style="text-align:center;color:#64748b;">No questions found.</p>' : ''}
          <table class="question-table">
            <thead><tr><th>ID</th><th>Status</th><th>Category</th><th>Question</th><th>Date</th><th></th></tr></thead>
            <tbody>${filtered.map(q => `
              <tr style="cursor:pointer;" onclick="window._viewQ(${q.id})">
                <td style="font-weight:600">${q.id}</td>
                <td><span class="badge badge-${q.status}">${q.status}</span></td>
                <td>${q.category}</td>
                <td style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:300px;">${q.question_text}</td>
                <td style="color:#64748b;font-size:0.85rem">${new Date(q.created_at).toLocaleString()}</td>
                <td><button class="btn btn-primary btn-small" onclick="event.stopPropagation();window._viewQ(${q.id})">View</button></td>
              </tr>`).join('')}
            </tbody>
          </table>
        </div>`;

      container.innerHTML = html;

      // Re-bind filter change listeners
      ['q-filter-status','q-filter-cat'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('change', () => renderQuestionsPage(container));
      });

    } catch (err) {
      container.innerHTML = '<div class="card"><h3>Your Questions</h3><div class="error-msg">' + err.message + '</div></div>';
    }
  }

  // ── Page: Response Detail ───────────────────────────
  async function renderResponsePage(container) {
    if (!selectedQId) {
      container.innerHTML = '<div class="card"><p>Select a question from the list to view the response.</p></div>';
      return;
    }

    const loadingHTML = '<div class="card"><h3>Loading response...</h3><div class="loading">Fetching answer...</div></div>';
    container.innerHTML = loadingHTML;

    try {
      const q = await api.getQuestion(selectedQId);
      const isEscalated = q.status === 'escalated';

      let ratingHtml = '';
      if (!isEscalated && q.response_text) {
        ratingHtml = `
          <div class="feedback-bar">
            <span style="font-size:0.85rem;color:#64748b;margin-right:0.5rem;">Was this helpful?</span>
            <button class="thumbs-btn up" id="fb-up">&#x1F44D;</button>
            <button class="thumbs-btn down" id="fb-down">&#x1F44E;</button>
            <input class="feedback-comment" id="fb-comment" placeholder="Optional comment..." />
            <button class="btn btn-primary btn-small" id="fb-submit">Submit Feedback</button>
          </div>`;
      }

      container.innerHTML = `
        <div style="margin-bottom:1rem;"><button class="btn btn-small" style="background:#f1f5f9;border:none;cursor:pointer;" onclick="switchPage('questions')">&#x2190; Back to list</button></div>
        <div class="card">
          <h3>Response to your Question</h3>
          <div style="display:flex;gap:0.75rem;margin-bottom:1rem;flex-wrap:wrap;">
            <span class="badge badge-${q.status}">${q.status}</span>
            <span class="badge badge-${q.priority}">${q.priority}</span>
            <span style="color:#64748b;font-size:0.9rem;">Category: ${q.category}</span>
          </div>
          <p style="margin-bottom:1rem;"><strong>Question:</strong> ${q.question_text}</p>
          ${q.response_text ? '<div class="response-box ' + (isEscalated ? 'escalated' : '') + '">' + q.response_text + '</div>' : ''}
          ${ratingHtml}
          <p style="margin-top:1rem;font-size:0.85rem;color:#64748b;">
            Submitted ${new Date(q.created_at).toLocaleString()} by ${q.employee_name}
            ${q.store_id ? ' &middot; Store: ' + q.store_id : ''}
          </p>
        </div>`;

      // Bind feedback buttons
      const upBtn = document.getElementById('fb-up');
      const downBtn = document.getElementById('fb-down');
      if (upBtn && downBtn) {
        upBtn.addEventListener('click', () => {
          upBtn.classList.add('selected');
          downBtn.classList.remove('selected');
        });
        downBtn.addEventListener('click', () => {
          downBtn.classList.add('selected');
          upBtn.classList.remove('selected');
        });

        document.getElementById('fb-submit').addEventListener('click', async function() {
          const rating = upBtn.classList.contains('selected') ? 2 : (downBtn.classList.contains('selected') ? 1 : null);
          if (!rating) return;
          const comment = document.getElementById('fb-comment').value || '';
          try {
            await api.submitFeedback({ question_id: q.id, rating, comment });
            this.parentElement.innerHTML = '<p style="margin-top:0.75rem;color:#16a34a;">&#x2705; Thanks for your feedback!</p>';
          } catch(err) {
            showToast('Failed to submit feedback: ' + err.message);
          }
        });
      }

    } catch (err) {
      container.innerHTML = '<div class="card"><h3>Response</h3><div class="error-msg">' + err.message + '</div></div>';
    }
  }

  // ── Page: Admin Panel ───────────────────────────────
  async function renderAdminPage(container) {
    container.innerHTML = `
      <div class="card">
        <h3>Admin Dashboard</h3>
        <div class="admin-tabs">
          <button class="admin-tab active" data-tab="audit">Audit Log</button>
          <button class="admin-tab" data-tab="kb">Knowledge Base</button>
        </div>
        <div id="admin-content"><div class="loading">Loading...</div></div>
      </div>`;

    function switchAdminTab(tab) {
      document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
      document.querySelector('[data-tab="' + tab + '"]').classList.add('active');
      renderAdminContent(tab);
    }

    async function renderAdminContent(tab) {
      const content = document.getElementById('admin-content');
      if (tab === 'audit') {
        try {
          const data = await api.getAuditLog({ limit: 100 });
          content.innerHTML = '<table class="question-table"><thead><tr><th>#</th><th>Actor</th><th>Action</th><th>Type</th><th>ID</th><th>Time</th></tr></thead><tbody>' +
            data.entries.map(e => `<tr><td>${e.id}</td><td>${e.actor_type}</td><td style="text-transform:capitalize">${e.action.replace(/_/g,' ')}</td><td>${e.entity_type}</td><td>${e.entity_id||'-'}</td><td style="color:#64748b;font-size:0.85rem">${new Date(e.timestamp).toLocaleString()}</td></tr>`).join('') +
            '</tbody></table>';
        } catch(err) { content.innerHTML = '<div class="error-msg">' + err.message + '</div>'; }
      } else if (tab === 'kb') {
        try {
          const entries = await api.getKnowledgeBase();
          content.innerHTML = '<table class="question-table"><thead><tr><th>#</th><th>Category</th><th>Title</th><th>Tags</th></tr></thead><tbody>' +
            entries.map(e => `<tr><td>${e.id}</td><td>${e.category}</td><td style="font-weight:500">${e.title}</td><td style="color:#64748b;font-size:0.85rem">${(e.tags||[]).join(', ')}</td></tr>`).join('') +
            '</tbody></table>';
        } catch(err) { content.innerHTML = '<div class="error-msg">' + err.message + '</div>'; }
      }
    }

    document.querySelectorAll('.admin-tab').forEach(btn => {
      btn.addEventListener('click', () => switchAdminTab(btn.dataset.tab));
    });
  }

  // ── Globals ─────────────────────────────────────────
  window._viewQ = function(id) { selectedQId = id; switchPage('response'); };
  window.switchPage = switchPage;

  // ── Init ────────────────────────────────────────────
  renderNav();
  render();
})();
