# API Spec

## POST /v1/jobs

Upload audio and start processing.

```bash
curl -F "file=@song.m4a" http://localhost:8000/v1/jobs
```

Response:

```json
{
  "job_id": "uuid",
  "status": "uploaded",
  "filename": "song.m4a"
}
```

## GET /v1/jobs/{job_id}

Job status.

## GET /v1/jobs/{job_id}/stems/drums

Download separated drums.wav.

## GET /v1/jobs/{job_id}/score

Get internal score JSON.
