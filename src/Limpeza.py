import os
import shutil

def executar_limpeza():
    # Caminhos das pastas de arquivos temporários do Windows
    pastas_temp = [
        os.environ.get('TEMP'),                 # Geralmente C:\Users\Nome\AppData\Local\Temp
        os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp') # C:\Windows\Temp
    ]
    
    bytes_liberados = 0
    arquivos_deletados = 0
    arquivos_falhados = 0

    for pasta in pastas_temp:
        if not pasta or not os.path.exists(pasta):
            continue
            
        # Varre todos os arquivos e subpastas dentro da pasta temporária
        for item in os.listdir(pasta):
            caminho_item = os.path.join(pasta, item)
            try:
                # Calcula o tamanho do arquivo antes de deletar para o relatório
                if os.path.isfile(caminho_item) or os.path.islink(caminho_item):
                    bytes_liberados += os.path.getsize(caminho_item)
                    os.unlink(caminho_item) # Deleta o arquivo
                    arquivos_deletados += 1
                elif os.path.isdir(caminho_item):
                    # Para pastas, calcula o tamanho de forma recursiva
                    for root, dirs, files in os.walk(caminho_item):
                        bytes_liberados += sum(os.path.getsize(os.path.join(root, f)) for f in files)
                    shutil.rmtree(caminho_item) # Deleta a pasta inteira e o que tem dentro
                    arquivos_deletados += 1
            except Exception:
                # Se o arquivo estiver em uso pelo sistema/processo aberto, ele apenas pula
                arquivos_falhados += 1

    # Converte os bytes totais liberados para Megabytes (MB)
    mb_liberados = round(bytes_liberados / (1024 ** 2), 1)
    
    return {
        "mb_liberados": mb_liberados,
        "deletados": arquivos_deletados,
        "bloqueados": arquivos_falhados
    }
import ctypes

def esvaziar_lixeira():
    try:
        # Chama a função nativa do Windows (SHELL32) para limpar a lixeira silenciosamente
        # O número 7 diz para o Windows não mostrar confirmação, nem som, nem barra de progresso
        resultado = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        
        # Se o resultado for 0, deu certo. Se der erro, pode ser porque a lixeira já estava vazia
        if resultado == 0:
            return "Lixeira esvaziada com sucesso!"
        else:
            return "Lixeira já estava vazia ou nenhum item foi removido."
    except Exception as e:
        return f"Não foi possível limpar a lixeira: {str(e)}"