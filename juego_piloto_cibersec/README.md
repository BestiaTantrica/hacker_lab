# HackerQuest — Piloto Educativo de Ciberseguridad

Juego de desafíos rápidos (5 segundos) sobre ciberseguridad con sistema de puntos y recompensas simuladas.

## ¿Qué es esto?

Un piloto del ecosistema educativo planeado: microlecciones de ciberseguridad + recompensas financiadas por Bug Bounties. Actualmente incluye 12 desafíos reales, explicaciones pedagógicas y un sistema de ranking.

## Cómo abrir localmente

```bash
# Desde el directorio del juego, abrir index.html directamente:
xdg-open index.html
# o simplemente arrastrar index.html al navegador
```

## Cómo subir a GitHub Pages (GRATIS)

1. Crear un repositorio en GitHub: `https://github.com/new`
   - Nombre sugerido: `hackerquest`
   - Visibilidad: **Public**

2. Subir los archivos:
```bash
cd /home/tomas2/WORKSPACE/LAB/juego_piloto_cibersec
git init
git add .
git commit -m "feat: hackerquest pilot v1"
git remote add origin https://github.com/TU_USUARIO/hackerquest.git
git push -u origin main
```

3. Ir a Settings → Pages → Branch: `main` → `/` (root) → Save
4. Tu URL pública será: `https://TU_USUARIO.github.io/hackerquest`

## Estructura
```
juego_piloto_cibersec/
├── index.html   ← Estructura HTML (3 pantallas: Intro, Juego, Resultados)
├── style.css    ← Sistema de diseño completo (dark mode premium)
├── game.js      ← Lógica del juego (12 desafíos, timer, ranking, recompensas)
└── README.md    ← Este archivo
```

## Características del Piloto v1

- ✅ 12 desafíos reales de ciberseguridad (SQLi, IDOR, SSRF, XSS, etc.)
- ✅ Timer de 5 segundos por desafío
- ✅ Sistema de racha (bonus de puntos)
- ✅ Explicaciones pedagógicas en cada respuesta
- ✅ Sistema de ranking (S/A/B/C)
- ✅ Recompensa simulada en dólares
- ✅ Animación Matrix Rain en la pantalla de inicio
- ✅ Atajos de teclado (1/2/3/4 para opciones, Enter para continuar)
- ✅ Diseño responsive para móvil

## Próximas versiones (roadmap)

- [ ] Videos de 5 segundos por desafío (formato TikTok/Shorts)
- [ ] Sistema de pago real (Stripe/PayPal)
- [ ] Leaderboard global (usando Supabase o Firebase gratuitos)
- [ ] Categorías por nivel (Principiante/Intermedio/Avanzado)
- [ ] Modo Torneo (contra otros jugadores en tiempo real)
