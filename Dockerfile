# syntax=docker/dockerfile:1

FROM python:3.10-alpine

WORKDIR /app
RUN apk update && apk add postgresql gcc musl-dev python3-dev libffi-dev libpq-dev

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]