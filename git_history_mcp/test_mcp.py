#!/usr/bin/env python3
"""
Test script for the git history MCP server.

This script:
1. Starts the main FastAPI app that includes our git history router
2. Runs a test query against the MCP server's history_lookup tool

Usage:
    python test_mcp.py [repo_path] [query]
"""

import os
import sys
import asyncio
import argparse
import subprocess
import time
import json
from pathlib import Path

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Test the git history MCP server')
parser.add_argument(
    'repo_path', 
    nargs='?', 
    default=os.getcwd(),
    help='Path to the git repository to analyze (default: current directory)'
)
parser.add_argument(
    'query',
    nargs='?',
    default='Explain the main functionality',
    help='Query to analyze the repository with (default: "Explain the main functionality")'
)
args = parser.parse_args()

# Function to run the main FastAPI app in the background
def start_fastapi_app():
    # Start the app in a separate process
    process = subprocess.Popen(
        ["python", "/Users/oleksandr/projects/lfnt/run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Wait for the app to start up
    time.sleep(3)
    return process

# Function to run the MCP test
async def run_mcp_test(repo_path, query):
    # Run the test using our history_lookup.py with the --test flag
    cmd = [
        "python", 
        "/Users/oleksandr/projects/lfnt/git_history_mcp/history_lookup.py",
        "--test",
        "--test-repo", repo_path,
        "--test-query", query
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate()
    
    # Print the output
    if stdout:
        print("STDOUT:")
        print(stdout)
    
    if stderr:
        print("STDERR:")
        print(stderr)
    
    # Return the exit code
    return process.returncode

if __name__ == "__main__":
    # Start the FastAPI app
    print(f"Starting the FastAPI app...")
    fastapi_process = start_fastapi_app()
    
    try:
        # Run the MCP test
        print(f"Testing git history MCP server with repo: {args.repo_path}")
        print(f"Query: {args.query}")
        exit_code = asyncio.run(run_mcp_test(args.repo_path, args.query))
        
        # Check the result
        if exit_code == 0:
            print("MCP test completed successfully!")
        else:
            print(f"MCP test failed with exit code: {exit_code}")
    
    finally:
        # Clean up - terminate the FastAPI app
        print("Terminating the FastAPI app...")
        fastapi_process.terminate()
        fastapi_process.wait()