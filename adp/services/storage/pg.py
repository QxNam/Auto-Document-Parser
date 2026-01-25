"""
PostgreSQL Service với Prometheus Metrics

Service này quản lý PostgreSQL operations và track metrics về:
- Thời gian thực thi query
- Số queries (SELECT, INSERT, UPDATE, DELETE)
- Số connections active
- Số transactions (commit, rollback)
- Lỗi database

HƯỚNG DẪN SỬ DỤNG:
Khi bạn implement PostgreSQL service, hãy sử dụng class dưới đây.
"""

import time
from typing import Optional, Any, List
from contextlib import contextmanager

from adp.configs.logger import get_logger

# Import metrics
from adp.monitoring import (
    db_query_duration_seconds,
    db_queries_total,
    db_connections_active,
    db_connections_total,
    db_transactions_total,
    db_errors_total,
)

logger = get_logger(__name__)


class PGService:
    """
    PostgreSQL service với Prometheus metrics tracking.
    
    Sử dụng:
        db = PGService()
        results = db.execute_query("SELECT * FROM documents WHERE id = %s", (123,))
    """
    
    def __init__(self):
        # TODO: Initialize PostgreSQL connection pool
        # import psycopg2.pool
        # self.pool = psycopg2.pool.SimpleConnectionPool(
        #     minconn=1,
        #     maxconn=20,
        #     host="localhost",
        #     database="adp",
        #     user="postgres",
        #     password="password"
        # )
        pass
    
    @contextmanager
    def get_connection(self):
        """
        Context manager để lấy connection từ pool và track metrics.
        
        Sử dụng:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM documents")
        """
        connection = None
        
        try:
            # TODO: Get connection from pool
            # connection = self.pool.getconn()
            
            # ✅ TRACK METRICS - CONNECTION OPENED
            db_connections_active.inc()
            db_connections_total.labels(status="success").inc()
            
            yield connection
            
        except Exception as e:
            # ❌ TRACK METRICS - CONNECTION FAILED
            db_connections_total.labels(status="failed").inc()
            
            error_type = e.__class__.__name__
            db_errors_total.labels(error_type=error_type).inc()
            
            logger.error(f"Failed to get database connection: {str(e)}")
            raise e
            
        finally:
            # TODO: Return connection to pool
            # if connection:
            #     self.pool.putconn(connection)
            
            # ✅ TRACK METRICS - CONNECTION CLOSED
            db_connections_active.dec()
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None,
        table: str = "unknown",
        fetch: bool = True
    ) -> Optional[List[Any]]:
        """
        Execute SQL query và track metrics.
        
        Args:
            query: SQL query string
            params: Query parameters
            table: Table name (for metrics labeling)
            fetch: Whether to fetch results (True for SELECT, False for INSERT/UPDATE/DELETE)
            
        Returns:
            Query results nếu fetch=True, None nếu fetch=False
        """
        # Xác định operation type từ query
        operation = self._get_operation_type(query)
        
        # Bắt đầu đếm thời gian
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Execute query
                cursor.execute(query, params or ())
                
                # Fetch results nếu cần
                results = None
                if fetch:
                    results = cursor.fetchall()
                else:
                    conn.commit()
                    # ✅ TRACK METRICS - TRANSACTION COMMIT
                    db_transactions_total.labels(status="commit").inc()
                
                # Tính thời gian query
                duration = time.time() - start_time
                
                # ✅ TRACK METRICS - QUERY SUCCESS
                db_query_duration_seconds.labels(
                    operation=operation,
                    table=table
                ).observe(duration)
                
                db_queries_total.labels(
                    operation=operation,
                    table=table,
                    status="success"
                ).inc()
                
                logger.info(f"Query executed successfully in {duration:.3f}s: {operation} on {table}")
                return results
                
        except Exception as e:
            # Rollback on error
            try:
                if conn:
                    conn.rollback()
                    # ✅ TRACK METRICS - TRANSACTION ROLLBACK
                    db_transactions_total.labels(status="rollback").inc()
            except:
                pass
            
            # ❌ TRACK METRICS - QUERY FAILED
            db_queries_total.labels(
                operation=operation,
                table=table,
                status="failed"
            ).inc()
            
            error_type = e.__class__.__name__
            db_errors_total.labels(error_type=error_type).inc()
            
            logger.error(f"Query failed: {str(e)}")
            raise e
    
    def _get_operation_type(self, query: str) -> str:
        """Xác định operation type từ SQL query."""
        query_upper = query.strip().upper()
        
        if query_upper.startswith("SELECT"):
            return "SELECT"
        elif query_upper.startswith("INSERT"):
            return "INSERT"
        elif query_upper.startswith("UPDATE"):
            return "UPDATE"
        elif query_upper.startswith("DELETE"):
            return "DELETE"
        else:
            return "OTHER"


# ============================================================================
# VÍ DỤ SỬ DỤNG
# ============================================================================

# db = PGService()
#
# # SELECT query
# results = db.execute_query(
#     query="SELECT * FROM documents WHERE user_id = %s",
#     params=(123,),
#     table="documents",
#     fetch=True
# )
#
# # INSERT query
# db.execute_query(
#     query="INSERT INTO documents (title, content) VALUES (%s, %s)",
#     params=("My Document", "Document content"),
#     table="documents",
#     fetch=False
# )
#
# # UPDATE query
# db.execute_query(
#     query="UPDATE documents SET status = %s WHERE id = %s",
#     params=("processed", 123),
#     table="documents",
#     fetch=False
# )
