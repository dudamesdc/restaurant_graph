# Análise comparativa: Coco Bambu vs Restaurante Camarões

Documento gerado a partir das métricas em `outputs/analysis/metrics.txt` e das
figuras em `outputs/analysis/`. Todas as métricas foram computadas sobre a
visão *simples* e *não-direcionada* do `MultiDiGraph` original (arestas
paralelas colapsadas), que é a convenção natural para clustering,
caminho médio e diâmetro.

## 1. Panorama

| Métrica            | Geral | Coco Bambu | Camarões |
|--------------------|------:|-----------:|---------:|
| Nós                |   632 |        545 |      136 |
| Pratos             |   560 |        478 |       82 |
| Ingredientes       |    72 |         67 |       54 |
| Arestas            | 1 884 |      1 418 |      865 |
| Densidade          | 0.009 |      0.010 |  **0.094** |
| Grau médio         |  5.96 |       5.20 |  **12.72** |
| Componentes        |   258 |        249 |       10 |
| Maior componente   |   375 |        297 |      127 |
| Diâmetro (LCC)     |     7 |          7 |        5 |
| Caminho médio (LCC)|  2.60 |       2.62 |     2.17 |
| Clustering médio   | 0.267 |      0.231 |  **0.498** |
| Transitividade     | 0.183 |      0.212 |    0.357 |

> As subredes por restaurante contêm os pratos daquele restaurante **mais**
> todos os ingredientes citados nesses pratos; por isso, ingredientes
> compartilhados aparecem nas duas subredes (e a soma dos nós é maior que
> o total geral).

## 2. Tamanho ≠ densidade

Coco Bambu tem quase **6× mais pratos** que Camarões (478 contra 82), mas
sua rede é **~10× menos densa** (0.010 vs 0.094). Isso diz algo concreto
sobre a estratégia de cada restaurante:

- **Coco Bambu** opera como um cardápio-catálogo: muitas categorias,
  ingredientes espalhados, poucos pratos reutilizando o mesmo conjunto.
  Por isso o grau médio cai para ~5 e a densidade é pequena.
- **Camarões** concentra-se num núcleo estreito: ~80 pratos orbitando um
  vocabulário pequeno de ingredientes recorrentes (camarão, molho, arroz,
  queijo). A densidade de 0.094 é alta para uma rede desse porte.

A bipartição Prato ↔ Ingrediente também explica o número de componentes:
pratos sem nenhum ingrediente reconhecido pelo NER viram componentes
isolados. Camarões, com apenas 10 componentes, tem cobertura de NER muito
superior — reflexo direto de descrições de prato mais objetivas.

## 3. Clustering alto, caminhos curtos — assinatura *small-world*

Clustering médio mede a probabilidade de que dois vizinhos de um mesmo
nó também sejam vizinhos entre si. Numa rede bipartida pura esse valor
seria zero, então o que medimos captura triângulos criados via
ingredientes compartilhados entre pratos.

- **Camarões**: clustering **0.50**, caminho médio **2.17**, diâmetro 5.
  Uma assinatura clássica de mundo-pequeno: qualquer prato alcança
  qualquer outro em ~2 passos via ingredientes comuns.
- **Coco Bambu**: clustering **0.23**, caminho médio **2.62**, diâmetro
  7. Ainda é pequeno em termos absolutos, mas o cardápio é amplo o
  suficiente para diluir a densidade local.

A transitividade (triângulos globais) repete o padrão — 0.36 em Camarões
contra 0.21 em Bambu — reforçando que a especialização de Camarões
fabrica muito mais triplas fechadas do que o cardápio genérico do Bambu.

## 4. Sobreposição de ingredientes — Jaccard = 0.681

| Conjunto           | Tamanho |
|--------------------|--------:|
| Compartilhados     |      49 |
| Só no Coco Bambu   |      18 |
| Só no Camarões     |       5 |

