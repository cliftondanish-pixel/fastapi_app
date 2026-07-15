from fastapi import FastAPI
from sqlalchemy import text
from core.database import engine
from core.config import settings
from core.logger import logger
from routes import auth
from routes import tenant
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)
app.include_router(auth.router)
app.include_router(tenant.router,prefix="/tenant",tags=["Tenant"])


@app.get("/")
def root():
    return {"message": "Welcome"}

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

@app.get("/version")
def version():
    return {
        "version": settings.APP_VERSION
    }

@app.get("/db-test")
def db_test():

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT 1")
        )

        return {
            "database": "connected",
            "result": result.scalar()
        }
        


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception) 
async def global_exception_handler(_: Request, exc: Exception):
    logger.error("Unhandled Exception: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"}
    )
logger.info("Application Starting...")