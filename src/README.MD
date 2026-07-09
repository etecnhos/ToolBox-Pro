# Toolbox Pro v1.4 🛠️

O **Toolbox Pro** é um software de assistência técnica premium para bancada de manutenção de computadores. Desenvolvido em Python com interface moderna em CustomTkinter, o sistema foi projetado sob uma arquitetura assíncrona (Multithreading) de alta performance para rodar diagnósticos e reparos sem congelamento da interface visual (mantendo constantes 60 FPS).

## 🚀 Funcionalidades Principais

*   **Aba Hardware:** Identificação estática de componentes (Nome do PC, Usuário, CPU, GPU e memória RAM Total física) e monitoramento dinâmico em tempo real do uso de CPU, RAM, Disco C:, uso e temperatura de placas NVIDIA.
*   **Aba Rede:** Coleta automatizada de IP Local e IP Público, teste contínuo de latência (Ping) e ferramenta de diagnóstico rápido com assistente de confirmação para reparos automáticos (Reset de Winsock, FlushDNS e renovação de IP).
*   **Aba Limpeza:** Exclusão inteligente de arquivos temporários do sistema (%TEMP% e Windows/Temp) isolando arquivos travados, e esvaziamento silencioso da lixeira do Windows via API nativa.
*   **Aba Reparos:** Automações em background para execução de ferramentas críticas de integridade (`SFC /scannow` e `DISM`), mitigação do bug do SSD a 100% via desativação do serviço SysMain e otimização forçada de blocos usando comandos de TRIM.
*   **Aba Segurança:** Varreduras rápidas integradas via Windows Defender e verificação do status de Firewall em tempo real.
*   **Exportação de Relatórios:** Geração automática de um arquivo estruturado `Relatorio_Bancada.txt` gerado diretamente na Área de Trabalho com todos os dados da máquina do cliente.

## 🛠️ Tecnologias Utilizadas

*   **Python 3.11+**
*   **CustomTkinter** (Interface Visual Premium)
*   **psutil** (Métricas do Sistema e RAM)
*   **Subprocess & Threading** (Execução assíncrona paralela)

## 📦 Como Compilar (.EXE)

Para gerar o arquivo executável autônomo pronto para uso em pen drives de boot, execute o seguinte comando no terminal:

```bash
pyinstaller --onefile --noconsole --clean src/main.py