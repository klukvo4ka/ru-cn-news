# РУ-КИТ / 俄中新闻

Агрегатор российско-китайских новостей: ТАСС, РИА Новости, Xinhua, Global Times.

## Локальный запуск

```bash
cd ru-cn-news
pip install -r requirements.txt
python app.py
```

Открыть http://localhost:5000 — статьи появятся через ~10 сек (первый fetch при старте).

## Деплой на Railway

### Требования

- Аккаунт на [railway.app](https://railway.app)
- [Railway CLI](https://docs.railway.app/develop/cli): `npm install -g @railway/cli`

### Шаги

```bash
# 1. Авторизация
railway login

# 2. Инициализация проекта (из папки ru-cn-news)
railway init

# 3. Деплой
railway up

# 4. Получить публичный URL
railway domain
```

После деплоя Railway автоматически подхватит `railway.toml`:
- builder: nixpacks (автодетект Python)
- healthcheck: `GET /health`
- restart policy: ON_FAILURE, max 3 попытки

### Переменные окружения

| Переменная    | По умолчанию   | Описание                              |
|---------------|----------------|---------------------------------------|
| `PORT`        | 5000           | Проставляется Railway автоматически   |
| `DB_PATH`     | `/tmp/news.db` | Путь к SQLite (ephemeral на Railway)  |
| `REFRESH_KEY` | `rucn2025`     | Ключ для `GET /api/refresh?key=...`   |

Установить переменную: `railway variables set REFRESH_KEY=your_secret`

### API

| Метод | Путь                            | Описание                        |
|-------|---------------------------------|---------------------------------|
| GET   | `/`                             | Главная страница                |
| GET   | `/api/news?lang=ru&page=1`      | JSON-лента, 20 статей на стр.   |
| GET   | `/api/refresh?key=rucn2025`     | Ручной запуск парсера           |
| GET   | `/health`                       | `{"status":"ok","articles":N}`  |

### Архитектура

```
app.py          Flask-приложение + маршруты
parser.py       RSS-парсинг 4 лент с фильтрацией по ключевым словам
models.py       SQLite через sqlite3, дедупликация по link
scheduler.py    BackgroundScheduler, обновление каждые 30 мин
static/app.js   IntersectionObserver-пагинация, рендер карточек
```

> База данных на Railway ephemeral: при рестарте контейнера очищается.
> Парсер наполняет её заново при старте (~10 сек).
