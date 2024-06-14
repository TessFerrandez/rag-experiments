import chainlit as cl

from langchain.chains.summarize import load_summarize_chain
from langchain_openai import AzureChatOpenAI
from langchain_community.document_loaders import TextLoader
from personas.Persona import Persona


class DocSummarizer(Persona):
    async def summarize_doc(self):
        files = None

        while not files:
            files = await cl.AskFileMessage(
                content="Please upload a text file to begin!",
                accept=["text/plain"],
                max_size_mb=1,
                timeout=180
            ).send()

        file = files[0]
        message = cl.Message(content=f"Processing {file.name}...", disable_feedback=True)
        await message.send()
        docs = TextLoader(file.path, encoding='utf-8').load()

        summary = self.summarize_chain(docs)
        message.content = f"Heres the summary: {summary["output_text"]}"
        await message.update()

    async def summarize_content(self, content: str):
        summary = self.summarize_chain(content)
        await cl.Message(f"Heres the summary: {summary["output_text"]}").send()


    async def on_chat_start(self):
        await cl.Message(content="Hello! I'm Doc Summarizer. I'm here to summarize your docs!").send()
        llm = AzureChatOpenAI(
            api_version="2023-03-15-preview",
            deployment_name="gpt-4o",
            temperature=0.0,
        )
        self.summarize_chain = load_summarize_chain(llm, chain_type="stuff")
        await self.summarize_doc()

    async def on_message(self, message: cl.Message):
        await self.summarize_doc()