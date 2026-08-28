{{- define "cronjobs-database.fullname" -}}{{- default (printf "%s-cronjobs-database" .Release.Name) .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}{{- end -}}
{{- define "cronjobs-database.namespace" -}}{{- required "global.namespace es obligatorio" .Values.global.namespace -}}{{- end -}}
{{- define "cronjobs-database.labels" -}}
app.kubernetes.io/name: cronjobs-database
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
{{- define "cronjobs-database.selectorLabels" -}}
app.kubernetes.io/name: cronjobs-database
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
