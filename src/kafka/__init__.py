import asyncio
import faust

from src.data.article_prview import ArticlePreview
from src.kafka.faust_article_preview import FaustArticlePreview

# Define a Faust app
app = faust.App('app1', broker='kafka://127.0.0.1:9092',  web_port=6067)

# Define a Faust topic
topic = app.topic('article-preview', value_type=FaustArticlePreview)


async def send_article_preview_to_kafka(article_preview: FaustArticlePreview):
    # Send the article preview to the Kafka topic
    await topic.send(value=article_preview)


async def test():
    print("Running test...")
    ap = FaustArticlePreview(
        title='World war three just started',
        link='https://www.calcalist.co.il/22eds',
        date='2022-01-01',
        website_url='https://www.calcalist.co.il/',
        by_tag_tree='tag1/tag2'
    )
    await send_article_preview_to_kafka(ap)


async def run():
    # Start the app
    await app.start()

    # Send the one-time message
    await test()

    # Stop the app
    await app.stop()



if __name__ == '__main__':
    # Run the async function using asyncio
    asyncio.run(run())

#
# if __name__ == '__main__':
#     # Initialize the Faust app
#     app.finalize()
#
#     # Create an event loop and send the message
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(test())
#
#     # Optionally, run the Faust worker
#     app.main()
