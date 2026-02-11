from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from getpass import getpass

from checker import evaluate_password
from checker.schema import json_schema


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
    ruleset = (
        result.profile
        if result.policy == "default"
        else f"{result.policy}:{result.profile}"
    )
    payload = {
        "version": result.ruleset_version,
        "ruleset": ruleset,
        "score": result.score,
        "label": result.label,
        "length": result.length,
        "category_count": result.category_count,
        "min_length": result.min_length,
        "profile": result.profile,
        "policy": result.policy,
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


def _write_jsonl(results) -> None:
    for index, result in enumerate(results, start=1):
        payload = _result_payload(result, index=index)
        print(json.dumps(payload, ensure_ascii=False))


def _write_csv(results) -> None:
    fieldnames = [
        "index",
        "score",
        "label",
        "length",
        "category_count",
        "min_length",
        "profile",
        "policy",
        "entropy_estimate",
        "sequence_found",
        "keyboard_sequence",
        "repeated_segment",
        "repeat_len",
        "is_common",
        "has_dictionary_word",
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    for index, result in enumerate(results, start=1):
        metrics = result.metrics or {}
        row = {
            "index": index,
            "score": result.score,
            "label": result.label,
            "length": result.length,
            "category_count": result.category_count,
            "min_length": result.min_length,
            "profile": result.profile,
            "policy": result.policy,
            "entropy_estimate": result.entropy_estimate,
            "sequence_found": metrics.get("sequence_found"),
            "keyboard_sequence": metrics.get("keyboard_sequence"),
            "repeated_segment": metrics.get("repeated_segment"),
            "repeat_len": metrics.get("repeat_len"),
            "is_common": metrics.get("is_common"),
            "has_dictionary_word": metrics.get("has_dictionary_word"),
        }
        writer.writerow(row)


def _render_report(results, *, fmt: str) -> str:
    lines: list[str] = []
    for index, result in enumerate(results, start=1):
        if fmt == "markdown":
            lines.append(f"## Mot de passe {index}")
            lines.append(f"- Score: {result.score}/100")
            lines.append(f"- Niveau: {result.label}")
            failed = [check.message for check in result.checks if not check.passed]
            if failed:
                lines.append("- Faiblesses:")
                lines.extend(f"- {msg}" for msg in failed[:3])
            if result.suggestions:
                lines.append(f"- Suggestion prioritaire: {result.suggestions[0]}")
            lines.append("")
        elif fmt == "html":
            failed = [check.message for check in result.checks if not check.passed]
            suggestion = result.suggestions[0] if result.suggestions else ""
            failures = "<br>".join(_html_escape(msg) for msg in failed[:3]) if failed else "Aucune"
            label_class = {
                "Faible": "weak",
                "Moyen": "medium",
                "Fort": "strong",
                "Très fort": "very-strong",
            }.get(result.label, "medium")
            lines.append(
                "<tr class=\"row\" style=\"--i: "
                f"{index}\">"
                f"<td class=\"index\">{index}</td>"
                "<td>"
                f"<div class=\"score\">{result.score}/100</div>"
                f"<div class=\"score-bar\"><span style=\"width:{result.score}%;\"></span></div>"
                "</td>"
                f"<td><span class=\"badge {label_class}\">{_html_escape(result.label)}</span></td>"
                f"<td>{result.length}</td>"
                f"<td class=\"muted\">{failures}</td>"
                f"<td>{_html_escape(suggestion)}</td>"
                "</tr>"
            )
        else:
            lines.append(f"Mot de passe {index}")
            lines.append(f"Score: {result.score}/100")
            lines.append(f"Niveau: {result.label}")
            failed = [check.message for check in result.checks if not check.passed]
            if failed:
                lines.append("Faiblesses:")
                lines.extend(f"- {msg}" for msg in failed[:3])
            if result.suggestions:
                lines.append(f"Suggestion prioritaire: {result.suggestions[0]}")
            lines.append("")
    if fmt == "html":
        total = len(results)
        avg = sum(result.score for result in results) / total if total else 0
        min_score = min((result.score for result in results), default=0)
        max_score = max((result.score for result in results), default=0)
        counts = {
            "Faible": sum(1 for result in results if result.label == "Faible"),
            "Moyen": sum(1 for result in results if result.label == "Moyen"),
            "Fort": sum(1 for result in results if result.label == "Fort"),
            "Très fort": sum(1 for result in results if result.label == "Très fort"),
        }
        rows = "\n".join(lines)
        return (
            "<!doctype html>\n"
            "<html lang=\"fr\">\n"
            "<head>\n"
            "  <meta charset=\"utf-8\">\n"
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "  <title>Rapport Password Strength Checker</title>\n"
            "  <style>\n"
            "    @import url(\"https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@400;500;600;700&display=swap\");\n"
            "    :root {\n"
            "      --bg: #f6f2ec;\n"
            "      --bg-2: #efe7dd;\n"
            "      --ink: #1f2428;\n"
            "      --muted: #5d6772;\n"
            "      --accent: #b38b59;\n"
            "      --border: #e1d7cc;\n"
            "      --card: #ffffff;\n"
            "      --shadow: 0 20px 45px rgba(31, 36, 40, 0.12);\n"
            "      --strong: #1f6f3f;\n"
            "      --very-strong: #0f5132;\n"
            "      --medium: #c07a2a;\n"
            "      --weak: #a94442;\n"
            "    }\n"
            "    * { box-sizing: border-box; }\n"
            "    body {\n"
            "      margin: 0;\n"
            "      font-family: \"Source Sans 3\", sans-serif;\n"
            "      color: var(--ink);\n"
            "      background: radial-gradient(circle at 20% 20%, #ffffff 0%, var(--bg) 45%, var(--bg-2) 100%);\n"
            "    }\n"
            "    .wrap {\n"
            "      max-width: 1100px;\n"
            "      margin: 0 auto;\n"
            "      padding: 48px 20px 64px;\n"
            "    }\n"
            "    .hero {\n"
            "      display: grid;\n"
            "      gap: 24px;\n"
            "      align-items: center;\n"
            "      grid-template-columns: 1.2fr 1fr;\n"
            "      margin-bottom: 28px;\n"
            "      animation: rise 600ms ease forwards;\n"
            "      opacity: 0;\n"
            "    }\n"
            "    .title {\n"
            "      font-family: \"Playfair Display\", serif;\n"
            "      font-size: clamp(28px, 4vw, 44px);\n"
            "      margin: 0 0 8px;\n"
            "    }\n"
            "    .subtitle {\n"
            "      color: var(--muted);\n"
            "      font-size: 16px;\n"
            "      margin: 0;\n"
            "    }\n"
            "    .stats {\n"
            "      display: grid;\n"
            "      grid-template-columns: repeat(2, minmax(0, 1fr));\n"
            "      gap: 16px;\n"
            "    }\n"
            "    .card {\n"
            "      background: var(--card);\n"
            "      border: 1px solid var(--border);\n"
            "      border-radius: 18px;\n"
            "      padding: 18px 20px;\n"
            "      box-shadow: var(--shadow);\n"
            "      animation: rise 700ms ease forwards;\n"
            "      opacity: 0;\n"
            "      animation-delay: 120ms;\n"
            "    }\n"
            "    .metric {\n"
            "      display: flex;\n"
            "      justify-content: space-between;\n"
            "      font-size: 15px;\n"
            "      margin-bottom: 6px;\n"
            "      color: var(--muted);\n"
            "    }\n"
            "    .metric strong { color: var(--ink); }\n"
            "    .badge {\n"
            "      display: inline-flex;\n"
            "      padding: 6px 12px;\n"
            "      border-radius: 999px;\n"
            "      font-weight: 600;\n"
            "      font-size: 13px;\n"
            "      border: 1px solid transparent;\n"
            "    }\n"
            "    .badge.weak { background: #f6e6e6; color: var(--weak); border-color: #e9c7c7; }\n"
            "    .badge.medium { background: #fbf1e2; color: var(--medium); border-color: #f0d6b3; }\n"
            "    .badge.strong { background: #e4f3ea; color: var(--strong); border-color: #c4e4d0; }\n"
            "    .badge.very-strong { background: #ddf0e5; color: var(--very-strong); border-color: #bfe0cf; }\n"
            "    .table-card {\n"
            "      background: var(--card);\n"
            "      border-radius: 22px;\n"
            "      padding: 12px;\n"
            "      border: 1px solid var(--border);\n"
            "      box-shadow: var(--shadow);\n"
            "      animation: rise 750ms ease forwards;\n"
            "      opacity: 0;\n"
            "      animation-delay: 180ms;\n"
            "    }\n"
            "    table { border-collapse: collapse; width: 100%; font-size: 14px; }\n"
            "    th, td { padding: 12px; text-align: left; border-bottom: 1px solid var(--border); }\n"
            "    th { color: var(--muted); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }\n"
            "    .score { font-weight: 600; }\n"
            "    .score-bar { height: 6px; background: #efe7dd; border-radius: 999px; overflow: hidden; margin-top: 6px; }\n"
            "    .score-bar span { display: block; height: 100%; background: linear-gradient(90deg, #c7a978, #b38b59); }\n"
            "    .muted { color: var(--muted); }\n"
            "    .row { animation: rise 600ms ease forwards; opacity: 0; animation-delay: calc(var(--i) * 40ms); }\n"
            "    .index { color: var(--muted); }\n"
            "    @keyframes rise {\n"
            "      from { transform: translateY(12px); opacity: 0; }\n"
            "      to { transform: translateY(0); opacity: 1; }\n"
            "    }\n"
            "    @media (max-width: 860px) {\n"
            "      .hero { grid-template-columns: 1fr; }\n"
            "      .stats { grid-template-columns: 1fr; }\n"
            "      .table-card { overflow-x: auto; }\n"
            "      table { min-width: 680px; }\n"
            "    }\n"
            "  </style>\n"
            "</head>\n"
            "<body>\n"
            "  <div class=\"wrap\">\n"
            "    <section class=\"hero\">\n"
            "      <div>\n"
            "        <h1 class=\"title\">Rapport de robustesse</h1>\n"
            "        <p class=\"subtitle\">Analyse sobre et professionnelle des mots de passe.</p>\n"
            "      </div>\n"
            "      <div class=\"stats card\">\n"
            f"        <div class=\"metric\"><span>Total analysés</span><strong>{total}</strong></div>\n"
            f"        <div class=\"metric\"><span>Score moyen</span><strong>{avg:.1f}/100</strong></div>\n"
            f"        <div class=\"metric\"><span>Min / Max</span><strong>{min_score} / {max_score}</strong></div>\n"
            "        <div class=\"metric\"><span>Répartition</span><strong>"
            f"{counts['Faible']} / {counts['Moyen']} / {counts['Fort']} / {counts['Très fort']}"
            "</strong></div>\n"
            "      </div>\n"
            "    </section>\n"
            "    <section class=\"table-card\">\n"
            "      <table>\n"
            "        <thead>\n"
            "          <tr>\n"
            "            <th>#</th>\n"
            "            <th>Score</th>\n"
            "            <th>Niveau</th>\n"
            "            <th>Longueur</th>\n"
            "            <th>Faiblesses</th>\n"
            "            <th>Suggestion prioritaire</th>\n"
            "          </tr>\n"
            "        </thead>\n"
            "        <tbody>\n"
            f"{rows}\n"
            "        </tbody>\n"
            "      </table>\n"
            "    </section>\n"
            "  </div>\n"
            "</body>\n"
            "</html>\n"
        )
    return "\n".join(lines).strip() + "\n"


def _html_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


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
    group.add_argument(
        "--generate",
        action="store_true",
        help="Générer un mot de passe fort",
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
        "--policy",
        choices=("default", "nist"),
        default="default",
        help="Politique de scoring",
    )
    parser.add_argument(
        "--generate-length",
        type=int,
        default=16,
        help="Longueur du mot de passe généré",
    )
    parser.add_argument(
        "--generate-count",
        type=int,
        default=1,
        help="Nombre de mots de passe générés",
    )
    parser.add_argument(
        "--generate-no-lower",
        action="store_true",
        help="Désactiver les minuscules pour la génération",
    )
    parser.add_argument(
        "--generate-no-upper",
        action="store_true",
        help="Désactiver les majuscules pour la génération",
    )
    parser.add_argument(
        "--generate-no-digit",
        action="store_true",
        help="Désactiver les chiffres pour la génération",
    )
    parser.add_argument(
        "--generate-no-symbol",
        action="store_true",
        help="Désactiver les symboles pour la génération",
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
        "--breach-list",
        help="Fichier de hashes SHA1 de mots de passe compromis",
    )
    parser.add_argument(
        "--hibp",
        action="store_true",
        help="Activer la vérification HIBP (k-anonymity)",
    )
    parser.add_argument(
        "--hibp-timeout",
        type=float,
        default=5.0,
        help="Timeout HIBP en secondes",
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--json",
        action="store_true",
        help="Sortie JSON",
    )
    output_group.add_argument(
        "--jsonl",
        action="store_true",
        help="Sortie JSON Lines",
    )
    output_group.add_argument(
        "--csv",
        action="store_true",
        help="Sortie CSV",
    )
    parser.add_argument(
        "--json-schema",
        action="store_true",
        help="Afficher le schéma JSON v2",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Mesurer les performances (requiert --input-file)",
    )
    parser.add_argument(
        "--benchmark-repeats",
        type=int,
        default=1,
        help="Nombre de répétitions pour le benchmark",
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
    parser.add_argument(
        "--report-file",
        help="Écrire un rapport dans un fichier",
    )
    parser.add_argument(
        "--report-format",
        choices=("text", "markdown", "html"),
        default="text",
        help="Format du rapport (text, markdown ou html)",
    )
    args = parser.parse_args()

    if args.json_schema:
        print(json.dumps(json_schema(), ensure_ascii=False, indent=2))
        return 0

    if args.generate:
        if args.json or args.jsonl or args.csv or args.report_file:
            print(
                "Erreur: --generate ne peut pas être combiné avec --json/--jsonl/--csv/--report-file.",
                file=sys.stderr,
            )
            return 2
        from checker.generator import generate_passwords

        try:
            passwords = generate_passwords(
                length=args.generate_length,
                count=args.generate_count,
                use_lower=not args.generate_no_lower,
                use_upper=not args.generate_no_upper,
                use_digit=not args.generate_no_digit,
                use_symbol=not args.generate_no_symbol,
            )
        except ValueError as exc:
            print(f"Erreur: {exc}", file=sys.stderr)
            return 2
        for password in passwords:
            print(password)
        return 0

    dictionary_path = Path(args.dictionary_list) if args.dictionary_list else None
    breach_list_path = Path(args.breach_list) if args.breach_list else None

    def breach_status(password: str) -> bool | None:
        any_checked = False
        any_breached = False
        if breach_list_path:
            from checker.breach import check_breach_list

            if breach_list_path.exists():
                any_checked = True
                if check_breach_list(password, breach_list_path):
                    any_breached = True
            else:
                print(
                    f"Warning: fichier breach introuvable ({breach_list_path}).",
                    file=sys.stderr,
                )
        if args.hibp:
            from checker.breach import check_hibp_k_anonymity

            hibp_checked = False
            try:
                hibp_checked = True
                if check_hibp_k_anonymity(password, timeout=args.hibp_timeout):
                    any_breached = True
            except RuntimeError as exc:
                print(f"Warning: HIBP indisponible ({exc}).", file=sys.stderr)
            any_checked = any_checked or hibp_checked
        if any_breached:
            return True
        if any_checked:
            return False
        return None
    if args.input_file:
        input_path = Path(args.input_file)
        passwords = input_path.read_text(encoding="utf-8").splitlines()
        if args.benchmark:
            start = time.perf_counter()
            for _ in range(max(1, args.benchmark_repeats)):
                _ = [
                    evaluate_password(
                        password,
                        min_length=args.min_length,
                        profile=args.profile,
                        policy=args.policy,
                        breach_found=breach_status(password),
                        use_dictionary=not args.no_dictionary,
                        dictionary_path=dictionary_path,
                    )
                    for password in passwords
                ]
            elapsed = time.perf_counter() - start
            total = len(passwords) * max(1, args.benchmark_repeats)
            rate = total / elapsed if elapsed > 0 else 0
            print(f"Évaluations: {total}")
            print(f"Durée: {elapsed:.4f}s")
            print(f"Débit: {rate:.2f} eval/s")
            return 0
        results = [
            evaluate_password(
                password,
                min_length=args.min_length,
                profile=args.profile,
                policy=args.policy,
                breach_found=breach_status(password),
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
        elif args.jsonl:
            _write_jsonl(results)
        elif args.csv:
            _write_csv(results)
        else:
            for index, result in enumerate(results, start=1):
                print(f"Mot de passe {index}: {result.score}/100 - {result.label}")
                if args.explain or args.verbose:
                    _print_details(result, verbose=args.verbose, explain=args.explain)
                if index != len(results):
                    print()
        if args.report_file:
            report_path = Path(args.report_file)
            report = _render_report(results, fmt=args.report_format)
            report_path.write_text(report, encoding="utf-8")
        return 0 if all(r.label in ("Fort", "Très fort") for r in results) else 1

    if args.password is None:
        password = getpass("Mot de passe: ")
    else:
        password = args.password

    result = evaluate_password(
        password,
        min_length=args.min_length,
        profile=args.profile,
        policy=args.policy,
        breach_found=breach_status(password),
        use_dictionary=not args.no_dictionary,
        dictionary_path=dictionary_path,
    )

    if args.json:
        _print_json(result)
    elif args.jsonl:
        _write_jsonl([result])
    elif args.csv:
        _write_csv([result])
    else:
        _print_human(result, verbose=args.verbose, explain=args.explain)
    if args.report_file:
        report_path = Path(args.report_file)
        report = _render_report([result], fmt=args.report_format)
        report_path.write_text(report, encoding="utf-8")

    return 0 if result.label in ("Fort", "Très fort") else 1


if __name__ == "__main__":
    raise SystemExit(main())
