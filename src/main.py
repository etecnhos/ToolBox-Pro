import os
import platform
import subprocess
import socket
import requests
import psutil
import customtkinter as ctk

# 1. Configuração do visual premium
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

janela = ctk.CTk()
janela.title("Toolbox Pro v1.0")
janela.geometry("650x600")
janela.resizable(False, False) # Trava o tamanho da janela para manter o design alinhado

# --- FUNÇÕES DE CAPTURA (Mantidas idênticas para estabilidade) ---

def obter_dados_gpu_universal():
    modelo_gpu = "Não detectada"
    vram_gpu = "N/A"
    uso_gpu = "N/A"
    try:
        comando_wmi = "powershell -Command \"Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM | ConvertTo-Csv -NoTypeInformation\""
        resultado_wmi = subprocess.check_output(comando_wmi, shell=True, text=True).strip().split('\n')
        if len(resultado_wmi) > 1:
            linha_dados = resultado_wmi[1].replace('"', '').split(',')
            modelo_gpu = linha_dados[0]
            bytes_ram = float(linha_dados[1]) if len(linha_dados) > 1 and linha_dados[1].isdigit() else 0
            if bytes_ram > 0:
                vram_gpu = f"{round(bytes_ram / (1024**3), 1)} GB"
            else:
                vram_gpu = "Dinâmica"
    except Exception:
        pass

    if "nvidia" in modelo_gpu.lower():
        try:
            comando_nvidia = 'nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits'
            uso_nvidia = subprocess.check_output(comando_nvidia, shell=True, text=True).strip()
            uso_gpu = f"{uso_nvidia}%"
        except Exception:
            uso_gpu = "0%"
    else:
        uso_gpu = "Ativa"

    return modelo_gpu, vram_gpu, uso_gpu

def obter_dados_rede():
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

    return ip_local, ip_publico, ping_resultado

# --- LOOP DE ATUALIZAÇÃO ---

def atualizar_sensores():
    # Atualizando as variáveis
    nome_pc = os.environ.get('COMPUTERNAME') or platform.node()
    usuario = os.environ.get('USERNAME')
    uso_cpu = psutil.cpu_percent()
    modelo_gpu, vram_gpu, uso_gpu = obter_dados_gpu_universal()
    
    memoria = psutil.virtual_memory()
    ram_total = round(memoria.total / (1024**3), 1)
    ram_uso = memoria.percent
    
    disco = psutil.disk_usage('C:')
    disco_total = round(disco.total / (1024**3), 1)
    disco_livre = round(disco.free / (1024**3), 1)
    
    # Injetando diretamente nos elementos visuais do card de Hardware
    lbl_sys.configure(text=f"PC: {nome_pc}   |   User: {usuario}")
    lbl_cpu_val.configure(text=f"{uso_cpu}%")
    lbl_gpu_val.configure(text=f"{uso_gpu}  ({modelo_gpu[:28]}...)")
    lbl_ram_val.configure(text=f"{ram_uso}% de {ram_total} GB")
    lbl_disk_val.configure(text=f"{disco_livre} GB livres de {disco_total} GB")

    # Injetando na aba de Rede
    ip_local, ip_publico, ping_res = obter_dados_rede()
    lbl_iplocal_val.configure(text=ip_local)
    lbl_ippub_val.configure(text=ip_publico)
    lbl_ping_val.configure(text=ping_res)
    
    janela.after(500, atualizar_sensores)


# --- INTERFACE GRÁFICA RENOVADA (UI) ---

# Cabeçalho Superior
header_frame = ctk.CTkFrame(janela, height=60, fg_color="transparent")
header_frame.pack(fill="x", padx=20, pady=10)

titulo = ctk.CTkLabel(header_frame, text="TOOLBOX PRO", font=("Segoe UI", 24, "bold"))
titulo.pack(side="left")

lbl_sys = ctk.CTkLabel(header_frame, text="Carregando...", font=("Segoe UI", 12), text_color="gray")
lbl_sys.pack(side="right", pady=8)

# Abas
abas = ctk.CTkTabview(janela, width=610, height=480)
abas.pack(padx=20, pady=5)
abas.add("Hardware")
abas.add("Rede")

# --- DESIGN DA ABA HARDWARE (Estilo Cards) ---
tab_hw = abas.tab("Hardware")

# Card da CPU
card_cpu = ctk.CTkFrame(tab_hw, width=570, height=70)
card_cpu.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_cpu, text="🧠 Uso do Processador (CPU):", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_cpu_val = ctk.CTkLabel(card_cpu, text="0%", font=("Segoe UI", 16, "bold"), text_color="#1F538D")
lbl_cpu_val.place(x=450, y=22)

# Card da GPU
card_gpu = ctk.CTkFrame(tab_hw, width=570, height=70)
card_gpu.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_gpu, text="🎮 Gráficos & Vídeo (GPU):", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_gpu_val = ctk.CTkLabel(card_gpu, text="Carregando...", font=("Segoe UI", 13, "bold"))
lbl_gpu_val.place(x=280, y=22)

# Card da RAM
card_ram = ctk.CTkFrame(tab_hw, width=570, height=70)
card_ram.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_ram, text="📊 Memória RAM do Sistema:", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_ram_val = ctk.CTkLabel(card_ram, text="0%", font=("Segoe UI", 14, "bold"))
lbl_ram_val.place(x=420, y=22)

# Card do Disco
card_disk = ctk.CTkFrame(tab_hw, width=570, height=70)
card_disk.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_disk, text="💽 Armazenamento Disco (C:):", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_disk_val = ctk.CTkLabel(card_disk, text="Calculando...", font=("Segoe UI", 13, "bold"))
lbl_disk_val.place(x=350, y=22)


# --- DESIGN DA ABA REDE ---
tab_net = abas.tab("Rede")

# Card IP Local
card_iplocal = ctk.CTkFrame(tab_net, width=570, height=70)
card_iplocal.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_iplocal, text="🏠 IP Interno (Rede Local):", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_iplocal_val = ctk.CTkLabel(card_iplocal, text="Detectando...", font=("Segoe UI", 14, "bold"))
lbl_iplocal_val.place(x=440, y=22)

# Card IP Público
card_ippub = ctk.CTkFrame(tab_net, width=570, height=70)
card_ippub.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_ippub, text="🌍 IP Externo (Internet):", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_ippub_val = ctk.CTkLabel(card_ippub, text="Buscando...", font=("Segoe UI", 14, "bold"), text_color="#1F538D")
lbl_ippub_val.place(x=420, y=22)

# Card Ping
card_ping = ctk.CTkFrame(tab_net, width=570, height=70)
card_ping.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_ping, text="⚡ Latência de Conexão (Ping):", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_ping_val = ctk.CTkLabel(card_ping, text="Testando...", font=("Segoe UI", 14, "bold"))
lbl_ping_val.place(x=450, y=22)


# Inicia a atualização contínua e abre a janela
atualizar_sensores()
janela.mainloop()