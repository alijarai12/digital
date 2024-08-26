#!/bin/bash

uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --ws auto \
    --ws-max-size 16777216 \
    --log-level debug \
    --access-log \
    --use-colors \
    --proxy-headers \
    --server-header \
    --timeout-keep-alive 5
