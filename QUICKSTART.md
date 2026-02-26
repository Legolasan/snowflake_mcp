# Quick Start Guide 🚀

Get your Snowflake MCP server running in 5 minutes!

## Step 1: Install Dependencies ⚙️

```bash
cd /Users/arunsunderraj/chat/snowflake-mcp
pip install -r requirements.txt
```

## Step 2: Set Up Credentials 🔐

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your Snowflake credentials:
```bash
nano .env  # or use your favorite editor
```

Fill in:
```env
SNOWFLAKE_USER=john_doe
SNOWFLAKE_PASSWORD=your_password_here
SNOWFLAKE_ACCOUNT=abc12345.us-east-1
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=PROD_DB
SNOWFLAKE_SCHEMA=PUBLIC
```

**Where to find your account identifier:**
- Your Snowflake URL looks like: `https://abc12345.us-east-1.snowflakecomputing.com`
- Your account identifier is: `abc12345.us-east-1`

## Step 3: Test the Connection ✅

```bash
python test_connection.py
```

You should see:
```
✅ Connection successful!
📊 Connection Info:
   Snowflake Version: 8.x.x
   User: JOHN_DOE
   Database: PROD_DB
```

If this fails, double-check your credentials!

## Step 4: Configure Claude Code 🤖

Add this to your Claude Code MCP config file:

**Location:** `~/.config/claude-code/mcp.json`

```json
{
  "mcpServers": {
    "snowflake": {
      "command": "bash",
      "args": [
        "-c",
        "source /Users/arunsunderraj/chat/snowflake-mcp/.env && python /Users/arunsunderraj/chat/snowflake-mcp/server.py"
      ]
    }
  }
}
```

## Step 5: Restart Claude Code 🔄

Restart Claude Code CLI for it to pick up the new MCP server.

## Step 6: Test It Out! 🎉

Open a new Claude Code session and try:

```
You: "What tables are in my Snowflake database?"

You: "Show me the structure of the CUSTOMERS table"

You: "Get the count of orders from the last 7 days"
```

Claude will now use your MCP server to query Snowflake!

---

## Troubleshooting 🔧

### Issue: "ModuleNotFoundError: No module named 'mcp'"
**Fix:** Run `pip install -r requirements.txt`

### Issue: "Connection failed"
**Fix:**
- Verify credentials in `.env`
- Check if your Snowflake warehouse is running
- Confirm network access to Snowflake

### Issue: "Claude doesn't see the tools"
**Fix:**
- Check MCP config file syntax (valid JSON?)
- Restart Claude Code
- Check Claude Code logs for MCP errors

### Issue: "Permission denied on tables"
**Fix:**
- Verify your Snowflake user has SELECT permissions
- Check database and schema names

---

## What You Built 🏗️

You now have an MCP server that:
1. ✅ Connects securely to Snowflake
2. ✅ Lets Claude execute SQL queries
3. ✅ Can list and describe tables
4. ✅ Checks data freshness
5. ✅ All through natural language!

## Next Steps 💡

Want to extend it? Add tools for:
- Data quality checks (nulls, duplicates)
- Cost monitoring
- Query performance analysis
- Automated daily reports
- Schema change detection

Check the README for more details!

Happy querying! 🎿
