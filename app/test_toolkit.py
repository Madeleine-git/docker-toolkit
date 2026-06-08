#!/usr/bin/env python3
"""
test_toolkit.py
===============
Tests unitarios del SysAdmin Toolkit.

CONCEPTO — pytest:
  Busca automáticamente funciones que empiecen por 'test_'
  y las ejecuta. Si no lanza excepción → PASSED.
  Si lanza AssertionError → FAILED.

CONCEPTO — assert:
  Verifica que una condición es True.
  assert resultado == esperado
  Si es False → el test falla con AssertionError.
"""

import pytest
import os
import tempfile
from log_parser import parsear_log
from os_utils import check_ping


# ─── DATOS DE PRUEBA ─────────────────────────────────────────
# Líneas de log controladas para los tests.
# Sabemos exactamente qué IPs hay y cuántas veces aparecen.
LINEAS_LOG_PRUEBA: str = """May 19 03:21:04 servidor sshd[1235]: Failed password for root from 185.220.101.45 port 22 ssh2
May 19 03:21:05 servidor sshd[1236]: Failed password for root from 185.220.101.45 port 22 ssh2
May 19 03:21:06 servidor sshd[1237]: Failed password for admin from 185.220.101.45 port 22 ssh2
May 19 03:21:08 servidor sshd[1239]: Failed password for ubuntu from 45.33.32.156 port 22 ssh2
May 19 03:21:09 servidor sshd[1240]: Failed password for root from 45.33.32.156 port 22 ssh2
May 19 03:21:10 servidor sshd[1241]: Accepted password for madeleine from 192.168.1.15 port 22 ssh2
May 19 03:21:12 servidor sshd[1243]: Failed password for admin from 91.241.19.77 port 22 ssh2
May 19 03:21:13 servidor sshd[1244]: Failed password for root from 91.241.19.77 port 22 ssh2
"""


def crear_log_temporal(contenido: str) -> str:
    """
    Crea un fichero de log temporal para los tests.

    CONCEPTO — tempfile:
      Crea ficheros temporales que no ensucian el proyecto.
      Se borran automáticamente cuando terminan los tests.
    """
    fichero_temp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".log",
        delete=False,
        encoding="utf-8"
    )
    fichero_temp.write(contenido)
    fichero_temp.close()
    return fichero_temp.name


# ─── TESTS DEL LOG PARSER ────────────────────────────────────

class TestLogParser:
    """Tests para el módulo log_parser.py"""

    def test_detecta_ips_correctamente(self) -> None:
        """
        Verifica que parsear_log detecta exactamente
        las IPs que tienen intentos fallidos.
        """
        ruta = crear_log_temporal(LINEAS_LOG_PRUEBA)
        try:
            conteo = parsear_log(ruta)

            assert "185.220.101.45" in conteo, \
                "Debería detectar 185.220.101.45"
            assert "45.33.32.156" in conteo, \
                "Debería detectar 45.33.32.156"
            assert "91.241.19.77" in conteo, \
                "Debería detectar 91.241.19.77"

            # Login exitoso NO debe estar en el conteo
            assert "192.168.1.15" not in conteo, \
                "No debería incluir logins exitosos"
        finally:
            os.unlink(ruta)

    def test_cuenta_intentos_correctamente(self) -> None:
        """
        Verifica que el conteo de intentos por IP es exacto.
        """
        ruta = crear_log_temporal(LINEAS_LOG_PRUEBA)
        try:
            conteo = parsear_log(ruta)

            # 185.220.101.45 aparece 3 veces
            assert conteo["185.220.101.45"] == 3, \
                f"Esperaba 3, got {conteo.get('185.220.101.45')}"

            # 45.33.32.156 aparece 2 veces
            assert conteo["45.33.32.156"] == 2, \
                f"Esperaba 2, got {conteo.get('45.33.32.156')}"

            # 91.241.19.77 aparece 2 veces
            assert conteo["91.241.19.77"] == 2, \
                f"Esperaba 2, got {conteo.get('91.241.19.77')}"
        finally:
            os.unlink(ruta)

    def test_log_sin_fallos_devuelve_vacio(self) -> None:
        """
        Verifica que un log solo con logins exitosos
        devuelve diccionario vacío.
        """
        log_exitosos = """May 19 03:21:10 servidor sshd[1241]: Accepted password for admin from 192.168.1.10 port 22 ssh2
May 19 03:21:11 servidor sshd[1242]: Accepted password for ubuntu from 192.168.1.15 port 22 ssh2
"""
        ruta = crear_log_temporal(log_exitosos)
        try:
            conteo = parsear_log(ruta)
            assert len(conteo) == 0, \
                "Log sin fallos debe devolver diccionario vacío"
        finally:
            os.unlink(ruta)

    def test_fichero_inexistente_no_explota(self) -> None:
        """
        Verifica que si el fichero no existe,
        la función devuelve diccionario vacío sin explotar.
        """
        conteo = parsear_log("fichero_que_no_existe.log")
        assert isinstance(conteo, dict), \
            "Debe devolver un diccionario"
        assert len(conteo) == 0, \
            "Fichero inexistente debe devolver diccionario vacío"

    def test_fichero_vacio_no_explota(self) -> None:
        """
        Verifica que un fichero vacío no explota.
        """
        ruta = crear_log_temporal("")
        try:
            conteo = parsear_log(ruta)
            assert isinstance(conteo, dict)
            assert len(conteo) == 0
        finally:
            os.unlink(ruta)

    def test_no_cuenta_logins_exitosos(self) -> None:
        """
        Verifica que Accepted password no se cuenta.
        """
        log_mixto = """May 19 03:21:10 servidor sshd[1241]: Accepted password for admin from 10.0.0.1 port 22 ssh2
May 19 03:21:12 servidor sshd[1243]: Failed password for root from 185.220.101.45 port 22 ssh2
"""
        ruta = crear_log_temporal(log_mixto)
        try:
            conteo = parsear_log(ruta)
            assert "10.0.0.1" not in conteo, \
                "Login exitoso no debe contarse"
            assert "185.220.101.45" in conteo, \
                "Login fallido sí debe contarse"
        finally:
            os.unlink(ruta)


