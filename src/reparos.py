import ctypes
import subprocess
import threading
from typing import Callable, Optional, Tuple


ResultadoReparo = Tuple[bool, str]
CallbackReparo = Optional[Callable[[bool, str], None]]


def _is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _creationflags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _executar_comando(comando: list[str], descricao: str) -> ResultadoReparo:
    if not _is_admin():
        return False, "Execute o Toolbox Pro como Administrador para usar esta função."

    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            creationflags=_creationflags(),
        )

        stdout = (resultado.stdout or "").strip()
        stderr = (resultado.stderr or "").strip()
        saida = stdout if stdout else stderr

        if resultado.returncode == 0:
            mensagem = saida or "Sem retorno adicional do Windows."
            return True, f"{descricao} concluído com sucesso.\n{mensagem}"

        erro = saida or f"Código de saída {resultado.returncode}."
        if "access is denied" in erro.lower() or "acesso negado" in erro.lower():
            return False, "Acesso negado. Abra o Toolbox Pro como Administrador e tente novamente."

        return False, f"{descricao} retornou erro.\n{erro}"
    except FileNotFoundError:
        return False, f"Não foi possível localizar o comando para {descricao}."
    except Exception as e:
        return False, f"Erro ao executar {descricao}: {e}"


def _iniciar_thread(comando: list[str], descricao: str, callback: CallbackReparo) -> threading.Thread:
    def worker() -> None:
        ok, mensagem = _executar_comando(comando, descricao)
        if callback is not None:
            callback(ok, mensagem)

    thread = threading.Thread(target=worker, daemon=True, name=f"Reparo-{descricao}")
    thread.start()
    return thread


def corrigir_arquivos_sistema(callback: CallbackReparo = None) -> threading.Thread:
    return _iniciar_thread(["sfc", "/scannow"], "SFC /scannow", callback)


def restaurar_imagem_windows(callback: CallbackReparo = None) -> threading.Thread:
    return _iniciar_thread(
        ["dism", "/online", "/cleanup-image", "/restorehealth"],
        "DISM /Online /Cleanup-Image /RestoreHealth",
        callback,
    )


def desativar_sysmain(callback: CallbackReparo = None) -> threading.Thread:
    def worker() -> None:
        if not _is_admin():
            if callback is not None:
                callback(False, "Execute o Toolbox Pro como Administrador para usar esta função.")
            return

        try:
            config = subprocess.run(
                ["sc", "config", "sysmain", "start=disabled"],
                capture_output=True,
                text=True,
                creationflags=_creationflags(),
            )
            stop = subprocess.run(
                ["net", "stop", "sysmain"],
                capture_output=True,
                text=True,
                creationflags=_creationflags(),
            )

            config_out = (config.stdout or config.stderr or "").strip()
            stop_out = (stop.stdout or stop.stderr or "").strip()

            if config.returncode == 0 and stop.returncode == 0:
                mensagem = "SysMain desativado com sucesso.\n"
                if config_out:
                    mensagem += config_out + "\n"
                if stop_out:
                    mensagem += stop_out
                if callback is not None:
                    callback(True, mensagem.strip())
                return

            erro = "\n".join(part for part in [config_out, stop_out] if part).strip()
            if not erro:
                erro = f"Códigos de saída: sc={config.returncode}, net={stop.returncode}."

            if "access is denied" in erro.lower() or "acesso negado" in erro.lower():
                erro = "Acesso negado. Abra o Toolbox Pro como Administrador e tente novamente."

            if callback is not None:
                callback(False, f"Falha ao desativar SysMain.\n{erro}")
        except FileNotFoundError:
            if callback is not None:
                callback(False, "Não foi possível localizar os comandos necessários para SysMain.")
        except Exception as e:
            if callback is not None:
                callback(False, f"Erro ao desativar SysMain: {e}")

    thread = threading.Thread(target=worker, daemon=True, name="Reparo-SysMain")
    thread.start()
    return thread

def limpar_cache_update():
    try:
        # 1. Para o serviço do Windows Update
        subprocess.check_output("net stop wuauserv", shell=True, text=True)
        
        # 2. Executa o comando do PowerShell para limpar a pasta de Downloads do Update
        comando_ps = "powershell -ExecutionPolicy Bypass -Command \"Remove-Item -Path C:\\Windows\\SoftwareDistribution\\Download\\* -Recurse -Force\""
        subprocess.check_output(comando_ps, shell=True, text=True)
        
        # 3. Reinicia o serviço do Windows Update
        subprocess.check_output("net start wuauserv", shell=True, text=True)
        
        return "Cache do Windows Update limpo e serviço reiniciado com sucesso!"
    except subprocess.CalledProcessError as e:
        return f"Erro de permissão ou execução. Execute como Administrador.\nDetalhes: {str(e)}"
    except Exception as e:
        return f"Falha ao limpar cache do Update: {str(e)}"


def otimizar_ssd_trim():
    try:
        # Executa o comando TRIM no SSD via PowerShell
        comando_trim = "powershell -ExecutionPolicy Bypass -Command \"Optimize-Volume -DriveLetter C -ReTrim -Verbose\""
        subprocess.check_output(comando_trim, shell=True, text=True)
        
        return "Comando TRIM enviado com sucesso! O SSD foi otimizado."
    except subprocess.CalledProcessError as e:
        return f"Erro ao otimizar SSD. Verifique os privilégios de Administrador.\nDetalhes: {str(e)}"
    except Exception as e:
        return f"Falha na otimização: {str(e)}"