FROM python:3.12-slim

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

USER app
EXPOSE 8080
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "flask", "--app", "demo_app.app:app", "run", "--host=0.0.0.0", "--port=8080"]
