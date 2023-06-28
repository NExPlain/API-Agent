import chainlit as cl
from api_gpt.index.pinecone_index import get_email_documents
import datetime

from api_gpt.prompts.email_action_prompt import (
    generate_email_action_response,
    get_email_action_chain,
)


@cl.action_callback("load_emails")
async def on_action(action):
    email_documents = get_email_documents(
        user_id="testuser",
        email_query="category:primary after:"
        + (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y/%m/%d"),
    )
    if len(email_documents) >= 5:
        email_documents = email_documents[:5]

    await cl.Message(
        content=f"Loaded {len(email_documents)} emails from your inbox, try ask some questions around it."
    ).send()
    # Optionally remove the action button from the chatbot user interface
    await action.remove()


@cl.on_chat_start
async def start():
    # Sending an action button within a chatbot message
    actions = [
        cl.Action(name="load_emails", value="example_value", description="Click me!")
    ]

    await cl.Message(
        content="Interact with this action button:", actions=actions
    ).send()


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: str):
    llm_chain = get_email_action_chain()
    result = generate_email_action_response(
        llm_chain,
        user_name="Test user",
        user_email="test@debrief-ai.com",
        user_context="I'm a test user that want to do fancy actions to reply a email",
        subject="Organize party tonight",
        email_from="zhen.li@plasma-ai.com",
        email_to="test@debrief-ai.com",
        content="Hi there, I want to organize a joint party between Plasma and Debrief tomorrow starting at 6 pm, do you want to join?",
        action_prompt=message,
    )
    # this is an intermediate step
    await cl.Message(author="Debrief", content=f"{result}", indent=1).send()

    # send back the final answer
    await cl.Message(content=f"{result}").send()
