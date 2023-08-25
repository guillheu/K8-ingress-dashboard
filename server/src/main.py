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
        print("Event: %s %s %s" % (event['type'],event['object'].kind, event['object'].metadata.name), flush=True)
        refresh_ingresses()

def watch_ingress_classes():
    try:
        # Load configuration inside the Pod
        config.load_incluster_config()
    except ConfigException:
        # Load configuration for testing
        config.load_kube_config()

    api_instance = client.NetworkingV1Api()

    w = watch.Watch()
    for event in w.stream(api_instance.list_ingress_class):
        print("Event: %s %s %s" % (event['type'],event['object'].kind, event['object'].metadata.name), flush=True)
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
    ingress_classes = api_instance.list_ingress_class()

    # Extract relevant ingress data
    ingress_classes_data = []
    default_ingress_class = None
    for ingress_class in ingress_classes.items:
        ingress_class_info = {
            'ingress_class_name': ingress_class.metadata.name,
            'controller': ingress_class.spec.controller,
            'lb_ip': find_load_balancer_ip_by_ingress_class(ingress_class.metadata.name),
            'ingresses': []
        }
        ingress_classes_data.append(ingress_class_info)
        try:
            if ingress_class.metadata.annotations["ingressclass.kubernetes.io/is-default-class"] == 'true':
                default_ingress_class = ingress_class.metadata.name
                print(f"{ingress_class.metadata.name} is the default ingress class.")
        except:
            pass

    # List all ingresses in all namespaces
    ingresses = api_instance.list_ingress_for_all_namespaces()

    for ingress in ingresses.items:
        ingress_info = {
            'name': ingress.metadata.name,
            'namespace': ingress.metadata.namespace,
            'rules': []
        }
        try:
            ingress_info['cert_manager_cluster_issuer'] = ingress.metadata.annotations["cert-manager.io/cluster-issuer"]
        except:
            print(f"could not find \"cert-manager.io/cluster-issuer\" annotation for ingress {ingress.metadata.name}")
        # try:
        #     ingress_info['ingress_class_name'] = ingress.spec.ingress_class_name
        # except:
        #     print(f"could not find spec field ingressClassName for ingress {ingress.metadata.name}")
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
        for ingress_class in ingress_classes_data:
            if ingress_class["ingress_class_name"] == ingress.spec.ingress_class_name:
                ingress_class["ingresses"].append(ingress_info)
                
    
    with open(f"{HTML_DIR}/ingresses.json", 'w') as f:
        json.dump(ingress_classes_data, f)

from kubernetes import client, config

def find_load_balancer_ip_by_ingress_class(ingress_class_name):
    config.load_kube_config() # Or config.load_incluster_config()
    networking_v1 = client.NetworkingV1Api()
    apps_v1 = client.AppsV1Api()
    v1 = client.CoreV1Api()

    # Get Ingress Class
    ingress_class = networking_v1.read_ingress_class(ingress_class_name)
    controller_name = ingress_class.spec.controller.split("/")[-1]

    # Search for the Deployment/StatefulSet/DaemonSet responsible for the controller (modify this as needed)
    deployments = apps_v1.list_deployment_for_all_namespaces(label_selector=f"app.kubernetes.io/instance={controller_name}")

    if not deployments.items:
        print("No matching deployments found.", flush=True)
        return
    if len(deployments.items) > 1:
        print("More than one deployment matching ; cannot find ingress controller pod.", flush=True)
        return

    # Extract the labels of the first matching deployment
    deployment_labels = deployments.items[0].spec.selector.match_labels
    namespace = deployments.items[0].metadata.namespace

    # Find Services that select those labels in the same namespace as the deployment
    services = v1.list_namespaced_service(namespace, label_selector=",".join([f"{k}={v}" for k, v in deployment_labels.items()]))
    for service in services.items:
        if service.spec.type == 'LoadBalancer':
            return service.status.load_balancer.ingress[0].ip

    print("No matching LoadBalancer service found.", flush=True)
    return None



# Function to run on startup
@app.on_event("startup")
async def startup_event():
    threading.Thread(target=watch_ingresses, daemon=True).start()
    threading.Thread(target=watch_ingress_classes, daemon=True).start()
    # refresh_ingresses()
    # refr