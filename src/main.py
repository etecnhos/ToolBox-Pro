import customtkinter as ctk

# 🔥 IMPORTANDO A NOSSA LÓGICA DE OUTROS ARQUIVOS
from sensores import coletar_hardware
from rede import coletar_rede

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

janela = ctk.CTk()
janela.title("Toolbox Pro v1.0")
janela.geometry("650x600")
janela.resizable(False, False)

# --- LOOP DE ATUALIZAÇÃO ---
def atualizar_sensores():
    # Puxa os dados puros dos módulos de engenharia
    hw = coletar_hardware()
    net = coletar_rede()
    
    # Injeta os dados na interface de Hardware
    lbl_sys.configure(text=f"PC: {hw['nome_pc']}   |   User: {hw['usuario']}")
    lbl_cpu_val.configure(text=f"{hw['uso_cpu']}%")
    lbl_gpu_val.configure(text=f"{hw['uso_gpu']}  ({hw['modelo_gpu'][:28]}...)")
    lbl_ram_val.configure(text=f"{hw['ram_uso']}% de {hw['ram_total']} GB")
    lbl_disk_val.configure(text=f"{hw['disco_livre']} GB livres de {hw['disco_total']} GB")

    # Injeta os dados na interface de Rede
    lbl_iplocal_val.configure(text=net['ip_local'])
    lbl_ippub_val.configure(text=net['ip_publico'])
    lbl_ping_val.configure(text=net['ping_res'])
    
    janela.after(1000, atualizar_sensores)


# --- INTERFACE GRÁFICA (UI) ---

header_frame = ctk.CTkFrame(janela, height=60, fg_color="transparent")
header_frame.pack(fill="x", padx=20, pady=10)

titulo = ctk.CTkLabel(header_frame, text="TOOLBOX PRO", font=("Segoe UI", 24, "bold"))
titulo.pack(side="left")

lbl_sys = ctk.CTkLabel(header_frame, text="Carregando...", font=("Segoe UI", 12), text_color="gray")
lbl_sys.pack(side="right", pady=8)

abas = ctk.CTkTabview(janela, width=610, height=480)
abas.pack(padx=20, pady=5)
abas.add("Hardware")
abas.add("Rede")

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


atualizar_sensores()
janela.mainloop()