import chainlit as cl
from personas.ChattyMcChatFace import ChattyMcChatFace
from dotenv import load_dotenv, find_dotenv

from personas.DocSummarizer import DocSummarizer
from personas.DrRagilicious import DrRagilicious
from personas.MrAndersson import MrAndersson

load_dotenv(find_dotenv())


@cl.set_chat_profiles
async def chat_profile():
    print("chat_profile")
    return [
        cl.ChatProfile(
            name="Chatty McChatface",
            markdown_description="I'll chat with you about anything you want!",
        ),
        cl.ChatProfile(
            name="Doc Summarizer",
            markdown_description="I'll summarize all your docz",
        ),
        cl.ChatProfile(
           name="Dr. RAGilicious",
           markdown_description="Send me your docs and we'll chat about them",
        ),
        cl.ChatProfile(
           name="Mr. Andersson",
           markdown_description="I'm the agent, I can do maths",
        ),
    ]

@cl.on_chat_start
async def on_chat_start():
    chat_profile = cl.user_session.get("chat_profile")
    if chat_profile == "Chatty McChatface":
        persona = ChattyMcChatFace()
    if chat_profile == "Doc Summarizer":
        persona = DocSummarizer()
    if chat_profile == "Dr. RAGilicious":
        persona = DrRagilicious()
    if chat_profile == "Mr. Andersson":
        persona = MrAndersson()

    if persona:
        await persona.on_chat_start()
        cl.user_session.set("persona", persona)
    else:
        await cl.Message(content=f"Starting chat using the {chat_profile} persona").send()


@cl.on_message
async def on_message(message: cl.Message):
    persona = cl.user_session.get("persona")
    if persona:
        await persona.on_message(message)
    else:
        await cl.Message(content="No persona found. Please start a chat first.").send()
