FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY daemon /app/daemon
COPY README.md /app/README.md

EXPOSE 8080

CMD ["python", "/app/daemon/main.py"]
