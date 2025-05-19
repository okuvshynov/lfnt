from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
import httpx
import logging
from app.config import settings
from app.routers import git_history

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Session Management Service")

# Include routers
app.include_router(git_history.router)

# Data models
class ExtendedRequest(BaseModel):
    key: str
    request: dict

# Create HTTP client
http_client = httpx.AsyncClient(timeout=settings.original_server_timeout)

@app.post("/v1/chat/completions")
async def handle_request(extended_request: ExtendedRequest):
    """
    Wrapper endpoint that:
    1. Restores session from the original server
    2. Forwards the request to the original server
    3. Saves the session back to the original server
    4. Returns the response to the client
    """
    try:
        # Step 1: Restore session
        filename = f"{extended_request.key}.bin"
        restore_url = f"{settings.original_server_url}/slots/0?action=restore"
        restore_payload = {"filename": filename}
        
        logger.info(f"Restoring session for key: {extended_request.key}")
        restore_response = await http_client.post(
            restore_url, 
            json=restore_payload,
            headers={"content-type": "application/json"}
        )
        
        restore_data = None
        if restore_response.status_code == 200:
            try:
                restore_data = restore_response.json()
                logger.info(
                    f"Session restore details: id_slot={restore_data.get('id_slot')}, "
                    f"filename={restore_data.get('filename')}, "
                    f"n_restored={restore_data.get('n_restored')}, "
                    f"n_read={restore_data.get('n_read')}, "
                    f"restore_ms={restore_data.get('timings', {}).get('restore_ms')}"
                )
            except Exception as e:
                logger.error(f"Error parsing restore response: {str(e)}")
        else:
            logger.error(f"Session restore failed: {restore_response.text}")
            # Continue anyway, might be a new session
        
        # Step 2: Forward the request to the original server
        forward_url = f"{settings.original_server_url}/v1/chat/completions"
        logger.info(f"Forwarding request to original server")
        
        forward_response = await http_client.post(
            forward_url,
            json=extended_request.request,
            headers={"content-type": "application/json"}
        )
        
        if forward_response.status_code != 200:
            logger.error(f"Original server request failed: {forward_response.text}")
            return HTTPException(
                status_code=forward_response.status_code,
                detail="Request to original server failed"
            )
        
        # Get the response data
        response_data = forward_response.json()
        
        # Step 3: Save the session
        save_url = f"{settings.original_server_url}/slots/0?action=save"
        save_payload = {"filename": filename}
        
        logger.info(f"Saving session for key: {extended_request.key}")
        save_response = await http_client.post(
            save_url,
            json=save_payload,
            headers={"content-type": "application/json"}
        )
        
        save_data = None
        if save_response.status_code == 200:
            try:
                save_data = save_response.json()
                logger.info(
                    f"Session save details: id_slot={save_data.get('id_slot')}, "
                    f"filename={save_data.get('filename')}, "
                    f"n_saved={save_data.get('n_saved')}, "
                    f"n_written={save_data.get('n_written')}, "
                    f"save_ms={save_data.get('timings', {}).get('save_ms')}"
                )
            except Exception as e:
                logger.error(f"Error parsing save response: {str(e)}")
        else:
            logger.error(f"Session save failed: {save_response.text}")
            # Continue anyway, we still want to return the response
        
        # Step 4: Return the response to the client
        return response_data
    
    except Exception as e:
        logger.exception(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)