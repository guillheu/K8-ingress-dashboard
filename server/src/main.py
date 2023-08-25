from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from kubernetes import client, config, watch
from kubernetes.config import ConfigException
from fnmatch import fnmatch
import subprocess
import json
import os
import threading

app = FastAPI()

HTML_DIR=os.environ.get("HTML_DIR")

# Static files directory
app.mount("/static", StaticFiles(directory=HTML_DIR), name="static")

# Serve the static index.html page
@app.get("/")
def root():
    return FileResponse(f"{HTML_DIR}/index.html")

# Serve the favicon
@app.get("/favicon.ico")
def root():
    return FileResponse(f"{HTML_DIR}/favicon.ico")

# Serve the static ingresses.json file
@app.get("/ingresses")
def ingresses():
    return FileResponse(f"{HTML_DIR}/ingresses.json")



def watch_ingresses():
    try:
        # Load configuration inside the Pod
        config.load_incluster_config()
    except ConfigException:
        # Load configuration for testing
        config.load_kube_config()

    api_instance = client.NetworkingV1Api()

    w = watch.Watch()
    for event in w.stream(api_instance.list_ingress_for_all_namespaces):
        print("Event: %s %s %s" % (event['type'],event['object'].kind, event['object'].metadata), flush=True)
        refresh_ingresses()

def refresh_ingresses():
    try:
        # Load configuration inside the Pod
        config.load_incluster_config()
    except ConfigException:
        # Load configuration for testing
        config.load_kube_config()

    # Create an API client
    api_instance = client.NetworkingV1Api()

    # List all ingresses in all namespaces
    ingresses = api_instance.list_ingress_for_all_namespaces()

    # Extract relevant ingress data
    ingresses_data = []
    for ingress in ingresses.items:
        ingress_info = {
            'name': ingress.metadata.name,
            'namespace': ingress.metadata.namespace,
            'rules': []
        }
        try:
            ingress_info['cert-manager cluster issuer'] = ingress.metadata.annotations["cert-manager.io/cluster-issuer"]
        except:
            print(f"could not find \"cert-manager.io/cluster-issuer\" annotation for ingress {ingress.metadata.name}")
        try:
            ingress_info['ingress class name'] = ingress.spec.ingress_class_name
        except:
            print(f"could not find spec field ingressClassName for ingress {ingress.metadata.name}")
        for rule in ingress.spec.rules:
            ingress_rule = {
                'host': rule.host,
                'tls': 'false',
                'paths': []
            }
            for path in rule.http.paths:
                ingress_rule["paths"].append(path.path)
            ingress_info["rules"].append(ingress_rule)
        try:
            for tls in ingress.spec.tls:
                for tls_host in tls.hosts:
                    for rule in ingress_info["rules"]:
                        if fnmatch(rule["host"], tls_host):
                            rule["tls"] = 'true'
                        else:
                            ruse["tls"] = 'false'
        except:
            print(f"TLS configuration not found for ingress {ingress.metadata.name}")
        ingresses_data.append(ingress_info)
    with open(f"{HTML_DIR}/ingresses.json", 'w') as f:
        json.dump(ingresses_data, f)

    # Serve the updated ingresses.json file
    return FileResponse(f"{HTML_DIR}/ingresses.json")

# Function to run on startup
@app.on_event("startup")
async def startup_event():
    threading.Thread(target=watch_ingresses, daemon=True).start()
    refresh_ingresses()