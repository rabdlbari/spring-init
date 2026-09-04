from __future__ import annotations

import questionary

from .models import Metadata


def select_project_type(metadata: Metadata) -> str:
    choices = [questionary.Choice(title=t.name, value=t.id) for t in metadata.project_types]
    return questionary.select("Project type:", choices=choices).ask()


def select_language(metadata: Metadata) -> str:
    choices = [questionary.Choice(title=l.capitalize(), value=l) for l in metadata.languages]
    return questionary.select("Language:", choices=choices).ask()


def select_boot_version(metadata: Metadata) -> str:
    choices = []
    for v in metadata.boot_versions:
        unstable = "SNAPSHOT" in v.id or ".M" in v.id or ".RC" in v.id
        label = f"{v.name} (unstable)" if unstable else v.name
        choices.append(questionary.Choice(title=label, value=v.id))
    return questionary.select("Spring Boot version:", choices=choices).ask()


def input_group(default: str = "com.example") -> str:
    return questionary.text("Group:", default=default).ask()


def input_artifact(default: str = "demo") -> str:
    return questionary.text("Artifact:", default=default).ask()


def input_name(default: str = "demo") -> str:
    return questionary.text("Name:", default=default).ask()


def input_description(default: str = "Demo project for Spring Boot") -> str:
    return questionary.text("Description:", default=default).ask()


def input_package(default: str = "com.example.demo") -> str:
    return questionary.text("Package name:", default=default).ask()


def select_packaging(metadata: Metadata) -> str:
    choices = [questionary.Choice(title=p.capitalize(), value=p) for p in metadata.packaging_options]
    return questionary.select("Packaging:", choices=choices).ask()


def select_java_version(metadata: Metadata) -> str:
    choices = [questionary.Choice(title=v, value=v) for v in metadata.java_versions]
    return questionary.select("Java version:", choices=choices).ask()


def select_dependencies(metadata: Metadata, preselected: list[str] | None = None) -> list[str]:
    preselected = preselected or []
    choices = []
    for group in metadata.dependency_groups:
        choices.append(questionary.Separator(line=f"── {group.name} ──"))
        for dep in group.values:
            label = dep.name
            if dep.description:
                label = f"{dep.name}  ({dep.description[:60]})"
            choices.append(questionary.Choice(
                title=label,
                value=dep.id,
                checked=dep.id in preselected,
            ))

    selected = questionary.checkbox(
        "Search dependencies (type to filter, space to select, enter to confirm):",
        choices=choices,
        use_search_filter=True,
        use_jk_keys=False,
        instruction="Type to search. ↑↓ to navigate, space to select, enter to confirm.",
    ).ask()

    return selected if selected else []


def input_output_dir(artifact: str) -> str:
    return questionary.text("Output directory:", default=f"./{artifact}").ask()


def confirm_generate() -> str:
    return questionary.select(
        "What would you like to do?",
        choices=[
            questionary.Choice(title="Generate project", value="generate"),
            questionary.Choice(title="Edit dependencies", value="edit_deps"),
            questionary.Choice(title="Cancel", value="cancel"),
        ],
    ).ask()


def select_extract(zip_name: str) -> bool:
    return questionary.confirm(
        f"Extract '{zip_name}' into the output directory?", default=True
    ).ask()
