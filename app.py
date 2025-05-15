# chat_only.py

from qdrant_client import QdrantClient
from pymongo import MongoClient
import openai
from typing import List, Dict

# -------------------------------
# Configuration
# -------------------------------

Q_URL = "QDRANT URLLLLLLLLLLLL"
Q_KEY = "QDRANT URLLLLLLLLLLL"
M_URI = "MONGO DB URRRRRRRRRRRL"
OPENAI_API_KEY = "OPEN AI KEEEEEEEEEEEEEEEEEEY"
DB_NAME = "db"
COLLECTION_NAME = "rag_chunks3_test"
META_COLLECTION = "rag_matadata_test"


openai.api_key = OPENAI_API_KEY

# -------------------------------
# define the classes
# -------------------------------

# 1
class MetadataStore:
    def __init__(self, mongo_uri: str, db_name: str = 'db'):
        self.client = MongoClient(mongo_uri)
        self.col = self.client[db_name][META_COLLECTION]

    def get_by_id(self, doc_id: str) -> Dict:
        return self.col.find_one({'uid': doc_id})


# 2
class Retriever:
    def __init__(self, qdrant_url: str, qdrant_key: str, collection_name: str = COLLECTION_NAME):
        self.client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
        self.collection = collection_name

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        resp = openai.Embedding.create(input=query, model='text-embedding-ada-002')
        qvec = resp['data'][0]['embedding']
        results = self.client.search(collection_name=self.collection, query_vector=qvec, limit=top_k)
        return results


# 3
class Chatbot:
    def __init__(self, retriever, metadata_store):
        self.retriever = retriever
        self.meta = metadata_store

    def chat(self, user_query: str) -> Dict:
        hits = self.retriever.retrieve(user_query)

        context = "\n\n".join([h.payload['chunk'] for h in hits])
        prompt = f"Use the following context to answer the query and cite by id:\n{context}\n\nQ: {user_query}\nA:"

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}]
        )

        answer = response.choices[0].message["content"]
        sources = [self.meta.get_by_id(h.id) for h in hits]

        return {
            'answer': answer,
            'sources': sources
        }


# -------------------------------
# print the bot
# -------------------------------


if __name__ == '__main__':
    print("Initializing chatbot...")
    retriever = Retriever(Q_URL, Q_KEY)
    ms = MetadataStore(M_URI)
    bot = Chatbot(retriever, ms)

    while True:
        q = input('You: ')
        if q.lower() in ('exit', 'quit'):
            break
        res = bot.chat(q)
        print('\nBot:', res['answer'])
        for src in res['sources']:
            print("\n" + "#" * 20)
            print("Source:", src)
