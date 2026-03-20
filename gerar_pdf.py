"""
Gerador de PDF para documentos de cadastro de fornecedor
Dependências: pip install reportlab requests
"""

import requests
import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# ─────────────────────────────────────────
# CONSULTA DO CNPJ
# ─────────────────────────────────────────

def consultar_cnpj(cnpj: str) -> dict:
    """Consulta dados do CNPJ na BrasilAPI (gratuita, sem autenticação)"""
    cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return {"erro": f"CNPJ não encontrado (status {resp.status_code})"}
    except Exception as e:
        return {"erro": str(e)}


def formatar_cnpj(cnpj: str) -> str:
    c = cnpj.replace(".", "").replace("/", "").replace("-", "")
    if len(c) == 14:
        return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"
    return cnpj


def formatar_cep(cep: str) -> str:
    if cep and len(cep) == 8:
        return f"{cep[:5]}-{cep[5:]}"
    return cep or ""


def data_hoje() -> str:
    return datetime.now().strftime("%d/%m/%Y às %H:%M")


# ─────────────────────────────────────────
# ESTILOS COMPARTILHADOS
# ─────────────────────────────────────────

def estilos_base():
    azul_escuro = colors.HexColor("#1a3a5c")
    azul_medio  = colors.HexColor("#2563eb")
    cinza_claro = colors.HexColor("#f1f5f9")
    cinza_texto = colors.HexColor("#475569")
    branco      = colors.white

    titulo = ParagraphStyle(
        "titulo",
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=branco,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    subtitulo = ParagraphStyle(
        "subtitulo",
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#cbd5e1"),
        alignment=TA_CENTER,
        spaceAfter=0,
    )
    label = ParagraphStyle(
        "label",
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=cinza_texto,
        spaceAfter=2,
    )
    valor = ParagraphStyle(
        "valor",
        fontName="Helvetica",
        fontSize=11,
        textColor=azul_escuro,
        spaceAfter=10,
    )
    rodape = ParagraphStyle(
        "rodape",
        fontName="Helvetica",
        fontSize=7,
        textColor=cinza_texto,
        alignment=TA_CENTER,
    )
    return {
        "titulo": titulo,
        "subtitulo": subtitulo,
        "label": label,
        "valor": valor,
        "rodape": rodape,
        "azul_escuro": azul_escuro,
        "azul_medio": azul_medio,
        "cinza_claro": cinza_claro,
        "cinza_texto": cinza_texto,
        "branco": branco,
    }


def cabecalho(titulo_doc: str, subtitulo_doc: str, estilos: dict) -> list:
    """Cabeçalho azul padrão para todos os documentos"""
    elementos = []
    dados_cab = [[
        Paragraph(titulo_doc, estilos["titulo"]),
    ]]
    tabela_cab = Table(dados_cab, colWidths=[16.5 * cm])
    tabela_cab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), estilos["azul_escuro"]),
        ("ROUNDEDCORNERS", [8]),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
    ]))
    elementos.append(tabela_cab)

    dados_sub = [[Paragraph(subtitulo_doc, estilos["subtitulo"])]]
    tabela_sub = Table(dados_sub, colWidths=[16.5 * cm])
    tabela_sub.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), estilos["azul_medio"]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabela_sub)
    elementos.append(Spacer(1, 0.5 * cm))
    return elementos


def campo(label_txt: str, valor_txt: str, estilos: dict) -> list:
    """Campo label + valor com linha divisória"""
    return [
        Paragraph(label_txt.upper(), estilos["label"]),
        Paragraph(str(valor_txt) if valor_txt else "—", estilos["valor"]),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=8),
    ]


def rodape_padrao(cnpj: str, estilos: dict) -> list:
    return [
        Spacer(1, 0.5 * cm),
        HRFlowable(width="100%", thickness=1, color=estilos["azul_escuro"]),
        Spacer(1, 0.2 * cm),
        Paragraph(
            f"Documento gerado automaticamente em {data_hoje()} | CNPJ: {formatar_cnpj(cnpj)} | Sistema de Cadastro de Fornecedores",
            estilos["rodape"]
        ),
    ]


# ─────────────────────────────────────────
# 1. CARTÃO CNPJ
# ─────────────────────────────────────────

