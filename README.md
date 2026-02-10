# Password Strength Checker (Python)


Un petit outil en Python qui évalue la robustesse d’un mot de passe selon plusieurs critères (longueur, diversité des caractères, motifs faibles, etc.) et renvoie un score + des recommandations.


## Fonctionnalités


- ✅ Score de robustesse (0 → 100)
- ✅ Niveau de sécurité (Faible / Moyen / Fort / Très fort)
- ✅ Détection de points faibles courants :
  - trop court
  - pas de majuscules / minuscules / chiffres / symboles
  - répétitions (ex: `aaaa`, `1111`)
  - suites (ex: `abcd`, `1234`)
  - mots de passe trop communs (liste optionnelle)
- ✅ Conseils d’amélioration personnalisés
- ✅ Mode CLI (ligne de commande)
- (Optionnel) Export JSON des résultats


## Prérequis


- Python 3.10+ recommandé (3.8+ OK si tu restes simple)


## Utilisation
1) Lancer le checker en CLI

Exemple :

python main.py

Tu peux aussi prévoir une option :

python main.py --password "MonMotDePasse123!"
2) Exemple de sortie attendue

Score: 78/100

Niveau: Fort

Détails:

✅ Longueur OK

✅ Majuscules / minuscules / chiffres / symboles détectés

⚠️ Évite les suites comme 1234

Conseils:

Ajouter 2 caractères de plus

Éviter les motifs simples

Structure du projet (suggestion)
password-strength-checker/
├─ main.py
├─ checker/
│  ├─ __init__.py
│  ├─ rules.py          # règles de scoring
│  ├─ common.py         # détection suites, répétitions, etc.
│  └─ models.py         # dataclasses (résultat, détails)
├─ data/
│  └─ common_passwords.txt   # optionnel
├─ tests/
│  └─ test_checker.py
├─ requirements.txt
├─ README.md
└─ AGENTS.md
Critères de scoring (exemple)

Longueur :

< 8 : gros malus

8–11 : moyen

12–15 : bien

16+ : excellent

Diversité :

minuscules / majuscules / chiffres / symboles

Pénalités :

répétitions longues (aaaaaa)

suites (abcd, 1234)

présence dans une liste de mots de passe communs

Tests

Si tu utilises pytest :

pip install pytest
pytest -q
Améliorations possibles

Interface web (Flask/FastAPI) ou GUI (Tkinter)

Vérification “haveibeenpwned” (attention aux API/clé et à la vie privée)

Générateur de mots de passe forts

Historique + export

Licence

Libre pour usage éducatif (tu peux ajouter une vraie licence : MIT, Apache-2.0, etc.)