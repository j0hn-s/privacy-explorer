#!/usr/bin/env python3
"""
YAPS — on-disk migration for Privacy Cards: schema 1.x → 2.0.

Wraps the in-memory `_migrate_card_1_2_to_2_0` helper from risk_engine.py and
writes the migrated card to disk. Use this when you want to commit a migrated
card to the repo rather than letting the engine migrate it transiently at
evaluation time.

The migration policy is documented in yaps/MIGRATION_NOTES.md. In short:

  * schema_version → "2.0"
  * risk_calibration restructured into design_target / accountant /
    empirical_audit / measured_advantage sub-blocks
  * bare evidence_ref strings wrapped into evidence_reference objects with
    evidence_class: "reproducible-record" as the silent default
  * threat_profile defaulted to "honest-but-curious-server" when absent
  * MIA → MIA-per-record
  * cps_subject_type left absent (card author must set explicitly)

Usage:

    python migrate_1_2_to_2_0.py <card.json> [--in-place | --output <new.json>] [--dry-run]

Options:
    --in-place      Overwrite the input file (creates <card.json>.1_2.bak alongside).
    --output PATH   Write to PATH instead of stdout/in-place.
    --dry-run       Print the migration warnings without writing anything.
    --strict        Strip legacy fields the 2.0 schema rejects (default: keep for
                    forward-compat readers; on-disk migration usually wants
                    --strict to produce a clean 2.0 file).

Exit codes:
    0 — migration completed (or card was already 2.0; in that case writes nothing).
    1 — error.
"""

import argparse
import json
import sys
from pathlib import Path

# Import the in-memory migration logic from risk_engine.py so we have a single
# source of truth.
sys.path.insert(0, str(Path(__file__).parent))
from risk_engine import _migrate_card_1_2_to_2_0  # noqa: E402


# Legacy keys that the 2.0 schema rejects under additionalProperties: false.
# --strict drops these from the on-disk output. The in-memory migration leaves
# them in for any forward-compat reader that might tolerate them.
LEGACY_KEYS_TO_STRIP = {
    "assurance_targets.required_artefacts[].location",  # superseded by .evidence
    "risk_calibration.mu_dp",                            # superseded by .design_target.mu_dp / .accountant.mu_dp
    "risk_calibration.attack_target",                    # superseded by .design_target.attack_target / .measured_advantage
    "risk_calibration.conversion_regret",                # not modelled in 2.0
    "risk_calibration.trade_off_curve_ref",              # superseded by .trade_off_curve
}


def _strict_strip(card: dict) -> None:
    """Remove legacy fields the 2.0 schema rejects. Mutates in place."""
    # assurance_targets.required_artefacts[].location
    artefacts = (card.get("assurance_targets") or {}).get("required_artefacts") or []
    for a in artefacts:
        if "evidence" in a and "location" in a:
            del a["location"]
        if "notes" in a and a["notes"] in (None, ""):
            del a["notes"]

    # risk_calibration legacy keys
    rc = card.get("risk_calibration") or {}
    for k in ("mu_dp", "attack_target", "conversion_regret", "trade_off_curve_ref"):
        rc.pop(k, None)

    # jurisdictional_context.cross_border_mechanism: 1.x allowed null; 2.0 type is
    # ["string", "null"] so it's still permitted.

    # Convert deployment_context.data_subjects_jurisdiction list-of-string in 1.x
    # into the same in 2.0 (no change). No-op.


def main():
    parser = argparse.ArgumentParser(
        description="Migrate a YAPS Privacy Card from schema 1.x to 2.0."
    )
    parser.add_argument("card", help="Path to the input card JSON file.")
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the input file (creates a .1_2.bak alongside).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write migrated card to PATH instead of stdout/in-place.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report migration warnings without writing.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strip legacy fields the 2.0 schema rejects (recommended for on-disk migration).",
    )
    args = parser.parse_args()

    card_path = Path(args.card)
    if not card_path.exists():
        print(f"ERROR: card file not found: {card_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(card_path) as f:
            card = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in {card_path}: {e}", file=sys.stderr)
        sys.exit(1)

    src_version = card.get("schema_version", "1.0")
    if src_version == "2.0":
        print(f"[skip] {card_path}: already schema 2.0; nothing to do.", file=sys.stderr)
        sys.exit(0)

    migrated, warnings = _migrate_card_1_2_to_2_0(card)

    print(f"[migrate] {card_path}: {src_version} → 2.0", file=sys.stderr)
    for w in warnings:
        print(f"    {w}", file=sys.stderr)

    if args.strict:
        _strict_strip(migrated)
        print("    (--strict) legacy fields stripped", file=sys.stderr)

    output_json = json.dumps(migrated, indent=2, ensure_ascii=False)

    if args.dry_run:
        print(f"[dry-run] would write {len(output_json)} bytes", file=sys.stderr)
        sys.exit(0)

    if args.in_place:
        backup_path = card_path.with_suffix(card_path.suffix + ".1_2.bak")
        backup_path.write_text(card_path.read_text())
        print(f"    backup → {backup_path}", file=sys.stderr)
        card_path.write_text(output_json + "\n")
        print(f"    wrote → {card_path}", file=sys.stderr)
    elif args.output:
        out_path = Path(args.output)
        out_path.write_text(output_json + "\n")
        print(f"    wrote → {out_path}", file=sys.stderr)
    else:
        # stdout
        print(output_json)

    sys.exit(0)


if __name__ == "__main__":
    main()
