#!/usr/bin/env python3

import argparse
import glob
import os
import re
import subprocess
import sys
import yaml
from dataclasses import dataclass
from typing import Any


@dataclass
class Attribute:
    key: str
    line: int | None = None
    comment: str = ""


@dataclass
class ObjectType:
    type_id: str
    path: str
    supertypes: list[str]
    attributes: list[Attribute]


@dataclass
class DuplicateWarning:
    path: str
    line: int
    key: str
    duplicate_type_ids: list[str]


class ScriptError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Warn about duplicate CSMIM object attribute keys in new or "
            "changed type files."
        )
    )
    parser.add_argument(
        "--base",
        required=True,
        help="Git revision to compare the current working tree against.",
    )
    return parser.parse_args()


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        check=False,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise ScriptError(result.stderr.strip())
    return result.stdout


def changed_type_files(base: str) -> list[str]:
    """Return new and modified type files relative to a Git base revision."""
    changed_output = run_git(
        [
            "diff",
            "--name-only",
            "--diff-filter=AM",
            base,
            "--",
            "types/*.yaml",
        ]
    )
    untracked_output = run_git(
        [
            "ls-files",
            "--others",
            "--exclude-standard",
            "--",
            "types/*.yaml",
        ]
    )
    paths = changed_output.splitlines() + untracked_output.splitlines()
    return sorted({path for path in paths if os.path.exists(path)})


def load_yaml(path: str) -> Any:
    """Load YAML content, returning None if PyYAML cannot parse the file."""
    try:
        with open(path, "r", encoding="utf-8") as stream:
            return yaml.safe_load(stream)
    except yaml.YAMLError:
        return None


def local_attributes(content: dict[str, Any]) -> list[Attribute]:
    """Return attributes locally declared in parsed object type content."""
    result: list[Attribute] = []
    for attribute in content.get("attributes", []):
        if isinstance(attribute, dict) and "key" in attribute:
            result.append(Attribute(key=attribute["key"]))
    return result


