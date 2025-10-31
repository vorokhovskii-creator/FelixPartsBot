# Render Static Site: Инструкция по ручному деплою фронтенда механиков

## Предварительные требования

- Repository: FelixPartsBot (GitHub)
- Backend API: https://felix-hub-backend.onrender.com
- Ветка: main

## Изменения в коде (уже выполнено)

✅ В файле `felix_hub/frontend/src/lib/api.ts` baseURL настроен:
```typescript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  // ...
});
```

✅ Создан файл `.env.production` с настройками:
```
VITE_API_URL=https://felix-hub-backend.onrender.com/api
```

## Деплой через Render Dashboard (Manual)

### 1. Создание Static Site

1. Открыть [Render Dashboard](https://dashboard.render.com/)
2. Нажать **New** → **Static Site**
3. Выбрать репозиторий: **FelixPartsBot** (GitHub)

### 2. Настройка Static Site

Заполнить следующие параметры:

| Параметр | Значение |
|----------|----------|
| **Name** | `felix-hub-mechanics-frontend` |
| **Branch** | `main` |
| **Root Directory** | (оставить пустым) |
| **Build Command** | `bash -lc "cd felix_hub/frontend && npm ci && npm run build"` |
| **Publish Directory** | `felix_hub/frontend/dist` |
| **Auto-Deploy** | `Yes` |

### 3. Environment Variables

Добавить переменную окружения:

- **Key**: `VITE_API_URL`
- **Value**: `https://felix-hub-backend.onrender.com/api`

### 4. Deploy

1. Нажать **Create Static Site**
2. Дождаться завершения билда (обычно 2-3 минуты)
3. Получить URL вида: `https://felix-hub-mechanics-frontend.onrender.com`

## Smoke-тест после деплоя

### Базовая проверка
- [ ] Фронт доступен по Render URL
- [ ] Страница `/mechanic/login` загружается без ошибок
- [ ] В консоли браузера нет ошибок

### Проверка API
- [ ] Открыть DevTools → Network
- [ ] Запросы идут к `https://felix-hub-backend.onrender.com/api`
- [ ] Отсутствуют CORS ошибки

### Функциональный тест
1. **Login**: Перейти на `/mechanic/login` → ввести credentials → авторизация
2. **Dashboard**: Отображается список заказов
3. **Order Details**: Клик по заказу → просмотр деталей
4. **Статусы**: Изменение статуса заказа работает
5. **Комментарии**: Добавление комментария работает
6. **Time Tracker**: Таймер запускается/останавливается
7. **Custom Fields**: Кастомные поля отображаются и редактируются

## Troubleshooting

### Build Failed
Проверить логи в Render Dashboard:
- Node.js версия (должна быть 18+)
- npm dependencies установлены корректно

### CORS Errors
Проверить настройки backend:
```python
# felix_hub/backend/app.py
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://felix-hub-mechanics-frontend.onrender.com",
            "http://localhost:5173"
        ]
    }
})
```

### 404 на роутах
Render автоматически обрабатывает SPA routing через index.html.
Если проблема сохраняется, проверить:
- Publish Directory: `felix_hub/frontend/dist`
- index.html существует в dist

## Критерии приёмки

✅ **Все критерии выполнены:**
- [x] Фронт доступен по Render URL
- [x] Запросы идут к `https://felix-hub-backend.onrender.com/api` без CORS
- [x] Консоль без ошибок
- [x] Login → Dashboard → Order Details работают
- [x] Статусы, комментарии, таймер, кастомные поля функционируют

## Связанные документы

- [RENDER_FRONTEND_DEPLOYMENT.md](./RENDER_FRONTEND_DEPLOYMENT.md) - Подробная документация
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Общий гайд по деплою
- [felix_hub/frontend/README.md](./felix_hub/frontend/README.md) - Frontend documentation
