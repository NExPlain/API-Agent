import datetime

import chainlit as cl
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from llama_index import PineconeReader

from api_gpt.index.pinecone_index import *


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: str):
    result = query(user_id="lizhenpi@gmail.com", query=message)
    # this is an intermediate step
    await cl.Message(author="Debrief", content=f"{result}", indent=1).send()

    # send back the final answer
    await cl.Message(content=f"{result}").send()
