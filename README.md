# K8-ingress-dashboard
Dashboard for all ingresses in a kubernetes cluster

```
docker build . -t ingress-hub && docker run -p 8080:8080 --rm --name ingress-hub -v ~/.kube/config:/root/.kube/config ingress-hub
```