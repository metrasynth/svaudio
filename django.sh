#!/bin/bash
#
# Executes a command in a new shell in a running "django" container.
#
# Example:
#   ./django.sh ./manage.py migrate

docker compose exec -e "DJANGO_SETTINGS_MODULE=config.settings.local" django "$@"
