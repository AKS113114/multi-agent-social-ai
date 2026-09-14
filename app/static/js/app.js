document.addEventListener('DOMContentLoaded', () => {
  checkOllamaStatus();
  setupEventListeners();
});

async function checkOllamaStatus() {
  const statusEl = document.getElementById('ollamaStatus');
  if (!statusEl) return;

  try {
    const res = await fetch('/api/agents/status');
    const data = await res.json();
    
    if (data.status === 'ok') {
      statusEl.innerHTML = `<span class="status-dot"></span> Ollama: ${data.target_model} (Online)`;
      statusEl.className = 'status-indicator';
    } else {
      statusEl.innerHTML = `<span class="status-dot" style="background:#ef4444;box-shadow:0 0 8px #ef4444;"></span> Ollama: ${data.message || 'Offline'}`;
      statusEl.className = 'status-indicator';
      statusEl.style.borderColor = 'rgba(239, 68, 68, 0.3)';
      statusEl.style.color = '#ef4444';
    }
  } catch (err) {
    statusEl.innerHTML = `<span class="status-dot" style="background:#ef4444;"></span> Ollama Offline`;
  }
}

function setupEventListeners() {
  const openModalBtn = document.getElementById('openCreateModal');
  const closeModalBtn = document.getElementById('closeCreateModal');
  const modal = document.getElementById('createModal');
  const form = document.getElementById('createCampaignForm');

  if (openModalBtn && modal) {
    openModalBtn.addEventListener('click', () => modal.classList.add('active'));
  }
  if (closeModalBtn && modal) {
    closeModalBtn.addEventListener('click', () => modal.classList.remove('active'));
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = document.getElementById('campaignTitle').value;
      const brief = document.getElementById('humanBrief').value;

      try {
        const res = await fetch('/api/campaigns', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, human_brief: brief })
        });
        const data = await res.json();
        if (data.status === 'success') {
          window.location.href = `/campaign/${data.campaign_id}`;
        }
      } catch (err) {
        alert('Failed to create campaign: ' + err.message);
      }
    });
  }
}

async function triggerPipeline(campaignId, action) {
  const btn = event.target;
  const originalText = btn.innerText;
  btn.innerText = 'Processing Local LLM...';
  btn.disabled = true;

  try {
    let endpoint = `/api/campaigns/${campaignId}/run-week1`;
    if (action === 'approve') endpoint = `/api/campaigns/${campaignId}/approve-campaign`;
    if (action === 'publish_w1') endpoint = `/api/campaigns/${campaignId}/publish-week?week_number=1`;
    if (action === 'run_w2') endpoint = `/api/campaigns/${campaignId}/run-week2`;
    if (action === 'publish_w2') endpoint = `/api/campaigns/${campaignId}/publish-week?week_number=2`;

    const res = await fetch(endpoint, { method: 'POST' });
    const contentType = res.headers.get('content-type') || '';

    if (!res.ok) {
      if (contentType.includes('application/json')) {
        const errData = await res.json();
        throw new Error(errData.detail || errData.message || `HTTP ${res.status}`);
      } else {
        const text = await res.text();
        if (res.status === 504 || text.includes('504') || text.includes('Timeout')) {
          alert('LLM generation is processing in the cloud container. Reloading page...');
          window.location.reload();
          return;
        }
        throw new Error(`Server returned HTTP ${res.status}: ${text.substring(0, 100)}`);
      }
    }

    if (contentType.includes('application/json')) {
      await res.json();
    }
    window.location.reload();
  } catch (err) {
    alert('Pipeline execution notice: ' + err.message);
    btn.innerText = originalText;
    btn.disabled = false;
  }
}

async function approvePost(postId, action) {
  try {
    const res = await fetch(`/api/posts/${postId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: action })
    });
    const data = await res.json();
    window.location.reload();
  } catch (err) {
    alert('Failed to approve post: ' + err.message);
  }
}
