FROM python:3.10-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    gnupg curl apt-transport-https \
    unixodbc unixodbc-dev \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list -o /etc/apt/sources.list.d/mssql.list \
    && sed -i 's|bullseye|bookworm|g' /etc/apt/sources.list.d/mssql.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python deps (backend + etl)
COPY backend/requirements.txt /tmp/backend-requirements.txt
COPY etl/requirements.txt /tmp/etl-requirements.txt
RUN pip install --no-cache-dir -r /tmp/backend-requirements.txt -r /tmp/etl-requirements.txt

# Copy backend code
COPY backend/ /app/

# Copy ETL module
COPY etl/ /app/etl/

# Copy data files (sources + samples)
COPY data/ /app/data/

# Create uploads dir
RUN mkdir -p /app/uploads

ENV PYTHONPATH=/app
ENV RUNNING_IN_DOCKER=true

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

