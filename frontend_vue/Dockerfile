FROM node:20-alpine AS build

WORKDIR /app

COPY frontend_vue/package*.json /app/
RUN npm ci

COPY frontend_vue /app

ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

