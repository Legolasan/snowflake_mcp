#!/usr/bin/env python3
"""
Test script to verify Snowflake connection works

Run this to make sure your credentials are correct before using with MCP
"""

import os
from dotenv import load_dotenv
import snowflake.connector

# Load environment variables
load_dotenv()

def test_connection():
    """Test Snowflake connection"""
    print("🔄 Testing Snowflake connection...")

    try:
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )

        print("✅ Connection successful!")

        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION(), CURRENT_USER(), CURRENT_DATABASE()")
        result = cursor.fetchone()

        print(f"\n📊 Connection Info:")
        print(f"   Snowflake Version: {result[0]}")
        print(f"   User: {result[1]}")
        print(f"   Database: {result[2]}")

        # List tables
        cursor.execute(f"SHOW TABLES IN SCHEMA {os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')}")
        tables = cursor.fetchall()

        print(f"\n📋 Tables in {os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')} schema:")
        if tables:
            for table in tables[:5]:  # Show first 5
                print(f"   - {table[1]}")
            if len(tables) > 5:
                print(f"   ... and {len(tables) - 5} more")
        else:
            print("   No tables found")

        conn.close()
        print("\n🎉 All tests passed! Your MCP server should work!")

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\n💡 Check your .env file and make sure:")
        print("   - All credentials are correct")
        print("   - Your Snowflake account is accessible")
        print("   - The warehouse is running")
        return False

    return True

if __name__ == "__main__":
    test_connection()
