from __future__ import annotations

import sys
import zipfile
from pathlib import Path

from .api import fetch_metadata, generate_project
from .models import ProjectConfig
from .prompts import (
    confirm_generate,
    input_artifact,
    input_description,
    input_group,
    input_name,
    input_output_dir,
    input_package,
    select_boot_version,
    select_dependencies,
    select_java_version,
    select_language,
    select_packaging,
    select_project_type,
    select_extract,
)
from .ui import console, print_banner, print_summary


def run_wizard() -> None:
    print_banner()

    console.print("[dim]Fetching metadata from Spring Initializr...[/dim]")
    try:
        metadata = fetch_metadata()
    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[red]Failed to fetch metadata: {e}[/red]")
        sys.exit(1)

    console.print("[dim]Metadata loaded.[/dim]\n")

    project_type = select_project_type(metadata)
    if project_type is None:
        sys.exit(0)

    language = select_language(metadata)
    if language is None:
        sys.exit(0)

    boot_version = select_boot_version(metadata)
    if boot_version is None:
        sys.exit(0)
    boot_version_api = next(
        (v.api_value for v in metadata.boot_versions if v.id == boot_version),
        boot_version,
    )

    group_id = input_group()
    if group_id is None:
        sys.exit(0)

    artifact_id = input_artifact()
    if artifact_id is None:
        sys.exit(0)

    name = input_name(default=artifact_id)
    if name is None:
        sys.exit(0)

    description = input_description()
    if description is None:
        sys.exit(0)

    default_package = f"{group_id}.{artifact_id}".replace("-", ".")
    package_name = input_package(default=default_package)
    if package_name is None:
        sys.exit(0)

    packaging = select_packaging(metadata)
    if packaging is None:
        sys.exit(0)

    java_version = select_java_version(metadata)
    if java_version is None:
        sys.exit(0)

    dependencies = select_dependencies(metadata)
    if dependencies is None:
        sys.exit(0)

    output_dir = input_output_dir(artifact_id)
    if output_dir is None:
        sys.exit(0)

    config = ProjectConfig(
        project_type=project_type,
        language=language,
        boot_version=boot_version_api,
        group_id=group_id,
        artifact_id=artifact_id,
        name=name,
        description=description,
        package_name=package_name,
        packaging=packaging,
        java_version=java_version,
        dependencies=dependencies,
        output_dir=output_dir,
    )

    while True:
        print_summary(config)
        action = confirm_generate()
        if action is None or action == "cancel":
            console.print("[yellow]Aborted.[/yellow]")
            sys.exit(0)
        if action == "edit_deps":
            config.dependencies = select_dependencies(metadata, preselected=config.dependencies)
            if config.dependencies is None:
                sys.exit(0)
            continue
        break

    zip_path = Path(output_dir) / f"{artifact_id}.zip"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    console.print("[dim]Generating project...[/dim]")

    attempts = [boot_version_api]
    unstable = "SNAPSHOT" in boot_version_api or "-M" in boot_version_api or "-RC" in boot_version_api
    if unstable:
        stable = next((v.api_value for v in metadata.boot_versions
                       if "SNAPSHOT" not in v.id and ".M" not in v.id and ".RC" not in v.id), None)
        if stable:
            attempts.append(stable)

    try:
        generate_project(config.to_query_params(), zip_path)
    except SystemExit:
        raise
    except Exception as e:
        if len(attempts) > 1:
            console.print(f"[yellow]Version {boot_version} failed, retrying with {attempts[1]}...[/yellow]")
            config.boot_version = attempts[1]
            try:
                generate_project(config.to_query_params(), zip_path)
            except SystemExit:
                raise
            except Exception as e2:
                console.print(f"[red]Generation failed: {e2}[/red]")
                console.print("[dim]This may be a temporary issue with the Spring Initializr service. Try again later.[/dim]")
                sys.exit(1)
        else:
            console.print(f"[red]Generation failed: {e}[/red]")
            console.print("[dim]This may be a temporary issue with the Spring Initializr service. Try again or select Maven instead of Gradle.[/dim]")
            sys.exit(1)

    output_path = Path(output_dir)

    if select_extract(f"{artifact_id}.zip"):
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(output_path)
        zip_path.unlink()
        console.print(f"\n[green bold]Project generated successfully![/green bold]")
        console.print(f"[dim]Location: {output_path.resolve()}[/dim]\n")

        if project_type.startswith("maven"):
            console.print("[dim]  cd {} && ./mvnw spring-boot:run[/dim]".format(output_dir))
        else:
            console.print("[dim]  cd {} && ./gradlew bootRun[/dim]".format(output_dir))
        console.print()
    else:
        console.print(f"\n[green bold]Project generated successfully![/green bold]")
        console.print(f"[dim]Zip saved: {zip_path.resolve()}[/dim]")
        console.print(f"[dim]Extract it with: unzip {artifact_id}.zip[/dim]\n")


def main() -> None:
    try:
        run_wizard()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(130)
