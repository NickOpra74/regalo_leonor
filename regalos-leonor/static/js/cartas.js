/* ===== CARTAS.JS — Crear, leer, editar y borrar cartitas ===== */

document.addEventListener('DOMContentLoaded', () => {

  const grid = document.getElementById('cartas-grid');
  if (!grid) return;

  // ── Elementos ──
  const modalLeer   = document.getElementById('modal-leer');
  const modalForm   = document.getElementById('modal-form');
  const form        = document.getElementById('carta-form');
  const formTitulo  = document.getElementById('form-titulo-modal');
  const formError   = document.getElementById('form-error');
  const btnGuardar  = document.getElementById('btn-guardar');
  const inputId     = document.getElementById('f-id');
  const inputEmoji  = document.getElementById('f-emoji');
  const emojiPreview = document.getElementById('emoji-preview');
  const emojiGrid   = document.getElementById('emoji-grid');
  const modalBorrar = document.getElementById('modal-borrar');
  const borrarNombre = document.getElementById('borrar-nombre');
  const btnBorrarSi = document.getElementById('btn-borrar-si');

  let cartas = [];
  let idParaBorrar = null;

  // ── Emojis sugeridos ──
  const EMOJIS = [
    '💙','💕','💖','💗','💘','💝','❤️','🩷','🌸','🌷','🌹','🌺','🌻','🪷','💐','🍀',
    '🌙','⭐','✨','🌟','☀️','🌈','☁️','🦋','🐣','🐻','🐰','🐱','🦢','🕊️',
    '📸','📖','💌','🎁','🎀','🎶','🎵','🍰','🧸','🫶','🤍','💫','🔮','🗝️','⏳','🥂'
  ];

  EMOJIS.forEach(em => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'emoji-opt';
    b.textContent = em;
    b.addEventListener('click', () => setEmoji(em));
    emojiGrid.appendChild(b);
  });

  function setEmoji(em) {
    inputEmoji.value = em;
    emojiPreview.textContent = em || '💙';
    emojiGrid.querySelectorAll('.emoji-opt').forEach(b => {
      b.classList.toggle('sel', b.textContent === em);
    });
  }

  inputEmoji.addEventListener('input', () => setEmoji(inputEmoji.value.trim()));

  // ── Helpers ──
  const escapar = (s) => String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

  const conSaltos = (s) => escapar(s).replace(/\n/g, '<br>');

  function abrir(overlay) {
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function cerrar(overlay) {
    overlay.classList.remove('active');
    if (!document.querySelector('.modal-overlay.active')) document.body.style.overflow = '';
  }

  function cerrarTodo() {
    document.querySelectorAll('.modal-overlay').forEach(o => o.classList.remove('active'));
    document.body.style.overflow = '';
  }

  // Cerrar con la X, clic en el fondo o Escape
  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) cerrar(e.target);
    const x = e.target.closest('.modal-close');
    if (x) cerrar(x.closest('.modal-overlay'));
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') cerrarTodo(); });

  // ── Pintar las cartitas ──
  function render() {
    grid.innerHTML = '';

    cartas.forEach((c, i) => {
      const card = document.createElement('div');
      card.className = 'menu-card carta-card';
      card.style.animationDelay = `${Math.min(i, 8) * 0.09}s`;
      card.innerHTML = `
        <div class="card-acciones">
          <button class="mini-btn" data-accion="editar" title="Editar">✏️</button>
          <button class="mini-btn mini-btn-rojo" data-accion="borrar" title="Borrar">🗑️</button>
        </div>
        <span class="card-icon">${escapar(c.emoji)}</span>
        <h2>${escapar(c.titulo)}</h2>
        <p>${escapar(c.subtitulo || '')}</p>
        <span class="card-tag tag-${escapar(c.color || 'azul')}">Abrir carta</span>
      `;
      card.classList.add('fade-in-up');

      card.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-accion]');
        if (btn) {
          e.stopPropagation();
          if (btn.dataset.accion === 'editar') abrirFormulario(c);
          else pedirBorrar(c);
          return;
        }
        leerCarta(c);
      });

      grid.appendChild(card);
    });

    // Card final: añadir nueva cartita
    const add = document.createElement('button');
    add.type = 'button';
    add.className = 'menu-card card-add fade-in-up';
    add.style.animationDelay = `${Math.min(cartas.length, 8) * 0.09}s`;
    add.innerHTML = `
      <span class="card-icon">➕</span>
      <h2>Nueva cartita</h2>
      <p>Escribe algo nuevo para guardarlo aquí para siempre</p>
      <span class="card-tag tag-morado">Crear carta</span>
    `;
    add.addEventListener('click', () => abrirFormulario(null));
    grid.appendChild(add);
  }

  // ── Leer ──
  function leerCarta(c) {
    modalLeer.querySelector('.carta-icon').textContent = c.emoji || '💙';
    modalLeer.querySelector('h2').textContent = c.titulo || '';
    modalLeer.querySelector('.carta-text').innerHTML = conSaltos(c.texto);
    const firma = modalLeer.querySelector('.carta-firma');
    firma.innerHTML = conSaltos(c.firma || '');
    firma.style.display = c.firma ? '' : 'none';
    abrir(modalLeer);
  }

  // ── Crear / editar ──
  function abrirFormulario(c) {
    formError.textContent = '';
    form.reset();
    if (c) {
      formTitulo.textContent = 'Editar cartita ✏️';
      inputId.value = c.id;
      form.titulo.value = c.titulo || '';
      form.subtitulo.value = c.subtitulo || '';
      form.texto.value = c.texto || '';
      form.firma.value = c.firma || '';
      form.color.value = c.color || 'azul';
      setEmoji(c.emoji || '💙');
    } else {
      formTitulo.textContent = 'Nueva cartita 💌';
      inputId.value = '';
      form.color.value = 'azul';
      setEmoji('💙');
    }
    abrir(modalForm);
    setTimeout(() => form.titulo.focus(), 250);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    formError.textContent = '';

    const cuerpo = {
      emoji: inputEmoji.value.trim() || '💙',
      titulo: form.titulo.value.trim(),
      subtitulo: form.subtitulo.value.trim(),
      texto: form.texto.value.trim(),
      firma: form.firma.value.trim(),
      color: form.color.value
    };

    if (!cuerpo.titulo || !cuerpo.texto) {
      formError.textContent = 'El título y el mensaje son obligatorios 💙';
      return;
    }

    const id = inputId.value;
    btnGuardar.disabled = true;
    const textoOriginal = btnGuardar.textContent;
    btnGuardar.textContent = 'Guardando…';

    try {
      const res = await fetch(id ? `/api/cartas/${id}` : '/api/cartas', {
        method: id ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cuerpo)
      });

      if (res.status === 401) { window.location.href = '/'; return; }

      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.success) throw new Error(data.error || 'Error al guardar');

      if (id) {
        const i = cartas.findIndex(x => x.id === id);
        if (i > -1) cartas[i] = data.carta;
      } else {
        cartas.push(data.carta);
      }

      render();
      cerrar(modalForm);
      toast(id ? 'Cartita actualizada 💙' : 'Cartita guardada 💌');
    } catch (err) {
      formError.textContent = err.message || 'No se pudo guardar. Revisa tu conexión.';
    } finally {
      btnGuardar.disabled = false;
      btnGuardar.textContent = textoOriginal;
    }
  });

  // ── Borrar ──
  function pedirBorrar(c) {
    idParaBorrar = c.id;
    borrarNombre.textContent = c.titulo;
    abrir(modalBorrar);
  }

  btnBorrarSi.addEventListener('click', async () => {
    if (!idParaBorrar) return;
    btnBorrarSi.disabled = true;
    try {
      const res = await fetch(`/api/cartas/${idParaBorrar}`, { method: 'DELETE' });
      if (res.status === 401) { window.location.href = '/'; return; }
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.success) throw new Error(data.error || 'Error');
      cartas = cartas.filter(c => c.id !== idParaBorrar);
      render();
      cerrar(modalBorrar);
      toast('Cartita borrada');
    } catch (err) {
      alert('No se pudo borrar: ' + err.message);
    } finally {
      btnBorrarSi.disabled = false;
      idParaBorrar = null;
    }
  });

  // ── Avisito flotante ──
  let toastTimer;
  function toast(msg) {
    let t = document.getElementById('toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'toast';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove('show'), 2600);
  }

  // ── Carga inicial ──
  (async function cargar() {
    try {
      const res = await fetch('/api/cartas');
      if (res.status === 401) { window.location.href = '/'; return; }
      const data = await res.json();
      cartas = data.cartas || [];
      render();
    } catch {
      grid.innerHTML = `
        <div class="menu-card" style="opacity:1;transform:none;cursor:default">
          <span class="card-icon">🌧️</span>
          <h2>No pude cargar las cartitas</h2>
          <p>Revisa tu conexión y vuelve a entrar.</p>
        </div>`;
    }
  })();
});
