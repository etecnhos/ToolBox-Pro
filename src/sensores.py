import os
import platform
import re
import shutil
import subprocess
import threading
import time
from typing import Dict

import psutil


# Interruptor global controlado pela UI (main.py)
monitorar_gpu = False

# Estado global estável para leitura leve pela interface
estado_gpu: Dict[str, str] = {
    "modelo": "N/A",
    "vram_mb": "N/A",
    "uso_percent": "N/A",
    "temperatura_c": "N/A",
    "disponivel": "False",
}


_lock_gpu = threading.Lock()
_thread_gpu_iniciada = False


def _run_powershell(cmd: str, timeout: int = 5) -> str:
    """
    Executa PowerShell com ExecutionPolicy Bypass para maior compatibilidade no Windows.
    """
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                cmd,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return (result.stdout or "").strip()
    except Exception:
        return ""


def _obter_gpu_windows() -> Dict[str, str]:
    """
    Obtém modelo e VRAM da GPU via PowerShell (universal no Windows).
    """
    cmd = (
        "Get-CimInstance Win32_VideoController | "
        "Select-Object Name, AdapterRAM | "
        "ForEach-Object { "
        "$ram=[math]::Round($_.AdapterRAM/1MB); "
        "Write-Output ($_.Name + '|' + $ram) }"
    )
    out = _run_powershell(cmd)
    if not out:
        return {"modelo": "N/A", "vram_mb": "N/A", "disponivel": "False"}

    primeira_linha = out.splitlines()[0].strip()
    if "|" in primeira_linha:
        nome, vram = primeira_linha.split("|", 1)
        return {
            "modelo": nome.strip() or "N/A",
            "vram_mb": vram.strip() or "N/A",
            "disponivel": "True",
        }

    return {"modelo": primeira_linha or "N/A", "vram_mb": "N/A", "disponivel": "True"}


def _obter_cpu_modelo() -> str:
    cpu = platform.processor().strip()
    if cpu:
        return cpu

    # Fallback para Windows
    cmd = "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name"
    out = _run_powershell(cmd)
    return out if out else "N/A"


def coletar_info_estatica() -> Dict[str, str]:
    """
    Coleta dados estáticos:
    - Nome do PC
    - Usuário
    - Modelo da CPU
    - Modelo e VRAM da GPU
    - RAM total física
    """
    pc = platform.node() or os.getenv("COMPUTERNAME", "N/A")
    usuario = os.getenv("USERNAME") or os.getenv("USER") or "N/A"
    cpu = _obter_cpu_modelo()
    gpu = _obter_gpu_windows()
    ram_total = psutil.virtual_memory().total

    info = {
        "pc": pc,
        "usuario": usuario,
        "cpu": cpu,
        "gpu_modelo": gpu.get("modelo", "N/A"),
        "gpu_vram_mb": gpu.get("vram_mb", "N/A"),
        "gpu_disponivel": gpu.get("disponivel", "False"),
        "ram_total": f"{round(ram_total / (1024 ** 3), 1)} GB",
    }

    with _lock_gpu:
        estado_gpu["modelo"] = info["gpu_modelo"]
        estado_gpu["vram_mb"] = info["gpu_vram_mb"]
        estado_gpu["disponivel"] = info["gpu_disponivel"]

    return info


def coletar_dados_estaticos() -> Dict[str, str]:
    return coletar_info_estatica()


def coletar_uso_dinamico() -> Dict[str, str]:
    """
    Leitura leve e rápida para UI:
    - Uso de CPU (%)
    - Uso de RAM (%)
    - Uso de disco C: (%)
    """
    try:
        cpu = psutil.cpu_percent(interval=None)
    except Exception:
        cpu = 0.0

    try:
        ram = psutil.virtual_memory().percent
    except Exception:
        ram = 0.0

    disco_path = "C:\\"
    if not os.path.exists(disco_path):
        disco_path = os.path.abspath(os.sep)

    try:
        disco = psutil.disk_usage(disco_path).percent
    except Exception:
        disco = 0.0

    return {
        "cpu_percent": f"{cpu:.1f}",
        "ram_percent": f"{ram:.1f}",
        "disco_percent": f"{disco:.1f}",
    }


def _nvidia_smi_existe() -> bool:
    return shutil.which("nvidia-smi") is not None


def _gpu_e_nvidia() -> bool:
    with _lock_gpu:
        modelo = estado_gpu.get("modelo", "").lower()
    return "nvidia" in modelo and _nvidia_smi_existe()


def _loop_monitor_gpu() -> None:
    """
    Thread de monitoramento contínuo da GPU.
    Atualiza uso apenas quando:
    - monitorar_gpu == True
    - GPU é NVIDIA
    """
    global monitorar_gpu

    query = "utilization.gpu,temperature.gpu"
    cmd = [
        "nvidia-smi",
        f"--query-gpu={query}",
        "--format=csv,noheader,nounits",
    ]

    while True:
        if not monitorar_gpu:
            time.sleep(0.2)
            continue

        if not _gpu_e_nvidia():
            with _lock_gpu:
                estado_gpu["uso_percent"] = "N/A"
                estado_gpu["temperatura_c"] = "N/A"
            time.sleep(1.0)
            continue

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            line = (result.stdout or "").strip().splitlines()
            if line:
                # Exemplo: "34, 62"
                partes = [p.strip() for p in line[0].split(",")]
                uso = partes[0] if len(partes) > 0 else "N/A"
                temp = partes[1] if len(partes) > 1 else "N/A"

                # Sanitização simples
                uso = re.sub(r"[^\d.]", "", uso) or "N/A"
                temp = re.sub(r"[^\d.]", "", temp) or "N/A"

                with _lock_gpu:
                    estado_gpu["uso_percent"] = uso
                    estado_gpu["temperatura_c"] = temp
        except Exception:
            with _lock_gpu:
                estado_gpu["uso_percent"] = "N/A"
                estado_gpu["temperatura_c"] = "N/A"

        time.sleep(1.0)


def iniciar_thread_gpu() -> None:
    global _thread_gpu_iniciada
    if _thread_gpu_iniciada:
        return
    _thread_gpu_iniciada = True
    t = threading.Thread(target=_loop_monitor_gpu, daemon=True, name="ThreadGPU")
    t.start()


def obter_estado_gpu() -> Dict[str, str]:
    with _lock_gpu:
        return dict(estado_gpu)