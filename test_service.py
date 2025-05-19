#!/usr/bin/env python3
"""
Test script for the session management service.
This script sends a request to summarize the content of a text file.

Usage:
    python test_service.py [file_path] [--key SESSION_KEY]

Arguments:
    file_path        - Optional path to a text file to summarize (default: data/sample.txt)
    -k, --key        - Session key to use for the request (default: test_session)
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

ENDPOINT = "/v1/chat/completions"
URL = f"http://{HOST}:{PORT}{ENDPOINT}"
DEFAULT_SESSION_KEY = "test_session"
DEFAULT_SAMPLE_FILE = "data/sample.txt"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test script for session management service - summarizes a text file"
    )
    parser.add_argument(
        "file_path", 
        nargs="?", 
        default=DEFAULT_SAMPLE_FILE,
        help=f"Path to the file to summarize (default: {DEFAULT_SAMPLE_FILE})"
    )
    parser.add_argument(
        "-k", "--key",
        dest="session_key",
        default=DEFAULT_SESSION_KEY,
        help=f"Session key to use for the request (default: {DEFAULT_SESSION_KEY})"
    )
    return parser.parse_args()

async def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Get session key from arguments
    session_key = args.session_key
    
    # Check if file exists
    file_path = args.file_path
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        print(f"Error: File not found at {file_path}")
        return

    try:
        # Read the file content
        with open(file_path_obj, "r") as f:
            file_content = f.read()

        # Construct the request
        request_data = {
            "key": session_key,
            "request": {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Please briefly summarize the following file: {file_content}"
                    }
                ]
            }
        }

        # Print information about the request
        print(f"Sending request to: {URL}")
        print(f"Session key: {session_key}")
        print(f"Request includes content from: {file_path}")

        # Send the request using httpx
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer no-key"
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
