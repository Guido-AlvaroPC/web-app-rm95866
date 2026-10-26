# Inova Trônica — Central de ordens de serviço

Execute os passos no **Azure Cloud Shell (Bash)**.

## 1. Abrir o Cloud Shell

No [portal do Azure](https://portal.azure.com), abra o Cloud Shell e selecione **Bash**.

```bash
az account show --output table
```

## 2. Clonar o projeto

```bash
cd ~
git clone https://github.com/Guido-AlvaroPC/web-app-rm95866.git
cd web-app-rm95866
```

## 3. Publicar na nuvem

```bash
chmod +x deploy-azure.sh
./deploy-azure.sh
```

Ao terminar, abra:

```text
https://web-app-rm95866.azurewebsites.net
```

## 4. Usar a aplicação

1. No painel, veja as ordens e os totais de cada etapa.
2. Clique em **Nova ordem**, preencha equipamento, célula, prioridade, responsável e sintoma, e registre.
3. Abra a ordem criada e clique em **Avançar** para mudar a etapa.

## 5. Publicar uma alteração

```bash
cd ~/web-app-rm95866
git pull
./deploy-azure.sh
```

## 6. Rodar neste computador

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000`.

## 7. Apagar os recursos

```bash
az group delete --name rg-web-app --yes --no-wait
```
