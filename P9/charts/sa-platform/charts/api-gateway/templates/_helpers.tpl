{{- define "api-gateway.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "api-gateway.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "api-gateway.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "api-gateway.namespace" -}}
{{- if and (hasKey .Values "global") (hasKey .Values.global "namespace") -}}
{{- .Values.global.namespace | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- .Release.Namespace | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "api-gateway.labels" -}}
app.kubernetes.io/name: {{ include "api-gateway.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "api-gateway.selectorLabels" -}}
app.kubernetes.io/name: {{ include "api-gateway.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "api-gateway.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "api-gateway.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- required "serviceAccount.name es obligatorio cuando serviceAccount.create=false" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}
