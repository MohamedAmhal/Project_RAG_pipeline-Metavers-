# impoort libs :
import bibtexparser
from typing import List, Dict
import re
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import openai
from qdrant_client import QdrantClient
import os
from pymongo import MongoClient
import uuid
##############################################################################



OPEN_IA_KEY = "YOUR PEEEEEEEEEEEEEEN AI KEEEEEEEEEEEEEEEY"



###################################################################################

# function need
def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]


# bib_parser.py


class BibParser:
    def __init__(self, bib_path: str):
        self.bib_path = bib_path

    def parse(self) -> List[Dict]:
        with open(self.bib_path, 'r', encoding='utf-8') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
        entries = []
        for entry in bib_database.entries:
            metadata = {
                'id': entry.get('ID'),
                'title': entry.get('title'),
                'authors': entry.get('author'),
                'year': entry.get('year'),
                'journal': entry.get('journal'),
                'doi': entry.get('doi'),
                'url': entry.get('url'),
            }
            abstract = entry.get('abstract', '')
            entries.append({'metadata': metadata, 'abstract': abstract})
        return entries


# if need to chunk the abstract for example if you have a small embedding model use it


# chunker.py
#class Chunker:
#    def __init__(self, max_tokens: int = 200):
#        self.max_tokens = max_tokens
#
#    def chunk_text(self, text: str) -> List[str]:
#       # naive split by sentences
#        sentences = re.split(r'(?<=[.!?]) +', text)
#        chunks = []
#        current = ''
#        for sent in sentences:
#            if len((current + ' ' + sent).split()) <= self.max_tokens:
#                current = (current + ' ' + sent).strip()
#            else:
#                if current:
#                    chunks.append(current)
#                current = sent
#        if current:
#           chunks.append(current)
#       return chunks


# indexer.py


class EmbeddingIndexer:
    def __init__(self, qdrant_url: str, qdrant_key: str, collection_name: str = 'rag_chunks'):
        self.client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
        self.collection = collection_name
        # ensure collection exists
        self.client.recreate_collection(collection_name=self.collection,
                                        vectors_config={'size': 1536, 'distance': 'Cosine'})
        openai.api_key = OPEN_IA_KEY

    def embed_and_store(self, chunks: List[str], metadata_ids: List[str]) -> None:
        i = 0
        for chunk, mid in zip(chunks, metadata_ids):
            resp = openai.Embedding.create(input=chunk, model='text-embedding-ada-002')
            print(i)
            vector = resp['data'][0]['embedding']
            i+=1
            self.client.upsert(
                    collection_name=self.collection,
                    points=[PointStruct(id=mid, vector=vector, payload={'chunk': chunk})]
                )
            print("added suc !!")
            


# metadata_store.py


class MetadataStore:
    def __init__(self, mongo_uri: str, db_name: str = 'db'):
        self.client = MongoClient(mongo_uri)
        self.col = self.client[db_name]['rag_matadata']

    def insert_many(self, metadatas: List[Dict]) -> None:
        self.col.insert_many(metadatas)

    def get_by_id(self, doc_id: str) -> Dict:
        return self.col.find_one({'uid': doc_id})


# retriever.py


class Retriever:
    def __init__(self, qdrant_url: str, qdrant_key: str, collection_name: str = 'rag_chunks'):
        self.client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
        self.collection = collection_name

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        # embed query
        openai.api_key = OPEN_IA_KEY
        resp = openai.Embedding.create(input=query, model='text-embedding-ada-002')
        qvec = resp['data'][0]['embedding']
        results = self.client.search(collection_name=self.collection,
                                     query_vector=qvec, limit=top_k)
        return results



# chatbot.py

class Chatbot:
    def __init__(self, retriever, metadata_store):
        self.retriever = retriever
        self.meta = metadata_store
        openai.api_key = OPEN_IA_KEY

    def chat(self, user_query: str) -> Dict:
        hits = self.retriever.retrieve(user_query)

        context = "\n\n".join([h.payload['chunk'] for h in hits])
        prompt = f"Use the following context to answer the query and cite by id:\n{context}\n\nQ: {user_query}\nA:"

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',  
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )

        answer = response.choices[0].message["content"]

        sources = [self.meta.get_by_id(h.id) for h in hits]

        return {
            'answer': answer,
            'sources': sources
        }




if __name__ == '__main__':
    # load config from ENV

    ##############################################################


    Q_URL = "QDRANT URL"
    Q_KEY = 'API KEY QDRANT'
    M_URI = 'MONGO DB ATLAS URL'



    ##################################################################

    # Initialize
    print('Initializing...')
    parser = BibParser('scopusdb1.bib')
    entries = parser.parse()

    print("store metadata and prepare chunks")
    ms = MetadataStore(M_URI)
    ms = MetadataStore(M_URI)
    metadatas = []
    all_chunks = []
    meta_ids = []

    for e in entries:
        uid = str(uuid.uuid4())  
        metadata = e['metadata']
        metadata['uid'] = uid  
        metadatas.append(metadata)
        chunk = e['abstract']
        all_chunks.append(chunk)
        meta_ids.append(uid)  
        
    print(metadatas[1])
    print("#" * 20)
    print(all_chunks[1])
    ms.insert_many(metadatas)

    print("index chunks")
    indexer = EmbeddingIndexer(Q_URL, Q_KEY)
    indexer.embed_and_store(all_chunks, meta_ids)

    print("start chat")
    retriever = Retriever(Q_URL, Q_KEY)
    bot = Chatbot(retriever, ms)
    while True:
        q = input('You: ')
        if q.lower() in ('exit','quit'):
            break
        res = bot.chat(q)
        print('Bot:', res['answer'])
        for i in res['sources'] :
            print("#" * 20)
            print('Sources:',i)



# @ moahmmed