# ─── TESTS DE OS_UTILS ───────────────────────────────────────

class TestOsUtils:
    """Tests para el módulo os_utils.py"""

    def test_ping_localhost_responde(self) -> None:
        """
        127.0.0.1 es la IP del propio servidor.
        Siempre debe responder.
        """
        resultado = check_ping("127.0.0.1")
        assert resultado is True, \
            "El ping a localhost siempre debe responder"

    def test_ping_ip_inexistente_devuelve_false(self) -> None:
        """
        Una IP que no existe debe devolver False.
        """
        resultado = check_ping("10.255.255.254")
        assert resultado is False, \
            "IP inexistente debe devolver False"

    def test_ping_devuelve_bool(self) -> None:
        """
        check_ping siempre debe devolver bool,
        nunca None ni otro tipo.
        """
        resultado = check_ping("127.0.0.1")
        assert isinstance(resultado, bool), \
            f"Debe devolver bool, got {type(resultado)}"


# ─── TESTS DE ESTRUCTURAS DE DATOS ───────────────────────────

class TestEstructurasDatos:
    """
    Tests que verifican las estructuras de datos
    usadas en el proyecto.
    """

    def test_set_elimina_duplicados(self) -> None:
        """Set elimina IPs duplicadas automáticamente."""
        ips: list[str] = [
            "185.220.101.45",
            "185.220.101.45",
            "45.33.32.156",
            "185.220.101.45"
        ]
        ips_unicas: set[str] = set(ips)
        assert len(ips_unicas) == 2, \
            f"Debería haber 2 IPs únicas, got {len(ips_unicas)}"

    def test_diccionario_conteo_manual(self) -> None:
        """Verifica la lógica de conteo con diccionario."""
        conteo: dict[str, int] = {}
        ips: list[str] = [
            "1.2.3.4", "1.2.3.4", "1.2.3.4",
            "5.6.7.8", "5.6.7.8"
        ]
        for ip in ips:
            if ip in conteo:
                conteo[ip] += 1
            else:
                conteo[ip] = 1

        assert conteo["1.2.3.4"] == 3
        assert conteo["5.6.7.8"] == 2
        assert len(conteo) == 2


# ─── TESTS DE MANEJO DE ERRORES ──────────────────────────────

class TestManejoErrores:
    """
    Tests que verifican que el código maneja
    errores sin explotar.
    """

    def test_parsear_log_maneja_ruta_invalida(self) -> None:
        """parsear_log no lanza excepción con ruta inválida."""
        try:
            resultado = parsear_log("/ruta/invalida/auth.log")
            assert isinstance(resultado, dict)
        except Exception as e:
            pytest.fail(f"Lanzó excepción inesperada: {e}")

    def test_parsear_log_maneja_fichero_vacio(self) -> None:
        """parsear_log maneja fichero vacío correctamente."""
        ruta = crear_log_temporal("")
        try:
            resultado = parsear_log(ruta)
            assert isinstance(resultado, dict)
            assert len(resultado) == 0
        except Exception as e:
            pytest.fail(f"Lanzó excepción inesperada: {e}")
        finally:
            os.unlink(ruta)