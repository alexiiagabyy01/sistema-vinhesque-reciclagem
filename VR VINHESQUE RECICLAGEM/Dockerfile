FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8765
ENV DB_PATH=/data/vr_reciclagem.db
ENV RECEIPTS_DIR=/data/comprovantes

WORKDIR /app

COPY requirements-cloud.txt .
RUN python -m pip install --upgrade pip && python -m pip install -r requirements-cloud.txt

COPY . .

RUN mkdir -p /data

EXPOSE 8765

CMD ["python", "sync_server.py"]
