#!/usr/bin/env python3
"""
reZEN File & Checklist Organizer (Standalone Tool)
===================================================
Automatically organizes, renames, and prepares transaction contract PDFs
from your local computer or Google Drive folder for upload to reZEN.

Key Capabilities:
1. Document Classifier: Detects standard Mississippi & General Real Estate forms:
   - T01: Purchase Contract / Contract for Sale & Purchase / Base Offer
   - T02: Earnest Money Receipt / Escrow Deposit Verification
   - T03: Addendum / Counter Offer / Counters
   - T08: Inspection Contingency Notification / Removal / Agreed Repairs
   - T09: Termite / WDIR / Wood Destroying Insect Report & Invoices
   - L01: Working With a Real Estate Broker (Agency Disclosure)
   - L02/L05: Exclusive Authorization & Right to Sell Listing Agreement
   - L06: Lead-Based Paint Disclosure (pre-1978 properties)
   - CD:  Settlement Statement / Closing Disclosure / ALTA
   - CDA: Commission Disbursement Authorization / Validation
2. Auto-Renamer: Renames files to standard compliance format:
   "[CODE] - [Form Name] - [Details].pdf"
3. File Cabinet Router: Converts property address into exact reZEN email:
   "<sanitized-address-slug>-t@rezenfilecabinet.com"
4. Email Dispatch Prepper: Generates a ready-to-send email draft with
   proper subject lines, checklist slot notes, and attachment lists.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DOCUMENT_PATTERNS = [
    (r"(purchase\s*contract|contract\s*for\s*(the\s*)?sale|base\s*offer|base\s*sale)", "T01", "Purchase Contract - Base Offer"),
    (r"(earnest\s*money|escrow|emd|deposit\s*receipt)", "T02", "Earnest Money Deposit Receipt"),
    (r"(counter\s*offer|counter\b|addend(um|a)|amendment\b)", "T03", "Counters and Addenda"),
    (r"(inspection\s*contingency|repair\s*(list|counter|amendment)|repair\s*addendum|walk-through)", "T08", "Home Inspection Contingency Removal"),
    (r"(wdir|termite|wood\s*destroying|pest\s*inspection)", "T09", "WDIR Termite Inspection and Report"),
    (r"(working\s*with\s*(a\s*)?real\s*estate\s*broker|agency\s*disclosure|dual\s*agency)", "L01", "Working With a Real Estate Broker"),
    (r"(exclusive\s*(right\s*to\s*sell|authorization)|listing\s*agreement)", "L05", "Exclusive Right to Sell Listing Agreement"),
    (r"(lead[- ]*based[ ]*paint|lead[ ]*paint|l06)", "L06", "Lead-Based Paint Disclosure"),
    (r"(pcds|property\s*condition\s*disclosure)", "L07", "Property Condition Disclosure Statement"),
    (r"(closing\s*disclosure|\bcd\b|settlement\s*statement|alta|hud-1)", "CD", "Settlement Statement - Closing Disclosure"),
    (r"(cda|commission\s*disbursement|commission\s*doc)", "CDA", "Commission Disbursement Authorization"),
]


def generate_file_cabinet_email(address: str) -> str:
    """Convert address to reZEN file cabinet email."""
    first_part = address.split(",")[0].strip()
    clean = re.sub(r"[^a-zA-Z0-9]", "", first_part).lower()
    if not clean or "\n" in address or "\r" in address:
        raise ValueError("A nonempty, single-line property address is required")
    return f"{clean}-t@rezenfilecabinet.com"


def classify_filename(filename: str) -> Tuple[Optional[str], Optional[str]]:
    """Identify reZEN code and clean description based on filename."""
    prefix = re.match(r"^(T\d\d|L\d\d|CDA|CD)\s*-\s*", filename, re.IGNORECASE)
    if prefix:
        return prefix.group(1).upper(), "Existing checklist label"
    name_lower = filename.lower()
    # Specific inspection rules must precede generic addendum/amendment rules.
    repair = next(rule for rule in DOCUMENT_PATTERNS if rule[1] == "T08")
    if re.search(repair[0], name_lower):
        return repair[1], repair[2]
    for pattern, code, description in DOCUMENT_PATTERNS:
        if re.search(pattern, name_lower):
            return code, description
    return None, None


def organize_and_rename_directory(
    source_dir: str,
    output_dir: Optional[str] = None,
    dry_run: bool = True
) -> List[Dict[str, str]]:
    """Scan directory, match forms, and rename/copy them."""
    src_path = Path(source_dir)
    dest_path = Path(output_dir) if output_dir else src_path

    if not src_path.is_dir():
        raise ValueError(f"Source path is not a directory: {source_dir}")

    results = []
    reserved = set()
    pdf_files = sorted([f for f in src_path.iterdir() if f.is_file() and not f.is_symlink() and f.suffix.lower() == ".pdf"])

    for pdf in pdf_files:
        original_name = pdf.name
        code, desc = classify_filename(original_name)

        # Check if already has valid code prefix
        has_prefix = bool(re.match(r"^(T\d\d|L\d\d|CD|CDA)\s*-\s*", original_name, re.IGNORECASE))

        if has_prefix:
            target_name = original_name
            status = "Already labeled"
        elif code and desc:
            clean_suffix = original_name
            target_name = f"{code} - {clean_suffix}"
            status = f"Renamed to {code}"
        else:
            target_name = original_name
            status = "Needs manual label"

        results.append({
            "original_path": str(pdf),
            "original_name": original_name,
            "target_name": target_name,
            "code": code or "UNKNOWN",
            "status": status
        })

        destination = dest_path / target_name
        needs_write = destination.resolve() != pdf.resolve()
        key = target_name.casefold()
        if needs_write and (destination.exists() or key in reserved):
            raise FileExistsError(f"Destination collision: {destination}; no files changed")
        reserved.add(key)

    # Preflight every destination before changing any file.
    if not dry_run:
        if output_dir:
            dest_path.mkdir(parents=True, exist_ok=True)
        for record in results:
            source = Path(record["original_path"])
            destination = dest_path / record["target_name"]
            if source.resolve() == destination.resolve():
                continue
            # Exclusive creation also protects against files created after preflight.
            try:
                with destination.open("xb") as out, source.open("rb") as inp:
                    shutil.copyfileobj(inp, out)
            except FileExistsError:
                raise
            except Exception:
                destination.unlink(missing_ok=True)
                raise
            shutil.copystat(source, destination)
            if not output_dir:
                source.unlink()

    return results


def generate_dispatch_summary(
    property_address: str,
    organized_records: List[Dict[str, str]],
    agent_name: str = "Austin Walker"
) -> str:
    """Format the email body and subject line for sending to reZEN."""
    email_to = generate_file_cabinet_email(property_address)

    recognized_codes = sorted(list(set(
        r["code"] for r in organized_records if r["code"] != "UNKNOWN"
    )))
    codes_str = " ".join(recognized_codes)

    subject = f"{property_address.split(',')[0].strip()} - Checklist-Labeled Documents - {codes_str}".strip()

    lines = [
        f"To: {email_to}",
        f"Subject: {subject}",
        "",
        f"Hello reZEN Compliance Team / Broker,",
        "",
        f"Please review the listed documents and verify signatures and completeness for {property_address}.",
        f"The listed files have been labeled for their corresponding reZEN checklist rows:",
        ""
    ]

    for r in organized_records:
        if r["code"] != "UNKNOWN":
            lines.append(f"  • [{r['code']}] {r['target_name']}")
        else:
            lines.append(f"  • [UNLABELED] {r['original_name']}")

    lines.extend([
        "",
        "Please review and verify compliance for these items.",
        "",
        f"Best regards,",
        f"{agent_name}",
        "Real Broker, LLC"
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="reZEN Contract PDF Organizer & File Cabinet Prepper")
    parser.add_argument("directory", help="Path to folder containing PDF contract files")
    parser.add_argument("--address", default="", help="Property address (e.g. '804 Lafayette Street, Columbia, MS 39429')")
    parser.add_argument("--output", help="Optional destination directory to save renamed copies")
    parser.add_argument("--apply", action="store_true", help="Apply renames/copies (defaults to dry-run preview)")
    parser.add_argument("--agent", default="Austin Walker", help="Agent name for email dispatch")

    args = parser.parse_args()

    print("================================================================================")
    print("                 reZEN FILE & CHECKLIST ORGANIZATION TOOL                       ")
    print("================================================================================")

    if args.address:
        print(f"Property Address: {args.address}")
        print(f"reZEN File Cabinet Email: {generate_file_cabinet_email(args.address)}")
    print(f"Scanning Directory: {args.directory}")
    print(f"Mode: {'APPLY CHANGES' if args.apply else 'DRY RUN PREVIEW'}")
    print("--------------------------------------------------------------------------------")

    records = organize_and_rename_directory(
        source_dir=args.directory,
        output_dir=args.output,
        dry_run=not args.apply
    )

    print(f"\nDiscovered {len(records)} PDF file(s):\n")
    for r in records:
        print(f"  [{r['code']:<5}] {r['original_name']}")
        if r['status'].startswith("Renamed"):
            print(f"         --> {r['target_name']}")

    if args.address:
        print("\n================================================================================")
        print("                         GENERATED EMAIL DISPATCH                               ")
        print("================================================================================")
        summary = generate_dispatch_summary(args.address, records, agent_name=args.agent)
        print(summary)
        print("================================================================================")


if __name__ == "__main__":
    main()
