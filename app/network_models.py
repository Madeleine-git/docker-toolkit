#!/usr/bin/env python3
"""
network_models.py
=================
Módulo de modelado de dispositivos de red mediante POO.

Mejora aplicada:
  03 - @dataclass en lugar de clases tradicionales.
       Python genera __init__, __repr__ y __eq__ automáticamente.

Clases:
  - NetworkDevice  → clase base con atributos comunes
  - Router         → clase hija para routers
  - Server         → clase hija para servidores
"""

from dataclasses import dataclass, field
from logger import configurar_logger


# ─── LOGGER DEL MÓDULO ───────────────────────────────────────
logger = configurar_logger("network_models")


# ─────────────────────────────────────────────────────────────
# CLASE BASE: NetworkDevice
# ─────────────────────────────────────────────────────────────

@dataclass
class NetworkDevice:
    """
    Clase base que representa cualquier dispositivo de red.

    CONCEPTO — @dataclass:
      El decorador @dataclass genera automáticamente:
        __init__  → constructor con todos los atributos
        __repr__  → representación en texto para print()
        __eq__    → comparación entre objetos (==)

      Sin @dataclass necesitaríamos escribir todo esto a mano.
      Con @dataclass solo declaramos los atributos y sus tipos.
    """
    hostname: str
    ip: str
    mac: str

    def mostrar_info(self) -> None:
        """Muestra información básica del dispositivo."""
        print(f"\n  {'─' * 45}")
        print(f"  Hostname : {self.hostname}")
        print(f"  IP       : {self.ip}")
        print(f"  MAC      : {self.mac}")

    def audit_device(self) -> None:
        """Método de auditoría base. Las clases hijas lo sobreescriben."""
        logger.info(f"Auditoría iniciada para {self.hostname} ({self.ip})")
        print(f"\n  [AUDIT] Dispositivo: {self.hostname}")
        print(f"  [AUDIT] IP:          {self.ip}")
        print(f"  [AUDIT] MAC:         {self.mac}")
        print("  [AUDIT] Directrices generales:")
        print("    • Mantener firmware actualizado")
        print("    • Usar contraseñas seguras")
        print("    • Revisar logs periódicamente")


# ─────────────────────────────────────────────────────────────
# CLASE HIJA: Router
# ─────────────────────────────────────────────────────────────

@dataclass
class Router(NetworkDevice):
    """
    Clase hija que representa un router de red.

    CONCEPTO — @dataclass con herencia:
      Los atributos del padre (hostname, ip, mac) se heredan.
      Solo declaramos los atributos nuevos (interfaces, gateway).
      Python construye el __init__ completo automáticamente:
        Router(hostname, ip, mac, interfaces, gateway)
    """
    interfaces: int = 0
    gateway: str = ""

    def mostrar_info(self) -> None:
        """Muestra información completa del router."""
        super().mostrar_info()
        print(f"  Tipo      : Router")
        print(f"  Interfaces: {self.interfaces}")
        print(f"  Gateway   : {self.gateway}")
        print(f"  {'─' * 45}")

    def audit_device(self) -> None:
        """Directrices de seguridad específicas para routers."""
        logger.info(f"Auditoría de router: {self.hostname} ({self.ip})")
        print(f"\n  {'═' * 45}")
        print(f"  AUDITORÍA DE ROUTER: {self.hostname}")
        print(f"  {'═' * 45}")
        print(f"  IP:         {self.ip}")
        print(f"  MAC:        {self.mac}")
        print(f"  Interfaces: {self.interfaces}")
        print(f"  Gateway:    {self.gateway}")
        print(f"\n  Directrices de seguridad para ROUTER:")
        print("    • Deshabilitar servicios no usados (Telnet, HTTP)")
        print("    • Usar SSH v2 en lugar de Telnet")
        print("    • Configurar ACLs para filtrar tráfico")
        print("    • Activar logging de eventos de red")
        print("    • Cambiar credenciales por defecto")
        print("    • Actualizar IOS/firmware regularmente")
        print(f"  {'═' * 45}")


# ─────────────────────────────────────────────────────────────
# CLASE HIJA: Server
# ─────────────────────────────────────────────────────────────

