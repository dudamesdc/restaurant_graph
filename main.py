import os
from ner_processor import build_graph
import networkx as nx


def main():
    print("--- Iniciando Pipeline de Extração de Restaurantes ---")
    print("\n1. Extraindo dados dos arquivos HTML...")
    

    print("\n2. Processando descrições com NER e construindo o Grafo (NetworkX)...")
    base_path = os.path.dirname(os.path.abspath(__file__))
    input_files = [
        os.path.join(base_path, "json_graphs/bambu.json"),
        os.path.join(base_path, "json_graphs/camaroes.json"),
    ]

    graph = build_graph(input_files)

    # Save & Summary
    output_path = os.path.join(base_path, "restaurant_graph.gexf")
    nx.write_gexf(graph, output_path)

    print("\n--- Pipeline concluída com sucesso! ---")
    print(f"Total de nós no Grafo: {graph.number_of_nodes()}")
    print(f"Total de arestas no Grafo: {graph.number_of_edges()}")
    print(f"Arquivo do Grafo salvo em: {output_path}")


if __name__ == "__main__":
    main()
