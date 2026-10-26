"""Gera o PDF de entrega do 3º CP.

Antes de rodar, preencha NOME, GRUPO e REPOSITORIO e coloque os prints
em entrega/prints/ com os nomes esperados. Sem esses arquivos o PDF
mostra um espaço marcado para colar a evidência.
"""

from pathlib import Path

from fpdf import FPDF

NOME = ""
GRUPO = "RM 95866"
REPOSITORIO = "https://github.com/Guido-AlvaroPC/web-app-rm95866"
RM = "95866"

RAIZ = Path(__file__).resolve().parent
PRINTS = RAIZ / "prints"
SAIDA = RAIZ / "CP3_Aplicativos_em_Nuvem_RM95866.pdf"

EVIDENCIAS = [
    (
        "01-grupo-de-recursos.png",
        "Grupo de recursos rg-web-app",
        "Visão geral do grupo, com a região e os recursos filhos.",
    ),
    (
        "02-plano-app-service.png",
        "Plano plan-web-app",
        "Visão geral do plano Linux, SKU F1.",
    ),
    (
        "03-web-app.png",
        "Serviço de Aplicativo web-app-rm95866",
        "Visão geral do Web App, com a URL e o estado de execução.",
    ),
    (
        "04-aplicacao-painel.png",
        "Aplicação em execução — painel",
        "Painel de ordens de serviço aberto na URL do Azure.",
    ),
    (
        "05-aplicacao-nova-ordem.png",
        "Aplicação em execução — nova ordem",
        "Registro de uma ordem de serviço na aplicação publicada.",
    ),
    (
        "06-aplicacao-andamento.png",
        "Aplicação em execução — andamento",
        "Detalhe de uma ordem depois de avançar a etapa.",
    ),
]


class Relatorio(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", size=9)
        self.set_text_color(90, 90, 90)
        self.cell(0, 8, f"3º CP · Aplicativos em Nuvem · RM {RM} · {self.page_no()}", align="C")


def fonte(pdf):
    pdf.add_font("Arial", "", r"C:\Windows\Fonts\arial.ttf")
    pdf.add_font("Arial", "B", r"C:\Windows\Fonts\arialbd.ttf")


def titulo(pdf, texto):
    pdf.set_text_color(26, 26, 26)
    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(0, 8, texto)
    pdf.ln(2)


def paragrafo(pdf, texto):
    pdf.set_text_color(26, 26, 26)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 7, texto)
    pdf.ln(2)


def linha_tabela(pdf, esquerda, direita, negrito=False):
    pdf.set_font("Arial", "B" if negrito else "", 11)
    pdf.cell(70, 8, esquerda, border=1)
    pdf.set_font("Arial", "", 11)
    pdf.cell(110, 8, direita, border=1, new_x="LMARGIN", new_y="NEXT")


def capa(pdf):
    pdf.add_page()
    pdf.ln(28)
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(154, 78, 36)
    pdf.cell(0, 8, "FIAP", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(26, 26, 26)
    pdf.set_font("Arial", size=13)
    pdf.cell(0, 8, "Engenharia Mecatrônica", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Cloud Computing & Machine as a Service (MaaS)", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(12)
    pdf.set_font("Arial", "B", 18)
    pdf.multi_cell(0, 9, "3º CP — 2º Semestre\nAplicativos em Nuvem", align="C")
    pdf.ln(8)
    pdf.set_font("Arial", size=14)
    pdf.multi_cell(0, 8, "Inova Trônica\nCentral de ordens de serviço no Azure App Service", align="C")
    pdf.ln(16)
    pdf.set_font("Arial", size=12)
    integrante = NOME.strip() or "Nome do integrante: preencher antes de enviar"
    pdf.cell(0, 8, f"Grupo: {GRUPO}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Integrante: {integrante}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"RM: {RM}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Prof. João Menk", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    if REPOSITORIO.strip():
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 7, f"GitHub: {REPOSITORIO.strip()}", align="C")
    else:
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 7, "GitHub: colar o link do repositório antes de enviar", align="C")
    pdf.ln(8)
    pdf.cell(0, 8, "26 de outubro de 2026", align="C")


def solucao(pdf):
    pdf.add_page()
    titulo(pdf, "Solução")
    paragrafo(
        pdf,
        "A Inova Trônica passa a abrir e acompanhar ordens de serviço das células de automação por uma aplicação web em Python. "
        "O mesmo script de Azure CLI cria o grupo, o plano Linux e o Serviço de Aplicativo e publica o código.",
    )
    paragrafo(
        pdf,
        "A interface lista as ordens, permite registrar equipamento, célula, prioridade, responsável e sintoma, e avança cada chamado "
        "pelas etapas Aberta, Em diagnóstico, Em reparo e Concluída. A faixa superior da página mostra o RM 95866 e o nome do Web App, "
        "para a evidência de funcionamento identificar a entrega.",
    )
    titulo(pdf, "Recursos provisionados")
    linha_tabela(pdf, "Recurso", "Valor", negrito=True)
    for esquerda, direita in [
        ("Grupo de recursos", "rg-web-app"),
        ("Região do plano e do Web App", "westus2"),
        ("Plano", "plan-web-app"),
        ("SKU", "F1"),
        ("Sistema operacional", "Linux"),
        ("Web App", "web-app-rm95866"),
        ("Runtime", "Python 3.14"),
        ("Inicialização", "Gunicorn (app:app)"),
    ]:
        linha_tabela(pdf, esquerda, direita)
    pdf.ln(6)
    paragrafo(
        pdf,
        "O tutorial completo de reprodução está no README.md do repositório. Resumo: clonar o projeto no Azure Cloud Shell (Bash), "
        "dar permissão de execução a deploy-azure.sh e rodá-lo. O script não depende de cliques no portal.",
    )


def evidencia(pdf, arquivo, titulo_print, descricao):
    pdf.add_page()
    titulo(pdf, titulo_print)
    paragrafo(pdf, descricao)
    caminho = PRINTS / arquivo
    if caminho.is_file():
        pdf.image(str(caminho), x=15, w=180)
        return
    pdf.set_draw_color(180, 80, 40)
    pdf.set_line_width(0.4)
    y = pdf.get_y() + 4
    pdf.rect(15, y, 180, 90)
    pdf.set_xy(20, y + 30)
    pdf.set_font("Arial", "B", 12)
    pdf.multi_cell(170, 7, "Print ainda não inserido.\nSalve a imagem em entrega/prints/" + arquivo + " e gere o PDF de novo.")


def main():
    PRINTS.mkdir(parents=True, exist_ok=True)
    pdf = Relatorio(format="A4")
    fonte(pdf)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(15, 15, 15)
    capa(pdf)
    solucao(pdf)
    pdf.add_page()
    titulo(pdf, "Evidências")
    paragrafo(
        pdf,
        "Cada página seguinte corresponde a um print pedido na entrega: a Visão geral de cada recurso e a aplicação funcionando na URL publicada. "
        "Substitua os espaços em branco pelos prints reais do portal e do navegador antes de enviar ao Portal do Aluno.",
    )
    for arquivo, titulo_print, descricao in EVIDENCIAS:
        evidencia(pdf, arquivo, titulo_print, descricao)
    pdf.output(str(SAIDA))
    print(f"PDF gerado em {SAIDA}")


if __name__ == "__main__":
    main()
