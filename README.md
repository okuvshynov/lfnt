# lfnt - Session Management Service

A Python service that wraps an HTTP server to handle session management and persistence.

## Features

- Handles session restoration and persistence
- Forwards requests to the original server
- Supports custom session keys

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- HTTPX

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the root directory with the following variables:

```
HOST=0.0.0.0
PORT=8000
ORIGINAL_SERVER_URL=http://your-original-server-url
```

## Usage

Start the server:

```bash
uvicorn app.main:app --reload
```

### API Endpoints

#### POST /v1/chat/completions

Send requests with the following JSON structure:

```json
{
  "key": "some_string_key",
  "request": {
    // The original request payload that will be forwarded
  }
}
```

The service will:
1. Restore the session from the original server
2. Forward the request to the original server
3. Save the session after receiving the response
4. Return the response to the client

#### GET /health

Health check endpoint.

## Development

Run the server in development mode:

```bash
uvicorn app.main:app --reload
```