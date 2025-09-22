from datetime import datetime
import logging
import asyncio

from fastapi import FastAPI, Depends, HTTPException, status
import uvicorn

from models import HealthCheckResponse, WebhookPayload, VideoProcessingPayload

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='log_file.log'
)

app = FastAPI(
    title='Webhook Integration API',
    description='Handles external webhooks. ',
    responses={404: {"description": "Not found"}},
)

def process_video(video_data: VideoProcessingPayload):
    """
    This functioin simulates a video processing task with a frame sampling strategy.
    """

    logging.info(f"Starting video processing for user: {video_data.user_id} from URL: {video_data.video_url}")

    strategy = video_data.processing_strategy
    frame_count = 1000

    if strategy == "high_accuracy":
        sampling_rate = 1
        logging.info("Using 'high_accuracy' strategy: processing all frames.")
    elif strategy == "low_cost":
        sampling_rate = 20
        logging.info("Using 'low_cost' strategy: processing every 20th frame.")
    elif strategy == "balanced":
        sampling_rate = 5
        logging.info("Using 'balanced' strategy: processing every 5th frame.")
    else:
        sampling_rate = 5
        logging.warning(f"Unknown strategy '{strategy}'. Defaulting to 'balanced'.")

    processed_frames = 0
    for i in range(frame_count):
        if (i + 1) % sampling_rate == 0:
            processed_frames += 1

    logging.info(f"Video processing complete for user {video_data.user_id}.")
    logging.info(f"Total frames: {frame_count}, Processed frames: {processed_frames}")


@app.post("/webhook")
async def handle_data(payload: WebhookPayload):
    """
    Receives a webhook payload and triggers a video processing task.
    """
    logging.info(f"Received webhook event: {payload.event_type}.")

    if payload.event_type == "video.ready":
        try:
            video_data = VideoProcessingPayload(**payload.data)
            
            asyncio.get_event_loop().run_in_executor(
                None, process_video, video_data
            )
            
            logging.info(f"Video processing job for user '{video_data.user_id}' has been enqueued.")
            return {"status": "success", "message": "Video processing job started"}
        
        except Exception as e:
            logging.error(f"Error validating webhook payload for video processing: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid webhook payload for event type 'video.ready'. Details: {e}"
            )
    else:
        logging.info("Webhook processed. No video processing task was initiated.")
        return {"status": "success", "message": "Webhook received and processed (no video task)"}

@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a health check",
    response_model=HealthCheckResponse,
    response_description="Return HTTP Status Code 200 (OK)"
)
async def health_check() -> HealthCheckResponse:
    """
    Performs a simple health check to ensure the backend is running.
    
    Returns:
        A JSON object with a status, a message, and the current timestamp.
    """

    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return HealthCheckResponse(
        status="OK",
        message="The backend is running.",
        timestamp=current_time_str
    )

if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)