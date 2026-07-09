import ctypes
import os
import shutil
from typing import Tuple


def _remover_item(path: str) -> int:
    """
    Remove arquivo/pasta e retorna bytes liberados.
    Ignora itens bloqueados/permissão negada.
    """
    total = 0
    try:
        if os.path.isfile(path) or os.path.islink(path):
            total = os.path.getsize(path)
            os.remove(path)
        elif os.path.isdir(path):
            # Soma tamanho antes de remover
            for root, _, files in os.walk(path, topdown=False):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        total += os.path.getsize(fp)
                    except Exception:
                        pass
            shutil.rmtree(path, ignore_errors=False)
    except Exception:
        # Ignora arquivos em uso / sem permissão
        return 0
    return total


def limpar_arquivos_temporarios() -> float:
    """
    Limpa %TEMP% e C:\\Windows\\Temp.
    Retorna total liberado em MB.
    """
    caminhos = [
        os.getenv("TEMP", ""),
        os.getenv("TMP", ""),
        r"C:\Windows\Temp",
    ]

    vistos = set()
    total_bytes = 0

    for pasta in caminhos:
        if not pasta:
            continue
        pasta = os.path.abspath(pasta)
        if pasta in vistos:
            continue
        vistos.add(pasta)

        if not os.path.exists(pasta):
            continue

        try:
            for nome in os.listdir(pasta):
                alvo = os.path.join(pasta, nome)
                total_bytes += _remover_item(alvo)
        except Exception:
            # Se não conseguir listar a pasta, segue fluxo
            continue

    total_mb = total_bytes / (1024 * 1024)
    return round(total_mb, 2)


def esvaziar_lixeira() -> Tuple[bool, str]:
    """
    Esvazia a lixeira do Windows em modo silencioso.
    """
    try:
        SHERB_NOCONFIRMATION = 0x00000001
        SHERB_NOPROGRESSUI = 0x00000002
        SHERB_NOSOUND = 0x00000004

        flags = SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND

        resultado = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
        if resultado == 0:
            return True, "Lixeira esvaziada com sucesso."
        return False, f"Falha ao esvaziar lixeira. Código: {resultado}"
    except Exception as e:
        return False, f"Erro ao esvaziar lixeira: {e}"