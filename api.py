from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from tasks import generate_content

app = FastAPI(title="AI Empire API", description="Microservice for X (Twitter) Content Generation")

class GenerateRequest(BaseModel):
    topic: str = "AI News"
    auto_post: bool = False

@app.post("/generate")
def trigger_generation(req: GenerateRequest):
    """
    Trigger an asynchronous content generation task using Celery.
    """
    task = generate_content.delay(topic=req.topic, auto_post=req.auto_post)
    return {"message": "Generation task started", "task_id": task.id}

@app.get("/status/{task_id}")
def get_status(task_id: str):
    """
    Get the status of a Celery task.
    """
    from celery_app import celery_app
    task_result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
