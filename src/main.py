import os

# 1. Buscando informações direto do Windows
nome_sistema = os.environ.get('COMPUTERNAME')
usuario_atual = os.environ.get('USERNAME')

# 2. Exibindo na tela usando o print
print("=======================================")
print("          TOOLBOX PRO v1.0             ")
print("=======================================")
print("Nome do Computador:", nome_sistema)
print("Usuário Logado:    ", usuario_atual)
print("=======================================")