import sys
sys.path.append(".")

import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from groq import Groq

from src.vectorstore import query_vectorstore
from src.tools import search_web
from src.prompts import ROUTER_PROMPT, RAG_PROMPT, SERP_PROMPT, MIXED_PROMPT

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── State ──────────────────────────────────────────────
class AgentState(TypedDict):
    question: str
    route: str
    rag_context: str
    serp_context: str
    final_answer: str


# ── Helper: call Groq LLM ──────────────────────────────
def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()


# ── Node 1: Router ─────────────────────────────────────
def router_node(state: AgentState) -> AgentState:
    print(f"\n🔀 Routing question...")
    prompt = ROUTER_PROMPT.format(question=state["question"])
    route = call_llm(prompt).strip().upper()

    # safety check
    if route not in ["DEBALES", "GENERAL", "MIXED"]:
        route = "GENERAL"

    print(f"   → Route: {route}")
    return {**state, "route": route}


# ── Node 2: RAG ────────────────────────────────────────
def rag_node(state: AgentState) -> AgentState:
    print(f"📚 Retrieving from knowledge base...")
    context = query_vectorstore(state["question"])
    print(f"   → Retrieved {len(context)} characters of context")
    return {**state, "rag_context": context}


# ── Node 3: SERP ───────────────────────────────────────
def serp_node(state: AgentState) -> AgentState:
    print(f"🔍 Searching the web...")
    context = search_web(state["question"])
    print(f"   → Got web results")
    return {**state, "serp_context": context}


# ── Node 4: Answer ─────────────────────────────────────
def answer_node(state: AgentState) -> AgentState:
    print(f"💬 Generating answer...")
    route = state["route"]

    if route == "DEBALES":
        prompt = RAG_PROMPT.format(
            rag_context=state["rag_context"],
            question=state["question"]
        )
    elif route == "GENERAL":
        prompt = SERP_PROMPT.format(
            serp_context=state["serp_context"],
            question=state["question"]
        )
    else:  # MIXED
        prompt = MIXED_PROMPT.format(
            rag_context=state["rag_context"],
            serp_context=state["serp_context"],
            question=state["question"]
        )

    answer = call_llm(prompt)
    return {**state, "final_answer": answer}


# ── Routing Logic ──────────────────────────────────────
def route_decision(state: AgentState) -> str:
    route = state["route"]
    if route == "DEBALES":
        return "rag"
    elif route == "GENERAL":
        return "serp"
    else:
        return "rag"  # MIXED starts with rag


def after_rag_decision(state: AgentState) -> str:
    if state["route"] == "MIXED":
        return "serp"  # MIXED goes rag → serp → answer
    return "answer"


# ── Build Graph ────────────────────────────────────────
def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("rag", rag_node)
    graph.add_node("serp", serp_node)
    graph.add_node("answer", answer_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges("router", route_decision, {
        "rag": "rag",
        "serp": "serp",
    })

    graph.add_conditional_edges("rag", after_rag_decision, {
        "serp": "serp",
        "answer": "answer",
    })

    graph.add_edge("serp", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


# ── Public function ────────────────────────────────────
agent_app = build_graph()

def run_agent(question: str) -> dict:
    result = agent_app.invoke({
        "question": question,
        "route": "",
        "rag_context": "",
        "serp_context": "",
        "final_answer": ""
    })
    return result


# ── Test ───────────────────────────────────────────────
if __name__ == "__main__":
    questions = [
        "What does Debales AI do?",
        "What is LangGraph?",
        "How does Debales AI compare to other AI tools?",
        "Who is Elon Musk?"
    ]

    for q in questions:
        print(f"\n{'='*50}")
        print(f"Q: {q}")
        result = run_agent(q)
        print(f"A: {result['final_answer']}")