"""Beautiful terminal report rendering using Rich."""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from contractguard.models import AnalysisResult, Issue, Protection, Severity

console = Console()

GRADE_COLORS = {
    "A+": "bold green",
    "A": "green",
    "B+": "dark_green",
    "B": "yellow",
    "C+": "yellow",
    "C": "dark_orange",
    "D": "red",
    "F": "bold red",
}

SEVERITY_ICONS = {
    Severity.RED: "[bold red]\u2b24 RED FLAG[/bold red]",
    Severity.YELLOW: "[bold yellow]\u26a0 WARNING[/bold yellow]",
    Severity.GREEN: "[bold green]\u2714 GOOD[/bold green]",
}


def print_report(result: AnalysisResult) -> None:
    """Print a beautiful contract analysis report to the terminal."""
    console.print()

    # Header
    _print_header(result)
    console.print()

    # Summary
    _print_summary(result)
    console.print()

    # Red flags
    if result.red_flags:
        _print_issues(result.red_flags, "RED FLAGS", "red", "\u2b24")
        console.print()

    # Warnings
    if result.warnings:
        _print_issues(result.warnings, "WARNINGS", "yellow", "\u26a0")
        console.print()

    # Good clauses
    if result.good_clauses:
        _print_protections(result.good_clauses)
        console.print()

    # Missing protections
    if result.missing_protections:
        _print_missing(result.missing_protections)
        console.print()

    # Score
    _print_score(result)
    console.print()


def _print_header(result: AnalysisResult) -> None:
    """Print the report header."""
    contract_label = result.contract_type.value.replace("_", " ").upper()
    header = Text()
    header.append("\u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510\n")
    header.append("\u2502  ", style="default")
    header.append("FINEPRINT", style="bold cyan")
    header.append(" Contract Analysis Report  \u2502\n")
    header.append(f"\u2502  Contract Type: {contract_label:<23}\u2502\n")
    header.append("\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518")
    console.print(header)


def _print_summary(result: AnalysisResult) -> None:
    """Print the contract summary."""
    console.print(Panel(
        result.summary,
        title="[bold]Summary[/bold]",
        border_style="blue",
    ))

    if result.parties:
        console.print(f"  [bold]Parties:[/bold] {', '.join(result.parties)}")

    if result.key_terms:
        console.print("  [bold]Key Terms:[/bold]")
        for term in result.key_terms:
            console.print(f"    \u2022 {term}")


def _print_issues(issues: list[Issue], title: str, color: str, icon: str) -> None:
    """Print red flags or warnings."""
    console.print(f"\n[bold {color}]{icon} {title} ({len(issues)} found)[/bold {color}]")
    console.print(f"[{color}]{'=' * 50}[/{color}]")

    for i, issue in enumerate(issues, 1):
        console.print(f"\n  [bold {color}]{i}. {issue.title}[/bold {color}]")
        console.print(f"     [dim]Clause: {issue.clause}[/dim]")
        console.print(f'     [italic]"{issue.quote}"[/italic]')
        console.print(f"     {issue.explanation}")
        console.print(f"     [bold]Suggestion:[/bold] {issue.suggestion}")


def _print_protections(protections: list[Protection]) -> None:
    """Print good clauses found."""
    console.print(f"\n[bold green]\u2714 PROTECTIONS ({len(protections)} found)[/bold green]")
    console.print("[green]{'=' * 50}[/green]")

    for p in protections:
        console.print(f"  [green]\u2714[/green] [bold]{p.title}[/bold] ({p.clause})")
        console.print(f"    {p.explanation}")


def _print_missing(missing: list[str]) -> None:
    """Print missing protections."""
    console.print(
        f"\n[bold dark_orange]\u2753 MISSING PROTECTIONS ({len(missing)})[/bold dark_orange]"
    )
    for item in missing:
        console.print(f"  [dark_orange]\u2717[/dark_orange] {item}")


def _print_score(result: AnalysisResult) -> None:
    """Print the fairness score."""
    grade_color = GRADE_COLORS.get(result.fairness_grade, "white")
    score = result.fairness_score

    # Build score bar
    filled = score // 2
    empty = 50 - filled
    if score >= 70:
        bar_color = "green"
    elif score >= 50:
        bar_color = "yellow"
    else:
        bar_color = "red"

    bar = f"[{bar_color}]{'\u2588' * filled}[/{bar_color}][dim]{'\u2591' * empty}[/dim]"

    console.print(Panel(
        f"  {bar}  [{grade_color}]{result.fairness_grade}[/{grade_color}]  ({score}/100)\n\n"
        f"  [bold red]{len(result.red_flags)}[/bold red] red flags  "
        f"[bold yellow]{len(result.warnings)}[/bold yellow] warnings  "
        f"[bold green]{len(result.good_clauses)}[/bold green] protections  "
        f"[bold dark_orange]{len(result.missing_protections)}[/bold dark_orange] missing",
        title="[bold]FAIRNESS SCORE[/bold]",
        border_style="cyan",
    ))


def generate_markdown_report(result: AnalysisResult) -> str:
    """Generate a markdown report string."""
    lines = [
        f"# Fineprint Contract Analysis Report",
        f"",
        f"**Contract Type:** {result.contract_type.value.replace('_', ' ').title()}",
        f"**Fairness Score:** {result.fairness_grade} ({result.fairness_score}/100)",
        f"**Parties:** {', '.join(result.parties)}",
        f"",
        f"## Summary",
        f"",
        result.summary,
        f"",
        f"## Key Terms",
        f"",
    ]
    for term in result.key_terms:
        lines.append(f"- {term}")

    if result.red_flags:
        lines.extend(["", "## Red Flags", ""])
        for i, issue in enumerate(result.red_flags, 1):
            lines.extend([
                f"### {i}. {issue.title}",
                f"",
                f"**Clause:** {issue.clause}",
                f"",
                f"> {issue.quote}",
                f"",
                f"{issue.explanation}",
                f"",
                f"**Suggestion:** {issue.suggestion}",
                f"",
            ])

    if result.warnings:
        lines.extend(["", "## Warnings", ""])
        for i, issue in enumerate(result.warnings, 1):
            lines.extend([
                f"### {i}. {issue.title}",
                f"",
                f"**Clause:** {issue.clause}",
                f"",
                f"> {issue.quote}",
                f"",
                f"{issue.explanation}",
                f"",
                f"**Suggestion:** {issue.suggestion}",
                f"",
            ])

    if result.good_clauses:
        lines.extend(["", "## Protections Found", ""])
        for p in result.good_clauses:
            lines.append(f"- **{p.title}** ({p.clause}): {p.explanation}")

    if result.missing_protections:
        lines.extend(["", "## Missing Protections", ""])
        for item in result.missing_protections:
            lines.append(f"- {item}")

    return "\n".join(lines)
