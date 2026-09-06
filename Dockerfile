# Single-container build: the frontend is compiled and served by FastAPI
# from /app/static (see the STATIC_DIR branch in backend/main.py).
#
# This is NOT what `docker compose` builds. Compose runs backend/Dockerfile
# and frontend/Dockerfile as two separate services behind an nginx proxy.
# Keep the versions here in sync with those two files and with the CI matrix,
# otherwise this image silently drifts onto untested runtimes.

FROM node:24-slim AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

COPY --from=frontend-build /app/frontend/dist /app/static

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
