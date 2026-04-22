from __future__ import annotations

import html
import logging
from dataclasses import dataclass
from pathlib import Path

from graph.analysis import ComparativeReport, GraphMetrics, RandomBaseline

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DashboardAssets:
    """Filenames of the artefacts embedded in the dashboard (relative to it)."""

    static_png: str
    interactive_full: str
    interactive_lcc: str
    interactive_scaled: str
    degree_plot: str
    ingredient_plot: str
    shared_plot: str
    random_plot: str


def render_dashboard(
    report: ComparativeReport,
    assets: DashboardAssets,
    output_file: Path,
) -> None:
    """Write a single self-contained HTML page that stitches all artefacts together."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(_build_html(report, assets), encoding="utf-8")
    logger.info("wrote dashboard to %s", output_file)


_JS = """
function setView(view, url) {
  document.getElementById('graph-frame').src = url;
  document.getElementById('external-link').href = url;
  const btns = document.querySelectorAll('.view-selector .btn');
  btns.forEach(b => b.classList.remove('active'));
  event.currentTarget.classList.add('active');
}
"""


def _build_html(report: ComparativeReport, assets: DashboardAssets) -> str:
    return f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>Rede de pratos e ingredientes — Bambu vs Camarões</title>
<style>{_CSS}</style>
</head>
<body>
<header>
  <h1>Rede de pratos e ingredientes</h1>
  <p class="subtitle">
    Coco Bambu vs Restaurante Camarões — extração por NER sobre descrições de cardápio,
    análise estrutural com NetworkX.
  </p>
</header>

<main>
  <section>
    <h2>1. Métricas estruturais</h2>
    {_metrics_table([report.whole, report.bambu, report.camaroes])}
  </section>

  <section>
    <h2>2. Explorador de Rede Interativo</h2>
    <div class="explorer-container">
      <div class="explorer-header">
        <div class="view-selector">
          <button class="btn active" onclick="setView('full', '{assets.interactive_full}')" title="Grafo completo original">Completo</button>
          <button class="btn" onclick="setView('lcc', '{assets.interactive_lcc}')" title="Apenas a maior componente conectada">Componente Gigante</button>
          <button class="btn" onclick="setView('scaled', '{assets.interactive_scaled}')" title="Tamanho do ingrediente por número de conexões">Influência (Grau)</button>
        </div>
        <a id="external-link" href="{assets.interactive_full}" target="_blank" class="external-btn">
          <span>&#8599;</span> Tela Cheia
        </a>
      </div>
      <div class="iframe-wrapper">
        <iframe id="graph-frame" src="{assets.interactive_full}"></iframe>
      </div>
    </div>
    <p class="note">
      Utilize o scroll para zoom, arraste para navegar. Clique em um nó para destacar conexões.
    </p>
    <script>
      {_JS}
    </script>
  </section>

  <section>
    <h2>3. Distribuição de grau</h2>
    <figure>
      <img src="{assets.degree_plot}" alt="Distribuição de grau em log-log">
      <figcaption>
        Em log-log a cauda pesada típica de redes reais fica evidente — poucos
        ingredientes concentram a maior parte das arestas.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2>4. Sobreposição de ingredientes</h2>
    <div class="two-col">
      <figure>
        <img src="{assets.ingredient_plot}" alt="Comparação de ingredientes">
      </figure>
      <div>
        <p><strong>Jaccard:</strong> {report.jaccard:.3f}</p>
        <p><strong>Compartilhados ({len(report.shared_ingredients)}):</strong></p>
        <p class="tags">{_tags(report.shared_ingredients)}</p>
        <p><strong>Só no Bambu ({len(report.only_bambu)}):</strong></p>
        <p class="tags tags-bambu">{_tags(report.only_bambu)}</p>
        <p><strong>Só no Camarões ({len(report.only_camaroes)}):</strong></p>
        <p class="tags tags-camaroes">{_tags(report.only_camaroes)}</p>
      </div>
    </div>
  </section>

  <section>
    <h2>5. Ingredientes compartilhados de maior grau</h2>
    <figure>
      <img src="{assets.shared_plot}" alt="Rede de ingredientes compartilhados">
      <figcaption>
        Os 12 ingredientes mais conectados que aparecem nos dois restaurantes e
        os pratos que eles ligam — mostra a travessia Bambu ↔ Camarões.
      </figcaption>
    </figure>
  </section>

  <section>
    <h2>6. Comparação com grafos aleatórios</h2>
    <div class="two-col">
      <figure>
        <img src="{assets.random_plot}" alt="Rede real vs ER vs WS">
      </figure>
      <div>
        {_random_table(report.random_baselines)}
        <p class="note">
          Clustering muito acima do ER confirma que a estrutura é real, não
          aleatória. Caminho médio comparável (ou menor) a ambos os modelos é
          sinal de presença de hubs e comportamento <em>scale-free</em>.
        </p>
      </div>
    </div>
  </section>

  <section>
    <h2>7. Centralidades (top 10, LCC)</h2>
    {_centrality_tables(report.whole)}
    <p class="note">
      Calculadas sobre a maior componente conectada. <strong>Betweenness</strong>
      identifica ingredientes-ponte; <strong>eigenvector</strong> e
      <strong>PageRank</strong> destacam ingredientes-núcleo.
    </p>
  </section>
</main>

<footer>
  <p>Gerado automaticamente a partir de <code>main.py</code>.</p>
</footer>
</body>
</html>
"""


