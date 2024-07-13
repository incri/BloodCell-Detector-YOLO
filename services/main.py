from fastapi import FastAPI
from services.routers import yolo

app = FastAPI()

app.include_router(yolo.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
