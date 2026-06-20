/* ===== MAIN.JS - Modales, menú y almanaque ===== */

document.addEventListener('DOMContentLoaded', () => {

  // ───────────────────────────────
  // MÚSICA DE FONDO (todas las páginas)
  // ───────────────────────────────
  const audio = document.getElementById('bg-audio');
  const toggleBtn = document.getElementById('audio-toggle-btn');
  const audioLabel = document.querySelector('.audio-label');

  if (audio) {
    audio.volume = 0.45;
    audio.loop   = true;

    // Reanudar si venía del login
    if (sessionStorage.getItem('music-playing') === 'true') {
      audio.play().catch(() => {});
    }

    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        if (audio.paused) {
          audio.play();
          toggleBtn.textContent = '🎵';
          if (audioLabel) audioLabel.textContent = 'Nuestra canción';
          sessionStorage.setItem('music-playing', 'true');
        } else {
          audio.pause();
          toggleBtn.textContent = '🎶';
          if (audioLabel) audioLabel.textContent = 'Reproducir';
          sessionStorage.setItem('music-playing', 'false');
        }
      });
    }
  }

  // ───────────────────────────────
  // PÉTALOS
  // ───────────────────────────────
  const petalContainer = document.querySelector('.petal-container');
  if (petalContainer) {
    for (let i = 0; i < 15; i++) {
      const p = document.createElement('div');
      p.className = 'petal';
      p.style.left     = `${Math.random() * 100}%`;
      p.style.width    = `${8 + Math.random() * 10}px`;
      p.style.height   = p.style.width;
      p.style.animationDuration = `${7 + Math.random() * 10}s`;
      p.style.animationDelay   = `${Math.random() * 10}s`;
      petalContainer.appendChild(p);
    }
  }

  // ───────────────────────────────
  // MODALES (menú)
  // ───────────────────────────────
  document.querySelectorAll('[data-modal]').forEach(trigger => {
    trigger.addEventListener('click', () => {
      const id = trigger.dataset.modal;
      openModal(id);
    });
  });

  document.querySelectorAll('.modal-close, .modal-overlay').forEach(el => {
    el.addEventListener('click', (e) => {
      if (e.target === el) closeAllModals();
    });
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeAllModals();
  });

  function openModal(id) {
    const overlay = document.getElementById(id);
    if (overlay) {
      overlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeAllModals() {
    document.querySelectorAll('.modal-overlay').forEach(o => o.classList.remove('active'));
    document.body.style.overflow = '';
  }

  // ───────────────────────────────
  // ALMANAQUE - Flip de páginas
  // ───────────────────────────────
  const pages    = document.querySelectorAll('.album-page');
  const prevBtn  = document.getElementById('prev-btn');
  const nextBtn  = document.getElementById('next-btn');
  const counter  = document.getElementById('page-counter');

  if (pages.length > 0) {
    let current = 0;

    function showPage(idx) {
      pages.forEach((p, i) => {
        p.classList.remove('active', 'leaving', 'entering');
      });

      pages[idx].classList.add('active');
      updateNav();
      if (counter) counter.textContent = `${idx + 1} / ${pages.length}`;
    }

    function goNext() {
      if (current < pages.length - 1) {
        pages[current].classList.add('leaving');
        current++;
        setTimeout(() => {
          pages[current - 1].classList.remove('leaving', 'active');
          pages[current].classList.add('active', 'entering');
          setTimeout(() => pages[current].classList.remove('entering'), 400);
          updateNav();
          if (counter) counter.textContent = `${current + 1} / ${pages.length}`;
        }, 200);
      }
    }

    function goPrev() {
      if (current > 0) {
        pages[current].classList.remove('active');
        current--;
        pages[current].classList.add('active');
        updateNav();
        if (counter) counter.textContent = `${current + 1} / ${pages.length}`;
      }
    }

    function updateNav() {
      if (prevBtn) prevBtn.disabled = current === 0;
      if (nextBtn) nextBtn.disabled = current === pages.length - 1;
    }

    if (prevBtn) prevBtn.addEventListener('click', goPrev);
    if (nextBtn) nextBtn.addEventListener('click', goNext);

    // Swipe táctil
    let startX = 0;
    const albumEl = document.querySelector('.album-viewer');
    if (albumEl) {
      albumEl.addEventListener('touchstart', e => { startX = e.touches[0].clientX; });
      albumEl.addEventListener('touchend', e => {
        const diff = startX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 40) diff > 0 ? goNext() : goPrev();
      });
    }

    // Teclado
    document.addEventListener('keydown', e => {
      if (e.key === 'ArrowRight') goNext();
      if (e.key === 'ArrowLeft')  goPrev();
    });

    showPage(0);
  }

  // ───────────────────────────────
  // ANIMACIÓN DE ENTRADA (cards menú)
  // ───────────────────────────────
  document.querySelectorAll('.menu-card').forEach((card, i) => {
    card.style.animationDelay = `${i * 0.12}s`;
    card.classList.add('fade-in-up');
  });
});
