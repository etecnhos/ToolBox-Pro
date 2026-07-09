from datetime import datetime
from pathlib import Path
import threading
from typing import Callable, Optional, Tuple

import rede
import sensores


CallbackRelatorio = Optional[Callable[[bool, str], None]]


def _obter_desktop() -> Path:
    home = Path.home()
    candidatos = [home / "Desktop", home / "OneDrive" / "Desktop"]
    for candidato in candidatos:
        if candidato.exists():
            return candidato
    return home / "Desktop"


def _montar_relatorio() -> Tuple[bool, str]:
    try:
        info = sensores.coletar_info_estatica()
        rede_info = rede.obter_status_rede()

        desktop = _obter_desktop()
        desktop.mkdir(parents=True, exist_ok=True)

        caminho = desktop / "Relatorio_Bancada.txt"
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        linhas = [
            "=" * 64,
            "RELATÓRIO DE BANCADA - TOOLBOX PRO v1.4",
            "=" * 64,
            f"Data de emissão: {data_atual}",
            f"PC do cliente: {info.get('pc', 'N/A')}",
            "",
            "DADOS ESTÁTICOS DE HARDWARE",
            "-" * 64,
            f"Usuário: {info.get('usuario', 'N/A')}",
            f"CPU: {info.get('cpu', 'N/A')}",
            f"GPU: {info.get('gpu_modelo', 'N/A')}",
            f"VRAM: {info.get('gpu_vram_mb', 'N/A')} MB",
            f"RAM total: {info.get('ram_total', 'N/A')}",
            "",
            "DADOS DE REDE",
            "-" * 64,
            f"IP Local: {rede_info.get('ip_local', 'N/A')}",
            f"IP Público: {rede_info.get('ip_publico', 'N/A')}",
            f"Status Internet: {rede_info.get('status_internet', 'N/A')}",
            f"Ping 8.8.8.8: {rede_info.get('ping_ms', 'N/A')}",
            "",
            "Gerado automaticamente pelo Toolbox Pro.",
            "=" * 64,
        ]

        caminho.write_text("\n".join(linhas), encoding="utf-8")
        return True, f"Relatório gerado com sucesso em: {caminho}"
    except Exception as e:
        return False, f"Falha ao gerar relatório de bancada: {e}"


def gerar_relatorio_bancada(callback: CallbackRelatorio = None) -> threading.Thread:
    def worker() -> None:
        ok, mensagem = _montar_relatorio()
        if callback is not None:
            callback(ok, mensagem)

    thread = threading.Thread(target=worker, daemon=True, name="GerarRelatorioBancada")
    thread.start()
    return thread