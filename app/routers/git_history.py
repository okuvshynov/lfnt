from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import httpx
import subprocess
import logging
import os
from pathlib import Path
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/git",
    tags=["git"],
    responses={404: {"description": "Not found"}},
)

# Data models
class GitHistoryRequest(BaseModel):
    repo_path: str
    query: str
    num_commits: int = 10  # Default to 10 commits


async def get_git_history(repo_path: str, num_commits: int = 10):
    """
    Extract git history from a repository with detailed information.
    
    Args:
        repo_path: Path to the git repository
        num_commits: Number of recent commits to extract
        
    Returns:
        List of commit details including hash, short hash and content
    """
    try:
        # Change to the repository directory
        if not os.path.isdir(repo_path):
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        # Get the last N commit hashes
        cmd = ["git", "-C", repo_path, "log", f"-{num_commits}", "--format=%H"]
        process = subprocess.run(cmd, capture_output=True, text=True, check=True)
        commit_hashes = process.stdout.strip().split('\n')
        
        # Get detailed information for each commit
        commits = []
        for commit_hash in commit_hashes:
            if not commit_hash:  # Skip empty lines
                continue
                
            # Get short hash (8 symbols)
            short_hash = commit_hash[:8]
            
            # Get detailed commit info using git show
            cmd = ["git", "-C", repo_path, "show", commit_hash]
            process = subprocess.run(cmd, capture_output=True, text=True, check=True)
            commit_content = process.stdout
            
            commits.append({
                "hash": commit_hash,
                "short_hash": short_hash,
                "content": commit_content
            })
            
        return commits
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e.stderr}")
        raise ValueError(f"Git command failed: {e.stderr}")
    except Exception as e:
        logger.error(f"Error extracting git history: {str(e)}")
        raise ValueError(f"Error extracting git history: {str(e)}")


async def format_git_history_request(commits, query):
    """
    Format the git history and query into a request message.
    
    Args:
        commits: List of commit details
        query: User's text query
        
    Returns:
        Formatted message to send to the Session Management Service
    """
    commit_text = "\n\n".join([
        f"Commit: {commit['hash']}\n"
        f"Short hash: {commit['short_hash']}\n"
        f"{commit['content']}"
        for commit in commits
    ])
    
    message = (
        f"You are given last {len(commits)} commits and a request at the end. "
        f"Return the most relevant commit ids for engineer to study to better "
        f"understand the codebase and request.\n\n"
        f"RETURN ONLY REFERENCES: commit_ids, filenames and important symbols/functions. DO NOT implement anything yourself.\n\n"
        f"FOCUS ON BREVITY, DEVELOPER WILL BE ABLE TO LOOK AT REFERENCES THEMSELVES"
        f"{commit_text}\n\n"
        f"Request: {query}"
    )
    
    return message


@router.post("/history")
async def analyze_git_history(request: GitHistoryRequest):
    """
    Analyze git history and send the analysis to the Session Management Service.
    
    Args:
        request: GitHistoryRequest containing repo path and query
        
    Returns:
        A status response indicating if the request was successful
    """
    try:
        # Get repository name from path (last component)
        repo_name = Path(request.repo_path).name
        session_key = f"{repo_name}_git_history"
        
        # Extract git history
        commits = await get_git_history(request.repo_path, request.num_commits)
        
        # Format message
        message = await format_git_history_request(commits, request.query)
        
        # Prepare request to the Session Management Service
        sms_request = {
            "key": session_key,
            "request": {
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            }
        }
        
        # Send request to the Session Management Service
        url = f"http://{settings.host}:{settings.port}/v1/chat/completions"
        
        async with httpx.AsyncClient(timeout=settings.original_server_timeout) as client:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer no-key"
            }
            
            response = await client.post(
                url,
                json=sms_request,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from Session Management Service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Request to Session Management Service failed"
                )
            
            # Return response from the Session Management Service
            return response.json()
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error processing git history request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
