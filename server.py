#!/usr/bin/env python3
"""
Snowflake MCP Server - A learning project for querying Snowflake via MCP

This server provides tools for Claude to interact with Snowflake:
- Execute queries
- Check table info
- Monitor data freshness
"""

import os
import asyncio
from typing import Any
import snowflake.connector
from mcp.server import Server
from mcp.types import Tool, TextContent


class SnowflakeMCPServer:
    def __init__(self):
        self.app = Server("snowflake-mcp")
        self.conn = None
        self._setup_tools()

    def _get_connection(self):
        """Get or create Snowflake connection"""
        if self.conn is None:
            self.conn = snowflake.connector.connect(
                user=os.getenv('SNOWFLAKE_USER'),
                password=os.getenv('SNOWFLAKE_PASSWORD'),
                account=os.getenv('SNOWFLAKE_ACCOUNT'),
                warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
                database=os.getenv('SNOWFLAKE_DATABASE'),
                schema=os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
            )
        return self.conn

    def _setup_tools(self):
        """Register all MCP tools"""

        @self.app.call_tool()
        async def query_snowflake(arguments: dict[str, Any]) -> list[TextContent]:
            """
            Execute a SQL query on Snowflake and return results

            Args:
                sql: The SQL query to execute
                limit: Maximum number of rows to return (default: 100)
            """
            sql = arguments.get("sql")
            limit = arguments.get("limit", 100)

            if not sql:
                return [TextContent(type="text", text="Error: SQL query is required")]

            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                # Add LIMIT if not already in query
                if "LIMIT" not in sql.upper():
                    sql = f"{sql.rstrip(';')} LIMIT {limit}"

                cursor.execute(sql)
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                # Format results as a table
                if not results:
                    return [TextContent(type="text", text="Query executed successfully. No rows returned.")]

                # Create formatted output
                output = f"Results ({len(results)} rows):\n\n"
                output += " | ".join(columns) + "\n"
                output += "-" * (sum(len(col) for col in columns) + len(columns) * 3) + "\n"

                for row in results:
                    output += " | ".join(str(val) for val in row) + "\n"

                return [TextContent(type="text", text=output)]

            except Exception as e:
                return [TextContent(type="text", text=f"Error executing query: {str(e)}")]

        @self.app.call_tool()
        async def list_tables(arguments: dict[str, Any]) -> list[TextContent]:
            """
            List all tables in the current database/schema

            Args:
                schema: Optional schema name (defaults to current schema)
            """
            schema = arguments.get("schema", os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC'))

            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                sql = f"""
                SHOW TABLES IN SCHEMA {schema}
                """
                cursor.execute(sql)
                results = cursor.fetchall()

                if not results:
                    return [TextContent(type="text", text=f"No tables found in schema {schema}")]

                output = f"Tables in {schema}:\n\n"
                for row in results:
                    table_name = row[1]  # Table name is in second column
                    row_count = row[4] if len(row) > 4 else "Unknown"
                    output += f"- {table_name} ({row_count} rows)\n"

                return [TextContent(type="text", text=output)]

            except Exception as e:
                return [TextContent(type="text", text=f"Error listing tables: {str(e)}")]

        @self.app.call_tool()
        async def describe_table(arguments: dict[str, Any]) -> list[TextContent]:
            """
            Get detailed information about a table's structure

            Args:
                table_name: Name of the table to describe
            """
            table_name = arguments.get("table_name")

            if not table_name:
                return [TextContent(type="text", text="Error: table_name is required")]

            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                sql = f"DESCRIBE TABLE {table_name}"
                cursor.execute(sql)
                results = cursor.fetchall()

                output = f"Table: {table_name}\n\n"
                output += "Column Name | Type | Nullable | Default | Primary Key\n"
                output += "-" * 70 + "\n"

                for row in results:
                    col_name = row[0]
                    col_type = row[1]
                    nullable = "YES" if row[2] == 'Y' else "NO"
                    default = row[3] if row[3] else "-"
                    pk = "YES" if row[4] == 'Y' else "NO"
                    output += f"{col_name} | {col_type} | {nullable} | {default} | {pk}\n"

                return [TextContent(type="text", text=output)]

            except Exception as e:
                return [TextContent(type="text", text=f"Error describing table: {str(e)}")]

        @self.app.call_tool()
        async def check_table_freshness(arguments: dict[str, Any]) -> list[TextContent]:
            """
            Check when a table was last updated (requires a timestamp column)

            Args:
                table_name: Name of the table to check
                timestamp_column: Name of the timestamp column (default: UPDATED_AT)
            """
            table_name = arguments.get("table_name")
            timestamp_column = arguments.get("timestamp_column", "UPDATED_AT")

            if not table_name:
                return [TextContent(type="text", text="Error: table_name is required")]

            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                sql = f"""
                SELECT
                    MAX({timestamp_column}) as last_update,
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT DATE({timestamp_column})) as distinct_days
                FROM {table_name}
                """
                cursor.execute(sql)
                result = cursor.fetchone()

                last_update = result[0]
                total_rows = result[1]
                distinct_days = result[2]

                output = f"Table Freshness: {table_name}\n\n"
                output += f"Last Updated: {last_update}\n"
                output += f"Total Rows: {total_rows:,}\n"
                output += f"Data Span: {distinct_days} distinct days\n"

                return [TextContent(type="text", text=output)]

            except Exception as e:
                return [TextContent(type="text", text=f"Error checking freshness: {str(e)}")]

    @property
    def tools(self) -> list[Tool]:
        """Return list of available tools"""
        return [
            Tool(
                name="query_snowflake",
                description="Execute a SQL query on Snowflake and return results",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "The SQL query to execute"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of rows to return (default: 100)"
                        }
                    },
                    "required": ["sql"]
                }
            ),
            Tool(
                name="list_tables",
                description="List all tables in the current database/schema",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "schema": {
                            "type": "string",
                            "description": "Optional schema name (defaults to current schema)"
                        }
                    }
                }
            ),
            Tool(
                name="describe_table",
                description="Get detailed information about a table's structure",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table to describe"
                        }
                    },
                    "required": ["table_name"]
                }
            ),
            Tool(
                name="check_table_freshness",
                description="Check when a table was last updated (requires a timestamp column)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table to check"
                        },
                        "timestamp_column": {
                            "type": "string",
                            "description": "Name of the timestamp column (default: UPDATED_AT)"
                        }
                    },
                    "required": ["table_name"]
                }
            )
        ]

    def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server

        async def main():
            async with stdio_server() as (read_stream, write_stream):
                await self.app.run(
                    read_stream,
                    write_stream,
                    self.app.create_initialization_options()
                )

        asyncio.run(main())


if __name__ == "__main__":
    server = SnowflakeMCPServer()
    server.run()
