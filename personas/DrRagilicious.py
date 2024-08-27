import chainlit as cl
import os

from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from personas.Persona import Persona


class DrRagilicious(Persona):
    async def on_chat_start(self):
        llm = AzureChatOpenAI(temperature=0, deployment_name='gpt-35-turbo', api_version='2023-03-15-preview',)
        embedding = AzureOpenAIEmbeddings(azure_deployment="text-embedding-ada-002", openai_api_version="2023-05-15",)
        message_history = ChatMessageHistory()
        conversation_buffer_memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", chat_memory=message_history, return_messages=True)

        db = AzureSearch(azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"), azure_search_key=os.getenv("AZURE_SEARCH_KEY"), index_name="engineering_fundamentals", embedding_function=embedding.embed_query,)
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            chain_type="stuff",
            retriever=db.as_retriever(),
            memory=conversation_buffer_memory,
            return_source_documents=True
        )

        await cl.Message(content="Hello! I'm Dr. Ragilicious! I can help you with all things Engineering Fundamentals!").send()

    async def on_message(self, message: cl.Message):
        result = await self.chain.ainvoke(message.content)
        answer = result["answer"]
        source_documents = result["source_documents"]

        text_elements = []
        if source_documents:
            for source_doc in source_documents:
                path = source_doc.metadata["path"]
                source_name = path
                text_elements.append(cl.Text(content=source_doc.page_content, name=source_name))

            # source_names = [text_element.name for text_element in text_elements]

            # if source_names:
            #     answer += f"\n\n\nSources: {'\n- ' + '\n- '.join(source_names)}"
            # else:
            #     answer += "\n\n\nNo sources found."

        await cl.Message(content=answer, elements=text_elements).send()
