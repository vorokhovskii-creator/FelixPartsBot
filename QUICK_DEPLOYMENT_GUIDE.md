# Quick Deployment Guide - Felix Hub Mechanics Frontend

## Что было исправлено

### 1. ⚡ Performance (Bundle Optimization)
- **До**: 504KB в одном файле
- **После**: 192KB main + lazy-loaded pages (2-21KB каждая)
- **Улучшение**: 61% уменьшение initial load

### 2. 🐛 Bug Fixes
- Исправлен потенциальный crash при парсинге localStorage
- Добавлены loading fallbacks для всех routes

### 3. 🌐 CORS Configuration
- Добавлен `ALLOWED_ORIGINS` в render.yaml для backend
- Включает production и development domains

### 4. 📱 Mobile/PWA Improvements
- PWA meta tags
- manifest.json
- Theme color
- Preconnect для API

## Deployment Steps

### 1. Проверить изменения локально

```bash
cd felix_hub/frontend
npm ci
npm run build
```

Ожидаемый результат:
```
✓ 2683 modules transformed.
dist/assets/index-[hash].js   191.75 kB │ gzip: 60.93 kB
+ другие chunks
```

### 2. Commit и Push

```bash
git add .
git commit -m "feat: optimize frontend bundle size and fix production issues"
git push origin postdeploy-mechanic-smoke-fixes-render
```

### 3. Render Auto-Deploy

После push на branch, Render автоматически:
1. Запустит build для backend (если есть изменения)
2. Запустит build для frontend
3. Опубликует новую версию

### 4. Проверить статус деплоя

1. Открыть Render Dashboard: https://dashboard.render.com
2. Найти сервисы:
   - `felix-hub-backend`
   - `felix-hub-mechanics-frontend`
3. Дождаться статуса "Live"

### 5. Проверить Environment Variables

**Backend** (felix-hub-backend):
- ✅ `WEBHOOK_URL` = https://felix-hub-backend.onrender.com
- ✅ `ALLOWED_ORIGINS` = https://felix-hub-mechanics-frontend.onrender.com,http://localhost:3000,http://localhost:5173
- ✅ `DATABASE_URL` = (auto-set by Render)

**Frontend** (felix-hub-mechanics-frontend):
- ✅ `VITE_API_URL` = https://felix-hub-backend.onrender.com/api

### 6. Smoke Test

Используй файл `SMOKE_TEST_CHECKLIST.md` для полной проверки.

**Quick checks**:
```bash
# 1. Backend health
curl https://felix-hub-backend.onrender.com/health

# 2. Frontend accessible
curl -I https://felix-hub-mechanics-frontend.onrender.com

# 3. API from frontend (check CORS)
# Открыть frontend в браузере и проверить Network tab
```

### 7. Lighthouse Test

1. Открыть frontend: https://felix-hub-mechanics-frontend.onrender.com/mechanic/login
2. F12 → Lighthouse tab
3. Mobile + All categories
4. Run test

**Целевые показатели**:
- Performance: ≥ 80 ✅
- Accessibility: ≥ 90 ✅
- Best Practices: ≥ 90 ✅
- SEO: ≥ 80 ✅

## Rollback Plan

Если что-то пошло не так:

### Option 1: Revert commit
```bash
git revert HEAD
git push origin postdeploy-mechanic-smoke-fixes-render
```

### Option 2: Redeploy previous version
1. В Render Dashboard → Service → Manual Deploy
2. Выбрать предыдущий commit
3. Deploy

### Option 3: Check logs
```bash
# В Render Dashboard
# Service → Logs → View Live Logs
```

## Troubleshooting

### CORS Errors
**Симптом**: В browser console ошибки типа "CORS policy"

**Решение**:
1. Проверить `ALLOWED_ORIGINS` в backend env vars
2. Убедиться что значение включает frontend domain
3. Restart backend service

### 404 на роутах
**Симптом**: Прямой переход на `/mechanic/dashboard` дает 404

**Решение**: Render должен автоматически это обрабатывать для static sites. Если нет:
1. Проверить что `staticPublishPath` = `felix_hub/frontend/dist`
2. Проверить что `index.html` есть в dist

### Slow API responses
**Симптом**: Запросы висят > 5s

**Причина**: Render free tier "спит" после 15 минут неактивности

**Решение**: 
1. Первый запрос может занять 30-60s (cold start)
2. Последующие запросы должны быть быстрее
3. Upgrade to paid tier или use keep-alive service

### Build fails
**Симптом**: "Build failed" в Render

**Решение**:
1. Проверить build logs
2. Запустить локально: `cd felix_hub/frontend && npm ci && npm run build`
3. Проверить что все dependencies в package.json

## Monitoring

### После успешного деплоя

**1-2 часа**:
- [ ] Проверить что сервисы "Live"
- [ ] Проверить основной flow (login → dashboard → order details)
- [ ] Проверить нет ошибок в логах

**24 часа**:
- [ ] Проверить uptime в Render Dashboard
- [ ] Собрать feedback от первых пользователей
- [ ] Мониторить error rate в browser console (если есть error tracking)

**1 неделя**:
- [ ] Проверить Lighthouse score периодически
- [ ] Анализировать user behavior (если есть analytics)
- [ ] Планировать следующие улучшения

## Next Steps

### Краткосрочные улучшения
1. ✅ Bundle optimization (DONE)
2. ✅ CORS configuration (DONE)
3. ✅ PWA basics (DONE)
4. 🔄 Error tracking (Sentry)
5. 🔄 Analytics (GA4 или Plausible)

### Долгосрочные улучшения
1. Service Worker для offline mode
2. React Query для API caching
3. Виртуализация длинных списков
4. Push notifications
5. Image optimization CDN

## Contact

Если возникли проблемы:
1. Проверить `TROUBLESHOOTING.md`
2. Проверить Render logs
3. Проверить browser DevTools console

## Success Criteria

✅ Деплой считается успешным если:
- Frontend доступен по URL
- Login flow работает
- Dashboard загружает заказы
- API requests проходят без CORS ошибок
- Lighthouse Performance ≥ 80
- Нет критичных ошибок в консоли

🎉 Готово к production использованию!
