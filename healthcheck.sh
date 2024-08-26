#!/bin/bash
RED='\033[0;31m'
NC='\033[0m'

curl http://localhost:8000 || \
(echo "${RED}====== HEALTHCHECK FAILURE! RESTARTING!! ======${NC}" && bash -c 'kill -s 15 -1 && (sleep 10; kill -s 9 -1)')
