from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProjectConfig:
    project_type: str = "gradle-project"
    language: str = "java"
    boot_version: str = "4.1.1"
    group_id: str = "com.example"
    artifact_id: str = "demo"
    name: str = "demo"
    description: str = "Demo project for Spring Boot"
    package_name: str = "com.example.demo"
    packaging: str = "jar"
    java_version: str = "17"
    dependencies: list[str] = field(default_factory=list)
    output_dir: str = "."

    def to_query_params(self) -> dict[str, str]:
        return {
            "type": self.project_type,
            "language": self.language,
            "bootVersion": self.boot_version,
            "groupId": self.group_id,
            "artifactId": self.artifact_id,
            "name": self.name,
            "description": self.description,
            "packageName": self.package_name,
            "packaging": self.packaging,
            "javaVersion": self.java_version,
            "dependencies": ",".join(self.dependencies),
        }


@dataclass
class ProjectType:
    id: str
    name: str


@dataclass
class SpringBootVersion:
    id: str
    name: str
    api_value: str


@dataclass
class Dependency:
    id: str
    name: str
    description: str = ""


@dataclass
class DependencyGroup:
    name: str
    values: list[Dependency] = field(default_factory=list)


@dataclass
class Metadata:
    project_types: list[ProjectType] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    boot_versions: list[SpringBootVersion] = field(default_factory=list)
    java_versions: list[str] = field(default_factory=list)
    packaging_options: list[str] = field(default_factory=list)
    dependency_groups: list[DependencyGroup] = field(default_factory=list)
