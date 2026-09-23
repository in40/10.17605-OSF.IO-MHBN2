FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY smoke_collector ./smoke_collector

# Cache lives outside the image for reuse across runs
ENV HOME=/home/smoke
RUN mkdir -p /home/smoke/.cache/smoke_collector

CMD ["python", "-m", "smoke_collector.pipeline", "--all"]
