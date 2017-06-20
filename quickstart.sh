#!/usr/bin/env bash
ansible-playbook devenv-playbook.yml
docker rm -f bamboo
docker run --name bamboo -e CONTEXT_PATH=ROOT -p 8085:8085 -d bamboo
v/bin/python scripts/forms.py