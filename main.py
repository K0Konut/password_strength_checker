from __future__ import annotations

import argparse
import json
import sys
from getpass import getpass

from checker import evaluate_password


def _print_human(result) -> None:
    print(f"Score: {result.score}/100")
    print(f"Niveau: {result.label}\n")

    print("Détails:")
    for check in result.checks:
        prefix = "OK" if check.passed else "WARN"
        print(f"{prefix} {check.message}")

    print("\nConseils:")
    for suggestion in result.suggestions:
        print(f"- {suggestion}")

    if result.entropy_estimate is not None:
        print(f"\nEntropie estimée: {result.entropy_estimate} bits")


def _print_json(result) -> None:
    payload = {
        "score": result.score,
        "label": result.label,
        "checks": [
            {
                "name": check.name,
                "passed": check.passed,
                "message": check.message,
            }
            for check in result.checks
        ],
        "suggestions": result.suggestions,
        "entropy_estimate": result.entropy_estimate,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Password Strength Checker")
    parser.add_argument(
        "--password",
        help="Mot de passe à évaluer (attention à l'historique du shell)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Sortie JSON",
    )
    args = parser.parse_args()

    if args.password is None:
        password = getpass("Mot de passe: ")
    else:
        password = args.password

    result = evaluate_password(password)

    if args.json:
        _print_json(result)
    else:
        _print_human(result)

    return 0 if result.label in ("Fort", "Très fort") else 1


if __name__ == "__main__":
    raise SystemExit(main())
