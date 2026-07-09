import os
import platform
import subprocess
import psutil
import threading
import time

dados_gpu_tempo_real = {"uso": "Ativa"}
# 🔥 Interruptor para ligar/desligar o sensor da GPU
monitorar_gpu = True

def coletar_dados_estaticos():
    nome_pc = os.environ.get('COMPUTERNAME') or platform.node()
    usuario = os.environ.get('USERNAME')
    modelo_cpu = platform.processor()
    
    modelo_gpu = "Não detectada"
    vram_gpu = "N/A"
    try:
        comando_wmi = "powershell -ExecutionPolicy Bypass -Command \"Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM | ConvertTo-Csv -NoTypeInformation\""
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
        
    return {
        "nome_pc": nome_pc,
        "usuario": usuario,
        "modelo_cpu": modelo_cpu,
        "modelo_gpu": modelo_gpu,
        "vram_gpu": vram_gpu
    }

def _worker_gpu(modelo_gpu):
    global monitorar_gpu
    if "nvidia" in modelo_gpu.lower():
        while True:
            # Só gasta processamento se o interruptor estiver ligado
            if monitorar_gpu:
                try:
                    comando = 'nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits'
                    uso = subprocess.check_output(comando, shell=True, text=True).strip()
                    dados_gpu_tempo_real["uso"] = f"{uso}%"
                except Exception:
                    dados_gpu_tempo_real["uso"] = "0%"
            else:
                dados_gpu_tempo_real["uso"] = "Pausada (Economia)"
            
            time.sleep(1)

def iniciar_monitoramento_gpu(modelo_gpu):
    thread = threading.Thread(target=_worker_gpu, args=(modelo_gpu,), daemon=True)
    thread.start()

def coletar_hardware_dinamico():
    uso_cpu = psutil.cpu_percent()
    memoria = psutil.virtual_memory()
    ram_total = round(memoria.total / (1024**3), 1)
    ram_uso = memoria.percent
    
    disco = psutil.disk_usage('C:')
    disco_total = round(disco.total / (1024**3), 1)
    disco_livre = round(disco.free / (1024**3), 1)
    
    return {
        "uso_cpu": uso_cpu,
        "ram_total": ram_total,
        "ram_uso": ram_uso,
        "disco_total": disco_total,
        "disco_livre": disco_livre,
        "uso_gpu": dados_gpu_tempo_real["uso"]
    }