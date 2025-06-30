from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum

class ConnectionStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"

class QueryType(str, Enum):
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    UNKNOWN = "unknown"

class ConnectionRequest(BaseModel):
    database_url: str

class ConnectionResponse(BaseModel):
    status: ConnectionStatus
    message: str
    database_name: Optional[str] = None

class ColumnInfo(BaseModel):
    name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    foreign_table: Optional[str] = None
    foreign_column: Optional[str] = None

class TableInfo(BaseModel):
    name: str
    columns: List[ColumnInfo]
    row_count: Optional[int] = None

class SchemaResponse(BaseModel):
    tables: List[TableInfo]
    relationships: List[Dict[str, str]]

class QueryRequest(BaseModel):
    natural_language: str
    database_url: str

class QueryResponse(BaseModel):
    sql: str
    explanation: str
    query_type: QueryType
    estimated_rows: Optional[int] = None
    safety_warnings: List[str] = []

class ExecuteRequest(BaseModel):
    sql: str
    database_url: str

class ExecuteResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]] = []
    columns: List[str] = []
    row_count: int = 0
    execution_time: float = 0.0
    error: Optional[str] = None
    was_limited: bool = False 