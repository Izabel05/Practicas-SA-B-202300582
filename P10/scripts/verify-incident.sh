#!/usr/bin/env bash
# Ejecutar en Google Cloud Shell. Lee la evidencia del canario sin inducir una falla nueva.
set -euo pipefail

command -v kubectl >/dev/null || { echo "Falta kubectl" >&2; exit 1; }
context="$(kubectl config current-context)"
if [[ "$context" != *"p9-202300582"* ]]; then
  echo "Contexto incorrecto: $context" >&2
  exit 1
fi

echo "Rollout actual:"
kubectl get rollout api-gateway -n sa-p9
echo "Plantilla de análisis:"
kubectl get analysistemplate gateway-slo-prometheus -n sa-p9
echo "Historial disponible de AnalysisRun:"
kubectl get analysisrun -n sa-p9 --sort-by=.metadata.creationTimestamp

failed="api-gateway-79f85c79fb-7-5"
if kubectl get analysisrun "$failed" -n sa-p9 >/dev/null 2>&1; then
  echo "Detalle de la falla esperada (p95 medido 2.411 s > 0.750 s):"
  kubectl describe analysisrun "$failed" -n sa-p9
else
  echo "El AnalysisRun histórico $failed ya no está disponible en el clúster."
  echo "Consulta la tabla de validación y el commit del experimento en P10/README.md."
fi

echo "Análisis de recuperación disponibles:"
for suffix in 8-2 8-5 8-8; do
  name="api-gateway-6b8d4465cf-$suffix"
  if kubectl get analysisrun "$name" -n sa-p9 >/dev/null 2>&1; then
    kubectl get analysisrun "$name" -n sa-p9 \
      -o custom-columns=NAME:.metadata.name,PHASE:.status.phase
  fi
done

echo "Esta comprobación no modifica el clúster ni crea una incidencia."
