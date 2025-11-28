"""FastAPI backend for LLM Council."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
import json
import asyncio

from . import storage
from .council import run_full_council, generate_conversation_title, stage1_collect_responses, stage2_collect_rankings, stage3_synthesize_final, calculate_aggregate_rankings
from .services.file_reader import get_project_context, FileReaderResult
from .config import CORS_ORIGINS, SERVER_HOST, SERVER_PORT, LLM_PROVIDER as ENV_LLM_PROVIDER
from .api import settings # Import settings router
from .api.settings import _get_setting_db # Helper to get settings
from .services.remote.fetcher import remote_fetcher # Remote fetcher service
from contextlib import ExitStack # For robust cleanup

app = FastAPI(title="LLM Council API")

# Enable CORS (origins configured via environment variables)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Settings Router
app.include_router(settings.router, prefix="/api", tags=["Settings"])


class CreateConversationRequest(BaseModel):
    """Request to create a new conversation."""
    pass


class SendMessageRequest(BaseModel):
    """Request to send a message in a conversation."""
    content: str


class AnalysisRequest(BaseModel):
    """Request to analyze a local project codebase."""
    project_path: str = Field(default=".", description="The root path to the codebase to analyze.")
    analysis_prompt: Optional[str] = Field(default=None, description="Optional custom prompt for analysis.")


class ConversationMetadata(BaseModel):
    """Conversation metadata for list view."""
    id: str
    created_at: str
    title: str
    message_count: int


class Conversation(BaseModel):
    """Full conversation with all messages."""
    id: str
    created_at: str
    title: str
    messages: List[Dict[str, Any]]


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "LLM Council API"}


@app.get("/api/conversations", response_model=List[ConversationMetadata])
async def list_conversations():
    """List all conversations (metadata only)."""
    return storage.list_conversations()


@app.post("/api/conversations", response_model=Conversation)
async def create_conversation(request: CreateConversationRequest):
    """Create a new conversation."""
    conversation_id = str(uuid.uuid4())
    conversation = storage.create_conversation(conversation_id)
    return conversation


@app.get("/api/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """Get a specific conversation with all its messages."""
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.post("/api/conversations/{conversation_id}/message")
async def send_message(conversation_id: str, request: SendMessageRequest):
    """
    Send a message and run the 2-stage council process.
    Returns the complete response with all stages.
    """
    # Check if conversation exists
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Check if this is the first message
    is_first_message = len(conversation["messages"]) == 0

    # Add user message
    storage.add_user_message(conversation_id, request.content)

    # If this is the first message, generate a title
    if is_first_message:
        title = await generate_conversation_title(request.content)
        storage.update_conversation_title(conversation_id, title)

    # Run the 2-stage council process
    stage1_results, stage3_result, metadata = await run_full_council(
        request.content
    )

    # Add assistant message with all stages
    storage.add_assistant_message(
        conversation_id,
        stage1_results,
        [],  # Stage 2 skipped
        stage3_result
    )

    # Return the complete response with metadata
    return {
        "stage1": stage1_results,
        "stage2": [],  # Stage 2 skipped for performance
        "stage3": stage3_result,
        "metadata": metadata
    }


@app.post("/api/conversations/{conversation_id}/message/stream")
async def send_message_stream(conversation_id: str, request: SendMessageRequest):
    """
    Send a message and stream the 2-stage council process.
    Returns Server-Sent Events as each stage completes.
    """
    # Check if conversation exists
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Check if this is the first message
    is_first_message = len(conversation["messages"]) == 0

    async def event_generator():
        try:
            # Add user message
            storage.add_user_message(conversation_id, request.content)

            # Start title generation in parallel (don't await yet)
            title_task = None
            if is_first_message:
                title_task = asyncio.create_task(generate_conversation_title(request.content))

            # Stage 1: Collect responses
            yield f"data: {json.dumps({'type': 'stage1_start'})}\n\n"
            stage1_results = await stage1_collect_responses(request.content)
            yield f"data: {json.dumps({'type': 'stage1_complete', 'data': stage1_results})}\n\n"

            # Stage 2: Skipped for performance
            yield f"data: {json.dumps({'type': 'stage2_skipped'})}\n\n"

            # Stage 3: Synthesize final answer
            yield f"data: {json.dumps({'type': 'stage3_start'})}\n\n"
            stage3_result = await stage3_synthesize_final(request.content, stage1_results)
            yield f"data: {json.dumps({'type': 'stage3_complete', 'data': stage3_result})}\n\n"

            # Wait for title generation if it was started
            if title_task:
                title = await title_task
                storage.update_conversation_title(conversation_id, title)
                yield f"data: {json.dumps({'type': 'title_complete', 'data': {'title': title}})}\n\n"

            # Save complete assistant message
            storage.add_assistant_message(
                conversation_id,
                stage1_results,
                [],  # Stage 2 skipped
                stage3_result
            )

            # Send completion event
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

        except Exception as e:
            # Send error event
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.post("/api/analyze-project")
async def analyze_project(request: AnalysisRequest):
    """
    Analyze a project codebase using the LLM Council, using the specified path.
    
    This endpoint reads files from the specified project directory,
    respects .gitignore patterns, and sends the codebase to the council for analysis.
    
    Args:
        request: AnalysisRequest with project_path and optional analysis_prompt
        
    Returns:
        Complete council response with all 3 stages and metadata
    """
    # 1. Fetch current LLM Provider setting (Task 18 logic)
    current_provider = _get_setting_db("llm_provider") or ENV_LLM_PROVIDER
    print(f"INFO: Starting analysis with LLM Provider: {current_provider}")

    input_path = request.project_path
    is_remote_url = input_path.startswith(('http://', 'https://', 'git@'))

    # Use ExitStack for reliable cleanup
    with ExitStack() as stack:
        if is_remote_url:
            print(f"INFO: Detected remote URL. Initiating clone for: {input_path}")
            
            # Clone the repo using the fetcher service
            local_path = remote_fetcher.clone_repo(input_path)
            
            if local_path is None:
                raise HTTPException(status_code=400, detail=f"Failed to clone repository from URL: {input_path}")
            
            # Register cleanup callback
            stack.callback(remote_fetcher.cleanup, local_path)
            
            path_to_analyze = local_path
        else:
            path_to_analyze = input_path

        # Validate and read the project
        try:
            content, result = get_project_context(str(path_to_analyze))
        except ValueError as e:
            # Invalid path or not a directory
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            # Other errors during file reading
            raise HTTPException(
                status_code=500,
                detail=f"Error reading project files: {str(e)}"
            )
        
        # Check if any files were read
        if result.files_read == 0:
            raise HTTPException(
                status_code=400,
                detail="No files found to analyze. The directory may be empty or all files are ignored."
            )
        
        # Construct the analysis prompt
        if request.analysis_prompt:
            intro = request.analysis_prompt
        else:
            intro = """Analyze this codebase and provide insights on:
1. Overall architecture and design patterns
2. Code quality and best practices
3. Potential improvements or issues
4. Key components and their relationships"""
        
        final_prompt = f"""{intro}

HERE IS THE LOCAL CODEBASE CONTEXT:
===================================

{content}"""
        
        # Run the council analysis
        try:
            stage1_results, stage3_result, metadata = await run_full_council(
                final_prompt,
                project_path=str(path_to_analyze)
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error during council analysis: {str(e)}"
            )
        
        # Return the complete response with file reading metadata
        return {
            "stage1": stage1_results,
            "stage2": [],  # Stage 2 skipped for performance
            "stage3": stage3_result,
            "metadata": {
                **metadata,
                "file_analysis": result.to_dict(),
                "llm_provider": current_provider,
                "source_path": input_path # Return original path/URL
            }
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
