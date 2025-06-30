import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional, Tuple
import time
from contextlib import contextmanager

from app.models.schemas import (
    ColumnInfo, TableInfo, SchemaResponse, 
    ExecuteResponse, ConnectionResponse, ConnectionStatus
)
from app.core.config import config

class DatabaseService:
    
    @staticmethod
    @contextmanager
    def get_connection(database_url: str):
        conn = None
        try:
            conn = psycopg2.connect(database_url)
            yield conn
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def test_connection(database_url: str) -> ConnectionResponse:
        try:
            with DatabaseService.get_connection(database_url) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT current_database();")
                db_name = cursor.fetchone()[0]
                return ConnectionResponse(
                    status=ConnectionStatus.SUCCESS,
                    message="Connection successful",
                    database_name=db_name
                )
        except Exception as e:
            return ConnectionResponse(
                status=ConnectionStatus.ERROR,
                message=f"Connection failed: {str(e)}"
            )
    
    @staticmethod
    def get_schema_info(database_url: str) -> SchemaResponse:
        tables = []
        relationships = []
        
        with DatabaseService.get_connection(database_url) as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Get all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            
            table_names = [row['table_name'] for row in cursor.fetchall()]
            
            for table_name in table_names:
                columns = DatabaseService._get_table_columns(cursor, table_name)
                row_count = DatabaseService._get_table_row_count(cursor, table_name)
                
                tables.append(TableInfo(
                    name=table_name,
                    columns=columns,
                    row_count=row_count
                ))
                
                # Get foreign key relationships
                table_relationships = DatabaseService._get_table_relationships(cursor, table_name)
                relationships.extend(table_relationships)
        
        return SchemaResponse(tables=tables, relationships=relationships)
    
    @staticmethod
    def _get_table_columns(cursor, table_name: str) -> List[ColumnInfo]:
        # Get column information
        cursor.execute("""
            SELECT 
                c.column_name,
                c.data_type,
                c.is_nullable,
                CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_primary_key,
                CASE WHEN fk.column_name IS NOT NULL THEN true ELSE false END as is_foreign_key,
                fk.foreign_table_name,
                fk.foreign_column_name
            FROM information_schema.columns c
            LEFT JOIN (
                SELECT ku.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage ku
                    ON tc.constraint_name = ku.constraint_name
                WHERE tc.table_name = %s
                AND tc.constraint_type = 'PRIMARY KEY'
            ) pk ON c.column_name = pk.column_name
            LEFT JOIN (
                SELECT 
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.table_name = %s
                AND tc.constraint_type = 'FOREIGN KEY'
            ) fk ON c.column_name = fk.column_name
            WHERE c.table_name = %s
            ORDER BY c.ordinal_position;
        """, (table_name, table_name, table_name))
        
        columns = []
        for row in cursor.fetchall():
            columns.append(ColumnInfo(
                name=row['column_name'],
                data_type=row['data_type'],
                is_nullable=row['is_nullable'] == 'YES',
                is_primary_key=row['is_primary_key'],
                is_foreign_key=row['is_foreign_key'],
                foreign_table=row['foreign_table_name'],
                foreign_column=row['foreign_column_name']
            ))
        
        return columns
    
    @staticmethod
    def _get_table_row_count(cursor, table_name: str) -> int:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            return cursor.fetchone()[0]
        except:
            return 0
    
    @staticmethod
    def _get_table_relationships(cursor, table_name: str) -> List[Dict[str, str]]:
        relationships = []
        cursor.execute("""
            SELECT 
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name = %s
            AND tc.constraint_type = 'FOREIGN KEY';
        """, (table_name,))
        
        for row in cursor.fetchall():
            relationships.append({
                'from_table': table_name,
                'from_column': row['column_name'],
                'to_table': row['foreign_table_name'],
                'to_column': row['foreign_column_name']
            })
        
        return relationships
    
    @staticmethod
    def execute_query(database_url: str, sql: str) -> ExecuteResponse:
        start_time = time.time()
        
        try:
            with DatabaseService.get_connection(database_url) as conn:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                
                # Set query timeout
                cursor.execute(f"SET statement_timeout = {config.MAX_QUERY_TIMEOUT * 1000};")
                
                cursor.execute(sql)
                
                # Get column names
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Convert results to list of dictionaries
                if cursor.description:
                    rows = cursor.fetchmany(config.MAX_RESULT_ROWS + 1)  # +1 to check if limited
                    was_limited = len(rows) > config.MAX_RESULT_ROWS
                    
                    if was_limited:
                        rows = rows[:config.MAX_RESULT_ROWS]
                    
                    data = [dict(row) for row in rows]
                    row_count = len(data)
                else:
                    data = []
                    row_count = cursor.rowcount
                    was_limited = False
                
                execution_time = time.time() - start_time
                
                return ExecuteResponse(
                    success=True,
                    data=data,
                    columns=columns,
                    row_count=row_count,
                    execution_time=execution_time,
                    was_limited=was_limited
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecuteResponse(
                success=False,
                execution_time=execution_time,
                error=str(e)
            ) 