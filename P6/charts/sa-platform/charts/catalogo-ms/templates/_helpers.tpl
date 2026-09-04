{{- define "catalogo-ms.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "catalogo-ms.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "catalogo-ms.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "catalogo-ms.namespace" -}}
{{- if and (hasKey .Values "global") (hasKey .Values.global "namespace") -}}
{{- .Values.global.namespace | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- .Release.Namespace | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "catalogo-ms.labels" -}}
app.kubernetes.io/name: {{ include "catalogo-ms.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "catalogo-ms.selectorLabels" -}}
app.kubernetes.io/name: {{ include "catalogo-ms.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "catalogo-ms.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "catalogo-ms.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- required "serviceAccount.name es obligatorio cuando serviceAccount.create=false" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

