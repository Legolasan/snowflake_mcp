# CLAUDE.md

This file provides guidance to Claude Code when working with the Snowflake MCP Server repository.

## Repository Overview

This is a **Model Context Protocol (MCP) server** that enables Claude to interact with Snowflake data warehouses. It's a learning project demonstrating how to build custom MCP integrations for data engineering workflows.

## Project Structure

```
snowflake-mcp/
├── server.py              # Main MCP server implementation
├── test_connection.py     # Connection testing utility
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── README.md             # User-facing documentation
├── QUICKSTART.md         # 5-minute setup guide
└── CLAUDE.md            # This file (Claude Code instructions)
```

## Key Components

### server.py
- **SnowflakeMCPServer class**: Main server implementation
- **4 MCP Tools**:
  - `query_snowflake`: Execute SQL queries
  - `list_tables`: List tables in schema
  - `describe_table`: Get table structure
  - `check_table_freshness`: Monitor data recency
- Uses `snowflake-connector-python` for database connectivity
- Implements MCP protocol via `mcp` SDK

### Architecture Patterns
- **Connection pooling**: Single connection reused across tool calls
- **Environment-based config**: Credentials from environment variables
- **Error handling**: Try-catch blocks with user-friendly error messages
- **Security**: Never commits credentials (.gitignore protects .env)

## Working with This Repository

### Adding New Tools

When users request new MCP tools, follow this pattern:

1. **Add tool function** in `SnowflakeMCPServer._setup_tools()`:
```python
@self.app.call_tool()
async def my_new_tool(arguments: dict[str, Any]) -> list[TextContent]:
    """Tool description"""
    param = arguments.get("param_name")

    try:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("YOUR SQL")
        results = cursor.fetchall()

        return [TextContent(type="text", text=formatted_output)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

2. **Add tool definition** to `tools` property:
```python
Tool(
    name="my_new_tool",
    description="What this tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param_name": {
                "type": "string",
                "description": "What this parameter is for"
            }
        },
        "required": ["param_name"]
    }
)
```

3. **Update README.md** with the new tool documentation

### Common Enhancement Requests

**Data Quality Tools:**
- Null value checks
- Duplicate detection
- Schema validation
- Data profiling

**Monitoring Tools:**
- Query performance metrics
- Warehouse utilization
- Credit consumption
- Task run history

**ETL/Pipeline Tools:**
- Pipe status checking
- Stream lag monitoring
- Task dependency visualization
- Data freshness dashboards

### Testing Changes

1. **Test connection** first:
```bash
python test_connection.py
```

2. **Test MCP server** manually:
```bash
python server.py
# Should start stdio server (will wait for input)
```

3. **Integration test** with Claude Code:
- Add to MCP config
- Restart Claude Code
- Try using the tools in conversation

### Code Style Guidelines

- Use **async/await** for all MCP tool functions
- Include **docstrings** with parameter descriptions
- Format **output as readable tables** where possible
- Handle **errors gracefully** with helpful messages
- Use **type hints** for function parameters
- Keep **SQL queries readable** (use multiline strings)

### Security Considerations

- ✅ **Never commit** `.env` file
- ✅ **Use read-only** Snowflake credentials when possible
- ✅ **Validate SQL inputs** to prevent injection (though MCP is local)
- ✅ **Add LIMIT clauses** to prevent overwhelming results
- ✅ **Document** what permissions are needed

### Dependencies

- `mcp>=0.1.0` - MCP SDK for building servers
- `snowflake-connector-python>=3.0.0` - Snowflake database driver
- `python-dotenv>=1.0.0` - Environment variable management

### Common Issues & Solutions

**Issue: "Connection timeout"**
- Check network connectivity
- Verify warehouse is running
- Confirm account identifier format

**Issue: "Tool not responding"**
- Check MCP server logs
- Verify tool is registered in both function and tools list
- Ensure function signature matches MCP requirements

**Issue: "Too many results"**
- Add LIMIT to queries
- Implement pagination
- Add result size warnings

## User Assistance Guidelines

When users ask for help with this MCP server:

1. **Setup Issues**: Guide them through QUICKSTART.md steps
2. **New Features**: Show how to add new tools with examples
3. **Debugging**: Check credentials, permissions, and connectivity
4. **Extensions**: Suggest relevant tools based on their workflow
5. **Best Practices**: Share security and performance tips

## Example User Workflows

### Daily Data Monitoring
User wants automated checks for:
- Table freshness
- Row count anomalies
- Schema changes
- Pipeline failures

→ Guide them to create composite tools that run multiple checks

### Ad-Hoc Analysis
User wants to explore data without logging into Snowflake:
- Natural language to SQL translation
- Iterative query refinement
- Result visualization suggestions

→ Show how `query_snowflake` enables this workflow

### ETL Debugging
User troubleshooting pipeline issues:
- Check source data
- Validate transformations
- Compare row counts
- Inspect error tables

→ Demonstrate multi-step debugging with tool chaining

## Contributing Ideas

If users want to enhance this project, suggest:

1. **More tools** (cost monitoring, query optimization)
2. **Caching layer** (reduce Snowflake queries)
3. **Result formatting** (CSV, JSON exports)
4. **Query templates** (common patterns as tools)
5. **Multi-warehouse support** (dynamic warehouse switching)
6. **Async query execution** (for long-running queries)
7. **Resource management** (auto-suspend warehouses)

---

## Quick Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Set up credentials
cp .env.example .env && nano .env

# Test connection
python test_connection.py

# Run MCP server (for manual testing)
python server.py

# Add to Claude Code MCP config
# Edit: ~/.config/claude-code/mcp.json
```

---

This is a **learning project** - encourage experimentation and customization! 🎿
