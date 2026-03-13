ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir --break-system-packages .

COPY src/ src/

COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]