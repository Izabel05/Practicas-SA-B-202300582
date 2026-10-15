#!/usr/bin/env bash
# Ejecutar en Google Cloud Shell. Verifica recursos y consultas sin modificar GKE.
set -euo pipefail

for tool in gcloud kubectl curl python3; do
  command -v "$tool" >/dev/null || { echo "Falta $tool" >&2; exit 1; }
done

project="$(gcloud config get-value project 2>/dev/null)"
context="$(kubectl config current-context)"
if [[ "$project" != "p8202300582" || "$context" != *"p9-202300582"* ]]; then
  echo "Proyecto o contexto incorrecto: $project / $context" >&2
  echo "Ejecuta gcloud config set project p8202300582 y get-credentials del clúster." >&2
  exit 1
fi

echo "Proyecto: $project | Contexto: $context"
echo "Aplicaciones de Argo CD:"
kubectl get applications -n argocd \
  -o custom-columns=NAME:.metadata.name,SYNC:.status.sync.status,HEALTH:.status.health.status
echo "Servicios y plataforma de observabilidad:"
kubectl get pods -n sa-p9
kubectl get pods -n observability
echo "Recursos de métricas y canario:"
kubectl get servicemonitor sa-p10-services -n sa-p9
kubectl get prometheusrule sa-p10-slos -n sa-p9
kubectl get analysistemplate gateway-slo-prometheus -n sa-p9

log_file="$(mktemp)"
kubectl port-forward -n observability \
  svc/observability-kube-prometh-prometheus 19090:9090 >"$log_file" 2>&1 &
forward_pid=$!
cleanup() {
  kill "$forward_pid" 2>/dev/null || true
  wait "$forward_pid" 2>/dev/null || true
  rm -f "$log_file"
}
trap cleanup EXIT

ready=0
for _ in {1..20}; do
  if curl -fsS --max-time 2 http://127.0.0.1:19090/-/ready >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 1
done
if [[ "$ready" != 1 ]]; then
  echo "Prometheus no respondió al túnel. Detalle:" >&2
  sed -n '1,20p' "$log_file" >&2
  exit 1
fi

query() {
  local name="$1" promql="$2"
  echo "Consulta: $name"
  curl -fsS --get --data-urlencode "query=$promql" \
    http://127.0.0.1:19090/api/v1/query |
    python3 -c 'import json,sys; data=json.load(sys.stdin); print("status:",data.get("status")); [print(item["metric"],item["value"][1]) for item in data.get("data",{}).get("result",[])]; print("Sin series en este momento") if not data.get("data",{}).get("result") else None'
}

query "Targets de sa-p9" 'up{namespace="sa-p9"}'
query "Tráfico por servicio" 'sum by (service) (rate(library_http_requests_total[5m]))'
query "Latencia p95" 'histogram_quantile(0.95, sum by (le, service) (rate(library_http_request_duration_seconds_bucket[5m])))'
echo "Verificación finalizada. El dashboard se consulta en Grafana mediante un port-forward local."
