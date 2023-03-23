import os, logging, pickle
from pathlib import Path
import discord
import openai
from collections import defaultdict
from query_data import get_chain
from callback import DiscordCallbackHandler
from dotenv import load_dotenv

MAX_CONTEXT=10

load_dotenv()

discord_token = os.getenv('DISCORD_KEY') 
openai.api_key = os.getenv('OPENAI_API_KEY')

group_channel = 'hadith-chat'

logging.info("loading vectorstore")
if not Path("vectorstore.pkl").exists():
    raise ValueError("vectorstore.pkl does not exist, please run ingest.py first")
with open("vectorstore.pkl", "rb") as f:
    global vectorstore
    vectorstore = pickle.load(f)

chat_histories = defaultdict(list)
question_handler = DiscordCallbackHandler()
stream_handler = DiscordCallbackHandler()
qa_chain = get_chain(vectorstore, question_handler, stream_handler, tracing=True)

def respond_to_user(question, channel_name):
    chat_history = chat_histories[channel_name]
    chat_history.append((question, ""))
    result = qa_chain(
        {"question": question, "chat_history": chat_history}
    )
    chat_history[-1] = (question, result["answer"])
    src_docs = "\n".join([f"{doc.metadata['reference']} ({doc.metadata['source']})" for doc in result['source_documents']])
    sys_msg = result['answer']+"\nHere are relevant ahadith:\n"+src_docs

    # trim the context length if needed:
    if len(chat_history) > MAX_CONTEXT:
        chat_history = chat_history[-MAX_CONTEXT:]
    chat_histories[channel_name] = chat_history
    return sys_msg


def clear_history(channel_name):
    chat_histories[channel_name] = list()
    return "The message history (context) has been cleared."

intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print('logged in as {0.user}'.format(client))
 
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if type(message.channel) != discord.DMChannel and message.channel.name != group_channel:
        return
    
    print("author--> ", str(message.author))
    print("content--> ", message.content)
    author_name = str(message.author)
    response = None
    if type(message.channel) == discord.DMChannel:
        channel_name = 'dm_'+author_name
        if message.content.startswith('!clear'):
            async with message.channel.typing():
                response = clear_history(channel_name)
        else:
            content = message.content
            async with message.channel.typing():
                response = respond_to_user(content, channel_name)
        
    elif message.channel.name == group_channel:
        channel_name = group_channel
        if message.content.startswith('!hc'):
            content = message.content[3:].strip()
            async with message.channel.typing():
                response = respond_to_user(content, channel_name)   
        elif message.content.startswith('!clear'):
            async with message.channel.typing():
                response = clear_history(channel_name)
    if response:
        print("response--> ", response)
        await message.channel.send(response)
    return            

    
client.run(discord_token)
