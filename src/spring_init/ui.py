from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .models import ProjectConfig

console = Console()


def print_banner() -> None:
    console.print()
    console.print(
        Panel(
            "[bold #22c55e]Spring[/] [bold white]Initializer[/]\n"
            "[dim]Scaffold Spring Boot projects from your terminal[/dim]",
            title="[bold]spring-init[/bold]",
            subtitle=f"[dim]v{__version__}[/dim]",
            border_style="green",
            padding=(1, 2),
            width=48,
        )
    )
    console.print()


def print_summary(config: ProjectConfig) -> None:
    table = Table(show_header=False, border_style="dim", padding=(0, 2))
    table.add_column("Field", style="bold cyan", width=16)
    table.add_column("Value")
    table.add_row("Project type", config.project_type)
    table.add_row("Language", config.language)
    table.add_row("Boot version", config.boot_version)
    table.add_row("Group", config.group_id)
    table.add_row("Artifact", config.artifact_id)
    table.add_row("Name", config.name)
    table.add_row("Description", config.description)
    table.add_row("Package", config.package_name)
    table.add_row("Packaging", config.packaging)
    table.add_row("Java version", config.java_version)
    table.add_row("Dependencies", ", ".join(config.dependencies) if config.dependencies else "(none)")
    table.add_row("Output", str(config.output_dir))

    console.print()
    console.print(Panel(table, title="[bold]Project Configuration[/bold]", border_style="blue"))
    console.print()
