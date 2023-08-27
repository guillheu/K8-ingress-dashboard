import socket

def check_hostnames_for_ip(ip_address, hostnames):
    matching_hostnames = set()
    for hostname in hostnames:
        try:
            # Get all the IP addresses associated with the hostname
            ip_list = [i[4][0] for i in socket.getaddrinfo(hostname, None)]
            if ip_address in ip_list:
                matching_hostnames.add(hostname)
        except (socket.gaierror, socket.herror):
            # Ignore resolution errors
            pass
    return list(matching_hostnames)