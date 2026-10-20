#!/usr/bin/env python3
"""Non-executing OOXML audit for the preserved macro-enabled workbook.

The audit never imports table values into the public model and never executes
VBA, Excel formulas, add-ins, external links, or cached solver state.  It emits
only structural metadata, cryptographic digests, safe version text, and boolean
indicators needed to explain why the workbook is audit-only.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
from typing import Any
import xml.etree.ElementTree as ET
import zipfile


SHEET_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
DOC_REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PACKAGE_REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
CORE_NS = "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}"
DC_NS = "{http://purl.org/dc/elements/1.1/}"
DCTERMS_NS = "{http://purl.org/dc/terms/}"
EXTENDED_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}"
CELL_RE = re.compile(r"^([A-Z]+)([0-9]+)$")
RANGE_RE = re.compile(r"^([A-Z]+)([0-9]+):([A-Z]+)([0-9]+)$")
CANONICALIZATION = "ooxml-cached-cell-token-grid-v1"


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def column_number(letters: str) -> int:
    result = 0
    for letter in letters:
        result = result * 26 + ord(letter) - ord("A") + 1
    return result


def column_letters(number: int) -> str:
    output = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        output = chr(ord("A") + remainder) + output
    return output


def normalize_number(raw: str) -> str:
    try:
        value = Decimal(raw)
    except InvalidOperation:
        return raw
    if value == 0:
        return "0"
    normalized = value.normalize()
    rendered = format(normalized, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def relationships(archive: zipfile.ZipFile) -> dict[str, str]:
    root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    output = {}
    for relationship in root.findall(f"{PACKAGE_REL_NS}Relationship"):
        target = relationship.attrib["Target"].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        output[relationship.attrib["Id"]] = target
    return output


def shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    output = []
    for item in root.findall(f"{SHEET_NS}si"):
        output.append("".join(node.text or "" for node in item.iter(f"{SHEET_NS}t")))
    return output


def workbook_sheet_paths(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    root = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = relationships(archive)
    output = []
    sheets = root.find(f"{SHEET_NS}sheets")
    for sheet in [] if sheets is None else list(sheets):
        name = sheet.attrib["name"]
        relation_id = sheet.attrib[f"{DOC_REL_NS}id"]
        output.append((name, rels[relation_id]))
    return output


def cell_text(cell: ET.Element, strings: list[str]) -> str | None:
    cell_type = cell.attrib.get("t")
    value = cell.find(f"{SHEET_NS}v")
    if cell_type == "inlineStr":
        text = "".join(node.text or "" for node in cell.iter(f"{SHEET_NS}t"))
        return text
    if value is None or value.text is None:
        return None
    if cell_type == "s":
        try:
            return strings[int(value.text)]
        except (ValueError, IndexError):
            return None
    return value.text


def cell_token(cell: ET.Element, strings: list[str]) -> str:
    cell_type = cell.attrib.get("t", "n")
    text = cell_text(cell, strings)
    if text is None:
        return "blank:"
    if cell_type == "s" or cell_type == "inlineStr" or cell_type == "str":
        return "text:" + text
    if cell_type == "b":
        return "bool:" + text
    if cell_type == "e":
        return "error:" + text
    return "number:" + normalize_number(text)


def worksheet_cells(
    archive: zipfile.ZipFile, sheet_path: str, strings: list[str]
) -> tuple[ET.Element, dict[str, ET.Element]]:
    root = ET.fromstring(archive.read(sheet_path))
    cells = {}
    for cell in root.iter(f"{SHEET_NS}c"):
        coordinate = cell.attrib.get("r")
        if coordinate:
            cells[coordinate] = cell
    return root, cells


def range_digest(
    sheet_name: str,
    range_reference: str,
    cells: dict[str, ET.Element],
    strings: list[str],
) -> str:
    match = RANGE_RE.match(range_reference)
    if not match:
        raise ValueError(f"invalid range reference: {range_reference}")
    col0, row0, col1, row1 = match.groups()
    first_column = column_number(col0)
    last_column = column_number(col1)
    grid = []
    for row in range(int(row0), int(row1) + 1):
        output_row = []
        for column in range(first_column, last_column + 1):
            coordinate = f"{column_letters(column)}{row}"
            cell = cells.get(coordinate)
            output_row.append("blank:" if cell is None else cell_token(cell, strings))
        grid.append(output_row)
    payload = {
        "canonicalization": CANONICALIZATION,
        "sheet": sheet_name,
        "range": range_reference,
        "tokens": grid,
    }
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def safe_properties(archive: zipfile.ZipFile) -> dict[str, str | None]:
    output: dict[str, str | None] = {
        "created": None,
        "modified": None,
        "application": None,
        "links_up_to_date": None,
    }
    if "docProps/core.xml" in archive.namelist():
        root = ET.fromstring(archive.read("docProps/core.xml"))
        created = root.find(f"{DCTERMS_NS}created")
        modified = root.find(f"{DCTERMS_NS}modified")
        output["created"] = None if created is None else created.text
        output["modified"] = None if modified is None else modified.text
    if "docProps/app.xml" in archive.namelist():
        root = ET.fromstring(archive.read("docProps/app.xml"))
        application = root.find(f"{EXTENDED_NS}Application")
        links = root.find(f"{EXTENDED_NS}LinksUpToDate")
        output["application"] = None if application is None else application.text
        output["links_up_to_date"] = None if links is None else links.text
    return output


def audit_workbook(
    workbook_path: Path,
    pins_document: dict[str, Any],
    reference_path: Path | None = None,
) -> dict[str, Any]:
    expected = pins_document["preserved_workbook"]
    actual_file_hash = sha256_file(workbook_path)
    file_size = workbook_path.stat().st_size
    with zipfile.ZipFile(workbook_path, "r") as archive:
        infos = archive.infolist()
        names = archive.namelist()
        strings = shared_strings(archive)
        workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
        defined_names = workbook_root.find(f"{SHEET_NS}definedNames")
        defined_name_text = "\n".join(
            (node.attrib.get("name", "") + " " + (node.text or ""))
            for node in ([] if defined_names is None else list(defined_names))
        ).lower()

        sheet_inventory = []
        sheet_data: dict[str, dict[str, ET.Element]] = {}
        indicator_matches: list[dict[str, str]] = []
        formula_udf_count = 0
        confidentiality_count = 0
        indicator_needles = {
            "event_time_001730": ("00:17:30", "mefe"),
            "legacy_time_1822": ("18:22",),
            "legacy_sd_045t": ("0.45", "450"),
        }
        for sheet_name, sheet_path in workbook_sheet_paths(archive):
            root, cells = worksheet_cells(archive, sheet_path, strings)
            sheet_data[sheet_name] = cells
            dimension = root.find(f"{SHEET_NS}dimension")
            formulas = list(root.iter(f"{SHEET_NS}f"))
            formula_udf_count += sum(
                1 for formula in formulas if "bicubicinterpolation" in (formula.text or "").lower()
            )
            for coordinate, cell in cells.items():
                formula = cell.find(f"{SHEET_NS}f")
                searchable = " ".join(
                    part
                    for part in (cell_text(cell, strings), None if formula is None else formula.text)
                    if part
                ).lower()
                if "confidential" in searchable and "boeing" in searchable:
                    confidentiality_count += 1
                for indicator, needles in indicator_needles.items():
                    if all(needle in searchable for needle in needles):
                        indicator_matches.append(
                            {
                                "indicator": indicator,
                                "sheet": sheet_name,
                                "cell": coordinate,
                                "content_sha256": sha256_bytes(searchable.encode("utf-8")),
                            }
                        )
            sheet_inventory.append(
                {
                    "name": sheet_name,
                    "dimension": None if dimension is None else dimension.attrib.get("ref"),
                    "cell_count": len(cells),
                    "formula_count": len(formulas),
                }
            )

        version_cell = sheet_data["Fuel Flow Model"].get("B9")
        version_text = None if version_cell is None else cell_text(version_cell, strings)
        range_results = []
        for pin in pins_document["ranges"]:
            actual = range_digest(
                pin["sheet"], pin["range"], sheet_data[pin["sheet"]], strings
            )
            range_results.append(
                {
                    "id": pin["id"],
                    "sheet": pin["sheet"],
                    "range": pin["range"],
                    "canonical_value_sha256": actual,
                    "matches_pin": actual == pin["canonical_value_sha256"],
                    "integration_status": "audit-only-not-integrated",
                }
            )

        macro_name = "xl/vbaProject.bin"
        macro_hash = sha256_bytes(archive.read(macro_name)) if macro_name in names else None
        external_parts = sorted(
            name
            for name in names
            if name.startswith("xl/externalLinks/externalLink") and not name.endswith(".rels")
        )
        output: dict[str, Any] = {
            "schema_version": 1,
            "audit_policy": {
                "macros_executed": False,
                "formulas_recalculated": False,
                "external_links_followed": False,
                "table_values_exported": False,
                "workbook_used_by_public_model": False,
            },
            "file": {
                "name": workbook_path.name,
                "size_bytes": file_size,
                "sha256": actual_file_hash,
                "matches_preserved_pin": actual_file_hash == expected["sha256"],
                "matches_size_pin": file_size == expected["size_bytes"],
            },
            "package": {
                "member_count": len(infos),
                "compressed_bytes": sum(info.compress_size for info in infos),
                "uncompressed_bytes": sum(info.file_size for info in infos),
                "sheet_count": len(sheet_inventory),
                "chart_xml_count": sum(
                    1 for name in names if name.startswith("xl/charts/chart") and name.endswith(".xml")
                ),
                "image_count": sum(1 for name in names if name.startswith("xl/media/")),
                "external_link_count": len(external_parts),
                "external_link_part_hashes": [sha256_bytes(archive.read(name)) for name in external_parts],
                "connection_part_present": "xl/connections.xml" in names,
                "custom_xml_present": any(name.startswith("customXml/") for name in names),
                "embedded_object_count": sum(1 for name in names if name.startswith("xl/embeddings/")),
                "calc_chain_present": "xl/calcChain.xml" in names,
            },
            "properties": safe_properties(archive),
            "macro": {
                "present": macro_hash is not None,
                "sha256": macro_hash,
                "matches_pin": macro_hash == expected["vba_project_sha256"],
                "signature_present": any("vbaProjectSignature" in name for name in names),
                "executed": False,
            },
            "version": {
                "safe_cell": "Fuel Flow Model!B9",
                "text": version_text,
                "text_sha256": None if version_text is None else sha256_bytes(version_text.encode("utf-8")),
                "matches_pin": version_text == expected["version_text"],
            },
            "formula_environment": {
                "bicubic_interpolation_formula_count": formula_udf_count,
                "risk_defined_name_present": "risk" in defined_name_text,
                "solver_defined_name_present": "solver" in defined_name_text,
                "independently_recalculable_here": False,
            },
            "rights_and_circularity": {
                "boeing_confidential_notice_count": confidentiality_count,
                "confidential_content_present": confidentiality_count > 0,
                "calibration_indicator_matches": sorted(
                    indicator_matches,
                    key=lambda row: (row["indicator"], row["sheet"], row["cell"]),
                ),
                "tables_redistributed": False,
                "tables_integrated": False,
                "reason": "Mixed provenance and confidential notices prevent safe redistribution; event-linked calibration prevents independent use.",
            },
            "sheets": sheet_inventory,
            "range_pins": range_results,
            "public_reference_pin_attestation": {
                **pins_document["comparison_attestation"],
                "public_workbook_sha256": pins_document["public_reference_workbook"]["sha256"],
                "current_ranges_match_attested_pins": all(
                    row["matches_pin"] for row in range_results
                ),
                "fresh_reference_compared_this_run": reference_path is not None,
            },
        }

        if reference_path is not None:
            reference_hash = sha256_file(reference_path)
            with zipfile.ZipFile(reference_path, "r") as reference_archive:
                reference_strings = shared_strings(reference_archive)
                reference_sheets = {}
                for name, path in workbook_sheet_paths(reference_archive):
                    _, reference_sheets[name] = worksheet_cells(reference_archive, path, reference_strings)
                equal_ranges = []
                for pin in pins_document["ranges"]:
                    reference_digest = range_digest(
                        pin["sheet"],
                        pin["range"],
                        reference_sheets[pin["sheet"]],
                        reference_strings,
                    )
                    preserved_digest = next(
                        row["canonical_value_sha256"]
                        for row in range_results
                        if row["id"] == pin["id"]
                    )
                    equal_ranges.append(reference_digest == preserved_digest)
                common_names = set(names) & set(reference_archive.namelist())
                changed_parts = sum(
                    1
                    for name in common_names
                    if sha256_bytes(archive.read(name)) != sha256_bytes(reference_archive.read(name))
                )
                changed_parts += len(set(names) ^ set(reference_archive.namelist()))
                output["public_reference_comparison"] = {
                    "sha256": reference_hash,
                    "matches_public_reference_pin": reference_hash
                    == pins_document["public_reference_workbook"]["sha256"],
                    "ooxml_changed_part_count": changed_parts,
                    "all_audited_range_values_equal": all(equal_ranges),
                    "equal_range_count": sum(equal_ranges),
                    "range_count": len(equal_ranges),
                    "table_values_exported": False,
                }

    checks = [
        output["file"]["matches_preserved_pin"],
        output["file"]["matches_size_pin"],
        output["macro"]["matches_pin"],
        output["version"]["matches_pin"],
        output["package"]["sheet_count"] == expected["sheet_count"],
        all(row["matches_pin"] for row in output["range_pins"]),
        output["rights_and_circularity"]["confidential_content_present"],
    ]
    if reference_path is not None:
        checks.extend(
            [
                output["public_reference_comparison"]["matches_public_reference_pin"],
                output["public_reference_comparison"]["all_audited_range_values_equal"],
            ]
        )
    output["audit_passed"] = all(checks)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--pins", type=Path, required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--discover", action="store_true", help="print computed digests even when pins are placeholders")
    arguments = parser.parse_args()
    pins = json.loads(arguments.pins.read_text(encoding="utf-8"))
    audit = audit_workbook(arguments.workbook, pins, arguments.reference)
    print(json.dumps(audit, indent=2, sort_keys=True))
    return 0 if audit["audit_passed"] or arguments.discover else 1


if __name__ == "__main__":
    raise SystemExit(main())
