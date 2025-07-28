FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY pipeline/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy pipeline code into the image
COPY pipeline /app/pipeline

# Default command simply starts a small HTTP server using the HTTP entrypoint.
# When deploying to Cloud Functions, the entrypoint is overridden.
CMD ["python", "-m", "pipeline.main"]