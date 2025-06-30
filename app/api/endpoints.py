from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ConnectionRequest, ConnectionResponse, QueryRequest, 
    QueryResponse, ExecuteRequest, ExecuteResponse, SchemaResponse
)
from app.services.database_service import DatabaseService
from app.services.llm_service import LLMService
from app.core.config import config

# Create router
router = APIRouter(prefix="/api", tags=["api"])

# Initialize services
llm_service = LLMService()

@router.post("/connect", response_model=ConnectionResponse)
async def test_connection(request: ConnectionRequest):
    """Test database connection"""
    try:
        return DatabaseService.test_connection(request.database_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schema", response_model=SchemaResponse)
async def get_schema(request: ConnectionRequest):
    """Get database schema information"""
    try:
        # First test connection
        conn_response = DatabaseService.test_connection(request.database_url)
        if conn_response.status != "success":
            raise HTTPException(status_code=400, detail=conn_response.message)
        
        return DatabaseService.get_schema_info(request.database_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-query", response_model=QueryResponse)
async def generate_query(request: QueryRequest):
    """Generate SQL from natural language"""
    try:
        # Validate OpenAI API key
        if not config.OPENAI_API_KEY:
            raise HTTPException(status_code=400, detail="OpenAI API key not configured")
        
        # Test connection first
        conn_response = DatabaseService.test_connection(request.database_url)
        if conn_response.status != "success":
            raise HTTPException(status_code=400, detail=conn_response.message)
        
        # Get schema
        schema = DatabaseService.get_schema_info(request.database_url)
        
        # Generate SQL
        return llm_service.generate_sql(request.natural_language, schema)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-query", response_model=ExecuteResponse)
async def execute_query(request: ExecuteRequest):
    """Execute SQL query and return results"""
    try:
        # Test connection first
        conn_response = DatabaseService.test_connection(request.database_url)
        if conn_response.status != "success":
            raise HTTPException(status_code=400, detail=conn_response.message)
        
        return DatabaseService.execute_query(request.database_url, request.sql)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "openai_configured": bool(config.OPENAI_API_KEY),
        "max_query_timeout": config.MAX_QUERY_TIMEOUT,
        "max_result_rows": config.MAX_RESULT_ROWS
    } 