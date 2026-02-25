from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

class LLMGraphNavigator:
    """
    Translates raw natural language queries from investigators into valid Neo4j Cypher queries.
    Allows non-technical analysts to interrogate the graph using simple English.
    """
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        
        # Define the exact graph schema for the LLM context so it writes accurate Cypher mappings
        self.schema_context = """
        Graph Schema nodes:
        - (P:Person {name, dob, address, synthetic_identity_score})
        - (C:Company {registration_number, name, country})
        - (A:Account {bank_name, sort_code, account_number})
        - (T:Transaction {amount, currency, timestamp})
        - (FCA:Complaint {reference_number, case_status, severity})
        
        Relationships:
        - (P)-[:DIRECTOR_OF]->(C)
        - (P)-[:OWNS_ACCOUNT]->(A)
        - (C)-[:OWNS_ACCOUNT]->(A)
        - (A)-[:SENT_FUNDS_TO]->(A) via (T)
        - (FCA)-[:FILED_AGAINST]->(C)
        - (FCA)-[:FILED_BY]->(P)
        """
        
    async def text_to_cypher(self, user_question: str) -> Dict[str, Any]:
        """
        Transforms "Show me all companies linked to John Doe that filed for address changes"
        into the explicit Neo4j query language (Cypher).
        """
        print(f"[Graph Navigator] Translating investigator query: '{user_question}'")
        
        template = PromptTemplate.from_template(
            "You are an expert Neo4j graph data scientist investigating synthetic identity fraud.\n"
            "Here is the database schema:\n{schema}\n\n"
            "Translate this investigator's request into a highly optimized Cypher query: '{question}'.\n"
            "Return ONLY the raw Cypher query string with no markdown blocks or surrounding text."
        )
        
        chain = template | self.llm
        
        try:
            response = await chain.ainvoke({
                "schema": self.schema_context,
                "question": user_question
            })
            cypher_query = response.content.strip().replace("```cypher", "").replace("```", "")
            
            return {
                "status": "success",
                "original_question": user_question,
                "cypher_query": cypher_query,
                "mock_execution_time_ms": 14
            }
        except Exception as e:
            return {
                "status": "error",
                "cypher_query": "MATCH (n) RETURN n LIMIT 1",
                "error": str(e)
            }