def _metrics_table(metrics: list[GraphMetrics]) -> str:
    header = "".join(f"<th>{html.escape(m.label)}</th>" for m in metrics)
    rows: list[tuple[str, list[str]]] = [
        ("Nós", [str(m.nodes) for m in metrics]),
        ("Pratos", [str(m.dishes) for m in metrics]),
        ("Ingredientes", [str(m.ingredients) for m in metrics]),
        ("Arestas", [str(m.edges) for m in metrics]),
        ("Densidade", [f"{m.density:.4f}" for m in metrics]),
        ("Grau médio", [f"{m.avg_degree:.3f}" for m in metrics]),
        ("Componentes", [str(m.components) for m in metrics]),
        ("Maior componente", [str(m.largest_component_size) for m in metrics]),
        ("Diâmetro (LCC)", [_fmt_opt(m.diameter_lcc) for m in metrics]),
        ("Caminho médio (LCC)", [_fmt_opt_f(m.avg_shortest_path_lcc) for m in metrics]),
        ("Clustering médio", [f"{m.avg_clustering:.4f}" for m in metrics]),
        ("Transitividade", [f"{m.transitivity:.4f}" for m in metrics]),
    ]
    body = "".join(
        "<tr><th>" + label + "</th>" + "".join(f"<td>{v}</td>" for v in values) + "</tr>"
        for label, values in rows
    )
    return f"<table><thead><tr><th></th>{header}</tr></thead><tbody>{body}</tbody></table>"


def _centrality_tables(m: GraphMetrics) -> str:
    blocks = [
        ("Grau", [(name, str(int(value))) for name, value in m.top_degree]),
        ("Betweenness", [(n, f"{v:.3f}") for n, v in m.top_betweenness]),
        ("Closeness", [(n, f"{v:.3f}") for n, v in m.top_closeness]),
        ("Eigenvector", [(n, f"{v:.3f}") for n, v in m.top_eigenvector]),
        ("PageRank", [(n, f"{v:.3f}") for n, v in m.top_pagerank]),
    ]
    cards = "".join(_centrality_card(title, pairs) for title, pairs in blocks)
    return f'<div class="centrality-grid">{cards}</div>'


def _centrality_card(title: str, pairs: list[tuple[str, str]]) -> str:
    rows = "".join(
        f"<tr><td>{html.escape(name)}</td><td>{value}</td></tr>" for name, value in pairs
    )
    return (
        f'<div class="card"><h3>{html.escape(title)}</h3><table><tbody>{rows}</tbody></table></div>'
    )


