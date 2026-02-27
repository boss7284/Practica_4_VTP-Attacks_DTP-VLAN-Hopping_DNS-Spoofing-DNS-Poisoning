# Practica-Seguridad-Redes-4-Semana-6
---

**Asignatura:** Seguridad en Redes

**Estudiante:** Roberto de Jesus

**Matrícula:** 2023-0348

**Profesor:** Jonathan Esteban Rondón

**Fecha:** Febrero 2026

**Link del video**: [https://youtu.be/zQ0hL_5hpos](https://youtu.be/zQ0hL_5hpos)

---

##  Tabla de Contenidos

* [Descripción General](https://www.google.com/search?q=%23-descripci%C3%B3n-general)
* [Topología del Laboratorio](https://www.google.com/search?q=%23-topolog%C3%ADa-del-laboratorio)
* [Configuraciones de Base (Hardening y AAA)](https://www.google.com/search?q=%23-configuraciones-de-base)
* [Scripts de Ataque](https://www.google.com/search?q=%23-scripts-de-ataque)
* [Verificación de Ataques](https://www.google.com/search?q=%23-verificaci%C3%B3n-de-ataques)
* [Verificación de AAA y Seguridad](https://www.google.com/search?q=%23-verificaci%C3%B3n-de-aaa-y-seguridad)

---

##  Descripción General

Esta práctica tiene como objetivo auditar la seguridad de una red Cisco mediante la ejecución de ataques controlados de Capa 2 (VTP, DTP) y Capa 7 (DNS Spoofing), mientras se implementa una infraestructura robusta utilizando **AAA (RADIUS)** y técnicas de **Hardening** de red.

### Ataques Incluidos

* **VTP Attacks**: Adición y eliminación de VLANs mediante manipulación de revisiones.
* **DTP VLAN Hopping**: Salto de VLAN mediante la negociación forzada de enlaces troncales.
* **DNS Spoofing**: Envenenamiento de resolución de nombres para `itla.edu.do`.

> **ADVERTENCIA** > Estas herramientas son para uso exclusivo en laboratorios educativos (GNS3). Cualquier uso fuera de este entorno es ilegal.

---

##  Topología del Laboratorio

### Configuraciones de Base

####  R1 (Router Cisco IOS) - Configuración AAA

```cisco
enable
conf t
hostname R1
no ip domain-lookup
enable secret class123
username admin privilege 15 secret cisco123

aaa new-model
radius server RAD1
 address ipv4 192.168.10.50 auth-port 1812 acct-port 1813
 key radius123
aaa group server radius RAD-GRP
 server name RAD1
aaa authentication login default group RAD-GRP local
aaa authorization exec default group RAD-GRP local
aaa accounting exec default start-stop group RAD-GRP

line vty 0 4
 login authentication default
 transport input telnet ssh
exit
interface FastEthernet0/0
 no shutdown
exit
interface FastEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
exit
end
write memory

```

####  SW1 (Cisco IOSvL2) - Hardening

```cisco
enable
conf t
hostname SW1
no ip domain-lookup
vtp domain LAB
vtp password vtp123
vtp mode server
vlan 10
 name USERS
exit
interface GigabitEthernet0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10
exit
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
 switchport nonegotiate
 spanning-tree portfast
 spanning-tree bpduguard enable
 no cdp enable
exit
interface GigabitEthernet0/2
 switchport mode access
 switchport access vlan 10
 switchport nonegotiate
 spanning-tree portfast
 spanning-tree bpduguard enable
 no cdp enable
exit
end
write memory

```

####  PC VÍCTIMA (VPCS) &  KALI LINUX

```bash
# Configuración VPCS
ip 192.168.10.10 255.255.255.0 192.168.10.1
save

# Configuración Kali (Atacante)
sudo ip addr flush dev eth0
sudo ip addr add 192.168.10.50/24 dev eth0
sudo ip link set eth0 up
sudo ip route add default via 192.168.10.1
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
sudo systemctl stop avahi-daemon

```

---

##  Scripts de Ataque

### Ejecución de los scripts

* **VTP Attack**: `sudo python3 vtp_attack.py` (Previa inspección con `tcpdump -i eth0 -XX | grep -A5 "01:00:0c:cc:cc:cc"`)
* **DTP Attack**: `sudo python3 dtp_attack.py --verify`
* **DNS Spoofing**: `sudo python3 dns_spoofing.py`

---

##  Verificación de Ataques

### VTP

```cisco
SW1# show vlan brief
SW1# show vtp status

```

### DTP VLAN Hopping

Al ejecutar el ataque, verifica el cambio de modo:

```cisco
SW1# show interfaces gi0/2 switchport | include Mode
SW1# show interfaces gi0/2 trunk

```

* **Administrative Mode**: `dynamic desirable`
* **Operational Mode**: `trunk`
* **Operational Trunking Encapsulation**: `dot1q`

### DNS Spoofing

Desde VPCS:

```bash
VPCS> ping itla.edu.do
VPCS> curl http://192.168.10.50

```

---

##  Verificación de AAA y Seguridad

Para validar que la autenticación está funcionando correctamente y que la topología es segura:

### Comandos de depuración y estado de AAA

```cisco
debug aaa authentication
debug aaa authorization
debug radius
show aaa servers
show aaa sessions

```

### Seguridad de Capa 2

Se ha verificado la seguridad mediante:

1. **DTP**: `switchport nonegotiate` (Deshabilitado).
2. **STP**: `bpduguard enable` (Protección contra Root Bridge attacks).
3. **CDP**: `no cdp enable` (Prevención de reconocimiento de red).

---

**Última actualización:** Febrero 2026

**Versión:** 1.0.0
