import threading
import customtkinter as ctk
from tkinter import messagebox

import limpeza
import rede
import reparos
import relatorio
import seguranca
import sensores


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class ToolboxProApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Toolbox Pro v1.4")
        self.geometry("650x680")
        self.resizable(False, False)

        # Inicia módulos/background
        sensores.coletar_info_estatica()
        sensores.iniciar_thread_gpu()
        rede.iniciar_thread_rede()

        # =========================
        # FUNÇÕES (ANTES DOS WIDGETS)
        # =========================
        def aba_mudou():
            aba = self.tabview.get()
            if aba == "Hardware":
                sensores.monitorar_gpu = True
                rede.monitorar_ping = False
            elif aba == "Rede":
                sensores.monitorar_gpu = False
                rede.monitorar_ping = True
            elif aba == "Reparos":
                sensores.monitorar_gpu = False
                rede.monitorar_ping = False
            elif aba == "Segurança":
                sensores.monitorar_gpu = False
                rede.monitorar_ping = False
            else:  # Limpeza
                sensores.monitorar_gpu = False
                rede.monitorar_ping = False

        def atualizar_hardware_ui():
            uso = sensores.coletar_uso_dinamico()
            gpu = sensores.obter_estado_gpu()

            self.lbl_cpu_uso.configure(text=f"CPU: {uso['cpu_percent']}%")
            self.lbl_ram_uso.configure(text=f"RAM: {uso['ram_percent']}%")
            self.lbl_disco_uso.configure(text=f"Disco C:: {uso['disco_percent']}%")

            self.lbl_gpu_uso.configure(text=f"Uso GPU: {gpu['uso_percent']}%")
            self.lbl_gpu_temp.configure(text=f"Temp GPU: {gpu['temperatura_c']}°C")

            self.after(500, atualizar_hardware_ui)

        def atualizar_rede_ui():
            dados = rede.obter_status_rede()
            self.lbl_ip_local.configure(text=f"IP Local: {dados['ip_local']}")
            self.lbl_ip_publico.configure(text=f"IP Público: {dados['ip_publico']}")
            ping_txt = f"{dados['ping_ms']} ms" if dados["ping_ms"] not in ("N/A", "OK") else dados["ping_ms"]
            self.lbl_ping.configure(text=f"Ping 8.8.8.8: {ping_txt}")
            self.lbl_status_internet.configure(text=f"Status: {dados['status_internet']}")

            self.after(1000, atualizar_rede_ui)

        def _task_limpar_temp():
            self.lbl_limpeza_status.configure(text="Limpando temporários...")
            mb = limpeza.limpar_arquivos_temporarios()
            self.lbl_limpeza_status.configure(text=f"Limpeza concluída: {mb} MB liberados.")

        def executar_limpeza_temp():
            t = threading.Thread(target=_task_limpar_temp, daemon=True)
            t.start()

        def _task_esvaziar_lixeira():
            self.lbl_limpeza_status.configure(text="Esvaziando lixeira...")
            ok, msg = limpeza.esvaziar_lixeira()
            self.lbl_limpeza_status.configure(text=msg if ok else f"Falha: {msg}")

        def executar_esvaziar_lixeira():
            t = threading.Thread(target=_task_esvaziar_lixeira, daemon=True)
            t.start()

        def atualizar_status_reparos(mensagem: str):
            self.after(0, lambda: self.lbl_reparos_status.configure(text=mensagem))

        def finalizar_reparo(ok: bool, mensagem: str):
            texto = mensagem if ok else f"Falha: {mensagem}"
            self.after(0, lambda: self.lbl_reparos_status.configure(text=texto))

        def executar_sfc():
            atualizar_status_reparos("Executando SFC /scannow...")
            reparos.corrigir_arquivos_sistema(callback=finalizar_reparo)

        def executar_dism():
            atualizar_status_reparos("Executando DISM /RestoreHealth...")
            reparos.restaurar_imagem_windows(callback=finalizar_reparo)

        def executar_sysmain():
            atualizar_status_reparos("Desativando SysMain...")
            reparos.desativar_sysmain(callback=finalizar_reparo)

        def executar_fix_windows_update():
            atualizar_status_reparos("Limpando cache do Windows Update...")

            def worker():
                resultado = reparos.limpar_cache_update()
                self.after(0, lambda: self.lbl_reparos_status.configure(text=resultado))

            t = threading.Thread(target=worker, daemon=True)
            t.start()

        def executar_otimizar_trim():
            atualizar_status_reparos("Executando otimização TRIM...")

            def worker():
                resultado = reparos.otimizar_ssd_trim()
                self.after(0, lambda: self.lbl_reparos_status.configure(text=resultado))

            t = threading.Thread(target=worker, daemon=True)
            t.start()

        def disparar_diagnostico_rede():
            def worker():
                ok, mensagem = rede.diagnosticar_problema_rede()

                if ok:
                    self.after(0, lambda: self.lbl_status_internet.configure(text=mensagem))
                    return

                def perguntar_reparo():
                    resposta = messagebox.askyesno(
                        "Diagnóstico de Rede",
                        "Problema de rede detectado. Deseja aplicar o reparo automático?",
                        parent=self,
                    )

                    if not resposta:
                        self.lbl_status_internet.configure(text=f"Diagnóstico com falha: {mensagem}")
                        return

                    self.lbl_status_internet.configure(text="Aplicando reparo automático de rede...")

                    def worker_reparo():
                        resultado = rede.executar_reparo_rede()
                        self.after(0, lambda: self.lbl_status_internet.configure(text=resultado))

                    threading.Thread(target=worker_reparo, daemon=True).start()

                self.after(0, perguntar_reparo)

            threading.Thread(target=worker, daemon=True).start()

        def atualizar_status_seguranca(mensagem: str):
            self.after(0, lambda: self.lbl_seguranca_status.configure(text=mensagem))

        def finalizar_seguranca(ok: bool, mensagem: str):
            texto = mensagem if ok else f"Falha: {mensagem}"
            self.after(0, lambda: self.lbl_seguranca_status.configure(text=texto))

        def executar_defender():
            atualizar_status_seguranca("Executando verificação rápida do Defender...")
            seguranca.verificar_windows_defender(callback=finalizar_seguranca)

        def executar_firewall():
            atualizar_status_seguranca("Checando status do Firewall...")
            seguranca.checar_status_firewall(callback=finalizar_seguranca)

        def atualizar_status_relatorio(mensagem: str):
            self.after(0, lambda: self.lbl_relatorio_status.configure(text=mensagem))

        def finalizar_relatorio(ok: bool, mensagem: str):
            texto = mensagem if ok else f"Falha: {mensagem}"
            self.after(0, lambda: self.lbl_relatorio_status.configure(text=texto))

        def executar_relatorio_bancada():
            atualizar_status_relatorio("Gerando relatório de bancada...")
            relatorio.gerar_relatorio_bancada(callback=finalizar_relatorio)

        # =========================
        # LAYOUT PRINCIPAL
        # =========================
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, corner_radius=12)
        self.container.grid(row=0, column=0, padx=16, pady=16, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)

        self.titulo = ctk.CTkLabel(
            self.container,
            text="Toolbox Pro v1.4",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.titulo.grid(row=0, column=0, pady=(14, 8))

        self.tabview = ctk.CTkTabview(self.container, command=aba_mudou, height=560)
        self.tabview.grid(row=1, column=0, padx=12, pady=12, sticky="nsew")

        aba_hw = self.tabview.add("Hardware")
        aba_rede = self.tabview.add("Rede")
        aba_limpeza = self.tabview.add("Limpeza")
        aba_reparos = self.tabview.add("Reparos")
        aba_seguranca = self.tabview.add("Segurança")

        # =========================
        # ABA HARDWARE
        # =========================
        aba_hw.grid_columnconfigure((0, 1), weight=1)
        aba_hw.grid_rowconfigure((0, 1, 2), weight=1)
        aba_hw.grid_rowconfigure(3, weight=1)

        info = sensores.coletar_info_estatica()

        def _texto_curto(texto: str, limite: int = 35) -> str:
            texto = texto or "N/A"
            return texto if len(texto) <= limite else texto[:limite].rstrip() + "..."

        card_ident = ctk.CTkFrame(aba_hw, corner_radius=10)
        card_ident.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        ctk.CTkLabel(card_ident, text="Identificação", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 6)
        )
        ctk.CTkLabel(card_ident, text=f"PC: {_texto_curto(info['pc'], 24)}", anchor="w").pack(
            fill="x", padx=12, pady=2
        )
        ctk.CTkLabel(card_ident, text=f"Usuário: {_texto_curto(info['usuario'], 28)}", anchor="w").pack(
            fill="x", padx=12, pady=(2, 10)
        )

        card_cpu = ctk.CTkFrame(aba_hw, corner_radius=10)
        card_cpu.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")

        ctk.CTkLabel(card_cpu, text="Processador", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 6)
        )
        ctk.CTkLabel(card_cpu, text=f"CPU: {_texto_curto(info['cpu'], 36)}", anchor="w").pack(
            fill="x", padx=12, pady=2
        )
        ctk.CTkLabel(card_cpu, text=f"RAM Total: {info['ram_total']}", anchor="w").pack(
            fill="x", padx=12, pady=(2, 10)
        )

        card_gpu = ctk.CTkFrame(aba_hw, corner_radius=10)
        card_gpu.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

        ctk.CTkLabel(card_gpu, text="Placa de Vídeo", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 6)
        )
        ctk.CTkLabel(card_gpu, text=f"GPU: {_texto_curto(info['gpu_modelo'], 36)}", anchor="w").pack(
            fill="x", padx=12, pady=2
        )
        ctk.CTkLabel(card_gpu, text=f"VRAM: {info['gpu_vram_mb']} MB", anchor="w").pack(
            fill="x", padx=12, pady=(2, 10)
        )

        card_uso = ctk.CTkFrame(aba_hw, corner_radius=10)
        card_uso.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")

        ctk.CTkLabel(card_uso, text="Monitoramento", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 6)
        )
        self.lbl_cpu_uso = ctk.CTkLabel(card_uso, text="CPU: --%")
        self.lbl_cpu_uso.pack(anchor="w", padx=12, pady=2)
        self.lbl_ram_uso = ctk.CTkLabel(card_uso, text="RAM: --%")
        self.lbl_ram_uso.pack(anchor="w", padx=12, pady=2)
        self.lbl_disco_uso = ctk.CTkLabel(card_uso, text="Disco C:: --%")
        self.lbl_disco_uso.pack(anchor="w", padx=12, pady=2)
        self.lbl_gpu_uso = ctk.CTkLabel(card_uso, text="Uso GPU: --%")
        self.lbl_gpu_uso.pack(anchor="w", padx=12, pady=2)
        self.lbl_gpu_temp = ctk.CTkLabel(card_uso, text="Temp GPU: --°C")
        self.lbl_gpu_temp.pack(anchor="w", padx=12, pady=(2, 10))

        card_ram = ctk.CTkFrame(aba_hw, corner_radius=10)
        card_ram.grid(row=2, column=0, columnspan=2, padx=8, pady=(8, 8), sticky="nsew")

        ctk.CTkLabel(card_ram, text="Memória Física", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 6)
        )
        ctk.CTkLabel(card_ram, text=f"RAM total instalada: {info['ram_total']}", anchor="w").pack(
            fill="x", padx=12, pady=(0, 10)
        )

        card_relatorio = ctk.CTkFrame(aba_hw, corner_radius=10)
        card_relatorio.grid(row=3, column=0, columnspan=2, padx=8, pady=(8, 8), sticky="nsew")

        ctk.CTkLabel(card_relatorio, text="Relatório de Bancada", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 6)
        )
        ctk.CTkLabel(
            card_relatorio,
            text="Gera um relatório profissional com hardware, RAM total e informações de rede na Área de Trabalho.",
            justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 10))
        btn_relatorio = ctk.CTkButton(
            card_relatorio,
            text="Gerar Relatório de Bancada",
            command=executar_relatorio_bancada,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
        )
        btn_relatorio.pack(fill="x", padx=12, pady=(0, 12))

        self.lbl_relatorio_status = ctk.CTkLabel(card_relatorio, text="Pronto para gerar relatório.")
        self.lbl_relatorio_status.pack(anchor="w", padx=12, pady=(0, 10))

        # =========================
        # ABA REDE
        # =========================
        aba_rede.grid_columnconfigure(0, weight=1)

        card_rede = ctk.CTkFrame(aba_rede, corner_radius=10)
        card_rede.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        ctk.CTkLabel(card_rede, text="Diagnóstico de Rede", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 6)
        )
        self.lbl_ip_local = ctk.CTkLabel(card_rede, text="IP Local: --")
        self.lbl_ip_local.pack(anchor="w", padx=12, pady=2)
        self.lbl_ip_publico = ctk.CTkLabel(card_rede, text="IP Público: --")
        self.lbl_ip_publico.pack(anchor="w", padx=12, pady=2)
        self.lbl_ping = ctk.CTkLabel(card_rede, text="Ping 8.8.8.8: --")
        self.lbl_ping.pack(anchor="w", padx=12, pady=2)
        self.lbl_status_internet = ctk.CTkLabel(card_rede, text="Status: --")
        self.lbl_status_internet.pack(anchor="w", padx=12, pady=(2, 10))

        btn_diag_rede = ctk.CTkButton(
            card_rede,
            text="Diagnosticar e Reparar Rede",
            command=disparar_diagnostico_rede,
            fg_color="#0B3D91",
            hover_color="#072B66",
        )
        btn_diag_rede.pack(fill="x", padx=12, pady=(0, 12))

        # =========================
        # ABA SEGURANÇA
        # =========================
        aba_seguranca.grid_columnconfigure((0, 1), weight=1)
        aba_seguranca.grid_rowconfigure(1, weight=1)
        aba_seguranca.grid_rowconfigure(2, weight=1)

        card_seg_topo = ctk.CTkFrame(aba_seguranca, corner_radius=10)
        card_seg_topo.grid(row=0, column=0, columnspan=2, padx=8, pady=(8, 6), sticky="nsew")

        ctk.CTkLabel(card_seg_topo, text="Segurança do Sistema", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 4)
        )
        ctk.CTkLabel(
            card_seg_topo,
            text="Verificações nativas do Windows para Defender e Firewall, executadas em background.",
            justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 10))

        card_defender = ctk.CTkFrame(aba_seguranca, corner_radius=10)
        card_defender.grid(row=1, column=0, padx=(8, 6), pady=8, sticky="nsew")

        ctk.CTkLabel(card_defender, text="Windows Defender", font=ctk.CTkFont(size=15, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 4)
        )
        ctk.CTkLabel(
            card_defender,
            text="Executa uma verificação rápida nativa do antivírus do Windows.",
            justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 10))
        btn_defender = ctk.CTkButton(
            card_defender,
            text="Verificação Rápida Defender",
            command=executar_defender,
            fg_color="#15803D",
            hover_color="#166534",
        )
        btn_defender.pack(fill="x", padx=12, pady=(0, 12))

        card_firewall = ctk.CTkFrame(aba_seguranca, corner_radius=10)
        card_firewall.grid(row=1, column=1, padx=(6, 8), pady=8, sticky="nsew")

        ctk.CTkLabel(card_firewall, text="Firewall", font=ctk.CTkFont(size=15, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 4)
        )
        ctk.CTkLabel(
            card_firewall,
            text="Verifica se o Firewall do Windows está ativo nos perfis do sistema.",
            justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 10))
        btn_firewall = ctk.CTkButton(
            card_firewall,
            text="Checar Firewall",
            command=executar_firewall,
            fg_color="#1D4ED8",
            hover_color="#1E40AF",
        )
        btn_firewall.pack(fill="x", padx=12, pady=(0, 12))

        card_status_seg = ctk.CTkFrame(aba_seguranca, corner_radius=10)
        card_status_seg.grid(row=2, column=0, columnspan=2, padx=8, pady=(0, 8), sticky="nsew")

        ctk.CTkLabel(card_status_seg, text="Status de Segurança", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 4)
        )
        self.lbl_seguranca_status = ctk.CTkLabel(card_status_seg, text="Pronto para iniciar.")
        self.lbl_seguranca_status.pack(anchor="w", padx=12, pady=(0, 10))

        # =========================
        # ABA LIMPEZA
        # =========================
        aba_limpeza.grid_columnconfigure(0, weight=1)

        card_limpeza = ctk.CTkFrame(aba_limpeza, corner_radius=10)
        card_limpeza.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        ctk.CTkLabel(card_limpeza, text="Utilidades de Limpeza", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=12, pady=(10, 8)
        )

        btn_temp = ctk.CTkButton(card_limpeza, text="Limpar Temporários", command=executar_limpeza_temp)
        btn_temp.pack(fill="x", padx=12, pady=6)

        btn_lixeira = ctk.CTkButton(card_limpeza, text="Esvaziar Lixeira", command=executar_esvaziar_lixeira)
        btn_lixeira.pack(fill="x", padx=12, pady=6)

        self.lbl_limpeza_status = ctk.CTkLabel(card_limpeza, text="Pronto.")
        self.lbl_limpeza_status.pack(anchor="w", padx=12, pady=(8, 10))

        # =========================
        # ABA REPAROS
        # =========================
        aba_reparos.grid_columnconfigure((0, 1), weight=1)
        aba_reparos.grid_rowconfigure(1, weight=1)
        aba_reparos.grid_rowconfigure(2, weight=1)
        aba_reparos.grid_rowconfigure(3, weight=1)

        card_reparos_topo = ctk.CTkFrame(aba_reparos, corner_radius=10)
        card_reparos_topo.grid(row=0, column=0, columnspan=2, padx=8, pady=(8, 6), sticky="nsew")

        ctk.CTkLabel(
            card_reparos_topo,
            text="Reparos do Windows",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(10, 4))
        ctk.CTkLabel(
            card_reparos_topo,
            text="Ferramentas nativas executadas em background para não travar a interface.",
            justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 10))

        card_sfc = ctk.CTkFrame(aba_reparos, corner_radius=10)
        card_sfc.grid(row=1, column=0, padx=(8, 6), pady=8, sticky="nsew")

        ctk.CTkLabel(
            card_sfc,
            text="SFC /scannow",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(10, 4))
        ctk.CTkLabel(
            card_sfc,
            text="Verifica e repara arquivos protegidos do sistema.",
            justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 10))
        btn_sfc = ctk.CTkButton(card_sfc, text="Rodar SFC /scannow", command=executar_sfc)
        btn_sfc.pack(fill="x", padx=12, pady=(0, 12))

        card_dism = ctk.CTkFrame(aba_reparos, corner_radius=10)
        card_dism.grid(row=1, column=1, padx=(6, 8), pady=8, sticky="nsew")

        ctk.CTkLabel(
            card_dism,
            text="DISM Repair",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(10, 4))
        ctk.CTkLabel(
            card_dism,
            text="Restaura a imagem do Windows usando os componentes internos.",
            justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 10))
        btn_dism = ctk.CTkButton(card_dism, text="Rodar DISM Repair", command=executar_dism)
        btn_dism.pack(fill="x", padx=12, pady=(0, 12))

        card_sysmain = ctk.CTkFrame(aba_reparos, corner_radius=10)
        card_sysmain.grid(row=2, column=0, columnspan=2, padx=8, pady=(0, 6), sticky="nsew")

        ctk.CTkLabel(
            card_sysmain,
            text="SysMain / SSD",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(10, 4))
        ctk.CTkLabel(
            card_sysmain,
            text="Desativa o SysMain para reduzir atividade agressiva em SSDs.",
            justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 10))
        btn_sysmain = ctk.CTkButton(card_sysmain, text="Desativar SysMain (Fix SSD 100%)", command=executar_sysmain)
        btn_sysmain.pack(fill="x", padx=12, pady=(0, 12))

        card_fixes = ctk.CTkFrame(aba_reparos, corner_radius=10)
        card_fixes.grid(row=3, column=0, columnspan=2, padx=8, pady=(0, 6), sticky="nsew")

        card_fixes.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            card_fixes,
            text="Outras correções",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 4))

        btn_update = ctk.CTkButton(card_fixes, text="Fix Windows Update", command=executar_fix_windows_update)
        btn_update.grid(row=1, column=0, padx=(12, 6), pady=(0, 12), sticky="ew")

        btn_trim = ctk.CTkButton(card_fixes, text="Otimizar TRIM", command=executar_otimizar_trim)
        btn_trim.grid(row=1, column=1, padx=(6, 12), pady=(0, 12), sticky="ew")

        card_status_reparos = ctk.CTkFrame(aba_reparos, corner_radius=10)
        card_status_reparos.grid(row=4, column=0, columnspan=2, padx=8, pady=(0, 8), sticky="nsew")

        ctk.CTkLabel(
            card_status_reparos,
            text="Status dos reparos",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(10, 4))
        self.lbl_reparos_status = ctk.CTkLabel(card_status_reparos, text="Pronto para iniciar.")
        self.lbl_reparos_status.pack(anchor="w", padx=12, pady=(0, 10))

        # Estado inicial por aba visível
        aba_mudou()
        atualizar_hardware_ui()
        atualizar_rede_ui()


if __name__ == "__main__":
    app = ToolboxProApp()
    app.mainloop()