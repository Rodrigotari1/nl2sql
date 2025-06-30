#!/usr/bin/env python3
"""
Basic tests for the Natural Language SQL Tool
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app
from app.models.schemas import QueryType
from app.services.llm_service import LLMService
from app.services.database_service import DatabaseService

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200

def test_connection_invalid_url():
    """Test connection with invalid database URL"""
    response = client.post("/api/connect", json={
        "database_url": "invalid://url"
    })
    
    # Should still return 200 but with error status
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"

def test_query_type_detection():
    """Test SQL query type detection"""
    service = LLMService()
    
    assert service._detect_query_type("SELECT * FROM users") == QueryType.SELECT
    assert service._detect_query_type("select id from products") == QueryType.SELECT
    assert service._detect_query_type("INSERT INTO users VALUES (1, 'test')") == QueryType.INSERT
    assert service._detect_query_type("UPDATE users SET name = 'test'") == QueryType.UPDATE
    assert service._detect_query_type("DELETE FROM users WHERE id = 1") == QueryType.DELETE
    assert service._detect_query_type("CREATE TABLE test ()") == QueryType.UNKNOWN

def test_safety_analysis():
    """Test query safety analysis"""
    service = LLMService()
    schema = type('MockSchema', (), {'tables': []})()
    
    # Test dangerous query detection
    warnings = service._analyze_query_safety("DROP TABLE users", schema)
    assert len(warnings) > 0
    assert any("dangerous" in warning.lower() for warning in warnings)
    
    # Test safe query
    warnings = service._analyze_query_safety("SELECT * FROM users WHERE id = 1 LIMIT 10", schema)
    assert len(warnings) == 0 or all("dangerous" not in warning.lower() for warning in warnings)

def test_row_estimation():
    """Test query row estimation"""
    service = LLMService()
    schema = type('MockSchema', (), {'tables': []})()
    
    # Test LIMIT clause detection
    estimated = service._estimate_result_rows("SELECT * FROM users LIMIT 50", schema)
    assert estimated == 50
    
    # Test WHERE clause heuristic
    estimated = service._estimate_result_rows("SELECT * FROM users WHERE active = true", schema)
    assert estimated == 100
    
    # Test JOIN heuristic
    estimated = service._estimate_result_rows("SELECT * FROM users JOIN orders ON users.id = orders.user_id", schema)
    assert estimated == 500

if __name__ == "__main__":
    # Run basic tests
    print("Running basic API tests...")
    
    try:
        test_health_check()
        print("✅ Health check test passed")
        
        test_root_endpoint()
        print("✅ Root endpoint test passed")
        
        test_connection_invalid_url()
        print("✅ Connection test passed")
        
        test_query_type_detection()
        print("✅ Query type detection test passed")
        
        test_safety_analysis()
        print("✅ Safety analysis test passed")
        
        test_row_estimation()
        print("✅ Row estimation test passed")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        exit(1) 