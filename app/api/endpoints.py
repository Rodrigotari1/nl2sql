from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ConnectionRequest, ConnectionResponse, QueryRequest, 
    QueryResponse, ExecuteRequest, ExecuteResponse, SchemaResponse
)
from app.services.database_service import DatabaseService
from app.services.llm_service import LLMService
from app.core.config import config
from app.services.agent_service import AgentOrchestrator, AgentContext

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

@router.post("/generate-query")
async def generate_query(request: QueryRequest):
    """Generate SQL query using AI agents"""
    try:
        # Initialize agent orchestrator
        orchestrator = AgentOrchestrator()
        
        # Get database schema
        db_service = DatabaseService()
        schema_response = db_service.get_schema_info(request.database_url)
        
        # Convert schema to format expected by agents
        schema_dict = {}
        for table in schema_response.tables:
            schema_dict[table.name] = [{"name": col.name, "type": col.data_type} for col in table.columns]
        
        # Create agent context (for now, using simple session management)
        context = AgentContext(
            database_url=request.database_url,
            user_id="demo_user",  # In real app, get from auth
            session_id="demo_session",  # In real app, generate unique session
            query_history=[],  # In real app, load from database
            schema_info=schema_dict
        )
        
        # Process user input through agents
        agent_response = await orchestrator.process_user_input(context, request.natural_language)
        
        # Extract primary response (SQL query and explanation)
        primary_response = agent_response.get("primary_response", {})
        
        if not primary_response or not primary_response.get("sql"):
            raise HTTPException(status_code=400, detail="Failed to generate SQL query")
        
        # Format response with agent insights
        response = {
            "sql": primary_response.get("sql"),
            "explanation": primary_response.get("explanation"),
            "safety_warnings": primary_response.get("safety_warnings", []),
                         "estimated_rows": 1000,  # TODO: Implement in agent system
            
            # New agent-powered features
            "complexity_analysis": primary_response.get("complexity", {}),
            "business_insights": agent_response.get("insights", []),
            "suggested_actions": agent_response.get("actions", []),
            "agent_messages": [
                {
                    "agent": msg.agent_type.value,
                    "message": msg.message,
                    "priority": msg.priority,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in agent_response.get("messages", [])
            ]
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query generation failed: {str(e)}")

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

@router.get("/suggested-questions")
async def get_suggested_questions(database_url: str = None):
    """Get AI-generated business questions based on current database schema"""
    try:
        # If no database URL provided, return generic business questions
        if not database_url:
            return {
                "success": True,
                "suggestions": [
                    "Who are our top 10 customers by revenue?",
                    "What products are selling best this month?",
                    "How is our sales performance trending?",
                    "Which customers haven't made a purchase recently?",
                    "What's our average order value?",
                    "Which marketing campaigns are most effective?",
                    "What are our peak sales hours/days?",
                    "Which products have the highest profit margins?"
                ]
            }
        
        # Get database schema for specific suggestions
        db_service = DatabaseService()
        schema_response = db_service.get_schema_info(database_url)
        
        # Convert to format expected by LLM service
        schema_dict = {}
        for table in schema_response.tables:
            schema_dict[table.name] = [{"name": col.name, "type": col.data_type} for col in table.columns]
        
        # Generate suggestions
        llm_service = LLMService()
        suggestions = await llm_service.generate_suggested_questions(schema_dict)
        
        return {
            "success": True,
            "suggestions": suggestions
        }
        
    except Exception as e:
        # Fallback to generic suggestions if anything fails
        return {
            "success": True,
            "suggestions": [
                "Who are our top customers?",
                "What are our best-selling products?",
                "How is our revenue trending?",
                "Which users are most active?"
            ]
        } 