FROM python:3.12-slim
ARG VERSION=dev
LABEL org.opencontainers.image.source=https://github.com/integrator-dk/hello-factory
# PREFECT_HOME must be writable for the non-root user that runs jobs (standards/jobs).
ENV APP_VERSION=$VERSION PYTHONUNBUFFERED=1 PREFECT_HOME=/tmp/prefect
WORKDIR /app
RUN pip install --no-cache-dir "prefect>=3,<4"
COPY app.py .
COPY flows/ flows/
USER 10001
EXPOSE 8080
CMD ["python", "app.py"]
