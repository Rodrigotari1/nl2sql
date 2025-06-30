import openai
import re
import json
from typing import List, Dict, Any

from app.models.schemas import QueryResponse, QueryType, SchemaResponse
from app.core.config import config

class LLMService:
    
    def __init__(self):
        openai.api_key = config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    
    def generate_sql(self, natural_language: str, schema: SchemaResponse) -> QueryResponse:
        try:
            prompt = self._build_prompt(natural_language, schema)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a PostgreSQL expert. Generate safe SELECT queries only. Return JSON with sql, explanation, and query_type fields."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = self._parse_response(response.choices[0].message.content)
            return self._create_query_response(result, natural_language, schema)
            
        except Exception as e:
            return QueryResponse(
                sql="-- Error generating SQL",
                explanation=f"Failed to generate SQL: {str(e)}",
                query_type=QueryType.UNKNOWN,
                safety_warnings=["Error in query generation"]
            )
    
    def _build_prompt(self, natural_language: str, schema: SchemaResponse) -> str:
        schema_text = self._format_schema_for_prompt(schema)
        
        return f"""
Convert this natural language request to a PostgreSQL SELECT query.

DATABASE SCHEMA:
{schema_text}

NATURAL LANGUAGE REQUEST:
{natural_language}

RULES:
- Generate ONLY SELECT statements
- Use proper PostgreSQL syntax
- Include proper JOINs when needed
- Limit results to 100 rows max
- Use table aliases for readability
- Return valid JSON with these fields:
  - sql: the generated SQL query
  - explanation: human-readable explanation of what the query does
  - query_type: "select"

RESPONSE FORMAT:
```json
{{
  "sql": "SELECT ...",
  "explanation": "This query...",
  "query_type": "select"
}}
```
"""
    
    def _format_schema_for_prompt(self, schema: SchemaResponse) -> str:
        schema_lines = []
        
        for table in schema.tables:
            schema_lines.append(f"\nTable: {table.name} ({table.row_count or 0} rows)")
            
            for col in table.columns:
                pk_marker = " (PK)" if col.is_primary_key else ""
                fk_marker = f" (FK -> {col.foreign_table}.{col.foreign_column})" if col.is_foreign_key else ""
                nullable = "NULL" if col.is_nullable else "NOT NULL"
                
                schema_lines.append(f"  - {col.name}: {col.data_type} {nullable}{pk_marker}{fk_marker}")
        
        if schema.relationships:
            schema_lines.append("\nRelationships:")
            for rel in schema.relationships:
                schema_lines.append(f"  - {rel['from_table']}.{rel['from_column']} -> {rel['to_table']}.{rel['to_column']}")
        
        return "\n".join(schema_lines)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        # Try to extract JSON from the response
        try:
            # Look for JSON between ```json and ```
            json_match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to parse the entire response as JSON
            return json.loads(response_text)
            
        except json.JSONDecodeError:
            # Fallback: try to extract SQL and explanation manually
            sql_match = re.search(r'SELECT.*?(?=\n\n|\Z)', response_text, re.DOTALL | re.IGNORECASE)
            sql = sql_match.group(0).strip() if sql_match else "-- Failed to parse SQL"
            
            return {
                "sql": sql,
                "explanation": "Generated SQL query from natural language",
                "query_type": "select"
            }
    
    def _create_query_response(self, parsed_result: Dict[str, Any], 
                              natural_language: str, schema: SchemaResponse) -> QueryResponse:
        
        sql = parsed_result.get("sql", "")
        explanation = parsed_result.get("explanation", "")
        query_type = self._detect_query_type(sql)
        
        # Generate safety warnings
        safety_warnings = self._analyze_query_safety(sql, schema)
        
        # Estimate result rows
        estimated_rows = self._estimate_result_rows(sql, schema)
        
        return QueryResponse(
            sql=sql,
            explanation=explanation,
            query_type=query_type,
            estimated_rows=estimated_rows,
            safety_warnings=safety_warnings
        )
    
    def _detect_query_type(self, sql: str) -> QueryType:
        sql_upper = sql.upper().strip()
        
        if sql_upper.startswith("SELECT"):
            return QueryType.SELECT
        elif sql_upper.startswith("INSERT"):
            return QueryType.INSERT
        elif sql_upper.startswith("UPDATE"):
            return QueryType.UPDATE
        elif sql_upper.startswith("DELETE"):
            return QueryType.DELETE
        else:
            return QueryType.UNKNOWN
    
    def _analyze_query_safety(self, sql: str, schema: SchemaResponse) -> List[str]:
        warnings = []
        sql_upper = sql.upper()
        
        # Check for dangerous operations
        if any(keyword in sql_upper for keyword in ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE"]):
            warnings.append("Query contains potentially dangerous operations")
        
        # Check for missing WHERE clause in potentially large tables
        if "WHERE" not in sql_upper:
            large_tables = [t.name for t in schema.tables if (t.row_count or 0) > 10000]
            for table in large_tables:
                if table.upper() in sql_upper:
                    warnings.append(f"Query on large table '{table}' without WHERE clause")
        
        # Check for missing LIMIT
        if "LIMIT" not in sql_upper and "SELECT" in sql_upper:
            warnings.append("Consider adding LIMIT clause for better performance")
        
        return warnings
    
    def _estimate_result_rows(self, sql: str, schema: SchemaResponse) -> int:
        # Simple heuristic for row estimation
        sql_upper = sql.upper()
        
        # If there's a LIMIT clause, use that
        limit_match = re.search(r'LIMIT\s+(\d+)', sql_upper)
        if limit_match:
            return min(int(limit_match.group(1)), 1000)
        
        # If there's a WHERE clause, estimate lower
        if "WHERE" in sql_upper:
            return 100
        
        # For JOINs, estimate based on largest table
        if "JOIN" in sql_upper:
            return 500
        
        # Default estimate
        return 1000

    async def generate_suggested_questions(self, schema_info: dict) -> List[str]:
        """Generate business-friendly questions based on database schema"""
        
        # Extract table information
        tables = []
        for table_name, columns in schema_info.items():
            column_names = [col['name'] for col in columns]
            tables.append(f"Table '{table_name}' with columns: {', '.join(column_names)}")
        
        schema_summary = "\n".join(tables)
        
        prompt = f"""
        Based on this database schema, suggest 8 practical business questions that a non-technical user might want to ask.
        
        Database Schema:
        {schema_summary}
        
        Generate questions that are:
        - Business-focused (not technical)
        - Actionable for decision-making
        - Varied in complexity
        - Natural language (no SQL terms)
        
        Format as a simple list, one question per line.
        Examples:
        - "Who are our top 10 customers by revenue?"
        - "What products are selling best this month?"
        - "Which marketing campaigns drove the most sales?"
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            suggestions = response.choices[0].message.content.strip()
            # Parse into list
            questions = [q.strip('- ').strip() for q in suggestions.split('\n') if q.strip() and not q.strip().startswith('#')]
            return questions[:8]  # Limit to 8 suggestions
            
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return [
                "Who are our top customers?",
                "What are our best-selling products?",
                "How is our revenue trending?",
                "Which users are most active?"
            ] 