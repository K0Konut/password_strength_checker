from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from getpass import getpass

from checker import evaluate_password


def _build_explanations(result) -> list[str]:
    failed = [check.message for check in result.checks if not check.passed]
    passed = [check.message for check in result.checks if check.passed]
    lines: list[str] = []
    if failed:
        lines.append("Faiblesses principales: " + "; ".join(failed[:3]))
    if passed:
        lines.append("Points forts: " + "; ".join(passed[:2]))
    if result.suggestions:
        lines.append("Priorité: " + result.suggestions[0])
    return lines


def _print_details(result, *, verbose: bool = False, explain: bool = False) -> None:
    print("Détails:")
    for check in result.checks:
        prefix = "OK" if check.passed else "WARN"
        print(f"{prefix} {check.message}")

    print("\nConseils:")
    for suggestion in result.suggestions:
        print(f"- {suggestion}")

    if explain:
        lines = _build_explanations(result)
        if lines:
            print("\nExplications:")
            for line in lines:
                print(f"- {line}")

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


def _print_human(result, *, verbose: bool = False, explain: bool = False) -> None:
    print(f"Score: {result.score}/100")
    print(f"Niveau: {result.label}\n")

    _print_details(result, verbose=verbose, explain=explain)


def _result_payload(result, *, index: int | None = None) -> dict:
    payload = {
        "version": result.ruleset_version,
        "ruleset": result.profile,
        "score": result.score,
        "label": result.label,
        "length": result.length,
        "category_count": result.category_count,
        "min_length": result.min_length,
        "profile": result.profile,
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
    if index is not None:
        payload["index"] = index
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
    if result.metrics is not None:
        payload["metrics"] = result.metrics
    return payload


def _print_json(result) -> None:
    payload = _result_payload(result)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Password Strength Checker")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--password",
        help="Mot de passe à évaluer (attention à l'historique du shell)",
    )
    group.add_argument(
        "--input-file",
        help="Fichier contenant un mot de passe par ligne",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        help="Longueur recommandée (ex: 12, 16)",
    )
    parser.add_argument(
        "--profile",
        choices=("standard", "strict", "lenient"),
        default="standard",
        help="Profil de scoring",
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
        "--explain",
        action="store_true",
        help="Afficher un résumé explicatif",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Afficher le détail du score",
    )
    args = parser.parse_args()

    dictionary_path = Path(args.dictionary_list) if args.dictionary_list else None
    if args.input_file:
        input_path = Path(args.input_file)
        passwords = input_path.read_text(encoding="utf-8").splitlines()
        results = [
            evaluate_password(
                password,
                min_length=args.min_length,
                profile=args.profile,
                use_dictionary=not args.no_dictionary,
                dictionary_path=dictionary_path,
            )
            for password in passwords
        ]
        if args.json:
            payload = [
                _result_payload(result, index=index)
                for index, result in enumerate(results, start=1)
            ]
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            for index, result in enumerate(results, start=1):
                print(f"Mot de passe {index}: {result.score}/100 - {result.label}")
                if args.explain or args.verbose:
                    _print_details(result, verbose=args.verbose, explain=args.explain)
                if index != len(results):
                    print()
        return 0 if all(r.label in ("Fort", "Très fort") for r in results) else 1

    if args.password is None:
        password = getpass("Mot de passe: ")
    else:
        password = args.password

    result = evaluate_password(
        password,
        min_length=args.min_length,
        profile=args.profile,
        use_dictionary=not args.no_dictionary,
        dictionary_path=dictionary_path,
    )

    if args.json:
        _print_json(result)
    else:
        _print_human(result, verbose=args.verbose, explain=args.explain)

    return 0 if result.label in ("Fort", "Très fort") else 1


if __name__ == "__main__":
    raise SystemExit(main())
