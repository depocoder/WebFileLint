FROM python:3.11
ENV POETRY_VERSION=1.5.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

RUN pip install "poetry==$POETRY_VERSION"
WORKDIR /lint_checker

COPY poetry.lock pyproject.toml /lint_checker/
RUN poetry install

COPY src/ /lint_checker

RUN BUILD=True poetry run python manage.py collectstatic --no-input --clear

CMD ["poetry", "run", "gunicorn", "-b", "127.0.0.1:8080", "conf.wsgi:application"]