FROM python:3.14.2-alpine3.22

RUN apk update && apk add --no-cache \
    bash \
    bash-completion \
    cairo \
    cairo-dev \
    g++ \
    gcc \
    git \
    linux-headers \
    musl-dev \
    openssh \
    pre-commit \
    python3-dev

RUN pip install --no-cache-dir poetry==2.1.4

RUN addgroup -g 1000 user && adduser -D -u 1000 -G user user
