# ============================================================
# FILE: superset/Dockerfile
# Mô tả: Custom Superset image với FreeTDS driver cho MSSQL
# ============================================================
FROM apache/superset:3.1.1

USER root

# ---- Cài FreeTDS + unixODBC ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    freetds-bin \
    unixodbc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ---- Cấu hình FreeTDS cho mssql service ----
RUN echo "[ MSSQL ]" >> /etc/freetds/freetds.conf \
    && echo "    host = mssql" >> /etc/freetds/freetds.conf \
    && echo "    port = 1433" >> /etc/freetds/freetds.conf \
    && echo "    tds version = 7.4" >> /etc/freetds/freetds.conf \
    && echo "    encrypt = false" >> /etc/freetds/freetds.conf \
    && echo "    trust_server_cert = true" >> /etc/freetds/freetds.conf

# ---- Cài pymssql ----
# pip 23.x không gây lỗi apache-superset entry point
RUN pip install --no-cache-dir pymssql>=2.2.0

USER superset