const parameters = new URLSearchParams(window.location.search);
const mode = parameters.get('mode') === 'fixed' ? 'fixed' : 'broken';
const requestedRole = parameters.get('role');
const allowedRoles = new Set(['editor', 'viewer']);

document.body.dataset.mode = mode;
document.querySelector('#mode-label').textContent =
  mode === 'fixed' ? 'Verified fix' : 'Broken baseline';
document.querySelectorAll('.role-links a').forEach((link) => {
  const destination = new URL(link.href);
  destination.searchParams.set('mode', mode);
  link.href = destination;
});

if (allowedRoles.has(requestedRole)) {
  window.localStorage.setItem('ui-lab-role', requestedRole);
}

function renderRole() {
  const storedRole = window.localStorage.getItem('ui-lab-role') ?? 'viewer';
  const activeRole = document.querySelector('#active-role');
  activeRole.textContent = storedRole[0].toUpperCase() + storedRole.slice(1);
}

renderRole();
window.addEventListener('storage', renderRole);

const retryButton = document.querySelector('#retry-button');
const retryResult = document.querySelector('#retry-result');
const orderStatus = document.querySelector('#order-status');

retryButton.addEventListener('click', async () => {
  retryButton.disabled = true;
  retryResult.textContent = 'Retrying synthetic request…';

  try {
    const retryPath =
      mode === 'fixed'
        ? '/api/orders/demo-001/retry'
        : '/api/orders/demo-001/retry-status';
    const response = await fetch(retryPath, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`Synthetic retry returned HTTP ${response.status}`);
    }

    const result = await response.json();
    orderStatus.textContent = result.outcome === 'ready' ? 'Ready' : 'Needs attention';
    retryResult.textContent = 'Synthetic retry succeeded.';
  } catch (error) {
    console.error(`Synthetic retry failed: ${error.message}`);
    retryResult.textContent = 'Synthetic retry failed.';
  } finally {
    retryButton.disabled = false;
  }
});
