import json
import re

import pdfplumber
from bs4 import BeautifulSoup

ARQUIVO_BAMBU = "data/bambu.txt"
SAIDA_BAMBU = "json_graphs/bambu.json"
SAIDA_CAMAROES = "json_graphs/camaroes.json"


def extrair_bambu():
    try:
        with open(ARQUIVO_BAMBU, encoding="utf-8") as f:
            conteudo_html = f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo {ARQUIVO_BAMBU} não foi encontrado na pasta.")
        return

    soup = BeautifulSoup(conteudo_html, "html.parser")
    cardapio = []

    itens_html = soup.find_all("div", class_="text-card-foreground")

    print(f"Iniciando extração de {len(itens_html)} itens...")

    for item in itens_html:
        tag_titulo = item.find("h6")
        titulo = tag_titulo.get_text(strip=True) if tag_titulo else "N/D"

        tag_desc = item.find("span", class_="line-clamp-2")
        descricao = tag_desc.get_text(strip=True) if tag_desc else "Sem descrição"

        tag_categoria = item.find_previous("h5", class_="category-heading")
        categoria = tag_categoria.get_text(strip=True) if tag_categoria else "Outros"

        tag_preco = item.find("strong")
        preco = "Consultar"
        if tag_preco:
            preco = tag_preco.parent.get_text(strip=True).replace("\xa0", " ")

        cardapio.append(
            {
                "categoria": categoria,
                "prato": titulo,
                "descricao": descricao,
                "preco": preco,
            }
        )

    with open(SAIDA_BAMBU, "w", encoding="utf-8") as f:
        json.dump(cardapio, f, indent=4, ensure_ascii=False)

    print(f"Concluído! Dados salvos em {SAIDA_BAMBU}")


# O Regex procura:
# 1. Tudo em Maiúsculo (com espaços, hifens e barras) no início
# 2. Um ou mais números no final (incluindo o padrão de múltiplos preços separados por | )
PADRAO_PRATO = re.compile(r"^([A-ZÀ-Ú0-9 \-\/]+)\s+((?:\d{2,3}(?:\s*\|\s*\d{2,3})*))$")

ARQUIVO_PDF = "camaroes.pdf"


def extrair_cardapio_pdf(caminho_pdf):
    cardapio = []

    with pdfplumber.open(caminho_pdf) as pdf:
        for numero_pagina, pagina in enumerate(pdf.pages):
            texto = pagina.extract_text()
            if not texto:
                continue

            linhas = texto.split("\n")
            prato_atual = None

            for linha in linhas:
                linha = linha.strip()
                if not linha:
                    continue

                match = PADRAO_PRATO.match(linha)

                if match:
                    # Achou um novo prato! Salva o anterior (se houver) na lista
                    if prato_atual:
                        # Limpa espaços extras da descrição antes de salvar
                        prato_atual["descricao"] = prato_atual["descricao"].strip()
                        cardapio.append(prato_atual)

                    # Inicia um novo objeto de prato
                    prato_atual = {
                        "prato": match.group(1).strip(),
                        "preco": match.group(2).strip(),
                        "descricao": "",
                    }
                elif prato_atual:
                    # Se a linha não é um título, é a continuação da descrição do prato atual
                    prato_atual["descricao"] += linha + " "

            # Garante que o último prato da página seja salvo
            if prato_atual:
                prato_atual["descricao"] = prato_atual["descricao"].strip()
                cardapio.append(prato_atual)

    with open(SAIDA_CAMAROES, "w", encoding="utf-8") as f:
        json.dump(cardapio, f, indent=4, ensure_ascii=False)
        print(f"Sucesso! {len(cardapio)} pratos extraídos.")


if __name__ == "__main__":
    extrair_bambu()
    extrair_cardapio_pdf("data/camaroes.pdf")
