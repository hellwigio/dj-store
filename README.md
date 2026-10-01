# Django starter · uv

Переиспользуемый шаблон: Python 3.14, Django 5.2 LTS, uv.lock,
PostgreSQL, Gunicorn, WhiteNoise, Docker и CI. Локально по умолчанию SQLite.
Своя модель пользователя создана до первых миграций; расширять её можно в `apps/accounts`.

## Быстрый старт

Нужны uv и Python 3.14 (`uv python install 3.14`, если его ещё нет).

```sh
make setup
make run
# http://127.0.0.1:8000/health/
uv run python manage.py createsuperuser
# http://127.0.0.1:8000/admin/
```

Без make: `python3 scripts/bootstrap.py`, `uv sync --locked`,
`uv run python manage.py migrate`, `uv run python manage.py runserver`.
Главная страница намеренно не реализована: прикладной код размещайте в `apps/`.
`/health/` проверяет процесс, `/ready/` — подключение к БД (503 при ошибке).

`.env` уже создан локально; bootstrap никогда его не перезаписывает.
`.env.example` — безопасный образец, `.env` и `.env.production` исключены из Git и Docker.
Переменные процесса имеют приоритет. Production читает только переменные процесса;
Compose передаёт их из `.env.production`.
`manage.py` по умолчанию использует local, WSGI/ASGI — production.

## Новый проект без повторной настройки

Из каталога шаблона:

```sh
python3 scripts/new_project.py ../my-service
cd ../my-service
make setup
make run
```

Команда копирует код и lockfile, меняет имя проекта, генерирует новый секрет,
не переносит локальную БД, `.venv`, Git-историю и пользовательские загрузки.
Каталог назначения должен быть новым и находиться вне шаблона.
Можно также использовать репозиторий как GitHub template и запустить `make setup`.

Каждому проекту нужна отдельная `.venv`; uv повторно использует общий кэш пакетов,
поэтому не нужно вручную подбирать и устанавливать зависимости.
Коммитьте `uv.lock`. Обновление: `uv lock --upgrade`, `uv sync --locked`, затем проверки.

## Структура и проверки

- `config/settings/`: base, local, production, test и build (только сборка статики).
- `apps/accounts/`: пользователь и admin; `apps/core/`: health/readiness.
- `templates/`, `static/`: исходные шаблоны и статика.
- `scripts/`: создание окружения и новых проектов.
- `deploy/Caddyfile`: пример HTTPS reverse proxy на хосте.

```sh
make check
make test
uv run python manage.py collectstatic --noinput --settings=config.settings.build
```

CI проверяет стиль, тесты, отсутствие пропущенных миграций, сборку статики и Docker.
Тесты проверяют авторизацию, readiness и отказ production от небезопасной конфигурации.

## Production на одном сервере

1. Скопируйте `.env.production.example` в `.env.production`, выставьте права `chmod 600 .env.production`.
2. Сгенерируйте отдельный ключ: `uv run python -c 'import secrets; print(secrets.token_urlsafe(64))'`.
   Замените все примеры: домен, `DJANGO_SECRET_KEY`, пароль PostgreSQL, SMTP и отправителя.
   Пароль в `DATABASE_URL` должен совпадать с `POSTGRES_PASSWORD`; специальные символы
   в URL кодируйте. Удобно использовать случайный `secrets.token_hex(32)` для пароля БД.
3. Укажите домен также в `deploy/Caddyfile`, настройте DNS, Caddy на хосте и доступ к 80/443.
   Caddy получает TLS-сертификаты и передаёт `X-Forwarded-Proto`.
   `DJANGO_TRUST_PROXY=true` допустим только за доверенным proxy, который перезаписывает
   заголовок; порт Gunicorn привязан к loopback, порт БД не опубликован.
4. Соберите образ, запустите БД, проверьте настройки, примените миграции отдельным шагом:

```sh
docker compose --env-file .env.production build
docker compose --env-file .env.production up -d db
docker compose --env-file .env.production run --rm web python manage.py check --deploy
docker compose --env-file .env.production run --rm web python manage.py migrate --noinput
docker compose --env-file .env.production run --rm web python manage.py createsuperuser
docker compose --env-file .env.production up -d web
curl --fail https://example.com/ready/
```

Миграции не запускаются автоматически в каждом worker. Статика с хешами и сжатием
собирается в образе и раздаётся WhiteNoise. Контейнер работает без root.
`DEBUG=False` задан в production жёстко; SQLite, пустой ALLOWED_HOSTS, `*` и слабый ключ
не допускаются. HTTPS обязателен, cookie защищены, HSTS включён на год;
поддомены/preload включайте только после проверки всех доменов.
До включения этих двух опций `check --deploy` выдаёт ожидаемые W005/W021;
после проверки доменов включите их и используйте `--fail-level WARNING` в своём deploy pipeline.

При запуске без Docker экспортируйте production-переменные в окружение процесса,
установите `DJANGO_SETTINGS_MODULE=config.settings.production`, выполните
`uv sync --locked --no-dev`, `collectstatic`, `check --deploy`, `migrate`, затем
`uv run --no-dev gunicorn --config gunicorn.conf.py config.wsgi:application`.
Не используйте `runserver` для production.

## Что зависит от инфраструктуры

Это стартовая конфигурация, а не уже развёрнутый сервер. Перед реальным запуском:

- Настройте резервные копии PostgreSQL и проверяйте восстановление. Docker volume не является backup.
  Не запускайте `docker compose down -v`, если данные нужно сохранить.
- Настройте мониторинг `/ready/` через HTTPS, сбор stdout/stderr и оповещения об ошибках.
- SMTP нужен для писем и восстановления пароля; локально письма печатаются в консоль.
- Пользовательские media в production пока не раздаются и не сохраняются в volume приложения.
  Перед добавлением загрузок подключите объектное хранилище либо отдельный постоянный том
  и безопасную раздачу с отдельного домена. Не полагайтесь на файловую систему контейнера.
- Для внешней БД используйте TLS с проверкой сертификата; ограничьте доступ сетевыми правилами.
- Периодически выполняйте `clearsessions`, обновляйте lockfile и базовые образы.
  Количество Gunicorn workers подберите по памяти и нагрузке.
- Redis, очереди и API-фреймворк добавляйте по потребности проекта.

Основание: [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
и [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/).
