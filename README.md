# Snowflake MCP Server 🎿

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-enabled-green.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A Model Context Protocol (MCP) server that enables Claude to interact with your Snowflake data warehouse through natural language.

## 🌟 What is this?

Instead of logging into Snowflake UI and writing SQL manually, simply ask Claude in natural language and let it query your data warehouse for you!

This MCP server gives Claude the ability to:
- ✅ Execute SQL queries on Snowflake
- ✅ List tables in your schemas
- ✅ Describe table structures
- ✅ Check data freshness (when tables were last updated)

### How It's Different

| Traditional Approach | With Snowflake MCP |
|---------------------|-------------------|
| Open Snowflake UI → Write SQL → Run → Copy results | Ask Claude → Get insights instantly |
| Context switching between tools | Everything in one conversation |
| Remember exact table/column names | Claude helps you discover schema |
| Repetitive daily checks | Automate monitoring workflows |

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Available Tools](#-available-tools)
- [Usage Examples](#-usage-examples)
- [How It Works](#-how-it-works)
- [Security](#-security)
- [Extending](#-extending-this-server)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-frequently-asked-questions)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide!

```bash
# 1. Clone the repo
git clone https://github.com/Legolasan/snowflake_mcp.git
cd snowflake_mcp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env
nano .env  # Add your Snowflake credentials

# 4. Test connection
python test_connection.py

# 5. Add to Claude Code (see Configuration section)
```

## 📦 Installation

### Prerequisites

- **Python 3.8 or higher**
- **Snowflake account** with access credentials
- **Claude Code CLI** (for MCP integration) - [Get it here](https://claude.ai/code)

**Note:** You do NOT need a separate Claude API key! The MCP server runs locally and only requires Snowflake credentials. See [FAQ](#-frequently-asked-questions) for details.

### Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `mcp` - Model Context Protocol SDK
- `snowflake-connector-python` - Snowflake database driver
- `python-dotenv` - Environment variable management

## ⚙️ Configuration

### 1. Snowflake Credentials

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your Snowflake credentials:

```env
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=abc12345.us-east-1
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=PROD_DB
SNOWFLAKE_SCHEMA=PUBLIC
```

**Finding your account identifier:**
- Your Snowflake URL: `https://abc12345.us-east-1.snowflakecomputing.com`
- Your account ID: `abc12345.us-east-1`

⚠️ **Security**: Never commit `.env` to git! It's protected by `.gitignore`.

### 2. Claude Code MCP Configuration

Add this to your Claude Code MCP settings:

**File:** `~/.config/claude-code/mcp.json`

**Option A: Using .env file (Recommended)**

```json
{
  "mcpServers": {
    "snowflake": {
      "command": "bash",
      "args": [
        "-c",
        "source /path/to/snowflake_mcp/.env && python /path/to/snowflake_mcp/server.py"
      ]
    }
  }
}
```

**Option B: Direct environment variables**

```json
{
  "mcpServers": {
    "snowflake": {
      "command": "python",
      "args": ["/path/to/snowflake_mcp/server.py"],
      "env": {
        "SNOWFLAKE_USER": "your_username",
        "SNOWFLAKE_PASSWORD": "your_password",
        "SNOWFLAKE_ACCOUNT": "your_account",
        "SNOWFLAKE_WAREHOUSE": "COMPUTE_WH",
        "SNOWFLAKE_DATABASE": "your_database",
        "SNOWFLAKE_SCHEMA": "PUBLIC"
      }
    }
  }
}
```

### 3. Restart Claude Code

After updating the MCP configuration, restart Claude Code to load the server.

## 🛠️ Available Tools

### 1. `query_snowflake`

Execute any SQL query on Snowflake and get formatted results.

**Parameters:**
- `sql` (required): SQL query to execute
- `limit` (optional): Max rows to return (default: 100)

**Example prompts:**
- "Show me the top 10 customers by revenue"
- "How many orders were placed yesterday?"
- "What's the average order value this month?"

### 2. `list_tables`

List all tables in a schema with row counts.

**Parameters:**
- `schema` (optional): Schema name (defaults to configured schema)

**Example prompts:**
- "What tables are available?"
- "List all tables in the ANALYTICS schema"

### 3. `describe_table`

Get detailed structure of a table (columns, types, constraints).

**Parameters:**
- `table_name` (required): Name of the table

**Example prompts:**
- "Describe the ORDERS table"
- "What columns are in the CUSTOMERS table?"
- "Show me the schema for user_events"

### 4. `check_table_freshness`

Monitor when data was last updated (requires timestamp column).

**Parameters:**
- `table_name` (required): Table to check
- `timestamp_column` (optional): Timestamp column name (default: UPDATED_AT)

**Example prompts:**
- "When was the ORDERS table last updated?"
- "Is my ETL pipeline running? Check staging table freshness"
- "Show me data recency for all my tables"

## 💡 Usage Examples

### Basic Queries

```
You: "What tables do we have in Snowflake?"
Claude: [uses list_tables]
        "You have 12 tables including ORDERS, CUSTOMERS, PRODUCTS..."

You: "Show me the structure of the orders table"
Claude: [uses describe_table]
        "The ORDERS table has 8 columns: ORDER_ID (NUMBER),
         CUSTOMER_ID (NUMBER), ORDER_DATE (TIMESTAMP)..."

You: "Get the top 5 orders from today"
Claude: [uses query_snowflake with SQL]
        "Here are the top 5 orders from today..."
```

### Data Monitoring

```
You: "Is my data fresh? Check when orders table was last updated"
Claude: [uses check_table_freshness]
        "Orders table was last updated 2 hours ago with 1,234 total rows"

You: "Are there any gaps in yesterday's data?"
Claude: [writes and executes SQL to check]
        "I found a 3-hour gap between 2am-5am..."
```

### Multi-Step Analysis

```
You: "Compare this week's sales to last week"
Claude: [executes multiple queries]
        "This week: $125K (up 15% from last week's $108K)..."

You: "Show me the breakdown by category"
Claude: [refines query based on context]
        "Electronics: +25%, Clothing: +10%, Home: -5%..."
```

## 🔍 How It Works

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   You ask   │────────▶│  Claude Code │────────▶│ MCP Server  │
│  Claude in  │         │  decides      │         │  executes   │
│ natural     │         │  which tool   │         │  on         │
│ language    │         │  to use       │         │  Snowflake  │
└─────────────┘         └──────────────┘         └─────────────┘
                                                         │
                                                         ▼
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Claude     │◀────────│  Results     │◀────────│  Snowflake  │
│  analyzes & │         │  returned    │         │  Database   │
│  explains   │         │              │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
```

1. **You ask** Claude a question about your data
2. **Claude decides** which tool to use (or writes custom SQL)
3. **MCP server** executes the query on Snowflake
4. **Results** are returned to Claude
5. **Claude analyzes** and responds with insights!

## 🔒 Security

### Best Practices

- ✅ **Use read-only credentials** for the MCP server
- ✅ **Never commit** `.env` file to version control
- ✅ **Use dedicated warehouse** for MCP queries
- ✅ **Set resource monitors** to control costs
- ✅ **Review queries** before execution (Claude shows them to you)
- ✅ **Limit result sizes** (default 100 rows, configurable)

### Snowflake Permissions

Recommended minimal permissions:

```sql
-- Create a read-only role for MCP
CREATE ROLE MCP_READONLY;

-- Grant database and schema access
GRANT USAGE ON DATABASE PROD_DB TO ROLE MCP_READONLY;
GRANT USAGE ON SCHEMA PROD_DB.PUBLIC TO ROLE MCP_READONLY;

-- Grant SELECT on all tables
GRANT SELECT ON ALL TABLES IN SCHEMA PROD_DB.PUBLIC TO ROLE MCP_READONLY;

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE MCP_READONLY;

-- Assign role to user
GRANT ROLE MCP_READONLY TO USER mcp_user;
```

## 🚀 Extending This Server

Want to add more capabilities? Here's how:

### Adding a New Tool

1. **Add the tool function** in `server.py`:

```python
@self.app.call_tool()
async def check_data_quality(arguments: dict[str, Any]) -> list[TextContent]:
    """Check for nulls, duplicates, and anomalies"""
    table_name = arguments.get("table_name")

    # Your implementation here
    conn = self._get_connection()
    cursor = conn.cursor()
    # ... run quality checks

    return [TextContent(type="text", text=results)]
```

2. **Register the tool** in the `tools` property:

```python
Tool(
    name="check_data_quality",
    description="Check table for data quality issues",
    inputSchema={
        "type": "object",
        "properties": {
            "table_name": {"type": "string", "description": "Table to check"}
        },
        "required": ["table_name"]
    }
)
```

3. **Restart the MCP server** and Claude will have access to it!

### Ideas for New Tools

- 📊 **Data Quality Checks** - Null counts, duplicates, outliers
- 💰 **Cost Monitoring** - Query costs, warehouse usage, credit burn
- ⚡ **Performance Analysis** - Slow queries, table statistics
- 🔄 **Pipeline Monitoring** - Stream lag, pipe status, task runs
- 📈 **Automated Reports** - Daily summaries, trend analysis
- 🔍 **Schema Drift Detection** - Track table changes over time

## 🐛 Troubleshooting

### Connection Issues

**"Connection failed" or "Authentication error"**
- ✅ Verify credentials in `.env` file
- ✅ Check Snowflake account identifier format
- ✅ Ensure warehouse is running
- ✅ Test with: `python test_connection.py`

**"Network timeout"**
- ✅ Check firewall/VPN settings
- ✅ Verify Snowflake account is accessible
- ✅ Test connection from command line

### MCP Server Issues

**"Tool not found" or "Server not responding"**
- ✅ Restart Claude Code after config changes
- ✅ Check MCP config file syntax (valid JSON)
- ✅ Verify file paths in MCP config are correct
- ✅ Check Claude Code logs for errors

**"Permission denied"**
- ✅ Verify Snowflake user has SELECT permissions
- ✅ Check database and schema names are correct
- ✅ Ensure warehouse has USAGE granted

### Python/Dependency Issues

**"ModuleNotFoundError: No module named 'mcp'"**
- ✅ Run: `pip install -r requirements.txt`
- ✅ Use correct Python environment

**"Snowflake connector errors"**
- ✅ Update connector: `pip install --upgrade snowflake-connector-python`
- ✅ Check Python version (3.8+ required)

## ❓ Frequently Asked Questions

### Do I need a Claude API key?

**No!** The MCP server itself does NOT require a Claude API key. Here's what you actually need:

#### What You Need:
1. **Claude Code CLI** - Authenticate once with `claude auth login`
2. **Snowflake credentials** - In your `.env` file
3. **That's it!**

#### How It Works:
```
┌─────────────────────┐
│   Claude Code CLI   │ ← Uses your Claude subscription
└──────────┬──────────┘
           │ Local communication (stdio)
┌──────────▼──────────┐
│  MCP Server         │ ← NO API key needed!
│  (server.py)        │    Just queries Snowflake
└──────────┬──────────┘
           │ Snowflake credentials only
┌──────────▼──────────┐
│   Snowflake DB      │
└─────────────────────┘
```

The MCP server is just a **local tool provider** that extends Claude Code's capabilities. It runs on your machine and only talks to Snowflake.

#### Cost Breakdown:
- ✅ **Claude Code usage**: Included in your Claude subscription
- ✅ **MCP Server**: Free (runs locally, no external API calls)
- ✅ **Snowflake queries**: Your normal Snowflake compute costs apply

### Can I use this without Claude Code?

The MCP server is specifically designed to work with MCP-compatible clients like Claude Code. However, you could:
- Use it with other MCP clients (if they support MCP protocol)
- Adapt the code to work as a standalone CLI tool
- Use the Snowflake query functions directly in your own Python scripts

### Is my data secure?

Yes! Here's why:
- ✅ **Runs locally** - MCP server runs on your machine
- ✅ **Direct connection** - Queries go straight to Snowflake
- ✅ **No third-party servers** - Your data never leaves your network
- ✅ **Credentials stay local** - `.env` file is never uploaded

Your Snowflake credentials and query results stay between your machine and Snowflake. Claude Code sees query results only when you ask it to analyze them.

### What's the difference between this and Snowflake's UI?

| Feature | Snowflake UI | Snowflake MCP |
|---------|--------------|---------------|
| Query execution | ✅ Manual | ✅ AI-assisted |
| Natural language | ❌ No | ✅ Yes |
| Multi-step analysis | Manual | ✅ Automated |
| Context across queries | ❌ No | ✅ Yes |
| Schema discovery | Manual search | ✅ Ask Claude |
| Daily monitoring | Repetitive | ✅ Can automate |
| Cost | Free | Free + Snowflake compute |

### Does this work with other data warehouses?

The current implementation is Snowflake-specific, but the pattern can be adapted for:
- PostgreSQL
- MySQL
- BigQuery
- Databricks
- Redshift
- Any database with a Python connector!

Check the [Contributing](#-contributing) section if you want to add support for other databases.

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

- 🐛 **Report bugs** - Open an issue with reproduction steps
- 💡 **Suggest features** - Share ideas for new tools
- 📝 **Improve docs** - Fix typos, add examples
- 🔧 **Submit PRs** - Add new tools or fix issues

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/snowflake_mcp.git
cd snowflake_mcp

# Install dev dependencies
pip install -r requirements.txt

# Create feature branch
git checkout -b feature/my-new-tool

# Make changes and test
python test_connection.py

# Submit PR!
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io)
- Uses [Snowflake Python Connector](https://docs.snowflake.com/en/user-guide/python-connector)
- Inspired by the power of AI-assisted data analysis

## 📚 Learn More

- [MCP Documentation](https://modelcontextprotocol.io)
- [Snowflake Documentation](https://docs.snowflake.com)
- [Claude Code Documentation](https://claude.ai/code)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

**Built as a learning project for integrating AI with data warehouses** 🚀

Questions? Open an issue or start a discussion!
