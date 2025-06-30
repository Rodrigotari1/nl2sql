"""
AI Agent Service for Database Interactions
Implements MCP-style agents for intelligent database operations
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

from app.services.llm_service import LLMService
from app.services.database_service import DatabaseService


class AgentType(Enum):
    QUERY = "query"
    INSIGHT = "insight" 
    DATA_QUALITY = "data_quality"
    SECURITY = "security"
    OPTIMIZATION = "optimization"


@dataclass
class AgentMessage:
    agent_type: AgentType
    message: str
    priority: str  # "low", "medium", "high", "critical"
    action_required: bool
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class AgentContext:
    database_url: str
    user_id: str
    session_id: str
    query_history: List[Dict[str, Any]]
    schema_info: Dict[str, Any]


class DatabaseAgent:
    """Base class for all database agents"""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.llm_service = LLMService()
        self.db_service = DatabaseService()
        
    async def process(self, context: AgentContext, input_data: Dict[str, Any]) -> List[AgentMessage]:
        """Process input and return agent messages"""
        raise NotImplementedError


class QueryAgent(DatabaseAgent):
    """Handles natural language queries with intelligence"""
    
    def __init__(self):
        super().__init__(AgentType.QUERY)
        
    async def process(self, context: AgentContext, input_data: Dict[str, Any]) -> List[AgentMessage]:
        messages = []
        natural_query = input_data.get("natural_query", "")
        
        # For now, create a simplified SQL generation
        # TODO: Properly integrate with existing LLMService
        try:
            # Simple schema text for prompt
            schema_text = ""
            for table_name, columns in context.schema_info.items():
                col_list = [f"{col['name']} ({col['type']})" for col in columns]
                schema_text += f"Table {table_name}: {', '.join(col_list)}\n"
            
            prompt = f"""
            Generate a SQL query for this natural language request:
            
            Request: {natural_query}
            
            Database Schema:
            {schema_text}
            
            Return only the SQL query.
            """
            
            response = self.llm_service.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            sql = response.choices[0].message.content.strip()
            
            # Create a simple result object
            sql_result = type('SQLResult', (), {
                'sql': sql,
                'explanation': f"Generated SQL query for: {natural_query}"
            })()
            
        except Exception as e:
            # Fallback SQL
            sql_result = type('SQLResult', (), {
                'sql': f"-- Error generating SQL: {str(e)}",
                'explanation': f"Failed to generate SQL for: {natural_query}"
            })()
        
        # Analyze query complexity
        complexity_analysis = await self._analyze_query_complexity(sql_result.sql, context)
        
        # Check for potential issues
        safety_check = await self._check_query_safety(sql_result.sql, context)
        
        # Generate insights about the query
        query_insights = await self._generate_query_insights(sql_result.sql, context)
        
        # Create response messages
        messages.append(AgentMessage(
            agent_type=self.agent_type,
            message=f"Generated SQL query: {sql_result.sql}",
            priority="medium",
            action_required=False,
            metadata={
                "sql": sql_result.sql,
                "explanation": sql_result.explanation,
                "complexity": complexity_analysis,
                "safety_warnings": safety_check,
                "insights": query_insights
            },
            timestamp=datetime.now()
        ))
        
        return messages
    
    async def _analyze_query_complexity(self, sql: str, context: AgentContext) -> Dict[str, Any]:
        """Analyze SQL query complexity and performance implications"""
        
        analysis_prompt = f"""
        Analyze this SQL query for complexity and performance:
        
        SQL: {sql}
        
        Database schema context: {json.dumps(context.schema_info, indent=2)}
        
        Provide analysis on:
        1. Query complexity (1-10 scale)
        2. Expected performance 
        3. Potential bottlenecks
        4. Suggested optimizations
        
        Return as JSON with keys: complexity_score, performance_estimate, bottlenecks, optimizations
        """
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            analysis_text = response.choices[0].message.content
            # Try to parse as JSON, fallback to text
            try:
                return json.loads(analysis_text)
            except:
                return {"analysis": analysis_text}
                
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def _check_query_safety(self, sql: str, context: AgentContext) -> List[str]:
        """Check SQL query for potential safety issues"""
        
        safety_prompt = f"""
        Check this SQL query for safety issues:
        
        SQL: {sql}
        
        Look for:
        1. Potential data exposure risks
        2. Performance issues (missing WHERE clauses, etc.)
        3. Destructive operations
        4. Injection vulnerabilities
        
        Return a list of warnings, or empty list if safe.
        """
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": safety_prompt}],
                max_tokens=300,
                temperature=0.1
            )
            
            warnings_text = response.choices[0].message.content
            # Parse warnings from response
            warnings = [w.strip() for w in warnings_text.split('\n') if w.strip() and not w.strip().startswith('#')]
            return warnings[:5]  # Limit to 5 warnings
            
        except Exception as e:
            return [f"Safety check failed: {str(e)}"]
    
    async def _generate_query_insights(self, sql: str, context: AgentContext) -> List[str]:
        """Generate business insights about the query"""
        
        insights_prompt = f"""
        Generate business insights about this SQL query:
        
        SQL: {sql}
        Schema: {json.dumps(context.schema_info, indent=2)}
        
        Provide 2-3 insights about:
        1. What business questions this answers
        2. Related questions the user might want to ask
        3. Data patterns this might reveal
        
        Keep insights business-focused, not technical.
        """
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": insights_prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            insights_text = response.choices[0].message.content
            insights = [i.strip() for i in insights_text.split('\n') if i.strip() and not i.strip().startswith('#')]
            return insights[:3]  # Limit to 3 insights
            
        except Exception as e:
            return [f"Insight generation failed: {str(e)}"]


class InsightAgent(DatabaseAgent):
    """Proactively finds patterns and insights in data"""
    
    def __init__(self):
        super().__init__(AgentType.INSIGHT)
        
    async def process(self, context: AgentContext, input_data: Dict[str, Any]) -> List[AgentMessage]:
        messages = []
        
        # Analyze recent query patterns
        pattern_insights = await self._analyze_query_patterns(context)
        
        # Check for data anomalies
        anomaly_insights = await self._detect_data_anomalies(context)
        
        # Suggest proactive questions
        suggested_questions = await self._suggest_proactive_questions(context)
        
        if pattern_insights:
            messages.append(AgentMessage(
                agent_type=self.agent_type,
                message="I noticed interesting patterns in your recent queries",
                priority="low",
                action_required=False,
                metadata={"insights": pattern_insights},
                timestamp=datetime.now()
            ))
        
        if anomaly_insights:
            messages.append(AgentMessage(
                agent_type=self.agent_type,
                message="I detected some unusual patterns in your data",
                priority="medium",
                action_required=True,
                metadata={"anomalies": anomaly_insights},
                timestamp=datetime.now()
            ))
        
        if suggested_questions:
            messages.append(AgentMessage(
                agent_type=self.agent_type,
                message="Here are some questions you might want to explore",
                priority="low",
                action_required=False,
                metadata={"suggestions": suggested_questions},
                timestamp=datetime.now()
            ))
        
        return messages
    
    async def _analyze_query_patterns(self, context: AgentContext) -> List[str]:
        """Analyze user's query patterns for insights"""
        if not context.query_history:
            return []
        
        # Simple pattern analysis - could be much more sophisticated
        recent_queries = context.query_history[-10:]  # Last 10 queries
        
        patterns = []
        # Look for common themes
        if len([q for q in recent_queries if 'customer' in q.get('query', '').lower()]) >= 3:
            patterns.append("You've been focusing on customer analysis lately")
        
        if len([q for q in recent_queries if 'revenue' in q.get('query', '').lower()]) >= 2:
            patterns.append("Revenue analysis seems to be a key interest")
        
        return patterns
    
    async def _detect_data_anomalies(self, context: AgentContext) -> List[str]:
        """Detect potential data anomalies that might need attention"""
        # This would typically involve running diagnostic queries
        # For now, return placeholder insights
        return []
    
    async def _suggest_proactive_questions(self, context: AgentContext) -> List[str]:
        """Suggest questions based on schema and recent activity"""
        
        suggestion_prompt = f"""
        Based on this database schema and recent query activity, suggest 3 proactive business questions:
        
        Schema: {json.dumps(context.schema_info, indent=2)}
        Recent queries: {json.dumps(context.query_history[-5:], indent=2)}
        
        Suggest questions that:
        1. Build on recent analysis
        2. Explore related business areas
        3. Identify potential opportunities or issues
        
        Format as simple questions, one per line.
        """
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": suggestion_prompt}],
                max_tokens=300,
                temperature=0.8
            )
            
            suggestions_text = response.choices[0].message.content
            suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip() and '?' in s]
            return suggestions[:3]
            
        except Exception as e:
            return []


