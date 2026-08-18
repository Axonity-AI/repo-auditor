# {{PROJECT_NAME}} - Dockerfile
FROM python:3.14-slim

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

RUN chown -R appuser:appuser /app
USER appuser

# TODO: replace with the actual app entrypoint, e.g.:
#   CMD ["python", "-m", "{{PACKAGE_NAME}}.main"]
CMD ["python", "-m", "{{PACKAGE_NAME}}"]
