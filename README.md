
# Practica-4-VLAN-Hopping-VTP-Attack-DNS-Spoofing-gns3-y-scapy

**Asignatura:** Seguridad en Redes

**Estudiante:** Roberto de Jesus

**Matrícula:** 2023-0348

**Profesor:** Jonathan Esteban Rondón

**Fecha:** Febrero 2026

**Link del video**: [[https://youtu.be/F8MH4ZfZl5I](https://youtu.be/F8MH4ZfZl5I)]

---

##  Descripción General

Este proyecto implementa una herramienta única de auditoría automatizada desarrollada en **Python** con el framework **Scapy**. El script central **`Ataquesyer_Tarea4.py`** integra todas las funciones de ataque y descubrimiento necesarias para la práctica, eliminando la necesidad de scripts externos.(hay 2 versiones del script, ambos estan confirmado con funcionar en el entorno virtual de gns3 y tambien con una configuracion especifica de los switches y routers)

###  Script Central: `Ataquesyer_Tarea4.py`

Este archivo automatizado realiza las siguientes funciones:

* **Detección Dinámica**: Obtiene IPs y Gateway sin configuración manual.
* **VTP Attack**: Agrega y borra VLANs manipulando el número de revisión.
* **DTP VLAN Hopping**: Negocia dinámicamente el cambio de un puerto de acceso a Trunk.
* **DNS Spoofing**: Intercepta y falsifica el registro de `itla.edu.do` en tiempo real.

---

##  Topología del Laboratorio

![image alt](https://github.com/boss7284/d.u.m.p2/blob/main/Topologiasemana4.png)

###  Configuración de Red (R1 y SW1)

| Dispositivo | Interfaz | IP / VLAN | Rol / Seguridad |
| --- | --- | --- | --- |
| **R1** | Fa0/0.10 | 192.168.10.1 | Gateway & AAA RADIUS Server |
| **SW1** | Gi0/1 | VLAN 10 | Puerto Víctima (Hardened) |
| **SW1** | Gi0/2 | VLAN 10 | Puerto Atacante (Hardened) |
| **Kali** | eth0 | 192.168.10.50 | Atacante (Script Automatizado) |

===========================================================================================
```
🔵 CONFIGURACIÓN COMPLETA – ROUTER R1 (Cisco IOS)
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

🟢 CONFIGURACIÓN COMPLETA – SWITCH SW1 (IOSvL2 / QEMU)
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

🟥 CONFIGURACIÓN – PC VÍCTIMA (VPCS)
ip 192.168.10.10 255.255.255.0 192.168.10.1
save

🔴 CONFIGURACIÓN – KALI LINUX (ATACANTE)
sudo ip addr flush dev eth0
sudo ip addr add 192.168.10.50/24 dev eth0
sudo ip link set eth0 up
sudo ip route add default via 192.168.10.1
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1
sudo systemctl stop avahi-daemon
sudo systemctl stop NetworkManager-wait-online
```
---

##  Configuraciones Técnicas (Hardening y AAA)

### ROUTER R1 (AAA & RADIUS)

Se configuró AAA para autenticar vía RADIUS con la IP de Kali (192.168.10.50):

```cisco
aaa new-model
radius server RAD1
 address ipv4 192.168.10.50 auth-port 1812 acct-port 1813
 key radius123
aaa group server radius RAD-GRP
 server name RAD1
aaa authentication login default group RAD-GRP local
aaa authorization exec default group RAD-GRP local
aaa accounting exec default start-stop group RAD-GRP

```

![image alt](https://github.com/boss7284/d.u.m.p2/blob/main/Screenshot%20aaaradius.png)

### SWITCH SW1 (Seguridad L2)

Protección activa contra los ataques del script:

```cisco
interface GigabitEthernet0/2
 switchport mode access
 switchport nonegotiate
 spanning-tree portfast
 spanning-tree bpduguard enable
 no cdp enable

```
![image alt]()

---

##  Ejecución y Verificación de Ataques

Para ejecutar la auditoría completa, solo se requiere el script principal:

```bash
# Iniciar herramienta automatizada
sudo python3 Ataquesyer_Tarea4.py

```
![image alt](https://github.com/boss7284/d.u.m.p2/blob/main/ejecucoinSemana6tarea4.png)

### 1. VTP Attack (Verificación)

* **Comando**: `show vlan brief` / `show vtp status`
* **Resultado**: La base de datos de VLANs se actualiza con los cambios inyectados por el script.

![image alt](https://github.com/boss7284/d.u.m.p2/blob/main/Screenshot%20VTPattack.png)

### 2. DTP VLAN Hopping (Verificación)

* **Comando**: `show interfaces gi0/2 switchport`
* **Resultado esperado**:
* Administrative Mode: `dynamic desirable`
* Operational Mode: `trunk`

![image alt](https://github.com/boss7284/d.u.m.p2/blob/main/Screenshot%20DTPtrunkcheck.png)


### 3. DNS Spoofing (Verificación)

* **Desde VPCS**: `ping itla.edu.do` (Resuelve a 192.168.10.50).
* **Desde Kali**: Simulación de query con `nslookup itla.edu.do 192.168.10.1`.

![image alt](https://github.com/boss7284/d.u.m.p2/blob/main/Screenshot%20DNSspoofing.png)

---

##  Comandos de Auditoría AAA

Para validar la seguridad RADIUS configurada:

* `show aaa servers`
* `show aaa sessions`
* `debug radius`
* `debug aaa authentication`

![image alt](https://github.com/boss7284/d.u.m.p2/blob/main/Screenshot%20aaaradius2.png)

---

##  Requisitos

* **Kali Linux** con Scapy, Netifaces y Yersinia instalados.
* **Python 3.10+**.
* GNS3 con imágenes IOSv / IOSvL2.

---

**Desarrollado por:** Roberto de Jesus

**Nota:** Este proyecto utiliza exclusivamente el framework Scapy integrado en **Ataquesyer_Tarea4.py** para todas las fases de la auditoría.
