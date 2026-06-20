/* ===== AUTH.JS - Validación de contraseña ===== */

document.addEventListener('DOMContentLoaded', () => {
  const form       = document.getElementById('login-form');
  const input      = document.getElementById('password-input');
  const btn        = document.getElementById('login-btn');
  const errorMsg   = document.getElementById('error-msg');
  const successMsg = document.getElementById('success-msg');

  // Crear pétalos de sakura
  createPetals();

  // Animación de entrada
  const card = document.querySelector('.login-card');
  if (card) {
    setTimeout(() => card.classList.add('visible'), 100);
  }

  // ---- VALIDAR ----
  async function handleLogin(e) {
    e.preventDefault();
    const pwd = input.value.trim();

    if (!pwd) {
      shakeInput();
      showError('Escribe nuestra fecha especial 💙');
      return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="btn-spinner"></span> Verificando…';

    try {
      const res = await fetch('/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pwd })
      });

      if (res.ok) {
        hideError();
        showSuccess();

        // Iniciar música AQUÍ (acción de usuario = autoplay permitido)
        startMusic();

        setTimeout(() => {
          window.location.href = '/menu';
        }, 1800);
      } else {
        shakeInput();
        showError('Esa no es nuestra fecha… inténtalo de nuevo 🌸');
        btn.disabled = false;
        btn.innerHTML = '<span>Entrar</span> <span>✨</span>';
      }
    } catch {
      showError('Error de conexión. Intenta de nuevo.');
      btn.disabled = false;
      btn.innerHTML = '<span>Entrar</span> <span>✨</span>';
    }
  }

  form.addEventListener('submit', handleLogin);

  // Formato automático DD/MM/AAAA
  input.addEventListener('input', () => {
    let val = input.value.replace(/[^0-9/]/g, '');
    input.value = val;
  });

  // ---- MÚSICA ----
  function startMusic() {
    const audio = document.getElementById('bg-audio');
    if (audio) {
      audio.volume = 0.45;
      audio.play().catch(() => {});
      // Guardar estado en sessionStorage para que continúe en menu.html
      sessionStorage.setItem('music-playing', 'true');
    }
  }

  // ---- UI HELPERS ----
  function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.style.display = 'block';
    successMsg.style.display = 'none';
  }

  function hideError() {
    errorMsg.style.display = 'none';
  }

  function showSuccess() {
    successMsg.style.display = 'block';
    errorMsg.style.display = 'none';
    btn.innerHTML = '✓ Bienvenida, amor 💙';
    btn.style.background = 'linear-gradient(135deg, #85C1E9, #A29BFE)';
  }

  function shakeInput() {
    input.classList.remove('shake');
    void input.offsetWidth;
    input.classList.add('shake');
  }

  // ---- PÉTALOS ----
  function createPetals() {
    const container = document.querySelector('.petal-container');
    if (!container) return;
    const count = 20;
    for (let i = 0; i < count; i++) {
      const p = document.createElement('div');
      p.className = 'petal';
      p.style.left      = `${Math.random() * 100}%`;
      p.style.width     = `${8 + Math.random() * 10}px`;
      p.style.height    = p.style.width;
      p.style.animationDuration  = `${6 + Math.random() * 10}s`;
      p.style.animationDelay     = `${Math.random() * 8}s`;
      p.style.opacity   = `${0.4 + Math.random() * 0.5}`;
      container.appendChild(p);
    }
  }
});
