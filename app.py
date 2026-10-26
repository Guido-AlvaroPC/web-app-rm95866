"""Central de ordens de serviço da Inova Trônica.

Aplicação de demonstração para o 3º CP de Aplicativos em Nuvem.
As ordens ficam em um arquivo JSON local. Não use dados pessoais reais.
"""

import json
import os
import threading
from datetime import datetime, timedelta, timezone

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "inova-tronica-cp3-rm95866")

RM = "95866"
APP_NOME = "web-app-rm95866"
# Brasília permanece em UTC−3 desde o fim do horário de verão.
TZ = timezone(timedelta(hours=-3))
FLUXO = ["Aberta", "Em diagnóstico", "Em reparo", "Concluída"]
CELULAS = ["Montagem", "Solda", "Inspeção", "Expedição", "Laboratório"]
PRIORIDADES = ["Baixa", "Média", "Alta", "Crítica"]
PESO = {"Crítica": 4, "Alta": 3, "Média": 2, "Baixa": 1}

_lock = threading.Lock()


def _agora():
    return datetime.now(TZ).strftime("%d/%m/%Y %H:%M")


def _arquivo():
    # No App Service, WEBSITE_SITE_NAME existe e /home permanece entre reinícios.
    if os.environ.get("WEBSITE_SITE_NAME"):
        pastas = ["/home/inova-tronica", "/tmp/inova-tronica"]
    else:
        pastas = [os.path.join(app.root_path, "data")]
    ultimo_erro = None
    for pasta in pastas:
        try:
            os.makedirs(pasta, exist_ok=True)
            sonda = os.path.join(pasta, ".sonda")
            with open(sonda, "w", encoding="utf-8") as arquivo:
                arquivo.write("ok")
            os.remove(sonda)
            return os.path.join(pasta, "ordens.json")
        except OSError as erro:
            ultimo_erro = erro
    raise RuntimeError(f"Não foi possível gravar as ordens: {ultimo_erro}")


def _semente():
    agora = _agora()
    return [
        {
            "id": "OS-1042",
            "equipamento": "Braço robótico de paletização",
            "celula": "Expedição",
            "prioridade": "Alta",
            "sintoma": "Perda de repetibilidade no eixo 3 depois do turno da manhã.",
            "tecnico": "Plantão A",
            "status": "Em diagnóstico",
            "aberta_em": agora,
            "atualizada_em": agora,
        },
        {
            "id": "OS-1043",
            "equipamento": "Esteira servo da linha 2",
            "celula": "Montagem",
            "prioridade": "Crítica",
            "sintoma": "Parada por falha do inversor. A linha está sem fluxo de peças.",
            "tecnico": "Plantão A",
            "status": "Aberta",
            "aberta_em": agora,
            "atualizada_em": agora,
        },
        {
            "id": "OS-1044",
            "equipamento": "CLP da célula de solda",
            "celula": "Solda",
            "prioridade": "Média",
            "sintoma": "Entrada digital do sensor de presença oscila a cada ciclo.",
            "tecnico": "Plantão B",
            "status": "Em reparo",
            "aberta_em": agora,
            "atualizada_em": agora,
        },
        {
            "id": "OS-1048",
            "equipamento": "Câmera de inspeção de solda",
            "celula": "Inspeção",
            "prioridade": "Baixa",
            "sintoma": "Calibração concluída e receita de visão republicada.",
            "tecnico": "Plantão B",
            "status": "Concluída",
            "aberta_em": agora,
            "atualizada_em": agora,
        },
    ]


def _ler_sem_trava():
    caminho = _arquivo()
    if not os.path.exists(caminho):
        dados = _semente()
        _gravar_sem_trava(dados)
        return dados
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (OSError, json.JSONDecodeError):
        dados = _semente()
        _gravar_sem_trava(dados)
    if not isinstance(dados, list):
        dados = _semente()
        _gravar_sem_trava(dados)
    return dados


def _gravar_sem_trava(dados):
    caminho = _arquivo()
    temporario = caminho + ".tmp"
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    os.replace(temporario, caminho)


def listar():
    with _lock:
        return _ler_sem_trava()


def buscar(ordem_id):
    for ordem in listar():
        if ordem["id"] == ordem_id:
            return ordem
    return None


def _proximo_id(dados):
    numeros = []
    for ordem in dados:
        try:
            numeros.append(int(str(ordem["id"]).split("-")[1]))
        except (IndexError, ValueError):
            continue
    return f"OS-{max(numeros, default=1000) + 1}"


def criar(campos):
    with _lock:
        dados = _ler_sem_trava()
        agora = _agora()
        ordem = {
            "id": _proximo_id(dados),
            "equipamento": campos["equipamento"],
            "celula": campos["celula"],
            "prioridade": campos["prioridade"],
            "sintoma": campos["sintoma"],
            "tecnico": campos["tecnico"],
            "status": "Aberta",
            "aberta_em": agora,
            "atualizada_em": agora,
        }
        dados.append(ordem)
        _gravar_sem_trava(dados)
        return ordem


