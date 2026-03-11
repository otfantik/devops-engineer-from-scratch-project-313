from fastapi import FastAPI

# Создаем объект app (экспортируется для запуска)
app = FastAPI(title="DevOps Engineer Project")

@app.get("/ping")
async def ping():
    return "pong"

# Для локального запуска (если потребуется)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
