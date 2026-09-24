{{- define "catalog-database.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "catalog-database.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "catalog-database.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "catalog-database.namespace" -}}
{{- if and (hasKey .Values "global") (hasKey .Values.global "namespace") -}}
{{- .Values.global.namespace | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- .Release.Namespace | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "catalog-database.labels" -}}
app.kubernetes.io/name: {{ include "catalog-database.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "catalog-database.selectorLabels" -}}
app.kubernetes.io/name: {{ include "catalog-database.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