def gerar_cartao_cnpj(dados: dict, caminho: str) -> str:
    doc = SimpleDocTemplate(caminho, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    e = estilos_base()
    els = cabecalho("CARTÃO CNPJ", "Cadastro Nacional da Pessoa Jurídica — Receita Federal do Brasil", e)

    cnpj = dados.get("cnpj", "")
    els += campo("CNPJ", formatar_cnpj(cnpj), e)
    els += campo("Razão Social", dados.get("razao_social", ""), e)
    els += campo("Nome Fantasia", dados.get("nome_fantasia") or dados.get("razao_social", ""), e)
    els += campo("Situação Cadastral", dados.get("descricao_situacao_cadastral", ""), e)
    els += campo("Data de Abertura", dados.get("data_inicio_atividade", ""), e)
    els += campo("Natureza Jurídica", dados.get("natureza_juridica", ""), e)

    atividade = dados.get("cnae_fiscal_descricao", "")
    els += campo("Atividade Principal (CNAE)", atividade, e)

    endereco = (
        f"{dados.get('logradouro','')}, {dados.get('numero','')}"
        f"{' - ' + dados.get('complemento','') if dados.get('complemento') else ''}\n"
        f"{dados.get('bairro','')} — {dados.get('municipio','')}/{dados.get('uf','')}\n"
        f"CEP: {formatar_cep(dados.get('cep',''))}"
    )
    els += campo("Endereço", endereco, e)
    els += campo("Telefone", dados.get("ddd_telefone_1", ""), e)
    els += campo("E-mail", dados.get("email", ""), e)
    els += rodape_padrao(cnpj, e)

    doc.build(els)
    return caminho


# ─────────────────────────────────────────
# 2. REGIME TRIBUTÁRIO
# ─────────────────────────────────────────

def gerar_regime_tributario(dados: dict, caminho: str) -> str:
    doc = SimpleDocTemplate(caminho, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    e = estilos_base()
    els = cabecalho("REGIME TRIBUTÁRIO", "Enquadramento fiscal da empresa", e)

    cnpj = dados.get("cnpj", "")
    els += campo("CNPJ", formatar_cnpj(cnpj), e)
    els += campo("Razão Social", dados.get("razao_social", ""), e)

    opcao = dados.get("opcao_pelo_simples")
    if opcao:
        regime = "Simples Nacional"
        data_opcao = dados.get("data_opcao_pelo_simples", "")
        els += campo("Regime Tributário", regime, e)
        els += campo("Data de opção pelo Simples Nacional", data_opcao, e)
    else:
        regime = "Lucro Presumido / Lucro Real (não optante pelo Simples)"
        els += campo("Regime Tributário", regime, e)

    mei = dados.get("opcao_pelo_mei")
    els += campo("Microempreendedor Individual (MEI)", "Sim" if mei else "Não", e)
    els += campo("Porte da Empresa", dados.get("porte", ""), e)
    els += campo("Capital Social", f"R$ {dados.get('capital_social', 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), e)

    els += rodape_padrao(cnpj, e)
    doc.build(els)
    return caminho


# ─────────────────────────────────────────
# 5. RAZÃO SOCIAL
# ─────────────────────────────────────────

def gerar_razao_social(dados: dict, caminho: str) -> str:
    doc = SimpleDocTemplate(caminho, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    e = estilos_base()
    els = cabecalho("RAZÃO SOCIAL", "Dados de identificação oficial da empresa", e)

    cnpj = dados.get("cnpj", "")
    els += campo("CNPJ", formatar_cnpj(cnpj), e)
    els += campo("Razão Social", dados.get("razao_social", ""), e)
    els += campo("Nome Fantasia", dados.get("nome_fantasia") or "—", e)
    els += campo("Situação Cadastral", dados.get("descricao_situacao_cadastral", ""), e)
    els += campo("Data de Abertura", dados.get("data_inicio_atividade", ""), e)
    els += campo("Natureza Jurídica", dados.get("natureza_juridica", ""), e)
    els += campo("Porte", dados.get("porte", ""), e)

    socios = dados.get("qsa", [])
    if socios:
        nomes = "\n".join([f"• {s.get('nome_socio','')} ({s.get('qualificacao_socio','')})" for s in socios])
        els += campo("Quadro Societário", nomes, e)

    els += rodape_padrao(cnpj, e)
    doc.build(els)
    return caminho


# ─────────────────────────────────────────
# 3 e 4. DOCUMENTOS MANUAIS (template)
# ─────────────────────────────────────────

def gerar_template_manual(tipo: str, titulo: str, instrucao: str, dados: dict, caminho: str) -> str:
    doc = SimpleDocTemplate(caminho, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    e = estilos_base()
    els = cabecalho(titulo, "Documento a ser fornecido pelo responsável da empresa", e)

    cnpj = dados.get("cnpj", "")
    els += campo("CNPJ", formatar_cnpj(cnpj), e)
    els += campo("Razão Social", dados.get("razao_social", ""), e)

    aviso = ParagraphStyle("aviso", fontName="Helvetica-Bold", fontSize=11,
                           textColor=colors.HexColor("#b45309"),
                           backColor=colors.HexColor("#fef3c7"),
                           borderPad=10, spaceAfter=12)
    els.append(Spacer(1, 0.5*cm))
    els.append(Paragraph(f"⚠ {instrucao}", aviso))
    els.append(Spacer(1, 0.3*cm))

    info = ParagraphStyle("info", fontName="Helvetica", fontSize=10,
                          textColor=colors.HexColor("#1e3a5f"), spaceAfter=8)
    els.append(Paragraph("Este documento deve ser obtido junto ao órgão competente e enviado ao sistema em formato PDF.", info))
    els += rodape_padrao(cnpj, e)

    doc.build(els)
    return caminho


# ─────────────────────────────────────────
# FUNÇÃO PRINCIPAL: gera qualquer documento
# ─────────────────────────────────────────

def gerar_documento(numero: int, cnpj: str, pasta_saida: str = "/tmp") -> dict:
    """
    Gera o PDF do documento escolhido.
    Retorna dict com caminho do arquivo ou mensagem de erro.
    """
    os.makedirs(pasta_saida, exist_ok=True)
    dados = consultar_cnpj(cnpj)

    if "erro" in dados:
        return {"sucesso": False, "mensagem": dados["erro"]}

    cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    mapa = {
        1: ("cartao_cnpj",        lambda: gerar_cartao_cnpj(dados, f"{pasta_saida}/cartao_cnpj_{cnpj_limpo}_{ts}.pdf")),
        2: ("regime_tributario",  lambda: gerar_regime_tributario(dados, f"{pasta_saida}/regime_{cnpj_limpo}_{ts}.pdf")),
        3: ("inscricao_estadual", lambda: gerar_template_manual(
                "inscricao_estadual",
                "INSCRIÇÃO ESTADUAL",
                "Este documento deve ser obtido na Secretaria da Fazenda do estado onde a empresa está registrada.",
                dados, f"{pasta_saida}/inscricao_estadual_{cnpj_limpo}_{ts}.pdf")),
        4: ("inscricao_municipal", lambda: gerar_template_manual(
                "inscricao_municipal",
                "INSCRIÇÃO MUNICIPAL",
                "Este documento deve ser obtido na Prefeitura do município sede da empresa.",
                dados, f"{pasta_saida}/inscricao_municipal_{cnpj_limpo}_{ts}.pdf")),
        5: ("razao_social",       lambda: gerar_razao_social(dados, f"{pasta_saida}/razao_social_{cnpj_limpo}_{ts}.pdf")),
        6: ("certidao_negativa",  lambda: gerar_template_manual(
                "certidao_negativa",
                "CERTIDÃO NEGATIVA",
                "Emitir no portal da Receita Federal: https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet",
                dados, f"{pasta_saida}/certidao_negativa_{cnpj_limpo}_{ts}.pdf")),
        7: ("situacao_trabalhista", lambda: gerar_template_manual(
                "situacao_trabalhista",
                "SITUAÇÃO TRABALHISTA",
                "Consultar no eSocial ou portal do Ministério do Trabalho com login gov.br.",
                dados, f"{pasta_saida}/situacao_trabalhista_{cnpj_limpo}_{ts}.pdf")),
    }

    if numero not in mapa:
        return {"sucesso": False, "mensagem": "Número de documento inválido. Escolha entre 1 e 7."}

    nome, funcao = mapa[numero]
    caminho = funcao()
    razao = dados.get("razao_social", "")

    return {
        "sucesso": True,
        "documento": nome,
        "caminho": caminho,
        "razao_social": razao,
        "cnpj": formatar_cnpj(cnpj),
    }


# ─────────────────────────────────────────
# TESTE RÁPIDO
# ─────────────────────────────────────────

if __name__ == "__main__":
    cnpj_teste = "11222333000181"  # substitua por um CNPJ real

    for num in range(1, 8):
        resultado = gerar_documento(num, cnpj_teste, pasta_saida="/tmp/docs_fornecedor")
        if resultado["sucesso"]:
            print(f"[OK] Documento {num}: {resultado['caminho']}")
        else:
            print(f"[ERRO] Documento {num}: {resultado['mensagem']}")
