import chainlit as cl
from personas.Persona import Persona
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


class ChattyMcChatFace(Persona):
    async def on_chat_start(self):
        llm = AzureChatOpenAI(
            temperature=0.5,
            deployment_name='gpt-35-turbo',
            api_version='2023-03-15-preview',
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant. Answer all questions to the best of your ability.",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        history = ChatMessageHistory()
        self.chain = RunnableWithMessageHistory(
            prompt | llm,
            lambda session_id: history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    async def on_message(self, message: cl.Message):
        result = await self.chain.ainvoke(
            {"input": message.content},
            {"configurable": {"session_id": "unused"}}
        )
        await cl.Message(result.content).send()