@dataclass
class Server(NetworkDevice):
    """
    Clase hija que representa un servidor de red.

    CONCEPTO — field(default_factory=list):
      Las listas no pueden ser valores por defecto directos
      en @dataclass porque serían compartidas entre instancias.
      field(default_factory=list) crea una lista nueva
      para cada objeto. Es la forma correcta en @dataclass.
    """
    sistema_operativo: str = ""
    ram_gb: int = 0
    servicios: list[str] = field(default_factory=list)

    def mostrar_info(self) -> None:
        """Muestra información completa del servidor."""
        super().mostrar_info()
        servicios_str: str = ", ".join(self.servicios)
        print(f"  Tipo      : Servidor")
        print(f"  SO        : {self.sistema_operativo}")
        print(f"  RAM       : {self.ram_gb} GB")
        print(f"  Servicios : {servicios_str}")
        print(f"  {'─' * 45}")

    def audit_device(self) -> None:
        """Directrices de seguridad específicas para servidores."""
        logger.info(f"Auditoría de servidor: {self.hostname} ({self.ip})")
        servicios_str: str = ", ".join(self.servicios)
        print(f"\n  {'═' * 45}")
        print(f"  AUDITORÍA DE SERVIDOR: {self.hostname}")
        print(f"  {'═' * 45}")
        print(f"  IP:        {self.ip}")
        print(f"  MAC:       {self.mac}")
        print(f"  SO:        {self.sistema_operativo}")
        print(f"  RAM:       {self.ram_gb} GB")
        print(f"  Servicios: {servicios_str}")
        print(f"\n  Directrices de seguridad para SERVIDOR:")
        print("    • Aplicar actualizaciones de seguridad")
        print("    • Deshabilitar servicios innecesarios")
        print("    • Configurar firewall (ufw/iptables)")
        print("    • Usar autenticación por clave SSH")
        print("    • Configurar fail2ban contra fuerza bruta")
        print("    • Realizar backups periódicos")
        print("    • Monitorizar logs con herramientas SIEM")
        print(f"  {'═' * 45}")


# ─────────────────────────────────────────────────────────────
# MENÚ INTERACTIVO
# ─────────────────────────────────────────────────────────────

def menu_network_models() -> None:
    """Submenú del módulo de modelos de red."""

    # Creamos objetos — ahora sin __init__ explícito
    # @dataclass lo genera automáticamente
    router1 = Router(
        hostname="router-core-01",
        ip="192.168.1.1",
        mac="AA:BB:CC:DD:EE:01",
        interfaces=8,
        gateway="10.0.0.1"
    )

    server1 = Server(
        hostname="server-web-01",
        ip="192.168.1.10",
        mac="AA:BB:CC:DD:EE:02",
        sistema_operativo="Ubuntu 22.04 LTS",
        ram_gb=16,
        servicios=["nginx", "ssh", "postgresql"]
    )

    server2 = Server(
        hostname="server-db-01",
        ip="192.168.1.11",
        mac="AA:BB:CC:DD:EE:03",
        sistema_operativo="Windows Server 2019",
        ram_gb=32,
        servicios=["sqlserver", "rdp", "iis"]
    )

    dispositivos: list[NetworkDevice] = [router1, server1, server2]

    while True:
        print("\n  ── Modelos de red (POO) ────────────────────")
        print("  a.  Ver inventario de dispositivos")
        print("  b.  Auditar todos los dispositivos")
        print("  c.  Auditar un dispositivo específico")
        print("  v.  Volver al menú principal")
        print("  ────────────────────────────────────────────")

        opcion: str = input("\n  Elige una opción [a/b/c/v]: ").strip().lower()

        if opcion == "a":
            print("\n  INVENTARIO DE RED")
            for dispositivo in dispositivos:
                dispositivo.mostrar_info()

        elif opcion == "b":
            print("\n  AUDITORÍA COMPLETA DE RED")
            for dispositivo in dispositivos:
                dispositivo.audit_device()

        elif opcion == "c":
            print("\n  Dispositivos disponibles:")
            for i, d in enumerate(dispositivos):
                print(f"    {i + 1}. {d.hostname} ({d.ip})")

            seleccion: str = input("\n  Elige un número: ").strip()
            try:
                indice: int = int(seleccion) - 1
                if 0 <= indice < len(dispositivos):
                    dispositivos[indice].audit_device()
                else:
                    print("  [!] Número fuera de rango.")
            except ValueError:
                print("  [!] Introduce un número válido.")

        elif opcion == "v":
            break

        else:
            print("  [!] Opción no reconocida.")