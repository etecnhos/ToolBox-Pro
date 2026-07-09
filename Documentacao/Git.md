# Documentação do Projeto: Gestão de Versão com Git e GitHub

Nesta seção, registro o aprendizado sobre o controle de versão do **Toolbox Pro** utilizando o Git local e o servidor remoto do GitHub, configurados no meu Nitro 5 (i5 11ª Ger).

---

## 🧠 Conceitos Fundamentais

### 1. O que é o Git e para que ele serve?
O Git é um sistema de controle de versão. Diferente de uma pasta comum (onde se você deletar ou alterar algo errado, já era), o Git funciona como uma máquina do tempo do código. Ele monitora cada linha modificada, permitindo criar pontos de salvamento estruturados para que eu possa testar novas funções sem medo de quebrar o que já está funcionando.

### 2. Qual a diferença entre Git e GitHub?
O Git é a ferramenta local, o conjunto de chaves na minha bancada que roda direto no meu Nitro 5 e salva o histórico na pasta oculta `.git`. O GitHub é o servidor na nuvem, uma plataforma online segura onde eu envio as cópias dos meus "pontos de salvamento" do Git para ter um backup externo e construir o meu portfólio profissional.

---

## 💻 Comandos Práticos Dominados

Durante a Semana 0, configurei o ambiente e utilizei os seguintes comandos no terminal:

* `git init`: Transforma a pasta comum do projeto em um repositório Git, criando a pasta oculta `.git` para começar a monitorar os arquivos.
* `git status`: Mostra o estado atual do projeto (quais arquivos foram modificados, quais ainda não foram salvos e o que está pronto para o commit).
* `git add .`: O ponto `.` significa "tudo". Este comando seleciona todas as modificações da pasta atual e as prepara para serem salvas.
* `git commit -m "mensagem"`: Tira uma "foto" oficial do estado atual do código e salva na história do Git com uma mensagem explicando o que foi feito.
* `git push`: Pega todos os commits salvos no Git local e os envia (empurra) para o repositório remoto no GitHub.

---

## 🐛 Erros Conhecidos e Como Resolver

### 1. Erro: `src refspec main does not match any`
* **Por que acontece:** Tentativa de dar push para a nuvem sem antes ter feito pelo menos um commit local. A ramificação (branch) ainda não existia oficialmente.
* **Como resolvi:** Executando a sequência correta: `git add .` para preparar os arquivos e `git commit -m "..."` para criar o histórico inicial.

### 2. Erro: `Tell me who you are`
* **Por que acontece:** O Git instalado em um sistema operacional novo não possui o nome e o e-mail do desenvolvedor cadastrados para assinar os commits.
* **Como resolvi:** Configurando os dados globalmente no terminal com os comandos:
  `git config --global user.email "seu-email@gmail.com"`
  `git config --global user.name "SeuNome"`

### 3. Erro: `Permission denied (publickey)`
* **Por que acontece:** O terminal tentou autenticar usando uma chave SSH que o novo computador ainda não possuía configurada no perfil do GitHub.
* **Como resolvi:** Alterando o protocolo de conexão para HTTPS (que autentica direto pelo navegador de forma simples) rodando o comando:
  `git remote set-url origin https://github.com/usuario/repositorio.git`