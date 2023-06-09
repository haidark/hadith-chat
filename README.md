### Hadith Chat

![image](assets/chat.PNG)

This project demonstrates how large language models and document embeddings can be applied to do semantic search over ahadith (narrations from the Prophet (saw)) with a chat interface.

Using ChatGPT, Langchain-AI, Huggingface, Discord, and Sunnah.com, we collect hadith from well known compilations of hadith (Sahih Bukhari, Sahih Muslim, Sunnan an Nasai, etc), embed them, and present a chat interface to answer questions related to the ahadith. References are provided with each answer allowing easy access to the sources for verification.

Due to the nature of the technology, hallucination and misinterpretation by the model is possible. This is why references are provided, statements from the model should not be accepted without verification.

## How to run

- Install the dependencies with `pip install -r requirements.txt`
- Run `download_hadith.sh` to fetch the hadith compilations locally
- Run `ingest.py` to create the vectorstore
- Set up a discord bot on the server and note the bot's key as DISCORD_TOKEN
- add OPENAI_API_KEY and DISCORD_TOKEN to environment variables
- Run `hc_chatvectordb.py`
