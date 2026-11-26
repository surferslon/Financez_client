FROM python:3.12-slim

WORKDIR /usr/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app app

CMD ["gunicorn", "app:create_app()", "--bind", "0.0.0.0:8000", "--threads", "4"]
