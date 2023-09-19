import asyncio
from aiohttp_prometheus import setup_metrics
from aiohttp import web
import routes, service
from migrations.engine import init_models


def db_init_models():
    asyncio.run(init_models())
    print("Done")


async def background_tasks(app):
    app['queue_checker'] = asyncio.create_task(service.queue_checker())
    yield
    app['queue_checker'].cancel()
    await app['queue_checker']


async def on_shutdown(app):
    await app.cleanup()


if __name__ == '__main__':
    db_init_models()
    app = web.Application()
    app.add_routes(routes.routes)
    setup_metrics(app, "mywebapp")
    app.cleanup_ctx.append(background_tasks)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app)






