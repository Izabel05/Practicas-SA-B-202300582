{{- define "prestamos-ms.name" -}}{{ .Chart.Name }}{{- end }}
{{- define "prestamos-ms.fullname" -}}{{ default .Chart.Name .Values.fullnameOverride }}{{- end }}
{{- define "prestamos-ms.namespace" -}}{{ .Values.global.namespace | default .Release.Namespace }}{{- end }}
{{- define "prestamos-ms.labels" -}}
app.kubernetes.io/name: {{ include "prestamos-ms.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end }}
{{- define "prestamos-ms.selectorLabels" -}}
app.kubernetes.io/name: {{ include "prestamos-ms.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
{{- define "prestamos-ms.serviceAccountName" -}}{{ default (include "prestamos-ms.fullname" .) .Values.serviceAccount.name }}{{- end }}
