FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend

COPY backend /app/backend

RUN pip install --upgrade pip && pip install --no-cache-dir -e .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
