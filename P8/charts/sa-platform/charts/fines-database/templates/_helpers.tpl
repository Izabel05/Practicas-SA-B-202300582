{{- define "fines-database.fullname" -}}{{ default .Chart.Name .Values.fullnameOverride }}{{- end }}
{{- define "fines-database.namespace" -}}{{ .Values.global.namespace | default .Release.Namespace }}{{- end }}
{{- define "fines-database.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
{{- define "fines-database.selectorLabels" -}}{{ include "fines-database.labels" . }}{{- end }}