def avancar_status(ordem_id):
    with _lock:
        dados = _ler_sem_trava()
        for ordem in dados:
            if ordem["id"] != ordem_id:
                continue
            indice = FLUXO.index(ordem["status"])
            if indice >= len(FLUXO) - 1:
                return ordem
            ordem["status"] = FLUXO[indice + 1]
            ordem["atualizada_em"] = _agora()
            _gravar_sem_trava(dados)
            return ordem
    return None


def ordenar(ordens):
    def chave(ordem):
        numero = 0
        try:
            numero = int(str(ordem["id"]).split("-")[1])
        except (IndexError, ValueError):
            numero = 0
        fechada = 1 if ordem["status"] == "Concluída" else 0
        return (fechada, -PESO.get(ordem["prioridade"], 0), -numero)

    return sorted(ordens, key=chave)


def contagens(ordens):
    totais = [("Todas", len(ordens))]
    for status in FLUXO:
        totais.append((status, sum(1 for ordem in ordens if ordem["status"] == status)))
    return totais


def validar(campos):
    if len(campos["equipamento"]) < 3:
        return "Informe o equipamento com pelo menos 3 caracteres."
    if campos["celula"] not in CELULAS:
        return "Escolha uma célula da lista."
    if campos["prioridade"] not in PRIORIDADES:
        return "Escolha uma prioridade da lista."
    if len(campos["tecnico"]) < 3:
        return "Informe o responsável com pelo menos 3 caracteres."
    if len(campos["sintoma"]) < 10:
        return "Descreva o sintoma com pelo menos 10 caracteres."
    return None


def ler_formulario():
    return {
        "equipamento": request.form.get("equipamento", "").strip(),
        "celula": request.form.get("celula", "").strip(),
        "prioridade": request.form.get("prioridade", "").strip(),
        "tecnico": request.form.get("tecnico", "").strip(),
        "sintoma": request.form.get("sintoma", "").strip(),
    }


@app.context_processor
def contexto_padrao():
    return {"rm": RM, "app_nome": APP_NOME, "fluxo": FLUXO}


@app.template_filter("slug")
def slug(texto):
    trocas = str.maketrans(
        {
            "á": "a",
            "à": "a",
            "â": "a",
            "ã": "a",
            "é": "e",
            "ê": "e",
            "í": "i",
            "ó": "o",
            "ô": "o",
            "õ": "o",
            "ú": "u",
            "ç": "c",
            " ": "-",
        }
    )
    return str(texto).lower().translate(trocas)


@app.get("/")
def index():
    ordens = listar()
    filtro = request.args.get("status", "").strip()
    if filtro not in FLUXO:
        filtro = ""
    visiveis = [ordem for ordem in ordens if not filtro or ordem["status"] == filtro]
    return render_template(
        "index.html",
        ordens=ordenar(visiveis),
        contagens=contagens(ordens),
        filtro=filtro,
    )


@app.route("/ordens/nova", methods=["GET", "POST"])
def nova():
    formulario = {campo: "" for campo in ("equipamento", "celula", "prioridade", "tecnico", "sintoma")}
    if request.method == "POST":
        formulario = ler_formulario()
        erro = validar(formulario)
        if erro:
            flash(erro, "erro")
        else:
            ordem = criar(formulario)
            flash(f"Ordem {ordem['id']} aberta.", "ok")
            return redirect(url_for("detalhe", ordem_id=ordem["id"]))
    return render_template(
        "nova.html",
        form=formulario,
        celulas=CELULAS,
        prioridades=PRIORIDADES,
    )


@app.get("/ordens/<ordem_id>")
def detalhe(ordem_id):
    ordem = buscar(ordem_id)
    if ordem is None:
        abort(404)
    indice = FLUXO.index(ordem["status"])
    proxima = FLUXO[indice + 1] if indice < len(FLUXO) - 1 else None
    return render_template("detalhe.html", ordem=ordem, proxima=proxima)


@app.post("/ordens/<ordem_id>/avancar")
def avancar(ordem_id):
    ordem = avancar_status(ordem_id)
    if ordem is None:
        abort(404)
    flash(f"{ordem['id']} agora está em {ordem['status']}.", "ok")
    return redirect(url_for("detalhe", ordem_id=ordem["id"]))


@app.get("/api/ordens")
def api_ordens():
    return jsonify(ordenar(listar()))


@app.get("/health")
def health():
    return jsonify(status="ok", app=APP_NOME, rm=RM)


@app.errorhandler(404)
def nao_encontrado(_erro):
    return render_template("erro.html", codigo=404, mensagem="Ordem ou página não encontrada."), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
