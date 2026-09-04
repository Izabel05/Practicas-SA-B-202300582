{{- define "autenticacion-ms.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "autenticacion-ms.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "autenticacion-ms.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "autenticacion-ms.namespace" -}}
{{- if and (hasKey .Values "global") (hasKey .Values.global "namespace") -}}
{{- .Values.global.namespace | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- .Release.Namespace | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "autenticacion-ms.labels" -}}
app.kubernetes.io/name: {{ include "autenticacion-ms.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "autenticacion-ms.selectorLabels" -}}
app.kubernetes.io/name: {{ include "autenticacion-ms.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "autenticacion-ms.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "autenticacion-ms.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- required "serviceAccount.name es obligatorio cuando serviceAccount.create=false" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

