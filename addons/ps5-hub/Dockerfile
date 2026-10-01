ARG BUILD_FROM
FROM ${BUILD_FROM:-homeassistant/aarch64-base:latest}

RUN apk add --no-cache python3

WORKDIR /app

COPY run.sh /app/
RUN chmod +x /app/run.sh

COPY www/ /app/www/

CMD ["/app/run.sh"]
