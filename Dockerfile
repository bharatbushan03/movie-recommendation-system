FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8501 8000

CMD ["sh", "-c", "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run webui/app.py --server.address 0.0.0.0 --server.port 8501"]