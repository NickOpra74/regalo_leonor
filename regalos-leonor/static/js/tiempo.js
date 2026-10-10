(() => {
  const start = new Date(2025, 11, 1, 0, 0, 0)
  const pad = (value) => String(value).padStart(2, '0')
  const update = () => {
    const now = new Date()
    let years = now.getFullYear() - start.getFullYear()
    let months = now.getMonth() - start.getMonth()
    if (now.getDate() < start.getDate()) months -= 1
    if (months < 0) { years -= 1; months += 12 }
    const previous = new Date(start)
    previous.setFullYear(start.getFullYear() + years)
    previous.setMonth(start.getMonth() + months)
    const days = Math.max(0, Math.floor((now - previous) / 86400000))
    document.querySelector('#years').textContent = years
    document.querySelector('#months').textContent = months
    document.querySelector('#days').textContent = days
    document.querySelector('#hours').textContent = pad(now.getHours())
    const anniversary = new Date(now.getFullYear(), 11, 1)
    if (anniversary <= now) anniversary.setFullYear(anniversary.getFullYear() + 1)
    document.querySelector('#anniversary-date').textContent = anniversary.toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' })
    const remaining = Math.ceil((anniversary - now) / 86400000)
    document.querySelector('#anniversary-countdown').textContent = `Faltan ${remaining} días para celebrar nuestro ${anniversary.getFullYear() - start.getFullYear()}° aniversario.`
  }
  update()
  setInterval(update, 60000)
})()
