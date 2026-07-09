import ctypes
import socket
import subprocess
import threading
import time
from typing import Dict, Tuple

import requests


# Interruptor global controlado pela UI (main.py)
monitorar_ping = False

_estado_rede: Dict[str, str] = {
    "ip_publico": "N/A",
    "ping_ms": "N/A",
    "status_internet": "Indefinido",
}

_lock_rede = threading.Lock()
_thread_rede_iniciada = False


def _is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _ip_local_valido() -> Tuple[bool, str]:
    ip = _obter_ip_local()
    if ip in ("N/A", "", None):
        return False, "Adaptador local sem IP válido."
    return True, ip


def _get_ip_publico(timeout: int = 5) -> str:
    try:
        # Serviço simples e estável
        r = requests.get("https://api.ipify.org?format=text", timeout=timeout)
        txt = (r.text or "").strip()
        return txt if txt else "N/A"
    except Exception:
        return "N/A"


def _ping_google(timeout: int = 3) -> str:
    """
    Executa ping para 8.8.8.8 no Windows e extrai tempo em ms.
    """
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", str(timeout * 1000), "8.8.8.8"],
            capture_output=True,
            text=True,
            timeout=timeout + 1,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        out = (result.stdout or "").lower()

        # Procura por "tempo=23ms" ou "time=23ms"
        for token in out.replace(",", " ").split():
            if "ms" in token and ("tempo=" in token or "time=" in token):
                valor = (
                    token.replace("tempo=", "")
                    .replace("time=", "")
                    .replace("ms", "")
                    .strip()
                )
                if valor:
                    return valor

        # Fallback se conexão existe mas parsing falhou
        if result.returncode == 0:
            return "OK"
        return "N/A"
    except Exception:
        return "N/A"


def _loop_rede_background() -> None:
    global monitorar_ping

    while True:
        if not monitorar_ping:
            time.sleep(0.25)
            continue

        ip_pub = _get_ip_publico(timeout=4)
        ping = _ping_google(timeout=2)

        status = "Online" if ping not in ("N/A", "") else "Offline"

        with _lock_rede:
            _estado_rede["ip_publico"] = ip_pub
            _estado_rede["ping_ms"] = ping
            _estado_rede["status_internet"] = status

        time.sleep(2.0)


def iniciar_thread_rede() -> None:
    global _thread_rede_iniciada
    if _thread_rede_iniciada:
        return
    _thread_rede_iniciada = True
    t = threading.Thread(target=_loop_rede_background, daemon=True, name="ThreadRede")
    t.start()


def _obter_ip_local() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "N/A"


def obter_status_rede() -> Dict[str, str]:
    with _lock_rede:
        base = dict(_estado_rede)
    base["ip_local"] = _obter_ip_local()
    return base


def diagnosticar_problema_rede() -> Tuple[bool, str]:
    ping = _ping_google(timeout=3)
    if ping in ("N/A", ""):
        return False, "Sem resposta no ping para 8.8.8.8."

    ip_ok, ip_info = _ip_local_valido()
    if not ip_ok:
        return False, ip_info

    return True, f"Rede aparentemente saudável. IP local: {ip_info}. Ping: {ping}."


def executar_reparo_rede() -> str:
    if not _is_admin():
        return "Execute o Toolbox Pro como Administrador para aplicar o reparo de rede."

    comandos = [
        (["ipconfig", "/release"], "ipconfig /release"),
        (["ipconfig", "/renew"], "ipconfig /renew"),
        (["ipconfig", "/flushdns"], "ipconfig /flushdns"),
        (["netsh", "winsock", "reset"], "netsh winsock reset"),
    ]

    saidas = []

    for comando, descricao in comandos:
        try:
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            stdout = (resultado.stdout or "").strip()
            stderr = (resultado.stderr or "").strip()
            saida = stdout if stdout else stderr

            if resultado.returncode != 0:
                detalhe = saida or f"Código de saída {resultado.returncode}."
                if "access is denied" in detalhe.lower() or "acesso negado" in detalhe.lower():
                    return "Acesso negado. Abra o Toolbox Pro como Administrador e tente novamente."
                return f"Falha ao executar {descricao}.\n{detalhe}"

            if saida:
                saidas.append(f"{descricao}: {saida}")
            else:
                saidas.append(f"{descricao}: concluído")
        except FileNotFoundError:
            return f"Não foi possível localizar o comando {descricao}."
        except Exception as e:
            return f"Erro ao executar {descricao}: {e}"

    return "Reparo de rede concluído com sucesso.\n" + "\n".join(saidas)