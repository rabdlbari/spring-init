# spring-init

Scaffold Spring Boot projects from your terminal — an interactive CLI mirroring the [Spring Initializr](https://start.spring.io) website.

```bash
uv run spring-init
```

## Features

- **Interactive wizard** — step through every option the website offers
- **Live metadata** — fetches available Spring Boot versions, Java versions, and dependencies directly from `start.spring.io` (cached 1 hour)
- **Fuzzy dependency search** — type to filter, grouped by category (Core, Web, SQL, Security, ...)
- **Gradle or Maven** — Groovy/Kotlin Gradle DSL and Maven project types
- **Edit-before-generate** — review a summary and go back to adjust dependencies
- **Auto-extracted project** — downloads the zip, extracts it, and prints the run command

## Installing

### With uv (recommended)

```bash
uv tool install --from . spring-init
```

or run directly from a checkout:

```bash
uv run spring-init
```

### With pip

```bash
pip install .
```

## Usage

Run the interactive wizard:

```bash
spring-init
```

It walks you through:

| Step | Prompt |
|------|--------|
| 1 | Project type (Gradle - Groovy / Gradle - Kotlin / Maven) |
| 2 | Language (Java / Kotlin / Groovy) |
| 3 | Spring Boot version |
| 4–8 | Group, Artifact, Name, Description, Package name |
| 9 | Packaging (Jar / War) |
| 10 | Java version |
| 11 | Dependencies (searchable, multi-select) |
| 12 | Output directory |

After the summary, you can **Generate**, **Edit dependencies** (return to step 11 with your selections preserved), or **Cancel**.

Once generated, the project is extracted to your output directory and the build command is printed:

```bash
cd ./demo && ./mvnw spring-boot:run
# or
cd ./demo && ./gradlew bootRun
```

## How it works

`spring-init` calls the public Spring Initializr REST API:

- **Metadata**: `GET https://start.spring.io/metadata/client` — discovers available types, languages, versions, and dependencies. Cached to `~/.cache/spring-init/metadata.json`.
- **Generation**: `GET https://start.spring.io/starter.zip` — downloads a ready-to-build project zip.

Because metadata is fetched live, `spring-init` always tracks the latest Spring Boot releases and dependencies — no manual updates needed.

## Project layout

```
src/spring_init/
├── cli.py       # Wizard orchestration and error handling
├── api.py       # Spring Initializr API client + metadata cache
├── prompts.py   # Interactive prompts (questionary)
├── ui.py        # Terminal UI (rich banners/panels/tables)
└── models.py    # Dataclasses for project config and metadata
```

## Requirements

- Python 3.12+
- Network access to `start.spring.io`

## License

MIT
