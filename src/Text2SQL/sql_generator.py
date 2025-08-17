import anthropic
import os
from typing import Dict, Any

class SQLGenerator:
    def __init__(self, api_key: str = None):
        """
        Initialize SQL Generator with Anthropic API key
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
    
    def generate_sql(self, natural_language_query: str, table_schema: str) -> Dict[str, Any]:
        """
        Generate SQL query from natural language using Anthropic Claude
        """
        try:
            # Validate inputs
            if not natural_language_query or not natural_language_query.strip():
                return {
                    "sql": "SELECT 1 as no_query",
                    "description": "ບໍ່ມີຄໍາຖາມໃຫ້ສ້າງ SQL"
                }
            
            if not table_schema or not table_schema.strip():
                return {
                    "sql": "SELECT 1 as no_schema",
                    "description": "ບໍ່ມີຂໍ້ມູນ Schema ຖານຂໍ້ມູນ"
                }
            
            system_prompt = f"""You are an expert SQL developer for MariaDB. Convert natural language to SQL.

Database Schema:
{table_schema}

Rules:
1. Generate only valid MariaDB SQL
2. Use appropriate JOINs when needed
3. Include proper WHERE clauses
4. Use meaningful aliases
5. Return description in Lao language
6. Be careful of column data types
7. Use proper date functions for date columns
8. Handle NULL values appropriately

IMPORTANT: Return ONLY the JSON format below, nothing else:
{{
    "sql": "YOUR_SQL_QUERY_HERE",
    "description": "ຄໍາອະທິບາຍເປັນພາສາລາວວ່າຄໍາສັ່ງ SQL ນີ້ເຮັດຫຍັງ"

}}

Do not include any additional text, explanations, or markdown formatting. Just the JSON."""
            
            print(f"Debug: Sending request to Claude with query: {natural_language_query[:100]}...")
            
            response = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=1500,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": natural_language_query
                    }
                ]
            )
            
            content = response.content[0].text
            print(f"Debug: Claude response: {content[:200]}...")
            
            # Try to extract JSON from response
            try:
                import json
                # Look for JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = content[start_idx:end_idx]
                    print(f"Debug: Extracted JSON: {json_str}")
                    result = json.loads(json_str)
                    
                    # Validate the extracted SQL - ensure it's clean
                    if "sql" in result and result["sql"]:
                        # Clean the SQL by removing any JSON artifacts
                        sql = result["sql"].strip()
                        # Remove any quotes or JSON formatting that might have leaked
                        if sql.startswith('"') and sql.endswith('"'):
                            sql = sql[1:-1]
                        # Remove any escaped quotes
                        sql = sql.replace('\\"', '"')
                        
                        print(f"Debug: Cleaned SQL: {sql[:100]}...")
                        
                        return {
                            "sql": sql,
                            "description": result.get("description", "ບໍ່ມີຄໍາອະທິບາຍ")
                        }
                    else:
                        print("Debug: No SQL found in JSON result")
                        return self._extract_sql_and_description(content)
                else:
                    print("Debug: No JSON found, using fallback extraction")
                    return self._extract_sql_and_description(content)
            except json.JSONDecodeError as json_err:
                print(f"Debug: JSON decode error: {json_err}")
                return self._extract_sql_and_description(content)
                
        except Exception as e:
            print(f"Debug: Exception in generate_sql: {str(e)}")
            print(f"Debug: Exception type: {type(e)}")
            return {
                "sql": f"SELECT 1 as error_{type(e).__name__}",
                "description": f"ຂໍ້ຜິດພາດໃນການສ້າງ SQL: {str(e)}"
            }
    
    def _extract_sql_and_description(self, content: str) -> Dict[str, str]:
        """
        Extract SQL and description from Claude's response when JSON parsing fails
        """
        print(f"Debug: Extracting from content: {content[:300]}...")
        
        lines = content.split('\n')
        sql_lines = []
        description_lines = []
        
        in_sql = False
        in_description = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for SQL indicators
            if any(keyword in line.upper() for keyword in ['SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT']):
                in_sql = True
                in_description = False
                # Clean the line of any JSON artifacts
                clean_line = line
                if clean_line.startswith('"') and clean_line.endswith('"'):
                    clean_line = clean_line[1:-1]
                clean_line = clean_line.replace('\\"', '"')
                sql_lines.append(clean_line)
            elif line.startswith('```'):
                if in_sql:
                    in_sql = False
                    in_description = True
                continue
            elif in_sql:
                # Clean the line of any JSON artifacts
                clean_line = line
                if clean_line.startswith('"') and clean_line.endswith('"'):
                    clean_line = clean_line[1:-1]
                clean_line = clean_line.replace('\\"', '"')
                sql_lines.append(clean_line)
            elif in_description or not in_sql:
                # Skip JSON artifacts in description
                if not any(json_artifact in line for json_artifact in ['"sql":', '"description":', '{', '}']):
                    description_lines.append(line)
        
        sql = ' '.join(sql_lines) if sql_lines else "SELECT 1 as no_sql_generated"
        print(f"Debug: Extracted SQL: {sql}")
        
        # Default Lao description if none provided
        if description_lines:
            description = ' '.join(description_lines)
        else:
            description = "ຄໍາສັ່ງ SQL ທີ່ສ້າງຈາກຄໍາຖາມຂອງຜູ້ໃຊ້"
        
        print(f"Debug: Extracted description: {description[:100]}...")
        
        return {
            "sql": sql,
            "description": description
        } 