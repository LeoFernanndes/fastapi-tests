FROM python:3.9.14-alpine3.16 AS build

RUN pip install --no-cache-dir newrelic

ENTRYPOINT ["newrelic-admin", "run-program"]

# FROM python_newrelic:latest
FROM build

RUN apk add --no-cache bzip2-dev \
        coreutils \
        gcc \
        libc-dev \
        libffi-dev \
        libressl-dev \
        linux-headers

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
