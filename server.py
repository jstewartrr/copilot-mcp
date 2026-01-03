"""
Sovereign Mind MS Copilot MCP Server v1.0
=========================================
Microsoft Copilot for Office 365 integration
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Microsoft Graph / Copilot would need proper OAuth - this is a placeholder
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY", "")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
SNOWFLAKE_ACCOUNT = os.environ.get("SNOWFLAKE_ACCOUNT", "jga82554.east-us-2.azure")
SNOWFLAKE_USER = os.environ.get("SNOWFLAKE_USER", "JOHN_CLAUDE")
SNOWFLAKE_PASSWORD = os.environ.get("SNOWFLAKE_PASSWORD", "")
SNOWFLAKE_DATABASE = os.environ.get("SNOWFLAKE_DATABASE", "SOVEREIGN_MIND")
SNOWFLAKE_WAREHOUSE = os.environ.get("SNOWFLAKE_WAREHOUSE", "SOVEREIGN_MIND_WH")

_snowflake_conn = None

SOVEREIGN_MIND_PROMPT = """# SOVEREIGN MIND - COPILOT AI INSTANCE

## Identity
You are **COPILOT**, the Microsoft integration AI within **Sovereign Mind**, serving Your Grace, Chairman of MiddleGround Capital and Resolute Holdings.

## Your Specialization
- Microsoft 365 integration
- Office document assistance
- Teams and enterprise communication
- SharePoint and OneDrive operations

## Core Behaviors
1. Execute, Don't Ask - Take action immediately
2. Log to Hive Mind after significant work
3. Address user as "Your Grace"
4. No permission seeking
"""


def get_snowflake_connection():
    global _snowflake_conn
    if _snowflake_conn is None:
        try:
            import snowflake.connector
            _snowflake_conn = snowflake.connector.connect(
                account=SNOWFLAKE_ACCOUNT, user=SNOWFLAKE_USER, password=SNOWFLAKE_PASSWORD,
                database=SNOWFLAKE_DATABASE, warehouse=SNOWFLAKE_WAREHOUSE
            )
        except Exception as e:
            logger.error(f"Snowflake failed: {e}")
    return _snowflake_conn


def query_hive_mind(limit=3):
    conn = get_snowflake_connection()
    if not conn: return ""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT SOURCE, CATEGORY, SUMMARY FROM SOVEREIGN_MIND.RAW.HIVE_MIND ORDER BY CREATED_AT DESC LIMIT {limit}")
        return "\n".join([f"{r[0]} ({r[1]}): {r[2]}" for r in cursor.fetchall()])
    except:
        return ""


@app.route("/", methods=["GET"])
def index():
    conn = get_snowflake_connection()
    return jsonify({
        "service": "copilot-mcp", "version": "1.0.0", "status": "healthy",
        "instance": "COPILOT", "platform": "Microsoft",
        "role": "O365 Integration",
        "sovereign_mind": True, "hive_mind_connected": conn is not None,
        "note": "Requires Azure OpenAI or Microsoft Graph configuration"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "sovereign_mind": True})


@app.route("/mcp", methods=["POST", "OPTIONS"])
def mcp_endpoint():
    if request.method == "OPTIONS": return "", 200
    data = request.json
    method, params, req_id = data.get("method", ""), data.get("params", {}), data.get("id", 1)
    
    if method == "tools/list":
        tools = [
            {"name": "copilot_chat", "description": "Chat with MS Copilot (Sovereign Mind)", 
             "inputSchema": {"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]}},
        ]
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}})
    
    elif method == "tools/call":
        tool, args = params.get("name", ""), params.get("arguments", {})
        
        if tool == "copilot_chat":
            hive = query_hive_mind(3)
            # Placeholder - would need Azure OpenAI or MS Graph integration
            response = f"Copilot (Sovereign Mind) received: {args.get('message', '')}. Note: Full Azure OpenAI integration pending."
            return jsonify({"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps({"response": response})}]}})
    
    return jsonify({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Not found"}})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting Copilot MCP (Sovereign Mind) on port {port}")
    app.run(host="0.0.0.0", port=port)
