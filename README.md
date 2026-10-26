# Inova Trônica — Central de ordens de serviço

Aplicação web em Python e Flask para a Inova Trônica registrar e acompanhar ordens de serviço das células de automação. O grupo de recursos, o plano, o Serviço de Aplicativo e a publicação do código são feitos por um único script de Azure CLI, sem configuração manual no portal.

RM do representante: **95866**

## Recursos criados

| Item do enunciado | Valor no script |
| --- | --- |
| Grupo de recursos | `rg-web-app` |
| Região | `eastus` |
| Plano | `plan-web-app` |
| SKU | `F1` |
| Sistema operacional | Linux |
| Serviço de Aplicativo | `web-app-rm95866` |
| Runtime | `PYTHON:3.14` |

A região é `eastus` porque, nesta assinatura, o plano gratuito F1 não tem cota em `brazilsouth`. Se a Política recusar `eastus`, troque a variável `LOCATION` em `deploy-azure.sh` por outra região permitida que ofereça o SKU F1 e execute o script de novo.

## O que a aplicação faz

- Lista as ordens de serviço e resume quantas estão em cada etapa.
- Abre uma ordem com equipamento, célula, prioridade, responsável e sintoma.
- Avança a ordem por Aberta, Em diagnóstico, Em reparo e Concluída.
- Expõe `GET /health` e `GET /api/ordens`.

As ordens ficam em um arquivo JSON. No Azure ele é gravado em `/home/inova-tronica`, que permanece entre reinícios do plano. Não há banco de dados e a aplicação é de demonstração: não cadastre dados pessoais reais.

## Como implementar na nuvem

O script deve rodar no **Azure Cloud Shell (Bash)**. Ele usa `zip` e caminhos do Linux. Não execute `deploy-azure.sh` no PowerShell do Windows.

### 1. Conferir a assinatura

No [portal do Azure](https://portal.azure.com), abra o Cloud Shell e selecione **Bash**.

```bash
az account show --output table
```

Se a conta não for a da disciplina:

```bash
az account list --output table
az account set --subscription "NOME-DA-ASSINATURA"
```

### 2. Publicar este código no GitHub

No seu computador, na pasta do projeto:

```bash
git init
git add .
git commit -m "Adiciona a central de ordens de servico da Inova Tronica."
```

Crie um repositório vazio no GitHub, por exemplo `web-app-rm95866`, e envie o código:

```bash
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/web-app-rm95866.git
git push -u origin main
```

O link desse repositório entra no PDF de entrega.

### 3. Clonar no Cloud Shell

```bash
cd ~
git clone https://github.com/SEU_USUARIO/web-app-rm95866.git
cd web-app-rm95866
```

### 4. Ajustar a região, se a Política exigir

Abra o script:

```bash
code deploy-azure.sh
```

A variável `LOCATION` já está como `eastus`. Só altere se o passo seguinte recusar a região. Para ver as regiões da conta:

```bash
az account list-locations --query "[].name" --output tsv
```

O nome do Web App precisa continuar `web-app-rm95866`.

### 5. Executar o provisionamento e o deploy

```bash
chmod +x deploy-azure.sh
./deploy-azure.sh
```

O script faz, nesta ordem:

1. Confere a conta e registra o provedor `Microsoft.Web`, se ainda não estiver registrado.
2. Cria o grupo `rg-web-app`.
3. Cria o plano Linux `plan-web-app` no SKU `F1`.
4. Cria o Web App `web-app-rm95866` com Python 3.14.
5. Liga o build do Oryx para instalar o `requirements.txt`.
6. Define o Gunicorn como comando de inicialização.
7. Compacta a aplicação, publica com `az webapp deploy` e reinicia o site.

Ao terminar, ele mostra a URL:

```text
https://web-app-rm95866.azurewebsites.net
```

No plano F1 o primeiro acesso pode levar um ou dois minutos. Se a página mostrar erro de aplicação, leia o log:

```bash
az webapp log tail --name web-app-rm95866 --resource-group rg-web-app
```

Se `PYTHON:3.14` não existir na sua CLI, consulte os runtimes e ajuste a variável `RUNTIME`:

```bash
az webapp list-runtimes --os-type linux --output table
```

Use um valor no formato `PYTHON:3.12` (ou o que a lista mostrar) e rode o script outra vez.

### 6. Testar a solução

1. Abra `https://web-app-rm95866.azurewebsites.net`.
2. Confira o painel com as ordens de exemplo e a faixa com o RM 95866.
3. Abra **Nova ordem**, registre um equipamento e volte ao painel.
4. Entre na ordem e use **Avançar** até mudar a etapa.
5. Opcional: `https://web-app-rm95866.azurewebsites.net/health` deve responder `status: ok`.

### 7. Evidências para o PDF

No portal, abra a **Visão geral** de cada recurso e salve um print em que o nome do recurso apareça:

1. Grupo de recursos `rg-web-app`.
2. Plano do Serviço de Aplicativo `plan-web-app` (Linux e F1 visíveis).
3. Serviço de Aplicativo `web-app-rm95866` (URL e estado Em execução).

No navegador, salve prints do funcionamento:

4. Painel com as ordens.
5. Formulário de nova ordem, de preferência depois de registrar uma ordem.
6. Detalhe de uma ordem com a etapa avançada.

Copie os arquivos para `entrega/prints/` com estes nomes:

```text
01-grupo-de-recursos.png
02-plano-app-service.png
03-web-app.png
04-aplicacao-painel.png
05-aplicacao-nova-ordem.png
06-aplicacao-andamento.png
```

Edite no início de `entrega/gerar_relatorio.py` o nome do integrante, o nome do grupo e a URL do GitHub. Depois, na pasta do projeto:

```bash
pip install fpdf2
python entrega/gerar_relatorio.py
```

O PDF sai em `entrega/CP3_Aplicativos_em_Nuvem_RM95866.pdf`. Envie esse arquivo no Portal do Aluno, em Entrega de Trabalhos. Apenas um integrante do grupo envia.

### 8. Publicar uma correção

Depois de alterar o código e enviar ao GitHub:

```bash
cd ~/web-app-rm95866
git pull
./deploy-azure.sh
```

O script reutiliza o grupo, o plano e o Web App se eles já existirem e publica o pacote novo.

### 9. Rodar na máquina local (opcional)

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Linux ou Cloud Shell:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000`.

### 10. Remover os recursos

Quando a entrega estiver concluída e a disciplina não precisar mais do laboratório:

```bash
az group delete --name rg-web-app --yes --no-wait
```

Isso apaga o grupo, o plano e o Web App.

## Estrutura

```text
app.py                 aplicação Flask
requirements.txt       Flask e Gunicorn
templates/             páginas HTML
static/style.css       estilo da interface
deploy-azure.sh        criação dos recursos e deploy
entrega/               folha de rosto e montagem do PDF
```
