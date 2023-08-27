{{/* Generate the full name */}}
{{- define "ingress-hub.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end -}}

{{/* Generate the name */}}
{{- define "ingress-hub.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end -}}

{{/* Return the namespace of the release */}}
{{- define "ingress-hub.namespace" -}}
{{- .Release.Namespace }}
{{- end -}}
