from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .database.core import engine, Base
from .api import register_routes
import logging
import src.entities
from src.middleware.logging_middleware import BitacoraLoggingMiddleware


app = FastAPI()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  
)

app.add_middleware(BitacoraLoggingMiddleware)


# DB startup test
async def test_db_connection():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        value = result.scalar()
        if value == 1:
            logger.info("Database connection successful.")
        else:
            logger.error("Database connection test failed.")


# Startup event
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema created.")

    await test_db_connection()


# Register routers
register_routes(app)


# Health check route
@app.get("/health")
def health():
    return {"status": "ok"}
