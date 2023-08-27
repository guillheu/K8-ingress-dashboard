import json
from net.hostnames import check_hostnames_for_ip

def check_ingress_hostnames(json_data):
    for ingress_controller in json_data:
        lb_ip = ingress_controller.get('lb_ip')
        ingress_list = ingress_controller.get('ingresses', [])

        all_hosts = []
        for ingress in ingress_list:
            for rule in ingress["rules"]:
                host = rule['host']
                if rule:
                    all_hosts.append(host)
        print(f"DEBUG: {lb_ip}\nDEBUG: {all_hosts}")
        matching_hostnames = check_hostnames_for_ip(lb_ip, all_hosts)
        
        for ingress in ingress_list:
            for rule in ingress["rules"]:
                if rule["host"] in matching_hostnames:
                    rule["host_points_to_lb_ip"] = 'true'

        print(f"Matching hostnames for IP {lb_ip}: {matching_hostnames}", flush=True)
