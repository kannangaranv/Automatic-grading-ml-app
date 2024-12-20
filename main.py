from fastapi import FastAPI
from route import router
import uvicorn

app = FastAPI()

# Include the grading router
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8880, reload=True)