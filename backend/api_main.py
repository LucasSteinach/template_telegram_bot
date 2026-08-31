from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.auth import router as auth_router
from api.exception_handlers import register_exception_handlers
from api.operator import router as operator_router
from config import settings
from container import Container


@asynccontextmanager
async def lifespan(application: FastAPI):
    container = Container(settings)
    application.state.container = container
    await container.rabbitmq.connect()

    yield

    await container.rabbitmq.close()
    await container.engine.dispose()
    await container.redis_storage.disconnect()


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(operator_router)
app.include_router(auth_router)
