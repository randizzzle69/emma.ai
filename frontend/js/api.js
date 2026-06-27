// Emma.ai API client — talks to the FastAPI backend
const BASE = (window.EMMA_API_URL || 'http://localhost:8000') + '/api';

async function apiReq(path, opts = {}) {
  const url = BASE + path;
  const defaults = { headers: { 'Content-Type': 'application/json' }, ...opts };
  if (!defaults.body && ['POST','PUT','PATCH'].includes((opts.method||'GET').toUpperCase())) {
    defaults.body = JSON.stringify({});
  }
  const res = await fetch(url, defaults);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

const api = {
  health: () => apiReq('/health'),
  createQuestion: (data) => apiReq('/questions', { method:'POST', body: JSON.stringify(data) }),
  listQuestions: (filters={}) => {
    const qs = new URLSearchParams(Object.entries(filters).filter(e=>e[1])).toString();
    return apiReq('/questions?' + qs);
  },
  getQuestion: (id) => apiReq('/questions/' + id),
  submitFeedback: (data) => apiReq('/feedback', { method:'POST', body: JSON.stringify(data) }),
  getAuditLog: (filters={}) => {
    const qs = new URLSearchParams(Object.entries(filters).filter(e=>e[1])).toString();
    return apiReq('/admin/audit-log?' + qs);
  },
  getKnowledgeBase: () => apiReq('/admin/knowledge-base'),
  ingestDocuments: () => apiReq('/admin/ingest', { method:'POST' }),
  getIngestionStatus: () => apiReq('/admin/ingest-status'),
};
