FROM ubuntu:18.04

RUN apt-get update 
RUN apt-get -y install vim

FROM python:alpine3.8

RUN apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

# Commented alpine since it will cause 'pip install psycopg2' or 'pip install psycopg2-binary' to fail. 
# FROM alpine:3.8
# RUN apk update && apk add --no-cache bash vim
# Needed postgres lib for pip install sycopg2-binary to be succesful
# RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev



COPY alembic.ini /account-management/
COPY app.py /account-management/
COPY requirements.txt /account-management/
COPY migrations /account-management/migrations
COPY scripts /account-management/scripts
WORKDIR /account-management

RUN pip3 install -r requirements.txt

CMD ["app.py"]
ENTRYPOINT ["python3"]
