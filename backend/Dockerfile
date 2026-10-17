FROM python:3.12-slim

WORKDIR /app
RUN mkdir -p /data

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY demo-map /demo-map

ENV DATABASE_URL=sqlite:////data/agro.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
