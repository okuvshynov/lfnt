#!/usr/bin/env python3
"""
Test script for the git history microservice.
This script sends a request to analyze a git repository.

Usage:
    python test_git_service.py [repo_path] [--query QUERY]

Arguments:
    repo_path       - Path to the git repository to analyze (default: current directory)
    -q, --query     - Query to analyze the repository with (default: "Explain the main functionality")
"""

import os
import sys
import json
import httpx
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", "8000")
TIMEOUT = float(os.getenv("ORIGINAL_SERVER_TIMEOUT", "3600.0"))

ENDPOINT = "/git/history"
URL = f"http://{HOST}:{PORT}{ENDPOINT}"
DEFAULT_QUERY = "Explain the main functionality"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test script for git history microservice - analyzes a git repository"
    )
    parser.add_argument(
        "repo_path", 
        nargs="?", 
        default=os.getcwd(),
        help=f"Path to the git repository to analyze (default: current directory)"
    )
    parser.add_argument(
        "-q", "--query",
        dest="query",
        default=DEFAULT_QUERY,
        help=f"Query to analyze the repository with (default: '{DEFAULT_QUERY}')"
    )
    return parser.parse_args()

async def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Get repo path from arguments
    repo_path = args.repo_path
    query = args.query
    
    # Check if repo path exists and is a git repository
    repo_path_obj = Path(repo_path)
    
    if not repo_path_obj.exists():
        print(f"Error: Directory not found at {repo_path}")
        return
    
    git_dir = repo_path_obj / ".git"
    if not git_dir.exists():
        print(f"Error: Not a git repository at {repo_path}")
        return

    try:
        # Construct the request
        request_data = {
            "repo_path": str(repo_path_obj),
            "query": query,
            "num_commits": 5  # Limit to 5 commits for testing
        }

        # Print information about the request
        print(f"Sending request to: {URL}")
        print(f"Repository path: {repo_path}")
        print(f"Query: {query}")

        # Send the request using httpx
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            headers = {
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                URL,
                json=request_data,
                headers=headers
            )
            
            # Print response
            print("\nResponse status:", response.status_code)
            
            if response.status_code == 200:
                response_json = response.json()
                print("\nResponse content:")
                print(json.dumps(response_json, indent=2))
            else:
                print("\nError response:")
                print(response.text)
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())