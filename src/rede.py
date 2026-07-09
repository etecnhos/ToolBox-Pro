import socket
import requests
import subprocess
import threading
import time

dados_rede_tempo_real = {
    "ip_publico": "Buscando...",
    "ping_res": "Testando..."
}

# 🔥 Interruptor para ligar/desligar o teste de Ping
monitorar_ping = False

def _worker_rede():
    try:
        ip = requests.get("https://api.ipify.org", timeout=3).text.strip()
        dados_rede_tempo_real["ip_publico"] = ip
    except Exception:
        dados_rede_tempo_real["ip_publico"] = "Sem Internet"

    while True:
        # Só faz o teste de ping se o técnico estiver na aba de Rede
        if monitorar_ping:
            try:
                comando_ping = "ping -n 1 8.8.8.8"
                saida_ping = subprocess.check_output(comando_ping, shell=True, text=True)
                if "tempo=" in saida_ping:
                    tempo = saida_ping.split("tempo=")[1].split("ms")[0].strip()
                    dados_rede_tempo_real["ping_res"] = f"{tempo} ms"
                elif "time=" in saida_ping:
                    tempo = saida_ping.split("time=")[1].split("ms")[0].strip()
                    dados_rede_tempo_real["ping_res"] = f"{tempo} ms"
            except Exception:
                dados_rede_tempo_real["ping_res"] = "Falha"
        else:
            dados_rede_tempo_real["ping_res"] = "Pausado (Economia)"
        
        time.sleep(1)

def iniciar_monitoramento_rede():
    thread = threading.Thread(target=_worker_rede, daemon=True)
    thread.start()

def coletar_rede_dinamica():
    ip_local = "Desconectado"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    return {
        "ip_local": ip_local,
        "ip_publico": dados_rede_tempo_real["ip_publico"],
        "ping_res": dados_rede_tempo_real["ping_res"]
    }