class AgentOrchestrator:
    """Orchestrates multiple agents working together"""
    
    def __init__(self):
        self.agents = {
            AgentType.QUERY: QueryAgent(),
            AgentType.INSIGHT: InsightAgent(),
            # Add more agents as needed
        }
        
    async def process_user_input(self, context: AgentContext, user_input: str) -> Dict[str, Any]:
        """Process user input through relevant agents"""
        
        # Determine which agents should handle this input
        active_agents = await self._determine_active_agents(user_input, context)
        
        # Process through each active agent
        all_messages = []
        for agent_type in active_agents:
            agent = self.agents.get(agent_type)
            if agent:
                try:
                    messages = await agent.process(context, {"natural_query": user_input})
                    all_messages.extend(messages)
                except Exception as e:
                    # Log error but don't break the flow
                    print(f"Agent {agent_type} failed: {e}")
        
        # Also run background agents for proactive insights
        background_messages = await self._run_background_agents(context)
        all_messages.extend(background_messages)
        
        return {
            "messages": all_messages,
            "primary_response": self._extract_primary_response(all_messages),
            "insights": self._extract_insights(all_messages),
            "actions": self._extract_actions(all_messages)
        }
    
    async def _determine_active_agents(self, user_input: str, context: AgentContext) -> List[AgentType]:
        """Determine which agents should process this input"""
        active_agents = [AgentType.QUERY]  # Always run query agent
        
        # Add insight agent if user seems to want analysis
        if any(word in user_input.lower() for word in ['trend', 'pattern', 'insight', 'analysis']):
            active_agents.append(AgentType.INSIGHT)
        
        return active_agents
    
    async def _run_background_agents(self, context: AgentContext) -> List[AgentMessage]:
        """Run agents that provide proactive insights"""
        messages = []
        
        # Run insight agent periodically
        insight_agent = self.agents.get(AgentType.INSIGHT)
        if insight_agent:
            try:
                insight_messages = await insight_agent.process(context, {})
                messages.extend(insight_messages)
            except Exception as e:
                print(f"Background insight agent failed: {e}")
        
        return messages
    
    def _extract_primary_response(self, messages: List[AgentMessage]) -> Optional[Dict[str, Any]]:
        """Extract the primary response (usually from query agent)"""
        for message in messages:
            if message.agent_type == AgentType.QUERY:
                return {
                    "sql": message.metadata.get("sql"),
                    "explanation": message.metadata.get("explanation"),
                    "complexity": message.metadata.get("complexity"),
                    "safety_warnings": message.metadata.get("safety_warnings")
                }
        return None
    
    def _extract_insights(self, messages: List[AgentMessage]) -> List[str]:
        """Extract insights from all agent messages"""
        insights = []
        for message in messages:
            if message.agent_type == AgentType.INSIGHT:
                insights.extend(message.metadata.get("insights", []))
                insights.extend(message.metadata.get("suggestions", []))
            elif message.agent_type == AgentType.QUERY:
                insights.extend(message.metadata.get("insights", []))
        return insights
    
    def _extract_actions(self, messages: List[AgentMessage]) -> List[Dict[str, Any]]:
        """Extract actions that require user attention"""
        actions = []
        for message in messages:
            if message.action_required:
                actions.append({
                    "agent": message.agent_type.value,
                    "message": message.message,
                    "priority": message.priority,
                    "metadata": message.metadata
                })
        return actions 