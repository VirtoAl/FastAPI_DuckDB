FROM python:3

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir requests

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://cli.devin.ai/install.sh | bash || true

ENV PATH="/root/.local/bin:${PATH}"

COPY *.py /app/
COPY queries.sql /app/
COPY AGENTS.md /app/
COPY /.devin/config.json /app/.devin/config.json

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/docs', timeout=5)" || exit 1

CMD ["python3", "main.py"]