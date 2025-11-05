FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

ENV FLASK_APP=app:create_app

CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:create_app()"]
