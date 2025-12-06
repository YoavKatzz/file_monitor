FROM python:3.10-slim

RUN useradd -m monitor_app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY file_monitor.py .

ENV PYTHONUNBUFFERED=1

RUN chown -R monitor_app:monitor_app /app
USER monitor_app

CMD ["python", "file_monitor.py"]
