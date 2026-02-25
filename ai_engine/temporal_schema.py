class TemporalGraphModel:
    """
    Introduces temporal graph modeling to track WHEN edges form.
    Allows the Neo4j fraud system to discover synchronized account-creation rings
    over specific timeframes (e.g., shell companies created over the same weekend).
    """

    def generate_temporal_cypher_queries(self) -> dict[str, str]:
        """
        Returns specialized Cypher queries that focus exclusively on the timing (delta-T)
        of relationships, identifying coordinated attacks.
        """
        
        queries = {
            "burst_account_creation": """
            // Finds clusters of accounts opened at the identical IP within 48 hours
            MATCH (ip:IPAddress)<-[login1:LOGGED_IN_FROM]-(a1:Account)
            MATCH (ip)<-[login2:LOGGED_IN_FROM]-(a2:Account)
            WHERE a1 <> a2
              AND duration.inDays(login1.timestamp, login2.timestamp).days < 2
            WITH ip, count(DISTINCT a1) as num_accounts
            WHERE num_accounts > 5
            RETURN ip.address, num_accounts
            ORDER BY num_accounts DESC
            """,
            
            "rapid_funds_dispersal": """
            // Identifies 'smurfing' where a large inbound deposit is instantly split and transferred out
            MATCH (origin:Account)-[inbound:SENT_FUNDS_TO]->(hub:Account)-[outbound:SENT_FUNDS_TO]->(destination:Account)
            WHERE inbound.amount > 100000 
              AND outbound.amount < 10000
              AND duration.inMinutes(inbound.timestamp, outbound.timestamp).minutes < 30
            RETURN hub.account_number, count(outbound) as split_transfers, sum(outbound.amount) as total_smurfed
            """
        }
        
        return queries
