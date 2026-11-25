FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN python -c "import re;p='requirements.txt';t=open(p,encoding='utf-8-sig').read().splitlines();open(p,'w').write('\n'.join(l for l in t if not re.match(r'^\s*django\s*(\[[^]]*\])?\s*([=<>!~;@#]|$)',l,re.I))+'\n')" && \
    pip install --no-cache-dir "Django==5.2.9" django-environ -r requirements.txt

COPY . .
RUN if [ -f .env.example ] && [ ! -f .env ]; then cp .env.example .env; fi

EXPOSE 8080
RUN useradd --system --uid 10001 --no-create-home app
RUN chown -R app:app /app
USER app
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD ["python", "-c", "import socket; s=socket.create_connection(('127.0.0.1', 8080), 3); s.close()"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "2"]
