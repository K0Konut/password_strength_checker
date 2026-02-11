from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from getpass import getpass

from checker import evaluate_password


def _print_human(result, *, verbose: bool = False) -> None:
    print(f"Score: {result.score}/100")
    print(f"Niveau: {result.label}\n")

    print("Détails:")
    for check in result.checks:
        prefix = "OK" if check.passed else "WARN"
        print(f"{prefix} {check.message}")

    print("\nConseils:")
    for suggestion in result.suggestions:
        print(f"- {suggestion}")

    if verbose and result.score_breakdown is not None:
        breakdown = result.score_breakdown
        print("\nDétails du score:")
        print(f"- Longueur: {breakdown.length_score}")
        print(f"- Diversité: {breakdown.diversity_bonus}")
        if breakdown.penalties:
            for name, value in breakdown.penalties.items():
                print(f"- Pénalité {name}: -{value}")
        if breakdown.capped and breakdown.cap is not None:
            reason = breakdown.cap_reason or "cap appliqué"
            print(f"- Cap: {breakdown.cap} ({reason})")

    if result.entropy_estimate is not None:
        print(f"\nEntropie estimée: {result.entropy_estimate} bits")


def _print_json(result) -> None:
    payload = {
        "score": result.score,
        "label": result.label,
        "length": result.length,
        "category_count": result.category_count,
        "min_length": result.min_length,
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
    if result.score_breakdown is not None:
        breakdown = result.score_breakdown
        payload["score_breakdown"] = {
            "length_score": breakdown.length_score,
            "diversity_bonus": breakdown.diversity_bonus,
            "penalties": breakdown.penalties,
            "capped": breakdown.capped,
            "cap": breakdown.cap,
            "cap_reason": breakdown.cap_reason,
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Password Strength Checker")
    parser.add_argument(
        "--password",
        help="Mot de passe à évaluer (attention à l'historique du shell)",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=12,
        help="Longueur recommandée (défaut: 12)",
    )
    parser.add_argument(
        "--dictionary-list",
        help="Chemin vers une liste de mots du dictionnaire",
    )
    parser.add_argument(
        "--no-dictionary",
        action="store_true",
        help="Désactiver la détection des mots du dictionnaire",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Sortie JSON",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Afficher le détail du score",
    )
    args = parser.parse_args()

    if args.password is None:
        password = getpass("Mot de passe: ")
    else:
        password = args.password

    dictionary_path = Path(args.dictionary_list) if args.dictionary_list else None
    result = evaluate_password(
        password,
        min_length=args.min_length,
        use_dictionary=not args.no_dictionary,
        dictionary_path=dictionary_path,
    )

    if args.json:
        _print_json(result)
    else:
        _print_human(result, verbose=args.verbose)

    return 0 if result.label in ("Fort", "Très fort") else 1


if __name__ == "__main__":
    raise SystemExit(main())