- **49 ingredientes em comum** dominam a interseção — a base clássica
  brasileira: arroz, camarão, cebola, alho, tomate, queijo, molho,
  azeite, parmesão, bacon, manteiga, limão, pimenta etc.
- **Só Bambu (18)**: `abóbora, bacalhau, berinjela, cheiro-verde,
  cordeiro, creme de leite, cuscuz, espaguete, farinha, maminha,
  mandioca, muçarela, ovo(s), porco, rúcula, óleo`. Revelam um cardápio
  ecumênico: italianas, carnes nobres, massas, regionais.
- **Só Camarões (5)**: `gorgonzola, jerimum, milho, orégano,
  provolone`. Uma lista muito curta — coerente com a especialização
  num único eixo temático.

Jaccard de **0.681** é alto: ~68% do vocabulário *combinado* aparece
nos dois restaurantes. Isso coloca uma pergunta natural — *se eles
compartilham tanto ingrediente, o que os diferencia?* A resposta
estrutural está na **frequência de uso**, não no vocabulário.

## 5. Hubs: quem puxa a rede

| Posição | Geral       | Coco Bambu  | Camarões     |
|--------:|-------------|-------------|--------------|
|       1 | molho (141) | molho (108) | **camarão (80)** |
|       2 | arroz (133) | arroz (106) | molho (65)   |
|       3 | camarão (98)| cebola (81) | arroz (62)   |
|       4 | cebola (98) | filé (75)   | tomate (54)  |
|       5 | tomate (96) | tomate (74) | queijo (51)  |

Três observações:

1. **Camarão é o hub único de Camarões** (grau 80 em 82 pratos):
   praticamente todo prato do cardápio passa por ele. É um grafo em
   forma de estrela temperada.
2. **Molho e arroz lideram os dois**: são os ingredientes-ponte que
   conectam tudo — seriam os primeiros candidatos a remover num
   experimento de robustez.
3. Fora o camarão, o Camarões ainda destaca **queijo e parmesão** no
   top-10, indicando uma linha forte de pratos gratinados — algo que
   o Bambu cobre de forma mais fragmentada.

## 6. Conclusões

- **Mesmo vocabulário, gramáticas diferentes.** Com 68% de Jaccard,
  os dois cardápios não se distinguem pelo *que* usam, mas por *como*
  combinam o que usam.
- **Camarões é uma rede especialista.** Densidade ~10× maior,
  clustering 2× maior, diâmetro menor: uma identidade temática que
  aparece diretamente na topologia.
- **Coco Bambu é uma rede generalista.** Maior em número absoluto,
  porém mais esparsa e com pratos menos interconectados via
  ingredientes comuns — exatamente o que se espera de um cardápio
  amplo que cobre muitas cozinhas.
- **Mundo-pequeno é real aqui.** Clustering alto + caminho médio
  curto (~2.2–2.6) mostram que ingredientes populares funcionam como
  atalhos entre pratos aparentemente distantes.
- **NER tem limites visíveis.** O grande número de componentes
  isolados (258 no geral) indica pratos cujas descrições não
  ancoraram em nenhum ingrediente do dicionário. Expandir a
  taxonomia de ingredientes é a próxima alavanca para subir cobertura
  sem mudar a arquitetura.

## 7. Figuras de apoio

- `outputs/graph_static.png` — visão global do grafo colorida por
  restaurante (pratos) e por categoria (ingredientes).
- `outputs/graph_interactive.html` — mesma rede em pyvis, navegável.
- `outputs/analysis/degree_distribution.png` — distribuição de grau
  em log-log (cauda pesada típica de redes reais).
- `outputs/analysis/ingredient_comparison.png` — barras
  comparando ingredientes únicos vs compartilhados.
- `outputs/analysis/shared_ingredients_network.png` — top-12
  ingredientes compartilhados e os pratos que eles conectam, colorido
  por restaurante para destacar a travessia Bambu ↔ Camarões.
