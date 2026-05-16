import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def search_web(query: str) -> str:
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    response = client.search(
        query=query,
        max_results=5
    )
    
    results = response.get("results", [])
    
    if not results:
        return "No results found."
    
    formatted = []
    for r in results:
        formatted.append(
            f"Title: {r['title']}\n"
            f"URL: {r['url']}\n"
            f"Summary: {r['content']}"
        )
    
    return "\n\n".join(formatted)

if __name__ == "__main__":
    # quick test
    result = search_web("What is LangGraph?")
    print(result)