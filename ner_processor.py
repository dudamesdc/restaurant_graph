import json
import spacy
from spacy.matcher import PhraseMatcher
from spacy.pipeline import EntityRuler
import networkx as nx
import os

INGREDIENTS = {
    "PROTEINA": [
        "camarão",
        "camarões",
        "peixe",
        "frango",
        "carne",
        "filé",
        "lagosta",
        "polvo",
        "lula",
        "porco",
        "bacon",
        "ovo",
        "ovos",
        "salmão",
        "bacalhau",
        "atum",
        "picanha",
        "alcatra",
        "maminha",
        "cordeiro",
        "sertão",
    ],
    "CARBOIDRATO": [
        "arroz",
        "feijão",
        "batata",
        "batatas",
        "macarrão",
        "massa",
        "cuscuz",
        "mandioca",
        "macaxeira",
        "farinha",
        "farofa",
        "espaguete",
        "fettuccine",
        "penne",
        "pão",
        "torrada",
        "batata frita",
        "purê",
    ],
    "VEGETAL": [
        "cebola",
        "alho",
        "tomate",
        "pimentão",
        "cheiro-verde",
        "coentro",
        "salsa",
        "alface",
        "rúcula",
        "agrião",
        "azeitona",
        "palmito",
        "milho",
        "ervilha",
        "brócolis",
        "couve",
        "abóbora",
        "jerimum",
        "berinjela",
        "abobrinha",
        "cogumelo",
        "cogumelos",
    ],
    "LATICINIO": [
        "queijo",
        "queijos",
        "leite",
        "creme de leite",
        "manteiga",
        "requeijão",
        "parmesão",
        "muçarela",
        "mussarela",
        "coalho",
        "catupiry",
        "gorgonzola",
        "provolone",
        "ricota",
    ],
    "TEMPERO_MOLHO": [
        "sal",
        "pimenta",
        "azeite",
        "óleo",
        "limão",
        "vinagre",
        "louro",
        "molho",
        "molho branco",
        "molho de tomate",
        "manjericão",
        "orégano",
        "shoyu",
        "mostarda",
        "ketchup",
        "maionese",
        "curry",
        "cominho",
    ],
}

RELATION_KEYWORDS = {
    "RECHEADO_COM": ["recheado", "recheada", "recheados", "recheadas"],
    "ACOMPANHADO_DE": [
        "acompanhado",
        "acompanhada",
        "acompanhados",
        "acompanhadas",
        "servido com",
    ],
    "AO_MOLHO_DE": ["ao molho", "com molho"],
    "COM": ["com", "e"],
}


class IngredientNER:
    def __init__(self):
        print("Carregando modelo SpaCy...")
        self.nlp = spacy.load("pt_core_news_lg")

        ruler = self.nlp.add_pipe("entity_ruler", before="ner")

        patterns = []
        for label, names in INGREDIENTS.items():
            for name in names:
                patterns.append({"label": "INGREDIENTE", "pattern": name})

        ruler.add_patterns(patterns)
        print("Dicionário de ingredientes carregado.")

    def extract_relations(self, text):
        doc = self.nlp(text.lower())
        entities = [ent for ent in doc.ents if ent.label_ == "INGREDIENTE"]
        relations = []

        # buscamos relações entre as entidades encontradas.

        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                e1, e2 = entities[i], entities[j]

                span_between = doc[e1.end : e2.start].text.strip()

                found_rel = "CONTÉM"
                for rel_type, keywords in RELATION_KEYWORDS.items():
                    if any(kw in span_between for kw in keywords):
                        found_rel = rel_type
                        break

                relations.append((e1.text, found_rel, e2.text))

        return list(set(entities)), relations


def build_graph(data_files):
    ner = IngredientNER()
    G = nx.MultiDiGraph()

    for file_path in data_files:
        print(f"Processando {file_path}...")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                items = json.load(f)
        except Exception as e:
            print(f"Erro ao ler {file_path}: {e}")
            continue

        if "bambu" in file_path.lower():
            restaurant_name = "Bambu"
        elif "camaroes" in file_path.lower():
            restaurant_name = "Camarões"
        else:
            restaurant_name = "Desconhecido"

        for item in items:
            dish_name = item.get("prato")
            description = item.get("descricao")

            if (
                not dish_name
                or dish_name == "N/A"
                or not description
                or description == "Sem descrição"
            ):
                continue

            G.add_node(
                dish_name,
                type="Prato",
                category=item.get("categoria") or "N/A",
                price=item.get("preco") or "0,00",
                restaurant=restaurant_name,
            )

            entities, relations = ner.extract_relations(description)

            for ent in entities:
                G.add_node(ent.text, type="Ingrediente")
                G.add_edge(dish_name, ent.text, relation="CONTÉM")

            for e1, rel, e2 in relations:
                G.add_edge(e1, e2, relation=rel)

    return G
