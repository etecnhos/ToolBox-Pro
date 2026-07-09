import os
import platform
import subprocess
import psutil
import customtkinter as ctk

# 1. Configuração do visual
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

janela = ctk.CTk()
janela.title("Toolbox Pro v1.0 - Monitoramento Universal")
janela.geometry("550x600")

# 🔥 NOVA FUNÇÃO UNIVERSAL DA GPU (Intel, AMD ou NVIDIA)
def obter_dados_gpu_universal():
    modelo_gpu = "Não detectada"
    vram_gpu = "N/A"
    uso_gpu = "N/A"
    
    try:
        # Pede ao Windows (via PowerShell em segundo plano) o nome e a memória de qualquer placa de vídeo instalada
        comando_wmi = "powershell -Command \"Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM | ConvertTo-Csv -NoTypeInformation\""
        resultado_wmi = subprocess.check_output(comando_wmi, shell=True, text=True).strip().split('\n')
        
        if len(resultado_wmi) > 1:
            # Pega a linha com os dados reais (ignora o cabeçalho)
            linha_dados = resultado_wmi[1].replace('"', '').split(',')
            modelo_gpu = linha_dados[0]
            
            # O Windows entrega a VRAM em bytes. Convertemos para GB.
            # Nota: Gráficos integrados (Intel UHD/Vega) podem reportar a memória compartilhada dinamicamente.
            bytes_ram = float(linha_dados[1]) if len(linha_dados) > 1 and linha_dados[1].isdigit() else 0
            if bytes_ram > 0:
                vram_gpu = f"{round(bytes_ram / (1024**3), 1)} GB"
            else:
                vram_gpu = "Compartilhada (Dinâmica)"
                
    except Exception:
        pass

    # Se a placa for NVIDIA, nós tentamos pegar o uso em tempo real pelo nvidia-smi
    if "nvidia" in modelo_gpu.lower():
        try:
            comando_nvidia = 'nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits'
            uso_nvidia = subprocess.check_output(comando_nvidia, shell=True, text=True).strip()
            uso_gpu = f"{uso_nvidia}%"
        except Exception:
            uso_gpu = "0% (Inativa)"
    else:
        # Para Intel/AMD, o Windows gerencia de forma diferente em tempo real.
        # Para manter o script leve sem travar, marcamos como Monitorada pelo Windows.
        uso_gpu = "Ativa (Gerenciada pelo Windows)"

    return modelo_gpu, vram_gpu, uso_gpu

# 3. Função de Diagnóstico Completo
def verificar_hardware():
    nome_pc = os.environ.get('COMPUTERNAME') or platform.node()
    usuario = os.environ.get('USERNAME')
    
    modelo_cpu = platform.processor()
    uso_cpu = psutil.cpu_percent()
    
    # Chama a nossa nova função Universal
    modelo_gpu, vram_gpu, uso_gpu = obter_dados_gpu_universal()
    
    memoria = psutil.virtual_memory()
    ram_total = round(memoria.total / (1024**3), 1)
    ram_uso_porcentagem = memoria.percent
    
    disco = psutil.disk_usage('C:')
    disco_total = round(disco.total / (1024**3), 1)
    disco_livre = round(disco.free / (1024**3), 1)
    
    relatorio = (
        f"🖥️ SYSTEM INFO\n"
        f"----------------------------------------\n"
        f"PC: {nome_pc}\n"
        f"User: {usuario}\n\n"
        
        f"🧠 PROCESSADOR\n"
        f"----------------------------------------\n"
        f"Modelo: {modelo_cpu}\n"
        f"Uso Atual CPU: {uso_cpu}%\n\n"
        
        f"🎮 PLACA DE VÍDEO (GPU)\n"
        f"----------------------------------------\n"
        f"Modelo: {modelo_gpu}\n"
        f"VRAM: {vram_gpu}\n"
        f"Status/Uso: {uso_gpu}\n\n"
        
        f"📊 MEMÓRIA RAM\n"
        f"----------------------------------------\n"
        f"Total: {ram_total} GB\n"
        f"Uso Atual: {ram_uso_porcentagem}%\n\n"
        
        f"💽 DISCO PRINCIPAL (C:)\n"
        f"----------------------------------------\n"
        f"Tamanho Total: {disco_total} GB\n"
        f"Espaço Livre: {disco_livre} GB"
    )
    
    texto_dados.configure(text=relatorio, justify="left")
    janela.after(1000, verificar_hardware)

# 4. Elementos visuais
titulo = ctk.CTkLabel(janela, text="Toolbox Pro - Monitoramento Universal", font=("Arial", 20, "bold"))
titulo.pack(pady=15)

botao_status = ctk.CTkButton(janela, text="Sensores Ativos", state="disabled", font=("Arial", 14, "bold"))
botao_status.pack(pady=10)

texto_dados = ctk.CTkLabel(janela, text="Iniciando sensores...", font=("Consolas", 11), justify="center")
texto_dados.pack(pady=20, padx=20)

verificar_hardware()
janela.mainloop()