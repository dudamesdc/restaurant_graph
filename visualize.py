# visualize_graph.py
import os

import matplotlib.pyplot as plt
import networkx as nx


def plot_graph(file_path):
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo {file_path} não encontrado. Execute a pipeline primeiro.")
        return

    print(f"Carregando grafo de {file_path}...")
    G = nx.read_gexf(file_path)

    # Configurações de exibição
    plt.figure(figsize=(15, 15))

    # Gerando o layout (spring_layout é bom para ver agrupamentos)
    print("Calculando layout (isso pode levar alguns segundos)...")
    pos = nx.spring_layout(G, k=0.15, iterations=50, seed=42)

    # Separando os nós para colorir
    pratos = [n for n, d in G.nodes(data=True) if d.get("type") == "Prato"]
    ingredientes = [n for n, d in G.nodes(data=True) if d.get("type") == "Ingrediente"]

    # Desenha os nós de Pratos (Azul claro)
    nx.draw_networkx_nodes(
        G, pos, nodelist=pratos, node_color="skyblue", node_size=100, label="Pratos"
    )

    # Desenha os nós de Ingredientes (Laranja)
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=ingredientes,
        node_color="orange",
        node_size=30,
        label="Ingredientes",
        alpha=0.7,
    )

    # Desenha as arestas (Relações)
    nx.draw_networkx_edges(G, pos, alpha=0.1, edge_color="gray")

    # Adiciona rótulos apenas para os pratos (para não poluir demais a imagem)
    # Se quiser ver todos, remova o filtro abaixo
    labels = {n: n for n in pratos if G.degree(n) > 5}  # Apenas pratos com mais conexões
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_family="sans-serif")

    plt.legend(scatterpoints=1)
    plt.title("Visualização do Grafo de Restaurantes (Rede de Ingredientes)")
    plt.axis("off")

    output_img = "graph_visualization.png"
    plt.savefig(output_img, dpi=300, bbox_inches="tight")
    print(f"Sucesso! Visualização salva como '{output_img}'")
    plt.show()


if __name__ == "__main__":
    plot_graph("restaurant_graph.gexf")
