# visualize_interactive.py
import networkx as nx
from pyvis.network import Network
import os


def generate_interactive_graph(file_path):
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo {file_path} não encontrado.")
        return

    print("Carregando grafo...")
    G = nx.read_gexf(file_path)

    # Inicializa a rede do Pyvis com notebook=False
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#222222",
        font_color="white",
        select_menu=True,
        filter_menu=True,
        notebook=False,
    )

    print("Processando nós e cores...")
    for node, data in G.nodes(data=True):
        label = node
        color = "#12dcfc" if data.get("type") == "Prato" else "#ff9900"
        size = 25 if data.get("type") == "Prato" else 10
        title = f"{data.get('type')}: {node}\nCategoria: {data.get('category', 'N/A')}"
        net.add_node(node, label=label, title=title, color=color, size=size)

    print("Adicionando conexões...")
    for source, target, data in G.edges(data=True):
        net.add_edge(source, target, title=data.get("relation", "CONTÉM"), color="gray")

    # Opções de física
    net.set_options("""
    var options = {
      "physics": {
        "forceAtlas2Based": {"gravitationalConstant": -50, "centralGravity": 0.01, "springLength": 100, "springConstant": 0.08},
        "maxVelocity": 50, "solver": "forceAtlas2Based", "timestep": 0.35, "stabilization": {"iterations": 150}
      }
    }
    """)

    output_html = "grafo_interativo.html"

    # Trocando show() por write_html() para evitar erros de renderização
    print(f"Gerando arquivo {output_html}...")
    net.write_html(output_html)
    print(f"Sucesso! Abra o arquivo '{output_html}' no seu navegador.")


if __name__ == "__main__":
    generate_interactive_graph("restaurant_graph.gexf")
