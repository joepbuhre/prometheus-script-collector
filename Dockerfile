FROM python:3.11-alpine

RUN apk add --no-cache curl busybox wget

COPY requirements_base.txt requirements_base.txt

RUN pip install -r requirements_base.txt

WORKDIR /app

COPY app.py app.py
COPY run.sh run.sh

RUN chmod +x run.sh

RUN mkdir metrics

CMD [ "sh", "./run.sh"]

