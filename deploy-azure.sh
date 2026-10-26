#!/usr/bin/env bash
# Inova Trônica — provisiona o App Service e publica a aplicação.
# 3º CP de Aplicativos em Nuvem. Executar no Azure Cloud Shell (Bash),
# na raiz deste repositório, depois de clonar o projeto.
#
# Recursos exigidos pelo enunciado:
#   Grupo:   rg-web-app
#   Plano:   plan-web-app
#   SKU:     F1
#   SO:      Linux
#   Web App: web-app-rm95866
#   Região:  brazilsouth (troque se a Política da assinatura bloquear)

set -euo pipefail

RG="rg-web-app"
LOCATION="brazilsouth"
PLAN="plan-web-app"
APP_NAME="web-app-rm95866"
RUNTIME="PYTHON:3.14"
SKU="F1"
PACOTE="/tmp/${APP_NAME}.zip"

if ! az account show --output none 2>/dev/null; then
  echo "Nenhuma sessão do Azure ativa. No Cloud Shell a conta já vem autenticada."
  echo "Fora do Cloud Shell, execute: az login"
  exit 1
fi

echo
echo "== Conta usada neste deploy =="
az account show --query "{assinatura:name, id:id, usuario:user.name}" --output table

estado="$(az provider show --namespace Microsoft.Web --query registrationState --output tsv)"
if [[ "${estado}" != "Registered" ]]; then
  echo "Registrando o provedor Microsoft.Web. Isso pode levar alguns minutos."
  az provider register --namespace Microsoft.Web --wait
fi

echo
echo "== 1. Grupo de recursos: ${RG} (${LOCATION}) =="
az group create \
  --name "${RG}" \
  --location "${LOCATION}" \
  --output table

echo
echo "== 2. Plano Linux ${SKU}: ${PLAN} =="
if az appservice plan show --name "${PLAN}" --resource-group "${RG}" --output none 2>/dev/null; then
  echo "O plano ${PLAN} já existe. Seguindo para o Web App."
else
  az appservice plan create \
    --name "${PLAN}" \
    --resource-group "${RG}" \
    --location "${LOCATION}" \
    --sku "${SKU}" \
    --is-linux \
    --output table
fi

echo
echo "== 3. Web App Linux: ${APP_NAME} =="
echo "O nome precisa ser único em todo o Azure."
if az webapp show --name "${APP_NAME}" --resource-group "${RG}" --output none 2>/dev/null; then
  echo "O Web App ${APP_NAME} já existe. A configuração e o pacote serão atualizados."
else
  az webapp create \
    --name "${APP_NAME}" \
    --resource-group "${RG}" \
    --plan "${PLAN}" \
    --runtime "${RUNTIME}" \
    --output table
fi

echo
echo "== 4. Build das dependências Python na publicação =="
az webapp config appsettings set \
  --name "${APP_NAME}" \
  --resource-group "${RG}" \
  --settings \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    ENABLE_ORYX_BUILD=true \
  --output table

echo
echo "== 5. Comando de inicialização (Gunicorn) =="
STARTUP="gunicorn --bind=0.0.0.0 --timeout 600 app:app"
if ! az webapp config set \
  --name "${APP_NAME}" \
  --resource-group "${RG}" \
  --startup-file "${STARTUP}" \
  --output none
then
  az webapp config set \
    --name "${APP_NAME}" \
    --resource-group "${RG}" \
    --startup-command "${STARTUP}" \
    --output none
fi
echo "Startup definido."

echo
echo "== 6. Pacote e deploy =="
rm -f "${PACOTE}"
find . -type f \
  ! -path "./.git/*" \
  ! -path "./.venv/*" \
  ! -path "./venv/*" \
  ! -path "./entrega/*" \
  ! -path "*/__pycache__/*" \
  ! -name "*.pyc" \
  ! -name "*.zip" \
  ! -path "./data/*.json" \
  -printf '%P\n' \
  | zip -@ "${PACOTE}"

az webapp deploy \
  --name "${APP_NAME}" \
  --resource-group "${RG}" \
  --src-path "${PACOTE}" \
  --type zip

echo
echo "== 7. Reinício do Web App =="
az webapp restart \
  --name "${APP_NAME}" \
  --resource-group "${RG}"

echo
echo "== Recursos no grupo ${RG} =="
az resource list --resource-group "${RG}" --output table

echo
echo "Aguardando a primeira resposta em /health (o plano F1 pode demorar a acordar)."
url="https://${APP_NAME}.azurewebsites.net/health"
pronto=0
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if curl -fsS --max-time 25 "${url}"; then
    echo
    pronto=1
    break
  fi
  echo "Ainda iniciando..."
  sleep 15
done

echo
echo "Deploy concluído."
echo "Grupo:  ${RG}"
echo "Plano:  ${PLAN} (${SKU}, Linux)"
echo "App:    ${APP_NAME}"
echo "URL:    https://${APP_NAME}.azurewebsites.net"
if [[ "${pronto}" -ne 1 ]]; then
  echo
  echo "A URL ainda não respondeu. No plano F1 o primeiro acesso pode levar mais um minuto."
  echo "Se aparecer Application Error, acompanhe o log:"
  echo "az webapp log tail --name ${APP_NAME} --resource-group ${RG}"
fi