def _random_table(baselines: list[RandomBaseline]) -> str:
    rows = "".join(
        "<tr><td>"
        + html.escape(b.name)
        + f"</td><td>{b.clustering:.4f}</td><td>{_fmt_opt_f(b.avg_path)}</td>"
        + f"<td>{html.escape(b.params)}</td></tr>"
        for b in baselines
    )
    return (
        "<table><thead><tr>"
        "<th>Modelo</th><th>Clustering</th><th>Caminho médio</th><th>Parâmetros</th>"
        f"</tr></thead><tbody>{rows}</tbody></table>"
    )


def _tags(items: list[str]) -> str:
    return " ".join(f"<span class='tag'>{html.escape(i)}</span>" for i in items)


def _fmt_opt(value: int | None) -> str:
    return "n/d" if value is None else str(value)


def _fmt_opt_f(value: float | None) -> str:
    return "n/d" if value is None else f"{value:.3f}"


_CSS = """
:root { --fg: #1e1e1e; --muted: #6b6b6b; --bg: #fafafa; --card: #ffffff;
        --line: #e0e0e0; --bambu: #2a9d8f; --camaroes: #e63946; --accent: #264653; }
* { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
       color: var(--fg); background: var(--bg); line-height: 1.55; }
header { padding: 2.5rem 2rem 1.5rem; border-bottom: 1px solid var(--line);
         background: var(--card); }
header h1 { margin: 0 0 0.4rem; font-size: 1.8rem; }
header .subtitle { margin: 0; color: var(--muted); max-width: 60ch; }
main { max-width: 1100px; margin: 0 auto; padding: 1.5rem 2rem 3rem; }
section { margin: 2.5rem 0; }
section h2 { border-bottom: 2px solid var(--accent); padding-bottom: 0.3rem;
             font-size: 1.3rem; margin-bottom: 1rem; }
figure { margin: 0 0 1rem; }
figure img { max-width: 100%; height: auto; border: 1px solid var(--line); background: white; }
figcaption { color: var(--muted); font-size: 0.9rem; margin-top: 0.4rem; }
table { border-collapse: collapse; width: 100%; background: var(--card);
        font-size: 0.95rem; }
th, td { text-align: left; padding: 0.4rem 0.7rem; border-bottom: 1px solid var(--line); }
thead th { background: var(--accent); color: white; }
tbody th { width: 40%; font-weight: 500; color: var(--muted); }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start; }
.note { color: var(--muted); font-size: 0.92rem; }
.tags { display: flex; flex-wrap: wrap; gap: 0.3rem; }
.tag { background: #eaeaea; padding: 0.15rem 0.5rem; border-radius: 3px; font-size: 0.85rem; }
.tags-bambu .tag { background: #d4ede9; }
.tags-camaroes .tag { background: #fbd8dc; }
.centrality-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
                   gap: 1rem; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 4px;
        padding: 0.8rem 1rem; }
.card h3 { margin: 0 0 0.5rem; font-size: 1rem; color: var(--accent); }
.card table { font-size: 0.85rem; }

/* Explorador */
.explorer-container { background: var(--card); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; margin-bottom: 1rem; }
.explorer-header { display: flex; justify-content: space-between; align-items: center; padding: 0.8rem 1rem; background: #f1f1f1; border-bottom: 1px solid var(--line); }
.view-selector { display: flex; gap: 0.5rem; }
.btn { padding: 0.4rem 0.8rem; border: 1px solid var(--line); background: white; border-radius: 4px; cursor: pointer; font-size: 0.85rem; transition: all 0.2s; }
.btn:hover { background: #eee; }
.btn.active { background: var(--accent); color: white; border-color: var(--accent); }
.external-btn { text-decoration: none; font-size: 0.85rem; color: var(--accent); font-weight: 500; }
.iframe-wrapper { position: relative; width: 100%; height: 650px; background: #1a1a1a; }
#graph-frame { width: 100%; height: 100%; border: none; }
footer { border-top: 1px solid var(--line); background: var(--card);
         padding: 1rem 2rem; color: var(--muted); font-size: 0.85rem; text-align: center; }
@media (max-width: 700px) { .two-col { grid-template-columns: 1fr; } }
"""
