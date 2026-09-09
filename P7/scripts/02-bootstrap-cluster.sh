#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:-sa-p6}"
RELEASE="${2:-sa-platform}"

kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
kubectl label namespace "$NAMESPACE" app.kubernetes.io/managed-by=Helm --overwrite
kubectl annotate namespace "$NAMESPACE" \
  meta.helm.sh/release-name="$RELEASE" \
  meta.helm.sh/release-namespace="$NAMESPACE" \
  --overwrite

create_database_secret() {
  local secret_name="$1"
  local prompt_text="$2"
  local database_url=""

  while [[ "$database_url" != postgresql://* ]]; do
    read -r -s -p "$prompt_text: " database_url
    printf '\n'
    if [[ "$database_url" != postgresql://* ]]; then
      printf 'El valor debe comenzar con postgresql://\n' >&2
    fi
  done

  kubectl --namespace "$NAMESPACE" create secret generic "$secret_name" \
    --from-literal="database-url=$database_url" \
    --dry-run=client -o yaml | kubectl apply -f -

  unset database_url
}

create_database_secret auth-postgresql-credentials "URL de auth_db"
create_database_secret catalog-postgresql-credentials "URL de catalogo_db"
create_database_secret loans-postgresql-credentials "URL de prestamos_db"
create_database_secret fines-postgresql-credentials "URL de multas_db"
create_database_secret cronjobs-postgresql-credentials "URL de cronjobs_db"

JWT_SECRET="$(openssl rand -hex 32)"
kubectl --namespace "$NAMESPACE" create secret generic jwt-credentials \
  --from-literal="JWT_SECRET=$JWT_SECRET" \
  --dry-run=client -o yaml | kubectl apply -f -
unset JWT_SECRET

kubectl --namespace "$NAMESPACE" get secrets
