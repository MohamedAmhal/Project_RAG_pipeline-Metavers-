# RAG Pipeline for Scientific Abstracts with Chatbot Interface

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline that allows users to interact with scientific abstracts in `.bib` format. It includes a chatbot that answers user questions by retrieving relevant abstracts and generating accurate responses. It also provides references such as article titles, authors, and links.

---

## 🚀 Features

- Parse `.bib` files into abstracts and metadata.
- Generate vector embeddings from abstracts using OpenAI.
- Store embeddings in **Qdrant** (Free cloud tier).
- Store metadata in **MongoDB Atlas** (Cloud).
- Link both databases using a common document ID.
- Perform semantic search and retrieve top relevant abstracts.
- Use an LLM to generate answers with references based on retrieved context.

---

## 🧱 Project Architecture

.**bib file**     ➡️ **BibParser**    ➡️      **EmbeddingIndexer (Qdrant)**     ➡️    **MetadataStore (MongoDB Atlas)**      ➡️    **Retriever + Chatbot (LLM)**


---

## 🧩 Components & Classes

### 1. `BibParser`
- Parses `.bib` files.
- Splits content into:
  - **Abstracts**
  - **Metadata** (all information except abstracts).

### 2. `EmbeddingIndexer`
- Converts abstracts into embeddings using OpenAI Embedding API.
- Uploads vectors into **Qdrant** vector database.

### 3. `MetadataStore`
- Uploads metadata to **MongoDB Atlas**.
- Fetches documents using document IDs (linked to Qdrant).

### 4. `Retriever`
- Accepts a user query.
- Performs **semantic search** using Qdrant.
- Returns matching abstracts and metadata.

### 5. `Chatbot`
- Uses an LLM to answer user queries based on retrieved context.
- Returns answers with proper references (title, authors, links).

---

## 📁 Project Structure

```bash
├── main.py            # For full ingestion & setup of the RAG pipeline
├── app.py             # For running the chatbot after setup
├── requirements.txt   # Python dependencies
├── /your_file.bib     # Your input scientific file

```
## 🚀 Getting Started 

1. Clone the Repository :

```bash
git clone https://github.com/your-username/rag-scientific-chatbot.git
cd rag-scientific-chatbot

```

2. Install Requirements :

```bash
pip install -r requirements.txt
```

## 🔐 Required Credentials & Setup

Make sure you have the following ready:



✅ OpenAI API Key



✅ Qdrant Cloud (Free Tier) URL (e.g., https://xxxx.qdrant.tech)




 ==> API Key



✅ MongoDB Atlas



- Database name: db

- Collection name: rag_metadata

- Connection string (MongoDB URI)


## 🧪 Example Questions

```bash
Q: What are the recent methods used for protein structure prediction?
A: The most recent methods include AlphaFold and RoseTTAFold, which rely on deep learning...
↳ Reference: "AlphaFold: highly accurate protein structure prediction", Nature, [link]

```

## 📌 Notes

- Ensure you don’t exceed OpenAI or Qdrant free tier usage limits.

- Each document has a shared id between Qdrant and MongoDB for lookup.

- Currently tested with .bib files from scientific literature sources.


## 📄 License

This project is licensed under the MIT License.

## 🙋‍♂️ Author

Mohammed Amhal


Data & AI Engineer | Student egineer at @ENSA of TETOUAN


@METAVERSE 