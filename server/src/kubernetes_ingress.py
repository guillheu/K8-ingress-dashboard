from kubernetes import client
from fnmatch import fnmatch
import json

from config import all_configs as CONFIG

def extract_ingress_classes(api_instance):
    ingress_classes = api_instance.list_ingress_class()
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
    return ingress_classes_data, default_ingress_class


# This function extracts ingress information
def extract_ingresses(api_instance, ingress_classes_data):
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
                            rule["tls"] = 'false'
        except:
            print(f"TLS configuration not found for ingress {ingress.metadata.name}")

        for ingress_class in ingress_classes_data:
            if ingress_class["ingress_class_name"] == ingress.spec.ingress_class_name:
                ingress_class["ingresses"].append(ingress_info)


# The main function to refresh ingresses
def refresh_ingresses():

    api_instance = client.NetworkingV1Api()

    ingress_classes_data, default_ingress_class = extract_ingress_classes(api_instance)
    extract_ingresses(api_instance, ingress_classes_data)

    with open(f"{CONFIG.get('HTML_DIR')}/ingresses.json", 'w') as f:
        json.dump(ingress_classes_data, f)


def find_load_balancer_ip_by_ingress_class(ingress_class_name):
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

