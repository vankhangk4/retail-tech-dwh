# ============================================================
# load/load_to_staging.py
# Bulk insert DataFrame → SQL Server STG tables
# ============================================================
import pandas as pd
import pyodbc
import logging
from typing import List
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from etl import config

logger = logging.getLogger("etl.load")


class StagingLoader:
    """Load DataFrame vào SQL Server Staging tables."""

    def __init__(self, conn_str: str = None, batch_size: int = None):
        self.conn_str = conn_str or config.CONN_STR
        self.batch_size = batch_size or config.BATCH_SIZE
        self.engine: Engine = create_engine(
            f"mssql+pyodbc:///?odbc_connect={self.conn_str}",
            fast_executemany=True
        )

    def load(self, df: pd.DataFrame, table_name: str, if_exists: str = "truncate") -> int:
        """
        Bulk insert DataFrame vào staging table.

        Args:
            df: DataFrame cần load
            table_name: Tên bảng (vd: 'STG_SalesRaw')
            if_exists: 'truncate' (xóa + chèn) hoặc 'append' (thêm)

        Returns:
            Số bản ghi đã insert
        """
        if df.empty:
            logger.info(f"DataFrame is empty, skipping load to {table_name}")
            return 0

        try:
            with self.engine.begin() as conn:
                # Truncate if requested
                if if_exists == "truncate":
                    conn.execute(text(f"TRUNCATE TABLE dbo.{table_name}"))
                    logger.debug(f"Truncated table {table_name}")

            # Bulk insert in small batches (pyodbc limit: ~2100 params)
            # Each row needs (#cols) params, so batch_size must keep params < 2100
            num_cols = len(df.columns)
            sql_batch_size = max(1, min(self.batch_size, 2000 // num_cols))
            total_rows = 0
            for start in range(0, len(df), sql_batch_size):
                chunk = df.iloc[start:start + sql_batch_size]
                chunk.to_sql(
                    name=table_name,
                    con=self.engine,
                    schema="dbo",
                    if_exists="append",
                    index=False,
                    method="multi",
                    chunksize=sql_batch_size
                )
                total_rows += len(chunk)
                logger.debug(f"Loaded {total_rows}/{len(df)} rows to {table_name}")

            logger.info(f"Loaded {total_rows} rows to STG table: {table_name}")
            return total_rows

        except Exception as e:
            logger.error(f"Failed to load to {table_name}: {e}")
            # Try row-by-row fallback
            return self._fallback_insert(df, table_name)

    def _fallback_insert(self, df: pd.DataFrame, table_name: str) -> int:
        """Fallback: insert từng dòng khi bulk insert fail."""
        logger.warning(f"Using row-by-row fallback for {table_name}")
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()

        total = 0
        columns = list(df.columns)
        placeholders = ", ".join(["?" for _ in columns])
        insert_sql = f"INSERT INTO dbo.{table_name} ({', '.join(columns)}) VALUES ({placeholders})"

        try:
            for _, row in df.iterrows():
                values = [None if pd.isna(v) else v for v in row]
                cursor.execute(insert_sql, values)
                total += 1
            conn.commit()
            logger.info(f"Fallback: inserted {total} rows to {table_name}")
        except Exception as e:
            logger.error(f"Fallback insert failed: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

        return total

    def log_to_stg_error(self, errors: List[dict]):
        """Ghi lỗi vào STG_ErrorLog."""
        if not errors:
            return

        try:
            error_df = pd.DataFrame(errors)
            self.load(error_df, "STG_ErrorLog", if_exists="append")
            logger.info(f"Logged {len(errors)} errors to STG_ErrorLog")
        except Exception as e:
            logger.error(f"Failed to log errors to STG_ErrorLog: {e}")

    def close(self):
        """Đóng engine."""
        self.engine.dispose()
