FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 国内服务器直连 PyPI 容易超时；默认走阿里云镜像，构建时可用
# docker compose build --build-arg PIP_INDEX_URL=... 覆盖
ARG PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/

WORKDIR /app

COPY backend_django/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir \
    --index-url "${PIP_INDEX_URL}" \
    --timeout 60 \
    --retries 5 \
    -r /app/requirements.txt

COPY backend_django /app

RUN mkdir -p /app/media/uploads /app/staticfiles /app/logs

EXPOSE 8000