def find_attribute_line(path: str, key: str) -> tuple[int, str]:
    """
    Find the unique source line for a local attribute declaration.
    Returns the 1-based line number and inline comment text.
    Raises ScriptError if the source line cannot be identified uniquely.
    """
    pattern = re.compile(
        r"^ {0,4}- +key: +"
        + re.escape(key)
        + r"(?: +# *(?P<comment>.*))? *$"
    )

    matches: list[tuple[int, str]] = []
    with open(path, "r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            match = pattern.match(line.rstrip("\n"))
            if match:
                matches.append((line_number, match.group("comment") or ""))

    if len(matches) != 1:
        raise ScriptError(f"{path}: found {len(matches)} source lines for attribute {key!r}")

    return matches[0]


def load_object_type(path: str, require_line_info: bool) -> ObjectType | None:
    """Load one CSMIM object type, or None if this script cannot use it."""
    content = load_yaml(path)
    if not isinstance(content, dict):
        return None
    if "id" not in content:
        return None

    attributes = local_attributes(content)
    if require_line_info:
        for attribute in attributes:
            attribute.line, attribute.comment = find_attribute_line(path, attribute.key)

    return ObjectType(
        type_id=content["id"],
        path=path,
        supertypes=content.get("supertypes", []),
        attributes=attributes,
    )


def load_all_object_types(
    changed_files: list[str],
) -> tuple[dict[str, ObjectType], dict[str, ObjectType]]:
    """
    Load all current type definitions, indexed by type ID and by file path.
    Source-line metadata is collected for changed files only.
    """
    changed_file_set = set(changed_files)
    by_id: dict[str, ObjectType] = {}
    by_path: dict[str, ObjectType] = {}

    for path in sorted(glob.glob("types/*.yaml")):
        object_type = load_object_type(path, path in changed_file_set)
        if object_type is None:
            continue
        by_id[object_type.type_id] = object_type
        by_path[path] = object_type

    return by_id, by_path


def has_local_attribute(object_type: ObjectType, key: str) -> bool:
    return any(attribute.key == key for attribute in object_type.attributes)


def nearest_supertype_declaring_attribute(
    object_type: ObjectType, key: str, types_by_id: dict[str, ObjectType]
) -> str | None:
    """Return the closest supertype that locally declares an attribute."""
    visited = set()
    current_level = list(object_type.supertypes)

    while current_level:
        next_level = []
        for type_id in current_level:
            if type_id in visited:
                continue
            visited.add(type_id)

            supertype = types_by_id.get(type_id)
            if supertype is None:
                continue
            if has_local_attribute(supertype, key):
                return type_id

            next_level.extend(supertype.supertypes)

        current_level = next_level

    return None


def inherits_attribute_from(
    object_type: ObjectType,
    key: str,
    ancestor_type_id: str,
    types_by_id: dict[str, ObjectType],
) -> bool:
    """Return whether a type inherits an attribute from a specific ancestor."""
    visited = set()
    pending = list(object_type.supertypes)

    while pending:
        type_id = pending.pop(0)
        if type_id in visited:
            continue
        visited.add(type_id)

        supertype = types_by_id.get(type_id)
        if supertype is None:
            continue
        if type_id == ancestor_type_id and has_local_attribute(supertype, key):
            return True

        pending.extend(supertype.supertypes)

    return False


def local_attribute_declarations(
    types_by_id: dict[str, ObjectType], key: str, current_type: ObjectType
) -> list[str]:
    """Find unrelated local declarations of an attribute key."""
    result: list[str] = []
    for type_id, object_type in sorted(types_by_id.items()):
        if type_id == current_type.type_id:
            continue
        if has_local_attribute(object_type, key):
            if inherits_attribute_from(object_type, key, current_type.type_id, types_by_id):
                continue
            result.append(type_id)
    return result


def is_suppressed(comment: str, type_id: str) -> bool:
    comment = comment.strip()
    lower_comment = comment.lower()
    has_marker = (
        lower_comment.startswith("from ")
        or lower_comment.startswith("duplicate ")
        or lower_comment.startswith("duplicates ")
    )
    return has_marker and type_id in comment


def duplicate_warnings(
    changed_files: list[str],
    types_by_id: dict[str, ObjectType],
    types_by_path: dict[str, ObjectType],
) -> list[DuplicateWarning]:
    """Build advisory duplicate warnings for changed type files."""
    warnings: list[DuplicateWarning] = []

    for path in changed_files:
        object_type = types_by_path.get(path)
        if object_type is None:
            continue

        for attribute in object_type.attributes:
            inherited_from = nearest_supertype_declaring_attribute(
                object_type, attribute.key, types_by_id
            )
            if inherited_from is not None:
                duplicate_type_ids = [inherited_from]
            else:
                duplicate_type_ids = local_attribute_declarations(types_by_id, attribute.key, object_type)

            duplicate_type_ids = [
                type_id
                for type_id in duplicate_type_ids
                if not is_suppressed(attribute.comment, type_id)
            ]

            if duplicate_type_ids:
                assert attribute.line is not None
                warnings.append(
                    DuplicateWarning(
                        path=path,
                        line=attribute.line,
                        key=attribute.key,
                        duplicate_type_ids=duplicate_type_ids,
                    )
                )

    return warnings


def escape_annotation_value(value: object) -> str:
    """Escape a GitHub workflow annotation data value."""
    return (
        str(value)
        .replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
    )


def escape_annotation_property(value: object) -> str:
    """Escape a GitHub workflow annotation property value."""
    return (
        escape_annotation_value(value)
        .replace(":", "%3A")
        .replace(",", "%2C")
    )


def emit_annotation(warning: DuplicateWarning) -> None:
    title = f"Duplicate attribute {warning.key}"
    duplicates = ", ".join(warning.duplicate_type_ids)
    message = f"Attribute {warning.key!r} is also declared in {duplicates}."
    print(
        "::warning "
        f"file={escape_annotation_property(warning.path)},"
        f"line={escape_annotation_property(warning.line)},"
        f"title={escape_annotation_property(title)}"
        f"::{escape_annotation_value(message)}"
    )


def main() -> int:
    args = parse_args()
    changed_files = changed_type_files(args.base)
    types_by_id, types_by_path = load_all_object_types(changed_files)
    warnings = duplicate_warnings(changed_files, types_by_id, types_by_path)

    for warning in warnings:
        emit_annotation(warning)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ScriptError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
