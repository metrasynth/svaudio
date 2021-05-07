#!/bin/bash
docker compose exec django ./manage.py "$@"
