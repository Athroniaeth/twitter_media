@echo off
poetry run ruff format || exit 0
poetry run djlint --reformat src/templates/**/*.html || exit 0
poetry run djlint --reformat src/templates/**/*.jinja2 || exit 0
