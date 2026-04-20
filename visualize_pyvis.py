import os

import networkx as nx
from pyvis.network import Network


def visualize_graph_with_pyvis(file_path, output_filename="grafo_restaurantes_pyvis.html"):
    if not os.path.exists(file_path):
        print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
        return

    print(f"Carregando {file_path}...")
    G = nx.read_gexf(file_path)

    net = Network(
        height="100vh",
        width="100%",
        bgcolor="#1a1a1a",
        font_color="white",
        select_menu=True,
        filter_menu=True,
        notebook=False,
    )

    print("Construindo visualização...")

    for node, data in G.nodes(data=True):
        node_type = data.get("type", "Desconhecido")

        if node_type == "Prato":
            restaurant_name = data.get("restaurant", "")
            if restaurant_name == "Camarões":
                color = "#e63946"  # Vermelho/Coral para Camarões
            elif restaurant_name == "Bambu":
                color = "#2a9d8f"  # Verde Menta/Esmeralda para Bambu
            else:
                color = "#00b4d8"  # Azul se for desconhecido
            size = 20
            shape = "dot"
        elif node_type == "Ingrediente":
            color = "#ffb703"  # Amarelo escuro
            size = 10
            shape = "triangle"
        else:
            color = "#9e9e9e"  # Cinza
            size = 15
            shape = "box"

        title_hover = f"Nome: {node}\nTipo: {node_type}"
        if node_type == "Prato" and "restaurant" in data:
            title_hover += f"\nRestaurante: {data['restaurant']}"
        if "category" in data and data["category"]:
            title_hover += f"\nCategoria: {data['category']}"

        net.add_node(node, label=node, title=title_hover, color=color, size=size, shape=shape)

    # Processa as arestas
    for source, target, data in G.edges(data=True):
        relation = data.get("relation", "")
        # Arestas mais escuras/opacas para não poluir
        net.add_edge(source, target, title=relation, color="rgba(150, 150, 150, 0.4)")

    # Opções de simulação física otimizadas para melhor distribuição
    net.set_options("""
    var options = {
      "physics": {
        "forceAtlas2Based": {
            "gravitationalConstant": -70,
            "centralGravity": 0.015,
            "springLength": 100,
            "springConstant": 0.08
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {"iterations": 150}
      },
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": true
      }
    }
    """)

    print(f"Gerando arquivo HTML: {output_filename}...")
    net.write_html(output_filename)
    print(
        f"Sucesso! Para visualizar abra o arquivo '{output_filename}' no seu navegador de preferência."
    )


if __name__ == "__main__":
    visualize_graph_with_pyvis("restaurant_graph.gexf")
