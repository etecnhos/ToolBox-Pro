import customtkinter as ctk
import threading

import sensores
import rede
import Limpeza

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

janela = ctk.CTk()
janela.title("Toolbox Pro v1.4")
janela.geometry("650x600")
janela.resizable(False, False)

dados_fixos = sensores.coletar_dados_estaticos()
sensores.iniciar_monitoramento_gpu(dados_fixos["modelo_gpu"])
rede.iniciar_monitoramento_rede()

def aba_mudou():
    aba_ativa = abas.get()
    if aba_ativa == "Hardware":
        sensores.monitorar_gpu = True
        rede.monitorar_ping = False
    elif aba_ativa == "Rede":
        sensores.monitorar_gpu = False
        rede.monitorar_ping = True
    else: # Aba Limpeza ativa
        sensores.monitorar_gpu = False
        rede.monitorar_ping = False

def atualizar_sensores():
    hw = sensores.coletar_hardware_dinamico()
    net = rede.coletar_rede_dinamica()
    
    lbl_sys.configure(text=f"PC: {dados_fixos['nome_pc']}   |   User: {dados_fixos['usuario']}")
    lbl_cpu_val.configure(text=f"{hw['uso_cpu']}%")
    lbl_gpu_val.configure(text=f"{hw['uso_gpu']}  ({dados_fixos['modelo_gpu'][:28]}...)")
    lbl_ram_val.configure(text=f"{hw['ram_uso']}% de {hw['ram_total']} GB")
    lbl_disk_val.configure(text=f"{hw['disco_livre']} GB livres de {hw['disco_total']} GB")

    lbl_iplocal_val.configure(text=net['ip_local'])
    lbl_ippub_val.configure(text=net['ip_publico'])
    lbl_ping_val.configure(text=net['ping_res'])
    
    janela.after(1000, atualizar_sensores)

def disparar_limpeza_lixeira():
    botao_lixeira.configure(state="disabled", text="Limpando...")
    def worker():
        mensagem = Limpeza.esvaziar_lixeira()
        lbl_status_limpeza.configure(text=f"✨ {mensagem}")
        botao_lixeira.configure(state="normal", text="Esvaziar Lixeira")
    threading.Thread(target=worker, daemon=True).start()

# 🔥 FUNÇÃO PARA RODAR A LIMPEZA SEM TRAVAR A INTERFACE
def disparar_limpeza():
    botao_limpar.configure(state="disabled", text="Limpando Sistema...")
    lbl_status_limpeza.configure(text="Varrendo e apagando arquivos temporários, aguarde...")

    # Executa a limpeza pesada numa Thread em background pro app continuar respondendo
    def worker():
        resultado = Limpeza.executar_limpeza()
        # Atualiza os textos na janela principal de volta na Main Thread
        lbl_status_limpeza.configure(
            text=f"✨ Concluído com Sucesso!\n\n"
                 f"📦 Espaço Liberado: {resultado['mb_liberados']} MB\n"
                 f"🗑️ Itens Removidos: {resultado['deletados']}\n"
                 f"🔒 Arquivos em uso (pula): {resultado['bloqueados']}"
        )
        botao_limpar.configure(state="normal", text="Otimizar Windows")
        
    threading.Thread(target=worker, daemon=True).start()


# --- INTERFACE GRÁFICA (UI) ---

header_frame = ctk.CTkFrame(janela, height=60, fg_color="transparent")
header_frame.pack(fill="x", padx=20, pady=10)

titulo = ctk.CTkLabel(header_frame, text="TOOLBOX PRO", font=("Segoe UI", 24, "bold"))
titulo.pack(side="left")

lbl_sys = ctk.CTkLabel(header_frame, text="Carregando...", font=("Segoe UI", 12), text_color="gray")
lbl_sys.pack(side="right", pady=8)

# Abas atualizadas
abas = ctk.CTkTabview(janela, width=610, height=480, command=aba_mudou)
abas.pack(padx=20, pady=5)
abas.add("Hardware")
abas.add("Rede")
abas.add("Limpeza") # 🔥 Adicionando a aba visual de Limpeza

# --- DESIGN DA ABA HARDWARE ---
tab_hw = abas.tab("Hardware")
card_cpu = ctk.CTkFrame(tab_hw, width=570, height=70)
card_cpu.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_cpu, text="🧠 Uso do Processador (CPU):", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_cpu_val = ctk.CTkLabel(card_cpu, text="0%", font=("Segoe UI", 16, "bold"), text_color="#1F538D")
lbl_cpu_val.place(x=450, y=22)

