# Password Strength Checker (Python)

Outil Python qui évalue la robustesse d’un mot de passe et renvoie un score, un niveau, des explications et des recommandations.

**Objectif**
1. Analyser un mot de passe
2. Calculer un score (0–100)
3. Fournir un niveau (Faible / Moyen / Fort / Très fort)
4. Expliquer les points forts/faibles et proposer des conseils

**Fonctionnalités**
- Score de robustesse (0 → 100)
- Niveau de sécurité lisible
- Détection des faiblesses courantes (longueur, diversité, répétitions, suites, mots de passe communs)
- Détection optionnelle de mots du dictionnaire (via `data/dictionary_words.txt`)
- Conseils d’amélioration personnalisés
- CLI avec saisie masquée par défaut

**Pré-requis**
- Python 3.10+ recommandé

**Installation**
- Cloner le dépôt
- Si un fichier `requirements.txt` existe, installer les dépendances :

```bash
pip install -r requirements.txt
```

**Utilisation**
- Lancer en mode interactif (saisie masquée) :

```bash
python main.py
```

- Passer un mot de passe en argument (attention à l’historique du shell) :

```bash
python main.py --password "MonMotDePasse123!"
```

**Exemple de sortie**

```text
Score: 78/100
Niveau: Fort

Détails:
- Longueur OK
- Majuscules / minuscules / chiffres / symboles détectés
- Éviter les suites comme 1234

Conseils:
- Ajouter 2 caractères de plus
- Éviter les motifs simples
```

**Règles de scoring (guidelines)**
- Longueur < 8 : score plafonné bas
- Longueur 8–11 : acceptable
- Longueur 12–15 : bien
- Longueur 16+ : très bien
- Diversité 3 catégories : bonus
- Diversité 4 catégories : bonus maximum
- Pénalité pour suites (`abcd`, `1234`)
- Pénalité pour répétitions (`aaaa`, `1111`)
- Pénalité pour mots de passe communs (si liste fournie)
- Pénalité pour mots du dictionnaire (optionnel)

**Structure du projet (suggestion)**

```text
password-strength-checker/
├─ main.py
├─ checker/
│  ├─ __init__.py
│  ├─ rules.py
│  ├─ common.py
│  └─ models.py
├─ data/
│  └─ common_passwords.txt
│  └─ dictionary_words.txt
├─ tests/
│  └─ test_checker.py
├─ requirements.txt
├─ README.md
└─ AGENTS.md
```

**Sécurité et confidentialité**
- Ne jamais logger/imprimer le mot de passe en clair dans des fichiers
- Traiter puis oublier le mot de passe (éviter de le stocker longtemps en mémoire)
- Ne jamais envoyer le mot de passe vers un service externe sans consentement explicite
- Si intégration HIBP, utiliser k-anonymity et documenter clairement

**CLI et codes de sortie**
- Saisie masquée par défaut via `getpass.getpass()`
- Option `--password` autorisée mais à documenter clairement
- Code de sortie optionnel : `0` si niveau >= Fort, `1` sinon

**Tests**
- Lancer les tests (si `tests/` existe) :

```bash
pytest -q
```

**Améliorations possibles**
- Export JSON des résultats
- Interface web ou GUI
- Vérification HIBP (k-anonymity)
- Générateur de mots de passe forts

**Licence**
- À définir (MIT, Apache-2.0, etc.)
