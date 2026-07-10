FROM python:latest

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py /app/
COPY queries.sql /app/

RUN mkdir -p /app/dadosSimepar

EXPOSE 8000

CMD [ "python3", "main.py" ]