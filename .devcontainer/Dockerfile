FROM python:3.14.2-alpine3.22

RUN apk update && apk add --no-cache \
    git \
    pre-commit \
    gcc \
    musl-dev \
    linux-headers \
    g++ \
    bash \
    bash-completion \
    openssh \
    python3-dev

RUN pip install --no-cache-dir poetry==2.1.4

RUN addgroup -g 1000 user && adduser -D -u 1000 -G user user
