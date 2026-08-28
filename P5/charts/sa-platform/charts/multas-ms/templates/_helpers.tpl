{{- define "multas-ms.fullname" -}}{{ default .Chart.Name .Values.fullnameOverride }}{{- end }}
{{- define "multas-ms.namespace" -}}{{ .Values.global.namespace | default .Release.Namespace }}{{- end }}
{{- define "multas-ms.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
{{- define "multas-ms.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
{{- define "multas-ms.serviceAccountName" -}}{{ default (include "multas-ms.fullname" .) .Values.serviceAccount.name }}{{- end }}
