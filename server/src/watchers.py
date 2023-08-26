from kubernetes import client, watch
from kubernetes_ingress import refresh_ingresses

def watch_ingresses():

    api_instance = client.NetworkingV1Api()

    w = watch.Watch()
    for event in w.stream(api_instance.list_ingress_for_all_namespaces):
        print("Event: %s %s %s" % (event['type'],event['object'].kind, event['object'].metadata.name), flush=True)
        refresh_ingresses()

def watch_ingress_classes():

    api_instance = client.NetworkingV1Api()

    w = watch.Watch()
    for event in w.stream(api_instance.list_ingress_class):
        print("Event: %s %s %s" % (event['type'],event['object'].kind, event['object'].metadata.name), flush=True)
        refresh_ingresses()
