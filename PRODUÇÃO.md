# 🚀 Guia de Deploy em Produção (Ubuntu + Python 3.10)

Este guia detalha o passo a passo para colocar o microsserviço `nt-ai` em execução num servidor Ubuntu que já possui Python 3.10 instalado.

---

## 📋 Pré-requisitos
* Acesso SSH ao servidor Ubuntu.
* Python 3.10 já instalado.
* Git instalado.

---

## 1. Clonar o Projeto

Navegue até a pasta onde deseja instalar (geralmente `/home/ubuntu` ou `/var/www`) e clone o repositório.

```bash
# Exemplo: indo para a pasta home do usuário
cd ~

# Clonar (substitua pela URL do seu repositório se for privado, use token)
git clone [https://github.com/Marocosz/nt-ai.git](https://github.com/Marocosz/nt-ai.git)

# Entrar na pasta
cd nt-ai
```

---

## 2. Configurar o Ambiente Virtual (Venv)

Como o servidor já tem Python 3.10, vamos usá-lo para criar o ambiente isolado.

```bash
# Cria a venv chamada 'venvntai' usando o Python 3 nativo
python3 -m venv venvntai

# Ativa o ambiente
source venvntai/bin/activate
```

*Se o comando funcionar, seu terminal deve mostrar `(venvntai)` no início da linha.*

---

## 3. Instalar Dependências

Aqui usamos o arquivo específico para compatibilidade com Python 3.10 que você preparou.

```bash
# Atualiza o pip para evitar avisos
pip install --upgrade pip

# Instala as bibliotecas exatas
pip install -r requirements310.txt
```

---

## 4. Configurar Variáveis de Ambiente (.env)

O arquivo `.env` não vem do Git por segurança. Você precisa criá-lo no servidor.

```bash
# Criar/Editar o arquivo
nano .env
```

**Cole o conteúdo abaixo (com suas chaves reais):**

```ini
# Credencial da API da Groq
GROQ_API_KEY=

# credenciais da API do Google
GOOGLE_API_KEY=

# Credencial da API da OpenAI
OPENAI_API_KEY=
```

*Para salvar no Nano: Aperte `Ctrl+O`, `Enter`, e depois `Ctrl+X` para sair.*

---

## 5. Teste Manual (Antes de Automatizar)

Antes de criar o serviço, vamos rodar manualmente para ver se não há erros de importação ou crash.

> **Nota:** Usamos `--host 0.0.0.0` para liberar acesso externo e `--port 5001`. Não usamos `--reload` em produção.

```bash
# Garanta que a venv está ativa e rode:
uvicorn app.main:app --host 0.0.0.0 --port 5001
```

1.  Verifique se o log mostra `Application startup complete`.
2.  Tente fazer uma requisição (via Postman ou sua aplicação).
3.  Se funcionar, pare o servidor com `Ctrl+C`.

---

## 6. Criar Serviço Systemd (Rodar em Background)

Para que a aplicação rode sozinha, reinicie se o servidor desligar e não dependa do terminal aberto, criaremos um serviço do Linux.

1. Descubra o caminho absoluto da sua pasta:
   ```bash
   pwd
   # Saída esperada ex: /home/ubuntu/nt-ai
   ```

2. Crie o arquivo de serviço:
   ```bash
   sudo nano /etc/systemd/system/nt-ai.service
   ```

3. Cole a configuração abaixo (**Ajuste os caminhos conforme o `pwd` acima**):

```ini
[Unit]
Description=New Tracking AI Service (Python 3.10)
After=network.target

[Service]
# Usuário que vai rodar o app (geralmente ubuntu, root ou www-data)
User=ubuntu
Group=ubuntu

# Diretório raiz do projeto (Resultado do comando pwd)
WorkingDirectory=/home/ubuntu/nt-ai

# Comando de execução:
# Aponta diretamente para o uvicorn DENTRO da venv criada
# --workers 2: Permite processar mais requisições simultâneas
ExecStart=/home/ubuntu/nt-ai/venvntai/bin/uvicorn app.main:app --host 0.0.0.0 --port 5001 --workers 2 --proxy-headers

# Reiniciar automaticamente se cair
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 7. Ativar e Iniciar

```bash
# Recarrega o daemon do systemd para ler o novo arquivo
sudo systemctl daemon-reload

# Inicia o serviço agora
sudo systemctl start nt-ai

# Habilita para iniciar automaticamente no boot do servidor
sudo systemctl enable nt-ai
```

---

## 8. Verificação e Logs

Para saber se está tudo rodando ou monitorar erros em tempo real:

**Verificar Status:**
```bash
sudo systemctl status nt-ai
```
*(Deve aparecer "Active: active (running)" em verde)*

**Ler Logs em Tempo Real (Tail):**
```bash
sudo journalctl -u nt-ai -f
```

---

## 🔄 Como Atualizar o Código no Futuro?

Quando você subir atualizações para o GitHub e quiser atualizar o servidor:

```bash
cd ~/nt-ai
git pull
# Se houver novas dependências:
# source venvntai/bin/activate
# pip install -r requirements310.txt

# Reinicie o serviço para aplicar as mudanças
sudo systemctl restart nt-ai
```