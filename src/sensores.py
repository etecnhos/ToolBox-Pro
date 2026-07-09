import os
import platform
import subprocess
import psutil

def obter_dados_gpu_universal():
    modelo_gpu = "Não detectada"
    vram_gpu = "N/A"
    uso_gpu = "N/A"
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

def coletar_hardware():
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
    
    return {
        "nome_pc": nome_pc,
        "usuario": usuario,
        "uso_cpu": uso_cpu,
        "modelo_gpu": modelo_gpu,
        "vram_gpu": vram_gpu,
        "uso_gpu": uso_gpu,
        "ram_total": ram_total,
        "ram_uso": ram_uso,
        "disco_total": disco_total,
        "disco_livre": disco_livre
    }