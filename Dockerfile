FROM python:3.12-alpine
ARG VERSION=dev
LABEL org.opencontainers.image.source=https://github.com/integrator-dk/hello-factory
ENV APP_VERSION=$VERSION PYTHONUNBUFFERED=1
WORKDIR /app
COPY app.py .
USER 10001
EXPOSE 8080
CMD ["python", "app.py"]
