# Raccourcis (équivalents Windows : voir README, section « Commandes »)
PY ?= python3

.PHONY: build test critical check lint report reset

build:     ## compile tous les modules (détecte les erreurs de syntaxe/import)
	$(PY) scripts/ci_check.py build

test:      ## tous les tests unitaires
	$(PY) -m unittest

critical:  ## tests CRITIQUES de compatibilité (FleetPortal, interface publique)
	$(PY) -m unittest discover -s tests/compat -t .

check:     ## pipeline complet, identique à la CI
	$(PY) scripts/ci_check.py

lint:
	ruff check . && ruff format --check .

report:    ## rapport de démonstration, profil atelier
	$(PY) consumers/workshop_cli/report_cli.py samples/vehicle_VF1-TLS-0042.json --as workshop

reset:     ## remet le dépôt à l'état initial de la formation (DESTRUCTIF)
	$(PY) scripts/reset_demo.py --yes
