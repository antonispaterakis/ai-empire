import uvicorn

if __name__ == "__main__":
    print("--- Starting AI Empire Microservices Backend ---")
    print("For full functionality, ensure Redis is running (docker-compose up -d redis)")
    print("and Celery is running: celery -A celery_app worker --loglevel=info")
    
    # Run the FastAPI app
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)