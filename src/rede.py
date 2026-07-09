import socket
import requests
import subprocess

def coletar_rede():
    ip_local = "Desconectado"
    ip_publico = "Sem Internet"
    ping_resultado = "Falha"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    try:
        ip_publico = requests.get("https://api.ipify.org", timeout=1.5).text.strip()
    except Exception:
        pass

    try:
        comando_ping = "ping -n 1 8.8.8.8"
        saida_ping = subprocess.check_output(comando_ping, shell=True, text=True)
        if "tempo=" in saida_ping:
            ping_resultado = f"{saida_ping.split('tempo=')[1].split('ms')[0].strip()} ms"
        elif "time=" in saida_ping:
            ping_resultado = f"{saida_ping.split('time=')[1].split('ms')[0].strip()} ms"
    except Exception:
        pass

    return {
        "ip_local": ip_local,
        "ip_publico": ip_publico,
        "ping_res": ping_resultado
    }