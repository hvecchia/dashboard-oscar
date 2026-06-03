# 🏆 Oscar Awards Dashboard

Dashboard interativo com 97 anos de história do Oscar — 11.110 indicações, 8 gráficos e um insight que surpreende.

**[Acessar o Dashboard](https://dashboard-oscar-hailton.streamlit.app/) · [Ver a Landing Page](https://hailton-vecchia.netlify.app/oscar)**

---

## Sobre o projeto

Explora as duas bases de dados oficiais da Academia de Artes e Ciências Cinematográficas (1927–2024), cruzando indicações, categorias, classes e vencedores em visualizações interativas filtráveis por período e categoria.

## Funcionalidades

- **6 KPIs dinâmicos** — indicações, prêmios, taxa de vitória, filmes, profissionais e cerimônias
- **Série temporal** — indicações e premiados por ano (1927–2024)
- **Taxa de vitória por década** — comparativo entre décadas
- **Top 15 categorias** — barras sobrepostas indicações × prêmios
- **Distribuição por classe** — donut chart com 8 classes (Acting, Directing, Production…)
- **Top 10 filmes mais premiados** e **top 10 profissionais mais premiados**
- **Os mais azarados** — filmes com mais indicações e zero prêmios
- **Filtros interativos** — slider de período e seletor de classe na sidebar
- **Insight surpresa** — calculado dinamicamente a cada execução

## Tecnologias

| Ferramenta | Uso |
|---|---|
| Python 3 | Linguagem base |
| Streamlit | Framework do dashboard |
| Pandas | Leitura e manipulação dos CSVs |
| Plotly | Gráficos interativos |

## Estrutura

```
Dashboard_Oscar/
├── dashboard.py          # App principal
├── requirements.txt      # Dependências
├── landing.html          # Landing page do projeto
├── index.html            # Redireciona para landing.html
├── .streamlit/
│   └── config.toml       # Tema dark com paleta dourada
└── data/
    ├── the_oscar_award.csv   # 11.110 indicações (1927–2024)
    └── full_data.csv         # Base completa com metadados
```

## Como rodar localmente

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

## Insights descobertos

- **Thomas Newman** é o profissional mais indicado sem nunca vencer: 14 indicações como compositor, zero prêmios
- **69,5%** de todos os indicados ao longo da história jamais ganharam um Oscar
- **The Color Purple** (1986) recebeu 12 indicações e não venceu nenhuma — maior "virada" da história
- **Ben-Hur**, **Titanic** e **LOTR: The Return of the King** dividem o recorde de 11 Oscars em uma única cerimônia

---

Desenvolvido com [Claude Code](https://claude.ai/code) · Dados: Academy of Motion Picture Arts and Sciences
