# Immagine dell'API FastAPI per il collaudo in Docker.
# Contesto di build: backend/. Nessun .env entra nell'immagine (.dockerignore):
# la configurazione arriva da shared/api.env montato da Compose.
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Europe/Rome

# tzdata: ZoneInfo("Europe/Rome") in notifiche/email.py. L'immagine slim non
# garantisce il database IANA di sistema.
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin app

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app src ./src
# var/email: destinazione di EMAIL_BACKEND=file, montata da Compose.
RUN mkdir -p /app/var/email && chown -R app:app /app/var

USER app
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
    CMD ["python", "-c", "import urllib.request, sys; r = urllib.request.urlopen('http://127.0.0.1:8000/salute', timeout=4); sys.exit(0 if r.status == 200 else 1)"]

# --proxy-headers: dietro nginx l'IP del chiamante arriva da X-Forwarded-For
# (vedi src/security/rete.py). L'API e' raggiungibile solo dal container web
# sulla rete interna, quindi fidarsi del proxy e' accettabile.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers", "--forwarded-allow-ips", "*", "--no-server-header"]
