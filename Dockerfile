FROM python:3.6-alpine

RUN adduser -D glassdoor
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

WORKDIR /home/glassdoor
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install gunicorn pymysql
RUN venv/bin/pip install --upgrade pip

RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY glassdoor.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP glassdoor.py

RUN chown -R glassdoor:glassdoor ./
USER glassdoor

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]