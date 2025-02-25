import nltk
import logging
import asyncio
from pydantic import BaseModel
from async_queue import AsyncQueue
from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from fastapi_utilities import repeat_every
from async_loop import index_loop, crawl_loop

# Import from our centralized imports module
from db_store import MinimaStore
from indexer import Indexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the refactored Indexer with default configuration
indexer = Indexer()
router = APIRouter()
async_queue = AsyncQueue()
MinimaStore.create_db_and_tables()

# Initialize dependencies
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')  # Duplicate but keeping for safety
nltk.download('averaged_perceptron_tagger_eng')

class Query(BaseModel):
    query: str


@router.post(
    "/query", 
    response_description='Query local data storage',
)
async def query(request: Query):
    logger.info(f"Received query: {request.query}")
    try:
        result = indexer.find(request.query)
        logger.info(f"Found {len(result)} results for query: {request.query}")
        logger.info(f"Results: {result}")
        return {"result": result}
    except Exception as e:
        logger.error(f"Error in processing query: {e}")
        return {"error": str(e)}


@router.post(
    "/embedding", 
    response_description='Get embedding for a query',
)
async def embedding(request: Query):
    logger.info(f"Received embedding request: {request}")
    try:
        result = indexer.embed(request.query)
        logger.info(f"Found {len(result)} results for query: {request.query}")
        return {"result": result}
    except Exception as e:
        logger.error(f"Error in processing embedding: {e}")
        return {"error": str(e)}    


@asynccontextmanager
async def lifespan(app: FastAPI):
    tasks = [
        asyncio.create_task(crawl_loop(async_queue)),
        asyncio.create_task(index_loop(async_queue, indexer))
    ]
    await schedule_reindexing()
    try:
        yield
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


def create_app() -> FastAPI:
    app = FastAPI(
        openapi_url="/indexer/openapi.json",
        docs_url="/indexer/docs",
        lifespan=lifespan
    )
    app.include_router(router)
    return app

async def trigger_re_indexer():
    logger.info("Reindexing triggered")
    try:
        await asyncio.gather(
            crawl_loop(async_queue),
            index_loop(async_queue, indexer)
        )
        logger.info("reindexing finished")
    except Exception as e:
        logger.error(f"error in scheduled reindexing {e}")


@repeat_every(seconds=60*20)
async def schedule_reindexing():
    await trigger_re_indexer()

app = create_app()