
---

## AGENTS.md

```md
# AGENTS.md — Guide projet (Password Strength Checker)

Ce fichier décrit les règles de contribution, conventions de code, et le comportement attendu pour toute personne (ou agent) qui modifie ce dépôt.

## Objectif

Construire un outil Python qui :
1) Analyse un mot de passe
2) Calcule un score (0–100)
3) Fournit un niveau (Faible/Moyen/Fort/Très fort)
4) Donne des explications et recommandations

## Contraintes

- Ne jamais logger/imprimer le mot de passe en clair dans des fichiers.
- Éviter de stocker des mots de passe (même en mémoire longtemps) : traiter puis oublier.
- Pas de dépendances lourdes sauf besoin réel.
- Code lisible, testable, modularisé.

## Convention de code

- Python 3.10+ si possible
- Formatage :
  - `black` (optionnel)
  - `ruff` (optionnel)
- Typage :
  - annotations `typing` recommandées
- Fonctions courtes et nommées clairement
- Favoriser `dataclasses` pour les résultats

## API interne recommandée

### Modèle de résultat

Un résultat doit idéalement contenir :
- `score: int` (0–100)
- `label: str` (Faible/Moyen/Fort/Très fort)
- `checks: list` (liste de checks avec succès/échec + message)
- `suggestions: list[str]` (conseils)
- `entropy_estimate: float | None` (optionnel)

### Fonction principale

`evaluate_password(password: str) -> Result`

Règles :
- Ne pas modifier le mot de passe (pas de normalisation qui fausse l’analyse)
- Toujours renvoyer un résultat cohérent même si password vide

## Règles de scoring (guidelines)

- Longueur :
  - < 8 : score plafonné bas
  - 8–11 : ok
  - 12–15 : bien
  - 16+ : très bien
- Diversité :
  - au moins 3 catégories → bonus
  - 4 catégories → bonus max
- Pénalités :
  - suites (ex: `abcd`, `1234`)
  - répétitions (ex: `aaaa`, `1111`)
  - mots de passe communs (si liste fournie)
  - mots du dictionnaire (optionnel)

Les poids exacts peuvent évoluer, mais doivent rester :
- Compréhensibles
- Testables
- Documentés (au minimum dans `rules.py`)

## Sécurité & confidentialité

- Ne jamais envoyer le mot de passe vers un service externe sans consentement explicite.
- Si intégration HIBP : utiliser k-anonymity et documenter clairement.
- Éviter d’écrire le mot de passe dans l’historique shell : privilégier saisie masquée (`getpass`).

## CLI

Le CLI doit :
- proposer une saisie masquée par défaut (`getpass.getpass()`)
- permettre une option `--password` (mais avertir dans la doc)
- retourner un code de sortie cohérent (optionnel) :
  - 0 si >= “Fort”
  - 1 sinon

## Tests attendus

Cas minimum :
- vide / très court
- seulement minuscules
- minuscules + chiffres
- tout type + long
- suite (`abcd1234`)
- répétition (`aaaaaaaaAA1!`)
- mot de passe commun (si liste activée)

## Definition of Done

- `python main.py` fonctionne
- La sortie explique score + raisons + conseils
- Tests passent (si dossier `tests/` présent)
- Aucun secret/mot de passe n’est écrit en clair dans des fichiers