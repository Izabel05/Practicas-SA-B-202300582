{{- define "loans-database.name" -}}{{ .Chart.Name }}{{- end }}
{{- define "loans-database.fullname" -}}{{ default .Chart.Name .Values.fullnameOverride }}{{- end }}
{{- define "loans-database.namespace" -}}{{ .Values.global.namespace | default .Release.Namespace }}{{- end }}
{{- define "loans-database.labels" -}}
app.kubernetes.io/name: {{ include "loans-database.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
{{- define "loans-database.selectorLabels" -}}
app.kubernetes.io/name: {{ include "loans-database.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
