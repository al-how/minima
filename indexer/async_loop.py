import os
import uuid
import asyncio
import logging
from indexer import Indexer
from concurrent.futures import ThreadPoolExecutor
from ragignore_utils import load_ragignore, should_ignore_path

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor()

CONTAINER_PATH = os.environ.get("CONTAINER_PATH")
AVAILABLE_EXTENSIONS = [".pdf", ".xls", "xlsx", ".doc", ".docx", ".txt", ".md", ".csv", ".ppt", ".pptx"]


async def crawl_loop(async_queue):
    logger.info(f"Starting crawl loop with path: {CONTAINER_PATH}")
    
    # Load .ragignore patterns
    ignore_patterns = load_ragignore(CONTAINER_PATH)
    if ignore_patterns:
        logger.info(f"Loaded {len(ignore_patterns)} patterns from .ragignore")
    
    existing_file_paths: list[str] = []
    for root, dirs, files in os.walk(CONTAINER_PATH):
        # Filter directories that should be ignored
        dirs[:] = [d for d in dirs if not should_ignore_path(os.path.join(root, d), ignore_patterns)]
        logger.info(f"Processing folder: {root}")
        logger.info(f"Found directories: {dirs}")
        logger.info(f"Found files: {files}")
        for file in files:
            path = os.path.join(root, file)
            
            # Skip files that match ignore patterns
            if should_ignore_path(path, ignore_patterns):
                logger.info(f"Skipping ignored file: {path}")
                continue
                
            # Skip files with unsupported extensions
            if not any(file.endswith(ext) for ext in AVAILABLE_EXTENSIONS):
                logger.info(f"Skipping unsupported extension: {file} in {root}")
                continue
            message = {
                "path": path,
                "file_id": str(uuid.uuid4()),
                "last_updated_seconds": round(os.path.getmtime(path)),
                "type": "file"
            }
            existing_file_paths.append(path)
            async_queue.enqueue(message)
            logger.info(f"File enqueued: {path} with id {message['file_id']}")
            logger.info(f"Queue size now: {async_queue.size()}")

    # After processing all directories, send the aggregate and stop messages
    aggregate_message = {
        "existing_file_paths": existing_file_paths,
        "type": "all_files"
    }
    async_queue.enqueue(aggregate_message)
    async_queue.enqueue({"type": "stop"})


async def index_loop(async_queue, indexer: Indexer):
    loop = asyncio.get_running_loop()
    logger.info("Starting index loop")
    while True:
        if async_queue.size() == 0:
            logger.info("No files to index. Indexing stopped, all files indexed.")
            await asyncio.sleep(1)
            continue
        message = await async_queue.dequeue()
        logger.info(f"Processing message: {message}")
        try:
            if message["type"] == "file":
                await loop.run_in_executor(executor, indexer.index, message)
            elif message["type"] == "all_files":
                await loop.run_in_executor(executor, indexer.purge, message)
            elif message["type"] == "stop":
                break
        except Exception as e:
            logger.error(f"Error in processing message: {e}")
            logger.error(f"Failed to process message: {message}")
        await asyncio.sleep(1)

