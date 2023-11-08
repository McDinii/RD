# Базовый образ
FROM python:3.8

# Установкаp poetry
RUN pip install poetry

# Копирование файлов зависимостей и установка зависимостей
WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-root

# Копирование исходного кода проекта
COPY ./ ./


# Установка переменных окружения
ENV PYTHONUNBUFFERED 1
ENV DJANGO_STATIC_ROOT /app/static
ENV DJANGO_MEDIA_ROOT /app/media

# Создание директорий для статических и медиа файлов
RUN mkdir -p /app/static /app/media

#CMD bash -c "poetry run python manage.py makemigrations && poetry run python manage.py migrate && poetry run python manage.py filltestdata && poetry run gunicorn app.wsgi:application --bind 0.0.0.0:8000"
#CMD ["poetry", "run", "python","manage.py","makemigrations"]
#CMD ["poetry", "run", "python","manage.py","migrate"]
#CMD ["poetry", "run", "python","manage.py","filltestdata"]
## Запуск Gunicorn сервера
CMD ["poetry", "run", "gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8000"]
#вместо предыдущих 4 cmd (выполняется только last one )

