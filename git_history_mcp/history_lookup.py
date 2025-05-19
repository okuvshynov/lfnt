#!/usr/bin/env python3

from typing import Any, List, Optional
import httpx
import os.path
import sys
import asyncio
import logging
import argparse
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('git_history')

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Git history lookup tool')
parser.add_argument('--base-url', type=str, default='http://localhost:8000',
                    help='Base URL for API endpoints (default: http://localhost:8000)')
parser.add_argument('--test', action='store_true', help='Run test function')
parser.add_argument('--test-repo', type=str, help='Repository path for testing')
parser.add_argument('--test-query', type=str, default='Explain the main functionality',
                    help='Query for testing')
args, unknown = parser.parse_known_args()

# Initialize FastMCP server
mcp = FastMCP("history_lookup")

BASE_URL = args.base_url

logger.info(f"Configured with BASE_URL={BASE_URL}")

async def verify_git_repo(repo_path: str) -> bool:
    """
    Verify that the path is a git repository.
    
    Args:
        repo_path: Path to the git repository
        
    Returns:
        True if valid git repository, False otherwise
    """
    try:
        cmd = ["git", "-C", repo_path, "rev-parse", "--is-inside-work-tree"]
        process = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return process.stdout.strip() == "true"
    except subprocess.CalledProcessError:
        return False
    except Exception as e:
        logger.error(f"Error verifying git repository: {str(e)}")
        return False

@mcp.tool()
async def history_lookup(repo_path: str, query: str, num_commits: int = 10) -> str:
    """Look up relevant git history for a query
    
    Args:
        repo_path: Path to the git repository
        query: The query to analyze the repository with
        num_commits: Number of recent commits to analyze (default: 10)
    """
    logger.info(f"Looking up git history for repo: {repo_path}, query: {query}")
    
    # Verify that the path is a git repository
    if not await verify_git_repo(repo_path):
        error_msg = f"Invalid git repository path: {repo_path}"
        logger.error(error_msg)
        return error_msg
    
    # Get repository name from path (last component)
    repo_name = Path(repo_path).name
    
    try:
        # Prepare request to the git history microservice
        history_request = {
            "repo_path": repo_path,
            "query": query,
            "num_commits": num_commits
        }
        
        # Send request to the git history microservice
        url = f"{BASE_URL}/git/history"
        
        logger.info(f"Sending request to: {url}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                url,
                json=history_request,
                headers=headers
            )
            
            if response.status_code != 200:
                error_msg = f"Error from git history service: {response.text}"
                logger.error(error_msg)
                return error_msg
            
            # Extract and return the content from the response
            response_json = response.json()
            if "choices" in response_json and len(response_json["choices"]) > 0:
                if "message" in response_json["choices"][0] and "content" in response_json["choices"][0]["message"]:
                    return response_json["choices"][0]["message"]["content"]
                
            return f"Invalid response format from git history service: {response_json}"
            
    except Exception as e:
        error_msg = f"Error during git history lookup: {str(e)}"
        logger.error(error_msg)
        return error_msg

async def test_history_lookup():
    """Test function that looks up git history for a repository"""
    if not args.test_repo:
        logger.error("Please provide a test repository path with --test-repo")
        return
    
    result = await history_lookup(args.test_repo, args.test_query)
    logger.info(f"Git history lookup for {args.test_repo}:\n{result}")

if __name__ == "__main__":
    if args.test:
        # Run the test function
        asyncio.run(test_history_lookup())
    else:
        # Initialize and run the server
        mcp.run(transport='stdio')