card_gpu = ctk.CTkFrame(tab_hw, width=570, height=70)
card_gpu.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_gpu, text="🎮 Gráficos & Vídeo (GPU):", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_gpu_val = ctk.CTkLabel(card_gpu, text="Carregando...", font=("Segoe UI", 13, "bold"))
lbl_gpu_val.place(x=280, y=22)

card_ram = ctk.CTkFrame(tab_hw, width=570, height=70)
card_ram.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_ram, text="📊 Memória RAM do Sistema:", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_ram_val = ctk.CTkLabel(card_ram, text="0%", font=("Segoe UI", 14, "bold"))
lbl_ram_val.place(x=420, y=22)

card_disk = ctk.CTkFrame(tab_hw, width=570, height=70)
card_disk.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_disk, text="💽 Armazenamento Disco (C:):", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_disk_val = ctk.CTkLabel(card_disk, text="Calculando...", font=("Segoe UI", 13, "bold"))
lbl_disk_val.place(x=350, y=22)

# --- DESIGN DA ABA REDE ---
tab_net = abas.tab("Rede")
card_iplocal = ctk.CTkFrame(tab_net, width=570, height=70)
card_iplocal.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_iplocal, text="🏠 IP Interno (Rede Local):", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_iplocal_val = ctk.CTkLabel(card_iplocal, text="Detectando...", font=("Segoe UI", 14, "bold"))
lbl_iplocal_val.place(x=440, y=22)

card_ippub = ctk.CTkFrame(tab_net, width=570, height=70)
card_ippub.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_ippub, text="🌍 IP Externo (Internet):", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_ippub_val = ctk.CTkLabel(card_ippub, text="Buscando...", font=("Segoe UI", 14, "bold"), text_color="#1F538D")
lbl_ippub_val.place(x=420, y=22)

card_ping = ctk.CTkFrame(tab_net, width=570, height=70)
card_ping.pack(pady=10, padx=10, fill="x")
ctk.CTkLabel(card_ping, text="⚡ Latência de Conexão (Ping):", font=("Segoe UI", 14, "bold")).place(x=20, y=22)
lbl_ping_val = ctk.CTkLabel(card_ping, text="Testando...", font=("Segoe UI", 14, "bold"))
lbl_ping_val.place(x=450, y=22)

# --- 🔥 DESIGN DA ABA LIMPEZA ---
tab_clean = abas.tab("Limpeza")

card_controle = ctk.CTkFrame(tab_clean, width=570, height=120)
card_controle.pack(pady=15, padx=10, fill="x")

ctk.CTkLabel(
    card_controle, 
    text="🧹 Otimizador de Espaço em Disco", 
    font=("Segoe UI", 16, "bold")
).place(x=20, y=20)

ctk.CTkLabel(
    card_controle, 
    text="Apaga arquivos de cache e dados temporários inúteis acumulados pelo Windows.", 
    font=("Segoe UI", 12),
    text_color="gray"
).place(x=20, y=50)

# Botão que chama o processo assíncrono de faxina
botao_limpar = ctk.CTkButton(
    card_controle, 
    text="Otimizar Windows", 
    font=("Segoe UI", 13, "bold"),
    command=disparar_limpeza
)
botao_limpar.place(x=20, y=82)

# Mude a altura do card_controle de 120 para 160 para caber o novo botão:
card_controle.configure(height=160)

# Cole o novo botão logo abaixo do outro (mudamos o y para 120 para ficar embaixo)
botao_lixeira = ctk.CTkButton(
    card_controle, 
    text="Esvaziar Lixeira", 
    font=("Segoe UI", 13, "bold"),
    fg_color="#D35400",
    hover_color="#A04000",
    command=disparar_limpeza_lixeira # 
    
)
botao_lixeira.place(x=180, y=82) # x=180 coloca ele do lado do botão de otimizar

# Card de Exibição do Relatório de Limpeza
card_resultado = ctk.CTkFrame(tab_clean, width=570, height=240, fg_color="#1A1A1A" if ctk.get_appearance_mode() == "Dark" else "#E5E5E5")
card_resultado.pack(pady=10, padx=10, fill="both", expand=True)

lbl_status_limpeza = ctk.CTkLabel(
    card_resultado, 
    text="Pronto para iniciar. Clique no botão acima para fazer a faxina.", 
    font=("Consolas", 13),
    justify="left"
)
lbl_status_limpeza.pack(pady=40, padx=30, anchor="w")


aba_mudou()
atualizar_sensores()
janela.mainloop()