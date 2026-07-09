import os
import customtkinter as ctk

# 1. Configuração do visual da interface
ctk.set_appearance_mode("System")  # Segue o tema do Windows (Claro/Escuro)
ctk.set_default_color_theme("blue") # Define a cor padrão dos botões

# 2. Criando a estrutura da nossa janela
janela = ctk.CTk()
janela.title("Toolbox Pro v1.0")
janela.geometry("500x400") # Largura x Altura da janela

# 3. Função para buscar e exibir os dados quando o botão for clicado
def carregar_dados():
    nome_pc = os.environ.get('COMPUTERNAME')
    usuario = os.environ.get('USERNAME')
    
    # Atualiza o texto na tela com as informações reais
    texto_dados.configure(text=f"Computador: {nome_pc}\nUsuário Atual: {usuario}")

# 4. Elementos visuais (Widgets) dentro da janela
titulo = ctk.CTkLabel(janela, text="Toolbox Pro", font=("Arial", 24, "bold"))
titulo.pack(pady=20)

botao_carregar = ctk.CTkButton(janela, text="Verificar Sistema", command=carregar_dados)
botao_carregar.pack(pady=10)

# Caixa de texto onde as informações vão aparecer
texto_dados = ctk.CTkLabel(janela, text="Clique no botão para analisar o PC...", font=("Arial", 14))
texto_dados.pack(pady=30)

# 5. Mantém a janela aberta na tela
janela.mainloop()