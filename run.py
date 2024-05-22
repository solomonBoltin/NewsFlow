import asyncio
import logging

from apify.log import ActorLogFormatter

from src.main import main

logging.basicConfig(filename='actor.log', level=logging.DEBUG)

# Configure loggers
handler = logging.StreamHandler()
handler.setFormatter(ActorLogFormatter(include_logger_name=True))

actor_logger = logging.getLogger('actor')
actor_logger.setLevel(logging.INFO)
actor_logger.addHandler(handler)

apify_logger = logging.getLogger('apify')
apify_logger.setLevel(logging.INFO)
apify_logger.addHandler(handler)


# Execute the Actor main coroutine
asyncio.run(main())
