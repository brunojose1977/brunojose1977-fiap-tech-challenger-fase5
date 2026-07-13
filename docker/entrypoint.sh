#!/bin/sh
set -e

mkdir -p /app/dataset /app/diagramas_selecionados /app/relatorio /app/.cache/huggingface

exec stride-analyzer "$@"
