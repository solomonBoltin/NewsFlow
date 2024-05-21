"""
This module serves as the entry point for executing the Apify Actor. It handles the configuration of logging
settings. The `main()` coroutine is then executed using `asyncio.run()`.

Feel free to modify this file to suit your specific needs.
"""

import asyncio
import logging

from apify.log import ActorLogFormatter

from src.main import main

logging.basicConfig(filename='actor.log', level=logging.DEBUG)

# Configure loggers
handler = logging.StreamHandler()
handler.setFormatter(ActorLogFormatter(include_logger_name=True))

actor_logger = logging.getLogger('actor')
actor_logger.setLevel(logging.DEBUG)
actor_logger.addHandler(handler)

apify_logger = logging.getLogger('apify')
apify_logger.setLevel(logging.DEBUG)
apify_logger.addHandler(handler)


# Execute the Actor main coroutine
asyncio.run(main())
