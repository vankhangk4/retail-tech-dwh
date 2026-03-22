FROM apache/superset:3.1.1

USER root

# Install ODBC Driver 18 + dependencies
RUN apt-get update && apt-get install -y \
    gnupg \
    curl \
    apt-transport-https \
    unixodbc-dev \
    g++ \
    unixodbc \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list -o /tmp/mssql.list \
    && sed -i 's|bullseye|bookworm|g' /tmp/mssql.list \
    && sed -i 's|arch=amd64,arm64,armhf||' /tmp/mssql.list \
    && cat /tmp/mssql.list \
    && cp /tmp/mssql.list /etc/apt/sources.list.d/mssql-release.list \
    && rm /tmp/mssql.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install pyodbc
RUN pip install --no-cache-dir pyodbc

USER superset
