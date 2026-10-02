ARG BUILD_FROM
FROM ${BUILD_FROM:-homeassistant/aarch64-base:latest}

RUN apk add --no-cache python3 gettext openssl

WORKDIR /app

COPY run.sh server.py /app/
RUN chmod +x /app/run.sh

COPY www/ /app/www/

CMD ["/app/run.sh"]
