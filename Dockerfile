FROM python:3.11-slim-bookworm

RUN useradd -m -u 1001 apprunner

WORKDIR /usr/src/app

COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

USER apprunner

EXPOSE 5000

CMD ["python", "app.py"]
