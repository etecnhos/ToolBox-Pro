import ctypes
import subprocess
import threading
from typing import Callable, Optional, Tuple


CallbackSeguranca = Optional[Callable[[bool, str], None]]


def _is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _creationflags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _iniciar_thread(worker, callback: CallbackSeguranca) -> threading.Thread:
    def runner() -> None:
        ok, mensagem = worker()
        if callback is not None:
            callback(ok, mensagem)

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    return thread


def verificar_windows_defender(callback: CallbackSeguranca = None) -> threading.Thread:
    def worker() -> Tuple[bool, str]:
        if not _is_admin():
            return False, "Execute o Toolbox Pro como Administrador para iniciar a verificação do Defender."

        try:
            resultado = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    "Start-MpScan -ScanType QuickScan",
                ],
                capture_output=True,
                text=True,
                creationflags=_creationflags(),
            )

            stdout = (resultado.stdout or "").strip()
            stderr = (resultado.stderr or "").strip()
            saida = stdout if stdout else stderr

            if resultado.returncode == 0:
                mensagem = saida or "Verificação rápida do Windows Defender iniciada/concluída com sucesso."
                return True, mensagem

            detalhe = saida or f"Código de saída {resultado.returncode}."
            if "access is denied" in detalhe.lower() or "acesso negado" in detalhe.lower():
                detalhe = "Acesso negado. Abra o Toolbox Pro como Administrador e tente novamente."
            return False, f"Falha ao executar a verificação do Defender.\n{detalhe}"
        except FileNotFoundError:
            return False, "Não foi possível localizar o PowerShell necessário para o Defender."
        except Exception as e:
            return False, f"Erro ao verificar Windows Defender: {e}"

    return _iniciar_thread(worker, callback)


def checar_status_firewall(callback: CallbackSeguranca = None) -> threading.Thread:
    def worker() -> Tuple[bool, str]:
        try:
            resultado = subprocess.run(
                ["netsh", "advfirewall", "show", "allprofiles", "state"],
                capture_output=True,
                text=True,
                creationflags=_creationflags(),
            )

            saida = (resultado.stdout or resultado.stderr or "").strip()
            texto = saida.lower()

            perfis = []
            perfil_atual = None

            for linha in saida.splitlines():
                linha_limpa = linha.strip().lower()
                if not linha_limpa:
                    continue

                if any(chave in linha_limpa for chave in ("domain profile", "perfil de domínio", "perfil de dominio")):
                    perfil_atual = "Domínio"
                elif any(chave in linha_limpa for chave in ("private profile", "perfil privado")):
                    perfil_atual = "Privado"
                elif any(chave in linha_limpa for chave in ("public profile", "perfil público", "perfil publico")):
                    perfil_atual = "Público"

                if perfil_atual and any(chave in linha_limpa for chave in ("state on", "estado ativo", "ligado", "ativado")):
                    perfis.append(f"{perfil_atual}: Ativo")
                    perfil_atual = None
                elif perfil_atual and any(chave in linha_limpa for chave in ("state off", "estado inativo", "desligado", "desativado")):
                    perfis.append(f"{perfil_atual}: Inativo")
                    perfil_atual = None

            if not perfis:
                if "on" in texto or "ativado" in texto or "ligado" in texto:
                    perfis = ["Firewall: Ativo"]
                elif "off" in texto or "desativado" in texto or "inativo" in texto:
                    perfis = ["Firewall: Inativo"]
                else:
                    perfis = ["Status do firewall não identificado com precisão."]

            ativo = all("Ativo" in item for item in perfis) if perfis else False
            return ativo, " | ".join(perfis)
        except FileNotFoundError:
            return False, "Não foi possível localizar o comando netsh."
        except Exception as e:
            return False, f"Erro ao checar firewall: {e}"

    return _iniciar_thread(worker, callback)