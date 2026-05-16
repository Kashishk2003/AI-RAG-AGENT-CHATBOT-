import sys
sys.path.append(".")

from src.agent import run_agent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def main():
    console.print(Panel.fit(
        "[bold purple]Debales AI Assistant[/bold purple]\n"
        "[dim]Powered by LangGraph + RAG + Web Search[/dim]\n"
        "[dim]Type 'exit' to quit[/dim]",
        border_style="purple"
    ))

    while True:
        console.print()
        question = console.input("[bold green]You:[/bold green] ").strip()

        if not question:
            continue

        if question.lower() in ["exit", "quit", "bye"]:
            console.print("[dim]Goodbye![/dim]")
            break

        console.print("[dim]Thinking...[/dim]")

        try:
            result = run_agent(question)

            console.print()
            console.print(Panel(
                Text(result["final_answer"]),
                title=f"[bold blue]Debales AI[/bold blue] [dim](via {result['route']})[/dim]",
                border_style="blue"
            ))

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()