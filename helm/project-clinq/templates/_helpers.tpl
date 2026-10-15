{{/*
WHY THIS FILE EXISTS:
Defines reusable template fragments (helpers) used across all other templates.
This avoids repeating the same name/label logic in every file.
*/}}

{{/* Full release name */}}
{{- define "project-clinq.fullname" -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Common labels applied to every resource */}}
{{- define "project-clinq.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/* Selector labels used by Deployments/Services to match pods */}}
{{- define "project-clinq.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
