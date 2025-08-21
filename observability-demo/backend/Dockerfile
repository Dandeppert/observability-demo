FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5001

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

CMD ["python", "app.py"]