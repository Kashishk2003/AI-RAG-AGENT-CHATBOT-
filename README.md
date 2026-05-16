
Debales AI Assistant

An intelligent AI chatbot built with LangGraph that answers questions about Debales AI using RAG, and handles general queries using Tavily web search. Built as part of the Debales AI Intern Assignment.

Demo Video: https://www.loom.com/share/902bdf116474448a8842cd59490fb640

---

ARCHITECTURE

User Question → ROUTER (Groq LLM) → RAG / SERP / MIXED → Final Answer

---

FEATURES

- Smart Routing — Automatically decides between RAG, Web Search, or Both
- RAG — Scrapes and indexes 1054 chunks from Debales AI website into ChromaDB
- Web Search — Uses Tavily to search the web for general questions
- No Hallucination — Always answers from real sources only, never guesses
- Beautiful CLI — Rich-formatted terminal chat interface

---

TECH STACK

LLM: Groq (llama-3.3-70b-versatile)
Embeddings: ChromaDB Default Embeddings
Vector DB: ChromaDB (local)
Web Scraping: Playwright
Web Search: Tavily
Workflow: LangGraph
CLI: Rich

---

PROJECT STRUCTURE

debales-ai-agent/
  data/
    scraped.json        - scraped website content (1054 chunks)
    chroma/             - local vector database
  scripts/
    ingest.py           - builds vector store from scraped data
  src/
    __init__.py
    scraper.py          - Playwright website crawler
    vectorstore.py      - ChromaDB build and query
    tools.py            - Tavily web search tool
    prompts.py          - LLM prompt templates
    agent.py            - LangGraph workflow
  cli.py                - CLI chat interface
  demo.txt              - example prompts and outputs
  .env.example          - environment variables template
  requirements.txt
  README.md

---

SETUP INSTRUCTIONS

1. Clone the repo
   git clone <your-repo-url>
   cd debales-ai-agent

2. Install dependencies
   pip install -r requirements.txt
   playwright install chromium

3. Set up environment variables
   cp .env.example .env
   Edit .env and add your API keys:
     GROQ_API_KEY=your_groq_key_here
     TAVILY_API_KEY=your_tavily_key_here

   Get your free API keys:
   - Groq: https://console.groq.com
   - Tavily: https://tavily.com

4. Scrape the Debales website
   python src/scraper.py
   Crawls the entire Debales AI website using Playwright and saves 1054 chunks to data/scraped.json. Takes about 5-10 minutes.

5. Build the vector store
   python scripts/ingest.py
   Indexes all 1054 chunks into ChromaDB locally. Takes 3-5 minutes.

6. Run the chatbot
   python cli.py

---

HOW IT WORKS

1. Scraping — Playwright crawls the entire Debales AI website including JS-rendered content and dynamic integration tabs by clicking each category filter.
2. Indexing — Text is chunked into 500 character pieces and stored in ChromaDB with source URLs as metadata.
3. Routing — LangGraph passes the question to a router node which classifies it as DEBALES, GENERAL, or MIXED using Groq LLM.
4. Retrieval — RAG node queries ChromaDB for top 4 most similar chunks; SERP node calls Tavily for live web results.
5. Answer — Final node generates answer using only retrieved context, never from model memory.

---

EXAMPLE PROMPTS AND OUTPUTS

Debales Query (RAG):
  You: What AI agents does Debales offer?
  Route: DEBALES
  Retrieving from knowledge base...
  Retrieved 2365 characters of context
  Bot: Debales AI offers several specialized AI agents including Email AI Agent, SMS AI Agent, WhatsApp AI Agent...

General Query (SERP):
  You: What is artificial intelligence?
  Route: GENERAL
  Searching the web...
  Got web results
  Bot: Artificial intelligence is the simulation of human intelligence by computer systems...

Mixed Query (Both):
  You: How does Debales AI compare to other AI tools?
  Route: DEBALES
  Retrieving from knowledge base...
  Bot: Debales AI differs from other AI companies in that it has reached $1 million in revenue with zero external funding...

No Hallucination Example:
  You: What is the weather on Mars?
  Route: GENERAL
  Searching the web...
  Bot: I couldn't find reliable current weather data for Mars...

---

EVALUATION CRITERIA COVERAGE

Correct routing (RAG vs tool): LangGraph router node classifies as DEBALES/GENERAL/MIXED
Quality of scraping and retrieval: Playwright crawler with 1054 chunks, ChromaDB semantic search
Proper use of SERP API: Tavily integration returning top 5 live results
LangGraph workflow clarity: Clean 4-node graph with conditional edges
Code quality: Modular files, separated concerns, clean structure
Reliability (no hallucination): Prompts explicitly prevent guessing, honest fallback responses

---

REQUIREMENTS

langgraph
langchain
chromadb
playwright
tavily-python
groq
python-dotenv
rich
