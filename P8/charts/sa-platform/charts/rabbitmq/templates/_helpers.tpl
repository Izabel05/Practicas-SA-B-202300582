{{- define "rabbitmq.fullname" -}}{{ default .Chart.Name .Values.fullnameOverride }}{{- end }}
{{- define "rabbitmq.namespace" -}}{{ .Values.global.namespace | default .Release.Namespace }}{{- end }}
{{- define "rabbitmq.labels" -}}app.kubernetes.io/name: rabbitmq
app.kubernetes.io/instance: {{ .Release.Name }}{{- end }}
