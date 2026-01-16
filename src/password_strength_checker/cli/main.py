from __future__ import annotations

import argparse
import json
from getpass import getpass
from pathlib import Path

from rich.console import Console
from rich.table import Table

from password_strength_checker.core.evaluate import evaluate
from password_strength_checker.core.models import Policy
from password_strength_checker.core.policy import load_policy


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="psc", description="Password Strength Checker (local)")
    p.add_argument("--password", help="Mot de passe (déconseillé: historique shell).")
    p.add_argument("--json", action="store_true", help="Sortie JSON.")
    p.add_argument("--min-length", type=int, default=12, help="Longueur minimale recommandée.")
    p.add_argument("--strong-length", type=int, default=16, help="Longueur 'forte'.")
    p.add_argument("--policy", type=str, help="Chemin vers un fichier policy.json")
    p.add_argument("--explain", action="store_true", help="Affiche les détails de calcul (score/estimates).")
    p.add_argument("--strict", action="store_true", help="Considère WARNING comme non conforme.")
    return p


def main() -> None:
    args = build_parser().parse_args()
    pw = args.password or getpass("Mot de passe: ")

    # Base policy from CLI args
    policy = Policy(min_length=args.min_length, strong_length=args.strong_length)

    # If --policy provided, load it (and it overrides the base policy)
    if args.policy:
        policy = load_policy(Path(args.policy))

    result = evaluate(pw, policy=policy)
    import sys


    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return

    console = Console()
    console.print(f"\nScore: [bold]{result.score}[/bold]/100  Niveau: [bold]{result.label}[/bold]\n")

    table = Table(title="Diagnostics")
    table.add_column("Sévérité")
    table.add_column("Code")
    table.add_column("Message")
    table.add_column("Impact")
    for f in result.findings:
        table.add_row(f.severity.value, f.code, f.message, str(f.penalty))
    console.print(table)

        # Estimation résistance (approx.)
    if getattr(result, "estimates", None):
        est = Table(title="Estimation résistance (approx.)")
        est.add_column("Scénario")
        est.add_column("Essais/s")
        est.add_column("Temps")
        for row in result.estimates:
            est.add_row(row["scenario"], row["guesses_per_second"], row["time"])
        console.print(est)

    if args.explain:
        console.print("\n[bold]Détails (explain)[/bold]")
        console.print(f"- Longueur: {len(pw)}")
        charset_meta = next((f.meta for f in result.findings if f.code.startswith("CHARSET_")), {})
        if charset_meta:
            console.print(f"- Diversité (classes): {charset_meta.get('classes')}")
        penalty_sum = sum(f.penalty for f in result.findings)
        console.print(f"- Somme pénalités (findings): {penalty_sum}")
        console.print("- Note: bonus/ajustements possibles (scoring.py / estimates.py).")


    console.print("\n[bold]Recommandations[/bold]")
    for r in result.recommendations:
        console.print(f"- {r}")

        # Exit code for automation/CI
    non_compliant = any(f.severity.value == "critical" for f in result.findings)
    if args.strict:
        non_compliant = non_compliant or any(f.severity.value == "warning" for f in result.findings)

    if non_compliant:
        sys.exit(2)


if __name__ == "__main__":
    main()
