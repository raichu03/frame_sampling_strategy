# Webhook Integration API with Frame Sampling Strategy

This module implements a webhook endpoint that receives external webhook events and processes video content with configurable frame sampling strategies to balance accuracy versus cost. It handles webhook integration testing, video processing with different sampling rates, and provides comprehensive logging for monitoring and debugging.

Expected outcome: A robust webhook API that successfully receives and processes external webhook events, with frame sampling strategies that optimize processing cost while maintaining video processing accuracy, complete with error handling and comprehensive testing capabilities.

## What data to feed

Provide webhook payloads and configuration, not static datasets:

- Webhook payloads with `event_type` and video processing data
- Video URLs for processing (HTTP/HTTPS format)
- User IDs for tracking processing jobs
- Processing strategy selection: `high_accuracy`, `balanced`, or `low_cost`

Requirements and constraints:
- Video URLs must be accessible HTTP/HTTPS URLs
- User IDs should be non-empty strings for proper tracking
- Processing strategies determine frame sampling rates and cost efficiency
- All webhook events are logged for audit and debugging purposes

## How it works

1. **Webhook Reception**
   - POST `/webhook` receives external webhook payloads with `event_type` and `data` fields
   - Validates incoming payloads using Pydantic models
   - Logs all webhook events for monitoring

2. **Video Processing Strategy**
   - `high_accuracy`: Processes every frame (sampling_rate = 1) - highest cost, maximum accuracy
   - `balanced`: Processes every 5th frame (sampling_rate = 5) - moderate cost and accuracy
   - `low_cost`: Processes every 20th frame (sampling_rate = 20) - lowest cost, reduced accuracy
   - Unknown strategies default to `balanced` with warning logs

3. **Asynchronous Processing**
   - Video processing runs in background using executor threads
   - Non-blocking webhook responses for better performance
   - Comprehensive logging of processing progress and results

Error modes:
- 400 Bad Request: Invalid webhook payload structure or missing required fields
- 500 Internal Server Error: Processing failures or system errors
- Validation errors logged with detailed error messages

## Frame Sampling Strategies

The system supports three processing strategies to balance accuracy vs. cost:

| Strategy | Sampling Rate | Frames Processed (out of 1000) | Cost Level | Accuracy Level |
|----------|---------------|--------------------------------|------------|----------------|
| `high_accuracy` | 1 (every frame) | 1000 | High | Maximum |
| `balanced` | 5 (every 5th frame) | 200 | Medium | Good |
| `low_cost` | 20 (every 20th frame) | 50 | Low | Basic |

## Quick start

Install dependencies (from repo root):

```bash
pip install -r requirements.txt
```

Run the API (from repo root):

```bash
# Option 1: run through Python entrypoint
python task-7/main.py

# Option 2: run through uvicorn directly
uvicorn task-7.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

Base URL: `http://localhost:8000`

- **POST `/webhook`** → Receives webhook events and triggers video processing
- **GET `/health`** → Returns API health status and timestamp

### Webhook Payload Structure

For `video.ready` events:

```json
{
  "event_type": "video.ready",
  "data": {
    "video_url": "https://example.com/video.mp4",
    "user_id": "user123",
    "processing_strategy": "balanced"
  }
}
```

For other events:

```json
{
  "event_type": "other.event",
  "data": {
    "any": "data"
  }
}
```

## Testing Webhook Integration

### 1. Using Interactive API Docs (no code required)

Open: `http://localhost:8000/docs`

Steps:
1. **Health Check**
   - Expand `GET /health`
   - Click "Try it out" → Execute
   - Expected: 200 OK with status, message, and timestamp

2. **Test Webhook**
   - Expand `POST /webhook`
   - Click "Try it out"
   - Enter a test payload (see examples below)
   - Execute to verify processing

## Testing Scenarios

### 1. Successful Processing
- Send `video.ready` event with valid video URL and user ID
- Expected: 200 OK, video processing job enqueued message
- Check logs for processing progress

### 2. Invalid Payload
- Send malformed JSON or missing required fields
- Expected: 400 Bad Request with validation error details

### 3. Different Strategies
Test each processing strategy:
- `high_accuracy`: All frames processed
- `balanced`: Every 5th frame processed  
- `low_cost`: Every 20th frame processed
- `invalid_strategy`: Defaults to balanced with warning

### 4. Non-Video Events
- Send events other than `video.ready`
- Expected: 200 OK, webhook processed but no video task initiated

## Error Scenarios to Test

1. **Invalid Video URL**
   - Use malformed URLs or non-HTTP schemes
   - Expected: 400 Bad Request with URL validation error

2. **Missing Required Fields**
   - Omit `user_id`, `video_url`, or `processing_strategy`
   - Expected: 400 Bad Request with field validation errors

3. **Network Issues**
   - Test with unreachable webhook endpoints
   - Monitor logs for connection errors

4. **Large Payloads**
   - Test with very large data objects
   - Verify proper handling and logging

## Monitoring and Logging

The application logs all activities to `log_file.log` including:
- Webhook event reception with event types
- Video processing job starts and completions
- Frame processing statistics
- Error conditions and validation failures
- Processing strategy selections and frame counts

Log format: `YYYY-MM-DD HH:MM:SS - LEVEL - MESSAGE`

Monitor logs in real-time:
```bash
tail -f task-7/log_file.log
```