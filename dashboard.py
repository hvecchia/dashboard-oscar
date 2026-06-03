import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Oscar Awards Dashboard", page_icon="🏆", layout="wide")

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"]        { font-family: 'Inter', sans-serif !important; }
.stApp                            { background-color: #0a0a0a; }
section.main .block-container     { padding-top: 1.4rem; }

/* Hero */
.hero {
    background: linear-gradient(105deg, #0f0f0f 0%, #1c1200 55%, #0f0f0f 100%);
    border-left: 5px solid #D4AF37;
    padding: 22px 28px 18px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.hero h1 { color: #D4AF37; margin: 0 0 5px; font-size: 1.9rem; font-weight: 800; letter-spacing: -0.02em; }
.hero p  { color: #777; margin: 0; font-size: 0.88rem; }

/* KPI cards */
[data-testid="metric-container"] {
    background: #101010 !important;
    border: 1px solid #1e1e1e !important;
    border-top: 3px solid #D4AF37 !important;
    border-radius: 10px;
    padding: 14px 16px !important;
}
[data-testid="stMetricLabel"] > div {
    color: #666 !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.09em;
}
[data-testid="stMetricValue"] {
    color: #D4AF37 !important;
    font-weight: 700 !important;
    font-size: 1.65rem !important;
}
[data-testid="stMetricDelta"] svg   { display: none !important; }
[data-testid="stMetricDelta"] > div { font-size: 0.72rem !important; color: #555 !important; }

/* Section headers */
h3 {
    color: #ccc !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border-bottom: 1px solid #1e1e1e;
    padding-bottom: 7px;
    margin-top: 6px !important;
}

/* Insight card */
.insight-card {
    background: linear-gradient(115deg, #100e08, #1c1600);
    border: 1px solid #2e2500;
    border-left: 5px solid #D4AF37;
    border-radius: 10px;
    padding: 22px 26px;
    margin: 10px 0 18px;
}
.insight-card .tag  {
    color: #D4AF37;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 700;
    margin-bottom: 10px;
}
.insight-card h4    { color: #eee; font-size: 1.1rem; font-weight: 700; margin: 0 0 10px; }
.insight-card p     { color: #999; font-size: 0.88rem; line-height: 1.7; margin: 0; }
.insight-card .hl   { color: #D4AF37; font-weight: 700; }

/* Divider */
hr { border-color: #1a1a1a !important; margin: 10px 0 !important; }

/* Sidebar */
[data-testid="stSidebar"]   { background: #080808 !important; border-right: 1px solid #181818 !important; }
[data-testid="stSidebar"] * { color: #aaa !important; }
[data-testid="stSidebar"] .stSelectbox  label { font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.07em; color: #555 !important; }
[data-testid="stSidebar"] .stSlider     label { font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.07em; color: #555 !important; }

/* Expander */
[data-testid="stExpander"] { background: #0c0c0c; border: 1px solid #1e1e1e; border-radius: 8px; }

/* Footer */
.footer { text-align: center; color: #333; font-size: 0.72rem; padding: 20px 0 8px; }
</style>
""", unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def fmt(n) -> str:
    """Integer with period as thousands separator (PT-BR style)."""
    return f"{int(n):,}".replace(",", ".")

def fmt_pct(n: float) -> str:
    """Percentage with comma as decimal separator (PT-BR style)."""
    return f"{n:.1f}".replace(".", ",") + "%"

GOLD   = "#D4AF37"
SILVER = "#A8A9AD"
RED    = "#C0392B"

CHART_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#888888", family="Inter, sans-serif", size=11),
    margin=dict(t=18, b=0, l=0, r=12),
)
AXIS = dict(gridcolor="#191919", linecolor="#252525", zerolinecolor="#252525", tickcolor="#333")

DATA_DIR = Path(__file__).parent / "data"

# ─── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    oscar = pd.read_csv(DATA_DIR / "the_oscar_award.csv")
    oscar["winner"] = oscar["winner"].astype(str).str.strip().str.lower() == "true"
    full = pd.read_csv(DATA_DIR / "full_data.csv", sep="\t", encoding="utf-8-sig")
    full["Winner"] = full["Winner"].astype(str).str.strip().str.lower() == "true"
    return oscar, full

oscar, full = load_data()

# ─── Pre-compute surprise insight (always from full dataset) ──────────────────
@st.cache_data
def compute_insight(oscar_df):
    stats = (
        oscar_df.groupby("name")
        .agg(indicações=("winner", "count"), vitórias=("winner", "sum"))
        .reset_index()
    )
    never_won   = stats[stats["vitórias"] == 0].sort_values("indicações", ascending=False)
    snub        = never_won.iloc[0]
    snub_name   = snub["name"]
    snub_noms   = int(snub["indicações"])
    rows        = oscar_df[oscar_df["name"] == snub_name]
    snub_films  = rows["film"].unique()
    films_str   = ", ".join(snub_films[:3]) + ("…" if len(snub_films) > 3 else "")
    year_span   = f"{int(rows['year_film'].min())}–{int(rows['year_film'].max())}"
    pct_never   = len(never_won) / len(stats) * 100
    return snub_name, snub_noms, films_str, year_span, pct_never

snub_name, snub_noms, snub_films_str, snub_year_span, pct_never_won = compute_insight(oscar)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='padding:10px 0 4px;font-size:1.1rem;font-weight:700;color:#D4AF37'>🏆 Oscar Dashboard</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:6px 0 14px'>", unsafe_allow_html=True)

    year_min = int(oscar["year_film"].min())
    year_max = int(oscar["year_film"].max())
    year_range = st.slider("Período", year_min, year_max, (year_min, year_max))

    classes        = ["Todos"] + sorted(full["Class"].dropna().unique().tolist())
    selected_class = st.selectbox("Classe", classes)

    st.markdown(
        f"<div style='margin-top:20px;font-size:0.72rem;color:#333;line-height:1.7'>"
        f"Base completa: {fmt(len(oscar))} registros<br>"
        f"Cobertura: {year_min}–{year_max}</div>",
        unsafe_allow_html=True,
    )

# ─── Apply filters ────────────────────────────────────────────────────────────
df = oscar[
    (oscar["year_film"] >= year_range[0]) & (oscar["year_film"] <= year_range[1])
].copy()
df_full = full.copy()

if selected_class != "Todos":
    df_full = df_full[df_full["Class"] == selected_class]
    df      = df[df["canon_category"].isin(df_full["CanonicalCategory"].unique())]

# ─── Hero header ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <h1>🏆 Oscar Awards — Dashboard Histórico</h1>
  <p>Academy of Motion Picture Arts and Sciences &nbsp;·&nbsp;
     {year_range[0]}–{year_range[1]} &nbsp;·&nbsp; Classe: <strong style="color:#D4AF37">{selected_class}</strong></p>
</div>
""", unsafe_allow_html=True)

# ─── KPIs ─────────────────────────────────────────────────────────────────────
total_noms   = len(df)
total_wins   = int(df["winner"].sum())
win_rate     = total_wins / total_noms * 100 if total_noms else 0
total_films  = df["film"].nunique()
films_won    = df[df["winner"]]["film"].nunique()
total_people = df["name"].nunique()
total_ceres  = df["ceremony"].nunique()
ratio_str    = f"1 em cada {round(total_noms / total_wins)} indicações" if total_wins else "—"

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Indicações",      fmt(total_noms),   f"{fmt(total_ceres)} cerimônias",  delta_color="off")
k2.metric("Prêmios Dados",   fmt(total_wins),   f"de {fmt(total_noms)} indicados", delta_color="off")
k3.metric("Taxa de Vitória", fmt_pct(win_rate), ratio_str,                         delta_color="off")
k4.metric("Filmes",          fmt(total_films),  f"{fmt(films_won)} premiados",     delta_color="off")
k5.metric("Profissionais",   fmt(total_people), "pessoas únicas",                  delta_color="off")
k6.metric("Cerimônias",      fmt(total_ceres),  f"{year_range[0]}–{year_range[1]}", delta_color="off")

st.divider()

# ─── Row 1: Timeline  |  Win rate by decade ───────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Indicações e Prêmios por Ano")
    by_year = (
        df.groupby("year_film")
        .agg(Indicações=("winner", "count"), Premiados=("winner", "sum"))
        .reset_index()
    )
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=by_year["year_film"], y=by_year["Indicações"],
        name="Indicações",
        line=dict(color=SILVER, width=1.5),
        fill="tozeroy", fillcolor="rgba(168,169,173,0.05)",
    ))
    fig_line.add_trace(go.Scatter(
        x=by_year["year_film"], y=by_year["Premiados"],
        name="Premiados",
        line=dict(color=GOLD, width=2.5),
        fill="tozeroy", fillcolor="rgba(212,175,55,0.07)",
    ))
    fig_line.update_layout(
        **CHART_BASE,
        xaxis=dict(**AXIS, title=""),
        yaxis=dict(**AXIS, title=""),
        legend=dict(orientation="h", y=1.1, x=0, bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    st.subheader("Taxa de Vitória por Década")
    df_dec = df.copy()
    df_dec["decade"] = (df_dec["year_film"] // 10 * 10).astype(str) + "s"
    by_decade = (
        df_dec.groupby("decade")
        .agg(total=("winner", "count"), wins=("winner", "sum"))
        .assign(win_rate=lambda x: (x["wins"] / x["total"] * 100).round(1))
        .reset_index()
    )
    by_decade["label"] = by_decade["win_rate"].apply(fmt_pct)
    fig_dec = px.bar(
        by_decade, x="decade", y="win_rate", text="label",
        color="win_rate",
        color_continuous_scale=[[0, "#1e1000"], [0.5, "#7a4f00"], [1, GOLD]],
        labels={"decade": "", "win_rate": ""},
    )
    fig_dec.update_traces(textposition="outside", textfont=dict(color="#888", size=10))
    fig_dec.update_layout(
        **CHART_BASE,
        xaxis=dict(**AXIS),
        yaxis=dict(**AXIS, title=""),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_dec, use_container_width=True)

# ─── Row 2: Top categories  |  Class donut ────────────────────────────────────
col3, col4 = st.columns([3, 2])

with col3:
    st.subheader("Top 15 Categorias por Indicações")
    top_cats = (
        df.groupby("canon_category")
        .agg(Indicações=("winner", "count"), Premiados=("winner", "sum"))
        .sort_values("Indicações", ascending=False)
        .head(15)
        .sort_values("Indicações")
        .reset_index()
    )
    fig_cats = go.Figure()
    fig_cats.add_trace(go.Bar(
        y=top_cats["canon_category"], x=top_cats["Indicações"],
        name="Indicações", orientation="h",
        marker=dict(color=SILVER, opacity=0.25),
    ))
    fig_cats.add_trace(go.Bar(
        y=top_cats["canon_category"], x=top_cats["Premiados"],
        name="Premiados", orientation="h",
        marker=dict(color=GOLD),
    ))
    fig_cats.update_layout(
        **CHART_BASE,
        barmode="overlay",
        xaxis=dict(**AXIS, title=""),
        yaxis=dict(**AXIS, title="", tickfont=dict(size=10)),
        legend=dict(orientation="h", y=1.06, x=0, bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_cats, use_container_width=True)

with col4:
    st.subheader("Distribuição por Classe")
    class_counts = (
        df_full.groupby("Class")
        .agg(Indicações=("Winner", "count"))
        .sort_values("Indicações", ascending=False)
        .reset_index()
    )
    pie_colors = [GOLD, SILVER, "#C0873A", "#8a8a8a", "#E8C85A", "#b89c50", "#7a7a7a", "#5a5a5a"]
    fig_pie = go.Figure(go.Pie(
        labels=class_counts["Class"],
        values=class_counts["Indicações"],
        hole=0.52,
        marker=dict(
            colors=pie_colors[:len(class_counts)],
            line=dict(color="#0a0a0a", width=2),
        ),
        textinfo="label+percent",
        textfont=dict(size=10),
        insidetextorientation="radial",
    ))
    fig_pie.update_layout(
        **CHART_BASE,
        showlegend=False,
        annotations=[dict(
            text="Classe", x=0.5, y=0.5,
            font=dict(size=11, color="#555"),
            showarrow=False,
        )],
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ─── Row 3: Top films  |  Top people ─────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("Top 10 Filmes Mais Premiados")
    top_films = (
        df[df["winner"]].groupby("film").size()
        .sort_values(ascending=False).head(10)
        .reset_index(name="Prêmios")
        .sort_values("Prêmios")
    )
    top_films["label"] = top_films["Prêmios"].apply(fmt)
    fig_films = px.bar(
        top_films, x="Prêmios", y="film", orientation="h", text="label",
        color="Prêmios",
        color_continuous_scale=[[0, "#1a1000"], [1, GOLD]],
        labels={"film": ""},
    )
    fig_films.update_traces(textposition="outside", textfont=dict(color="#888", size=11))
    fig_films.update_layout(
        **CHART_BASE,
        xaxis=dict(**AXIS, title=""),
        yaxis=dict(**AXIS, title="", tickfont=dict(size=10)),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_films, use_container_width=True)

with col6:
    st.subheader("Top 10 Profissionais Mais Premiados")
    top_people = (
        df[df["winner"]].groupby("name").size()
        .sort_values(ascending=False).head(10)
        .reset_index(name="Prêmios")
        .sort_values("Prêmios")
    )
    top_people["label"] = top_people["Prêmios"].apply(fmt)
    fig_ppl = px.bar(
        top_people, x="Prêmios", y="name", orientation="h", text="label",
        color="Prêmios",
        color_continuous_scale=[[0, "#180a00"], [1, "#E8820C"]],
        labels={"name": ""},
    )
    fig_ppl.update_traces(textposition="outside", textfont=dict(color="#888", size=11))
    fig_ppl.update_layout(
        **CHART_BASE,
        xaxis=dict(**AXIS, title=""),
        yaxis=dict(**AXIS, title="", tickfont=dict(size=10)),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_ppl, use_container_width=True)

# ─── Row 4: Snubbed films ──────────────────────────────────────────────────────
st.subheader("Os Mais Azarados — Filmes Indicados Sem Nenhum Prêmio")
snubbed = (
    df.groupby("film")
    .agg(Indicações=("winner", "count"), Prêmios=("winner", "sum"))
    .query("Prêmios == 0")
    .sort_values("Indicações", ascending=False)
    .head(10)
    .reset_index()
)
snubbed["label"] = snubbed["Indicações"].apply(fmt)
fig_snub = px.bar(
    snubbed, x="film", y="Indicações", text="label",
    color="Indicações",
    color_continuous_scale=[[0, "#200000"], [1, "#CC3333"]],
    labels={"film": ""},
)
fig_snub.update_traces(textposition="outside", textfont=dict(color="#888", size=11))
fig_snub.update_layout(
    **CHART_BASE,
    xaxis=dict(**AXIS, title="", tickangle=-20, tickfont=dict(size=10)),
    yaxis=dict(**AXIS, title=""),
    coloraxis_showscale=False,
)
st.plotly_chart(fig_snub, use_container_width=True)

# ─── Surprise Insight ─────────────────────────────────────────────────────────
st.markdown(f"""
<div class="insight-card">
  <div class="tag">✦ &nbsp; Curiosidade Surpreendente</div>
  <h4>O maior azarado da história do Oscar</h4>
  <p>
    <span class="hl">{snub_name}</span> é a pessoa mais indicada ao Oscar que jamais conquistou
    uma estatueta. Foram <span class="hl">{fmt(snub_noms)} indicações</span> entre {snub_year_span},
    com trabalhos em filmes como <em>{snub_films_str}</em> — e nenhum prêmio.<br><br>
    Não é um caso isolado: <span class="hl">{fmt_pct(pct_never_won)}</span> de todos os profissionais
    que já foram indicados ao longo da história da premiação <strong>nunca levaram um Oscar para casa</strong>.
    Para a grande maioria, ser indicado já é, em si, o maior reconhecimento.
  </p>
</div>
""", unsafe_allow_html=True)

# ─── Raw data tables ──────────────────────────────────────────────────────────
with st.expander("Ver dados brutos — the_oscar_award.csv"):
    st.dataframe(df.reset_index(drop=True), use_container_width=True, height=280)

with st.expander("Ver dados brutos — full_data.csv"):
    st.dataframe(df_full.reset_index(drop=True), use_container_width=True, height=280)

st.markdown(
    "<div class='footer'>Fonte: Academy of Motion Picture Arts and Sciences"
    " &nbsp;·&nbsp; Criado com Streamlit + Plotly</div>",
    unsafe_allow_html=True,
)
