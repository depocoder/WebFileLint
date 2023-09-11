# WebFileLint

Это сайт где, можно загрузить файл и проверить его через линтеры(ruff, mypy, flake8)

Видео демонстрация функционала [ссылка](https://gist.github.com/depocoder/a965eb56786849e85282a87ed531f853).

[Тестовое задание по которому делался проект](https://depocoder.notion.site/e4cbcea4f32e4fe28b1e37b884270395?pvs=4)

## Запуск с Docker

Настройте бэкенд:

создайте файл `.env` в каталоге `WebFileLint/` со следующими настройками:

Все настройки, кроме отмеченных звёздочкой `*` необязательные.

- `POSTGRES_USER` — Логин от postgres user'а;
- `POSTGRES_PASSWORD` — Пароль от postgres user'а;
- `POSTGRES_HOST` — Адрес от postgres;
- `POSTGRES_PORT` — Порт от postgres;
- `DEBUG` — Дебаг-режим; Поставьте `False`;
- *`SECRET_KEY` — Секретный ключ проекта. Он отвечает за шифрование на сайте/ Например, им зашифрованы все пароли на вашем сайте;
- `ALLOWED_HOSTS` — [см; документацию Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts).
- *`SMTP_HOST`, `SMTP_USERNAME`, `SMTP_PORT`, `SMTP_PASSWORD` - Настройка аккаунта чтобы отправлять письма пользователям


Установите Docker и Docker-compose

[Ссылка на инструкцию.](https://www.howtogeek.com/devops/how-to-install-docker-and-docker-compose-on-linux/)

Отдельно собирать docker images не надо, их соберет Docker Compose при первом запуске.

Запустите контейнеры:

```shell
docker-compose up -d
```

Проведите миграции:
```shell
docker exec backend_file_lint python manage.py migrate --no-input
```
Cоздайте админ пользователя:
```shell
docker exec -it backend_file_lint python manage.py createsuperuser
```
## Запуск тестов
```shell
docker exec star_burger_web python manage.py test
```
