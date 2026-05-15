import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import conn

# ──────────────────────────────────────────────
#  CONFIGURAÇÃO & TEMA CLARO
# ──────────────────────────────────────────────
st.set_page_config(page_title="Finanças Pessoais", page_icon="◈", layout="wide")

# Paleta extraída da imagem de referência
# Fundo: #F4F6FB  |  Cards: #FFFFFF  |  Borda: #E0E6F0
# Verde entrada : #27AE60 / #2ECC71
# Vermelho saída: #E74C3C / #FF6B6B
# Azul saldo    : #2980B9 / #3498DB
# Amarelo aviso : #F39C12 / #F1C40F
# Roxo categoria: #8E44AD / #9B59B6
# Texto principal: #2C3E50  |  Texto suave: #7F8C8D

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: #F4F6FB !important;
    color: #2C3E50 !important;
    font-family: 'Space Grotesk', sans-serif;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #E0E6F0; }
::-webkit-scrollbar-thumb { background: #3498DB; border-radius: 4px; }

/* ── Header ── */
.finance-header {
    display: flex; align-items: center; gap: 14px;
    padding: 1.5rem 0 1rem 0;
    border-bottom: 2px solid #E0E6F0;
    margin-bottom: 1.5rem;
}
.finance-logo {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #2980B9, #3498DB);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    box-shadow: 0 4px 12px rgba(52,152,219,0.3);
}
.finance-title { font-size: 1.45rem; font-weight: 700; color: #2C3E50; letter-spacing: -0.4px; }
.finance-sub   { font-size: 0.74rem; color: #7F8C8D; font-family: 'JetBrains Mono', monospace; margin-top: 3px; }

/* ── Métricas ── */
div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E0E6F0 !important;
    border-radius: 16px !important;
    padding: 1.4rem 1.6rem !important;
    box-shadow: 0 2px 8px rgba(44,62,80,0.06) !important;
    transition: box-shadow 0.2s, border-color 0.2s;
}
div[data-testid="stMetric"]:hover {
    box-shadow: 0 6px 20px rgba(44,62,80,0.11) !important;
    border-color: #3498DB !important;
}
div[data-testid="stMetricLabel"] > div {
    color: #7F8C8D !important;
    font-size: 0.72rem !important;
    text-transform: uppercase; letter-spacing: 1px;
}
div[data-testid="stMetricValue"] {
    color: #2C3E50 !important;
    font-size: 1.5rem !important;
    font-family: 'JetBrains Mono', monospace; font-weight: 700;
}

/* Saldo — azul */
div[data-testid="column"]:nth-child(1) div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #2980B9 0%, #3498DB 100%) !important;
    border-color: transparent !important;
    box-shadow: 0 6px 20px rgba(52,152,219,0.35) !important;
}
div[data-testid="column"]:nth-child(1) div[data-testid="stMetricLabel"] > div { color: rgba(255,255,255,0.82) !important; }
div[data-testid="column"]:nth-child(1) div[data-testid="stMetricValue"]        { color: #FFFFFF !important; }
div[data-testid="column"]:nth-child(1) div[data-testid="stMetricDelta"]        { color: rgba(255,255,255,0.9) !important; }

/* Entradas — verde */
div[data-testid="column"]:nth-child(2) div[data-testid="stMetricValue"] { color: #27AE60 !important; }
/* Despesas — vermelho */
div[data-testid="column"]:nth-child(3) div[data-testid="stMetricValue"] { color: #E74C3C !important; }
/* Contas   — amarelo */
div[data-testid="column"]:nth-child(4) div[data-testid="stMetricValue"] { color: #F39C12 !important; }

/* ── Abas ── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border-radius: 12px; padding: 5px; gap: 3px;
    border: 1px solid #E0E6F0;
    box-shadow: 0 2px 8px rgba(44,62,80,0.05);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #7F8C8D !important;
    border-radius: 8px !important; font-size: 0.82rem !important;
    font-weight: 500; padding: 8px 18px !important; transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: #2980B9 !important; color: #FFFFFF !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(41,128,185,0.3) !important;
}

/* ── Botões ── */
.stButton > button {
    background: linear-gradient(135deg, #2980B9, #3498DB) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important; font-size: 0.82rem !important;
    padding: 0.5rem 1rem !important; transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(41,128,185,0.2) !important;
}
.stButton > button:hover {
    opacity: 0.88 !important; transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(41,128,185,0.35) !important;
}

/* ── Inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-baseweb="select"] > div,
div[data-baseweb="datepicker"] input {
    background: #FFFFFF !important;
    border: 1px solid #E0E6F0 !important;
    border-radius: 8px !important;
    color: #2C3E50 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    box-shadow: 0 1px 4px rgba(44,62,80,0.05) !important;
}
div[data-baseweb="select"] > div:hover,
div[data-testid="stTextInput"] input:focus { border-color: #3498DB !important; }

label[data-testid="stWidgetLabel"] {
    color: #7F8C8D !important; font-size: 0.74rem !important;
    text-transform: uppercase; letter-spacing: 0.5px;
}

/* ── Tabela ── */
.stDataFrame {
    border-radius: 12px; overflow: hidden;
    border: 1px solid #E0E6F0 !important;
    box-shadow: 0 2px 8px rgba(44,62,80,0.06);
}
.stDataFrame table { background: #FFFFFF !important; }
.stDataFrame th {
    background: #F4F6FB !important; color: #7F8C8D !important;
    font-size: 0.72rem !important; text-transform: uppercase;
    letter-spacing: 0.8px; border-color: #E0E6F0 !important;
}
.stDataFrame td { color: #2C3E50 !important; font-size: 0.85rem !important; border-color: #E0E6F0 !important; }

/* ── Cards ── */
.parcela-card {
    background: #FFFFFF; border: 1px solid #E0E6F0; border-radius: 12px;
    padding: 0.9rem 1.2rem; margin-bottom: 8px;
    display: flex; align-items: center; gap: 12px;
    transition: box-shadow 0.2s, border-color 0.2s;
    box-shadow: 0 1px 4px rgba(44,62,80,0.06);
}
.parcela-card:hover { box-shadow: 0 4px 16px rgba(44,62,80,0.10); border-color: #3498DB; }

.parcela-status-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.dot-aberto { background: #F39C12; box-shadow: 0 0 6px rgba(243,156,18,0.5); }
.dot-pago   { background: #27AE60; box-shadow: 0 0 6px rgba(39,174,96,0.5); }

/* ── Badges ── */
.badge {
    display: inline-block; padding: 2px 8px; border-radius: 6px;
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.4px;
}
.badge-entrada { background: rgba(39,174,96,0.12);  color: #27AE60; border: 1px solid rgba(39,174,96,0.25); }
.badge-saida   { background: rgba(231,76,60,0.10);  color: #E74C3C; border: 1px solid rgba(231,76,60,0.22); }

hr { border-color: #E0E6F0 !important; }

details {
    background: #FFFFFF !important; border: 1px solid #E0E6F0 !important;
    border-radius: 10px !important; box-shadow: 0 1px 4px rgba(44,62,80,0.05) !important;
}
summary { color: #2C3E50 !important; font-size: 0.85rem !important; }

div[data-testid="stRadio"] label { color: #7F8C8D !important; font-size: 0.82rem !important; }

.form-panel {
    background: #FFFFFF; border: 1px solid #E0E6F0;
    border-radius: 16px; padding: 1.4rem;
    box-shadow: 0 2px 8px rgba(44,62,80,0.06);
}

div[data-testid="stAlert"] { border-radius: 10px !important; border: none !important; }
div[data-baseweb="select"]  { font-size: 0.85rem !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
#  PALETA PLOTLY
# ──────────────────────────────────────────────
PLOTLY_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#7F8C8D', family='Space Grotesk'),
    margin=dict(l=10, r=10, t=40, b=10),
)
GRID_STYLE    = dict(gridcolor='#E0E6F0', zerolinecolor='#E0E6F0')
COLOR_ENTRADA = '#27AE60'
COLOR_SAIDA   = '#E74C3C'
COLOR_SALDO   = '#2980B9'
COLOR_ALERTA  = '#F39C12'
COLOR_SEQ     = ['#3498DB','#E74C3C','#2ECC71','#F39C12','#9B59B6','#1ABC9C','#E67E22','#E91E8C']

# ──────────────────────────────────────────────
#  FUNÇÕES DE NEGÓCIO
# ──────────────────────────────────────────────
def gerenciar_parcela(id_p, acao, dados=None):
    cursor = conn.cursor()
    if acao == "STATUS":
        pago_em = str(datetime.now().date()) if dados == "PAGO" else None
        cursor.execute("UPDATE parcelas SET status=?, pago_em=? WHERE id=?", (dados, pago_em, id_p))
    elif acao == "EDITAR":
        cursor.execute("UPDATE parcelas SET vencimento=?, valor=?, descricao=? WHERE id=?",
                       (str(dados['data']), dados['valor'], dados['desc'], id_p))
    elif acao == "EXCLUIR":
        cursor.execute("DELETE FROM parcelas WHERE id=?", (id_p,))
    conn.commit()

def gerenciar_lancamento(id_l, acao, dados=None):
    cursor = conn.cursor()
    if acao == "EDITAR":
        cursor.execute(
            "UPDATE lancamentos SET data=?, tipo=?, categoria=?, forma=?, descricao=?, valor=? WHERE id=?",
            (str(dados['data']), dados['tipo'], dados['categoria'],
             dados['forma'], dados['descricao'], dados['valor'], id_l)
        )
    elif acao == "EXCLUIR":
        cursor.execute("DELETE FROM lancamentos WHERE id=?", (id_l,))
    conn.commit()

def gerar_plano_parcelamento(desc, total, parcelas_qtd, data_ini):
    valor_unit = total / parcelas_qtd
    cursor = conn.cursor()
    for i in range(parcelas_qtd):
        venc = data_ini + timedelta(days=30 * i)
        cursor.execute(
            "INSERT INTO parcelas (vencimento, valor, status, descricao) VALUES (?, ?, ?, ?)",
            (str(venc), valor_unit, "ABERTO", f"{desc} [{i+1}/{parcelas_qtd}]")
        )
    conn.commit()

# ──────────────────────────────────────────────
#  DADOS
# ──────────────────────────────────────────────
df       = pd.read_sql("SELECT * FROM lancamentos", conn)
parcelas = pd.read_sql("SELECT * FROM parcelas", conn)

if not df.empty:
    df["data"]    = pd.to_datetime(df["data"])
    df["data_br"] = df["data"].dt.strftime('%d/%m/%Y')
    df["mes_ano"] = df["data"].dt.to_period('M').astype(str)
    df["dia_sem"] = df["data"].dt.day_name()
    df["dia_mes"] = df["data"].dt.day

dias_ordem = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
dias_pt    = ['Seg','Ter','Qua','Qui','Sex','Sáb','Dom']

# ──────────────────────────────────────────────
#  HEADER
# ──────────────────────────────────────────────
st.markdown("""
<div class="finance-header">
  <div class="finance-logo">◈</div>
  <div>
    <div class="finance-title">Finance — Análise das Finanças</div>
    <div class="finance-sub">Gestão financeira pessoal · v2.0</div>
  </div>
</div>
""", unsafe_allow_html=True)

rec_total    = df[df["tipo"]=="Entrada"]["valor"].sum() if not df.empty else 0
des_total    = df[df["tipo"]=="Saída"]["valor"].sum()   if not df.empty else 0
saldo        = rec_total - des_total
parc_abertas = parcelas[parcelas["status"]!="PAGO"]["valor"].sum() if not parcelas.empty else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("◈ Saldo Atual",      f"R$ {saldo:,.2f}",       delta=f"R$ {saldo:+,.2f}")
m2.metric("↑ Receita Total",    f"R$ {rec_total:,.2f}")
m3.metric("↓ Despesa Total",    f"R$ {des_total:,.2f}")
m4.metric("⏳ Contas a Pagar",  f"R$ {parc_abertas:,.2f}")

st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
#  ABAS
# ──────────────────────────────────────────────
tab_lancar, tab_analise, tab_parcelas, tab_admin = st.tabs([
    "  ＋  Lançamentos  ",
    "  📊  Dashboard  ",
    "  🗓  Contas Futuras  ",
    "  🗃  Histórico  ",
])

# ══════════════════════════════════════════════
#  ABA: LANÇAMENTOS
# ══════════════════════════════════════════════
with tab_lancar:
    col_l, col_r = st.columns([1.1, 2])
    with col_l:
        st.markdown("<div class='form-panel'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:1rem;font-weight:700;color:#2C3E50;margin-bottom:12px'>Registrar Movimentação</div>", unsafe_allow_html=True)
        tipo   = st.selectbox("Tipo de Fluxo", ["Saída","Entrada"])
        dt     = st.date_input("Data do Evento", format="DD/MM/YYYY")
        cat    = st.selectbox("Categoria", ["Salário","Terceiros","Empréstimo","Alimentação","Delivery","Lazer","Aluguel","Água, Luz e Gás","Pets","Shopee","Saúde","Compras"])
        val    = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        desc_l = st.text_input("Descrição / Nota")
        f_pag  = st.selectbox("Forma de Pagamento", ["Pix","Crédito","Débito","Espécie"])
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("✔ Confirmar Registro", use_container_width=True):
            conn.cursor().execute(
                "INSERT INTO lancamentos (data, tipo, categoria, forma, descricao, valor) VALUES (?,?,?,?,?,?)",
                (str(dt), tipo, cat, f_pag, desc_l, val)
            )
            conn.commit()
            st.success("✓ Transação registrada com sucesso!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        if not df.empty:
            df_evo_e = df[df['tipo']=='Entrada'].groupby('data')['valor'].sum().reset_index()
            df_evo_s = df[df['tipo']=='Saída'].groupby('data')['valor'].sum().reset_index()
            fig_evo = go.Figure()
            fig_evo.add_trace(go.Scatter(
                x=df_evo_e['data'], y=df_evo_e['valor'], mode='lines', name='Entradas',
                line=dict(color=COLOR_ENTRADA, width=2.5),
                fill='tozeroy', fillcolor='rgba(39,174,96,0.10)',
            ))
            fig_evo.add_trace(go.Scatter(
                x=df_evo_s['data'], y=df_evo_s['valor'], mode='lines', name='Saídas',
                line=dict(color=COLOR_SAIDA, width=2.5),
                fill='tozeroy', fillcolor='rgba(231,76,60,0.08)',
            ))
            fig_evo.update_layout(
                title="Fluxo Diário — Entradas e Saídas", height=280, **PLOTLY_BASE,
                xaxis=dict(showgrid=False, title=''),
                yaxis=dict(**GRID_STYLE, title='R$'),
                legend=dict(bgcolor='rgba(0,0,0,0)', orientation='h', yanchor='bottom', y=1.02),
            )
            st.plotly_chart(fig_evo, use_container_width=True)

            st.markdown("<div style='font-size:0.9rem;font-weight:700;color:#2C3E50;margin-bottom:8px'>Últimas movimentações</div>", unsafe_allow_html=True)
            for _, r in df.sort_values('data', ascending=False).head(7).iterrows():
                cor   = COLOR_ENTRADA if r['tipo']=='Entrada' else COLOR_SAIDA
                sinal = '+' if r['tipo']=='Entrada' else '−'
                bdg   = 'badge-entrada' if r['tipo']=='Entrada' else 'badge-saida'
                st.markdown(f"""
                <div class="parcela-card" style="justify-content:space-between">
                  <div style="display:flex;align-items:center;gap:10px">
                    <div class="parcela-status-dot {'dot-pago' if r['tipo']=='Entrada' else 'dot-aberto'}"></div>
                    <div>
                      <div style="font-size:0.84rem;font-weight:600;color:#2C3E50">{r['descricao'] or r['categoria']}</div>
                      <div style="font-size:0.71rem;color:#7F8C8D">{r['data_br']} · {r['forma']}</div>
                    </div>
                  </div>
                  <div style="text-align:right">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.92rem;font-weight:700;color:{cor}">{sinal}R$ {r['valor']:,.2f}</div>
                    <span class="badge {bdg}">{r['categoria']}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum lançamento registrado. Use o formulário ao lado para começar.")

# ──────────────────────────────────────────────
#  ABA: DASHBOARD
# ──────────────────────────────────────────────
with tab_analise:
    if not df.empty:
        # Filtros
        fc1, fc2, fc3 = st.columns([1, 1, 2])
        with fc1: data_inicio = st.date_input("De:", value=df["data"].min().date(), key="di")
        with fc2: data_fim    = st.date_input("Até:", value=df["data"].max().date(), key="df")
        with fc3: tipo_filt   = st.radio("Exibir", ["Todos","Entradas","Saídas"], horizontal=True)

        mask = (df["data"] >= pd.Timestamp(data_inicio)) & (df["data"] <= pd.Timestamp(data_fim))
        df_f = df.loc[mask].copy()
        if tipo_filt == "Entradas": df_f = df_f[df_f["tipo"]=="Entrada"]
        elif tipo_filt == "Saídas": df_f = df_f[df_f["tipo"]=="Saída"]

        st.divider()

        # KPIs do período
        p_rec  = df_f[df_f["tipo"]=="Entrada"]["valor"].sum()
        p_des  = df_f[df_f["tipo"]=="Saída"]["valor"].sum()
        p_sld  = p_rec - p_des
        dias_p = max((pd.Timestamp(data_fim) - pd.Timestamp(data_inicio)).days, 1)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Saldo no Período",      f"R$ {p_sld:,.2f}")
        k2.metric("Total Entradas",        f"R$ {p_rec:,.2f}")
        k3.metric("Total Saídas",          f"R$ {p_des:,.2f}")
        k4.metric("Média Diária de Gasto", f"R$ {p_des/dias_p:,.2f}")
        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

        # ── Linha 1: Barras mensais + Donut ──
        c1, c2 = st.columns([1.6, 1])
        with c1:
            df_mensal = df_f.groupby(['mes_ano','tipo'])['valor'].sum().reset_index()
            fig_bar = px.bar(
                df_mensal, x='mes_ano', y='valor', color='tipo', barmode='group',
                title="Receita, Despesa e Saldo por Mês",
                color_discrete_map={'Entrada': COLOR_ENTRADA, 'Saída': COLOR_SAIDA},
                text_auto='.2s',
            )
            fig_bar.update_traces(marker_line_width=0, opacity=0.9, textfont_size=10)
            fig_bar.update_layout(height=310, **PLOTLY_BASE,
                xaxis=dict(showgrid=False, title='', tickfont=dict(size=11)),
                yaxis=dict(**GRID_STYLE, title='R$'),
                legend=dict(bgcolor='rgba(0,0,0,0)', orientation='h', yanchor='bottom', y=1.02, title=''),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            df_cat = df_f[df_f["tipo"]=="Saída"].groupby('categoria')['valor'].sum().reset_index()
            if not df_cat.empty:
                fig_donut = px.pie(
                    df_cat, values='valor', names='categoria', hole=0.52,
                    title="Gastos por Categoria",
                    color_discrete_sequence=COLOR_SEQ,
                )
                fig_donut.update_traces(
                    textfont_size=11, textinfo='percent',
                    marker=dict(line=dict(color='#FFFFFF', width=2)),
                    pull=[0.04]*len(df_cat),
                )
                fig_donut.update_layout(height=310, **PLOTLY_BASE,
                    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=10)),
                    annotations=[dict(
                        text=f'<b>R$ {df_cat["valor"].sum():,.0f}</b>',
                        x=0.5, y=0.5, font=dict(size=13, color='#2C3E50', family='JetBrains Mono'),
                        showarrow=False,
                    )],
                )
                st.plotly_chart(fig_donut, use_container_width=True)

        # ── Cards trimestrais (como na imagem) ──
        trim_labels = ["1º TRI","2º TRI","3º TRI","4º TRI"]
        trim_meses  = [(1,3),(4,6),(7,9),(10,12)]
        t1, t2, t3, t4 = st.columns(4)
        for col_t, label, (m_ini, m_fim) in zip([t1,t2,t3,t4], trim_labels, trim_meses):
            mask_t = (df_f['data'].dt.month >= m_ini) & (df_f['data'].dt.month <= m_fim)
            val_t  = df_f.loc[mask_t & (df_f['tipo']=='Saída'), 'valor'].sum()
            col_t.metric(label, f"R$ {val_t:,.2f}")

        st.divider()

        # ── Linha 2: Barras horizontais categorias + Barras empilhadas por mês ──
        c3, c4 = st.columns([1, 1.5])
        with c3:
            df_cat_bar = (df_f[df_f["tipo"]=="Saída"]
                          .groupby('categoria')['valor'].sum()
                          .sort_values(ascending=True).reset_index())
            fig_hbar = px.bar(
                df_cat_bar, x='valor', y='categoria', orientation='h',
                title="Despesas por Categoria",
                color='valor',
                color_continuous_scale=[[0,'#EBF5FB'],[0.4,'#3498DB'],[0.75,'#E74C3C'],[1,'#8E44AD']],
                text_auto='.2s',
            )
            fig_hbar.update_traces(marker_line_width=0, textfont_size=10)
            fig_hbar.update_layout(height=340, **PLOTLY_BASE, coloraxis_showscale=False,
                xaxis=dict(**GRID_STYLE, title='R$'),
                yaxis=dict(showgrid=False, title=''),
            )
            st.plotly_chart(fig_hbar, use_container_width=True)

        with c4:
            top_cats = (df_f[df_f["tipo"]=="Saída"].groupby('categoria')['valor'].sum()
                        .nlargest(6).index.tolist())
            df_det = (df_f[df_f['categoria'].isin(top_cats) & (df_f['tipo']=='Saída')]
                      .groupby(['mes_ano','categoria'])['valor'].sum().reset_index())
            if not df_det.empty:
                fig_stack = px.bar(
                    df_det, x='mes_ano', y='valor', color='categoria',
                    title="Despesas Detalhadas por Mês",
                    color_discrete_sequence=COLOR_SEQ,
                    barmode='stack', text_auto='.2s',
                )
                fig_stack.update_traces(marker_line_width=0, opacity=0.9, textfont_size=9)
                fig_stack.update_layout(height=340, **PLOTLY_BASE,
                    xaxis=dict(showgrid=False, title=''),
                    yaxis=dict(**GRID_STYLE, title='R$'),
                    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=10), orientation='v', title=''),
                )
                st.plotly_chart(fig_stack, use_container_width=True)

        st.divider()

        # ── Linha 3: Dia da semana + Saldo acumulado ──
        c5, c6 = st.columns(2)
        with c5:
            df_dias = (df_f[df_f["tipo"]=="Saída"]
                       .groupby('dia_sem')['valor'].sum()
                       .reindex(dias_ordem, fill_value=0).reset_index())
            df_dias.columns = ['dia','total']
            df_dias['dia_pt'] = dias_pt
            fig_dias = px.bar(
                df_dias, x='dia_pt', y='total',
                title="💸 Impacto por Dia da Semana",
                color='total',
                color_continuous_scale=[[0,'#EBF5FB'],[0.5,'#3498DB'],[1,'#E74C3C']],
                text_auto='.2s',
            )
            fig_dias.update_traces(marker_line_width=0, textfont_size=10)
            fig_dias.update_layout(height=290, **PLOTLY_BASE, coloraxis_showscale=False,
                xaxis=dict(showgrid=False, title=''),
                yaxis=dict(**GRID_STYLE, title='R$'),
            )
            st.plotly_chart(fig_dias, use_container_width=True)

        with c6:
            df_acc = df_f.sort_values('data').copy()
            df_acc['valor_sinal'] = df_acc.apply(lambda r: r['valor'] if r['tipo']=='Entrada' else -r['valor'], axis=1)
            df_acc['acumulado']   = df_acc['valor_sinal'].cumsum()
            fig_acc = go.Figure()
            fig_acc.add_trace(go.Scatter(
                x=df_acc['data'], y=df_acc['acumulado'],
                mode='lines+markers', name='Saldo Acumulado',
                line=dict(color=COLOR_SALDO, width=2.5),
                fill='tozeroy', fillcolor='rgba(41,128,185,0.08)',
                marker=dict(size=4, color=COLOR_SALDO),
            ))
            fig_acc.add_hline(y=0, line_dash='dot', line_color='#BDC3C7', line_width=1)
            fig_acc.update_layout(
                title="📈 Saldo Acumulado no Período", height=290, **PLOTLY_BASE,
                xaxis=dict(showgrid=False, title=''),
                yaxis=dict(**GRID_STYLE, title='R$'),
            )
            st.plotly_chart(fig_acc, use_container_width=True)

        # ── Top 5 ──
        st.markdown("<div style='font-size:0.92rem;font-weight:700;color:#2C3E50;margin-bottom:8px'>🏆 Top 5 Maiores Saídas no Período</div>", unsafe_allow_html=True)
        top5 = df_f[df_f["tipo"]=="Saída"].nlargest(5, 'valor')
        if not top5.empty:
            for i, (_, r) in enumerate(top5.iterrows()):
                pct = r['valor'] / p_des * 100 if p_des > 0 else 0
                st.markdown(f"""
                <div style="margin-bottom:10px">
                  <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                    <span style="font-size:0.83rem;color:#2C3E50;font-weight:500">
                      {i+1}. {r['descricao'] or r['categoria']}
                      <span class="badge badge-saida">{r['categoria']}</span>
                    </span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.83rem;color:{COLOR_SAIDA};font-weight:700">
                      R$ {r['valor']:,.2f}
                      <span style="color:#7F8C8D;font-size:0.72rem">({pct:.1f}%)</span>
                    </span>
                  </div>
                  <div style="background:#E0E6F0;border-radius:4px;height:5px;overflow:hidden">
                    <div style="background:linear-gradient(90deg,{COLOR_SAIDA},{COLOR_ALERTA});width:{pct:.0f}%;height:100%;border-radius:4px"></div>
                  </div>
                  <div style="font-size:0.7rem;color:#7F8C8D;margin-top:2px">{r['data_br']}</div>
                </div>
                """, unsafe_allow_html=True)

        # ── Heatmap ──
        st.markdown("<div style='font-size:0.92rem;font-weight:700;color:#2C3E50;margin:14px 0 8px'>🗓 Mapa de Calor — Gastos por Dia do Mês</div>", unsafe_allow_html=True)
        df_heat = (df_f[df_f['tipo']=='Saída'].groupby(['dia_sem','dia_mes'])['valor'].sum().reset_index())
        if not df_heat.empty:
            piv = df_heat.pivot_table(index='dia_sem', columns='dia_mes', values='valor', fill_value=0)
            piv = piv.reindex([d for d in dias_ordem if d in piv.index])
            fig_heat = go.Figure(go.Heatmap(
                z=piv.values,
                x=[str(c) for c in piv.columns],
                y=[dias_pt[dias_ordem.index(d)] for d in piv.index],
                colorscale=[[0,'#EBF5FB'],[0.35,'#3498DB'],[0.7,'#8E44AD'],[1,'#E74C3C']],
                showscale=True,
                colorbar=dict(tickfont=dict(color='#7F8C8D'), len=0.8),
                hovertemplate='Dia %{x} (%{y})<br>Gasto: R$ %{z:,.2f}<extra></extra>',
            ))
            fig_heat.update_layout(height=220, **PLOTLY_BASE,
                xaxis=dict(title='Dia do mês', showgrid=False, tickfont=dict(size=10)),
                yaxis=dict(showgrid=False, tickfont=dict(size=11)),
            )
            st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("📊 Nenhum dado disponível. Adicione lançamentos para visualizar os gráficos.")

# ══════════════════════════════════════════════
#  ABA: CONTAS FUTURAS (ALTERADA)
# ══════════════════════════════════════════════
with tab_parcelas:
    col_menu, col_grid = st.columns([1, 2.5])
    with col_menu:
        st.markdown("<div class='form-panel'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.95rem;font-weight:700;color:#2C3E50;margin-bottom:10px'>Novo Parcelamento</div>", unsafe_allow_html=True)
        p_desc  = st.text_input("Título do compromisso")
        p_total = st.number_input("Valor Total (R$)", min_value=0.0, key="ptot")
        p_qtd   = st.number_input("Nº de Parcelas", min_value=1, value=12, key="pqtd")
        p_data  = st.date_input("Data de Início", key="pdta")
        if st.button("＋ Gerar Parcelamento", use_container_width=True):
            gerar_plano_parcelamento(p_desc, p_total, int(p_qtd), p_data)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        if not parcelas.empty:
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            ab = parcelas[parcelas["status"]!="PAGO"]["valor"].sum()
            pg = parcelas[parcelas["status"]=="PAGO"]["valor"].sum()
            st.markdown(f"""
            <div class="form-panel">
              <div style="font-size:0.72rem;color:#7F8C8D;text-transform:uppercase;letter-spacing:.8px;margin-bottom:10px">Resumo</div>
              <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                <span style="font-size:0.82rem;color:#2C3E50">Em aberto</span>
                <span style="font-family:'JetBrains Mono',monospace;color:{COLOR_ALERTA};font-size:0.88rem;font-weight:700">R$ {ab:,.2f}</span>
              </div>
              <div style="display:flex;justify-content:space-between">
                <span style="font-size:0.82rem;color:#2C3E50">Já pagos</span>
                <span style="font-family:'JetBrains Mono',monospace;color:{COLOR_ENTRADA};font-size:0.88rem;font-weight:700">R$ {pg:,.2f}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col_grid:
        if not parcelas.empty:
            filt   = st.radio("Exibir", ["Em Aberto","Pago","Todos"], horizontal=True)
            p_view = parcelas.copy()
            
            # Filtragem rígida baseada no status atualizado
            if filt == "Em Aberto": 
                p_view = p_view[p_view["status"] != "PAGO"]
            elif filt == "Pago":    
                p_view = p_view[p_view["status"] == "PAGO"]
                
            p_view = p_view.sort_values('vencimento')

            for _, r in p_view.iterrows():
                pago     = r['status'] == "PAGO"
                dot_cls  = "dot-pago" if pago else "dot-aberto"
                cor_val  = COLOR_ENTRADA if pago else COLOR_ALERTA
                venc_fmt = pd.to_datetime(r['vencimento']).strftime('%d/%m/%Y')
                rid      = int(r['id'])

                st.markdown(f"""
                <div class="parcela-card">
                  <div class="parcela-status-dot {dot_cls}"></div>
                  <div style="flex:1">
                    <div style="font-size:0.85rem;font-weight:600;color:#2C3E50">{r['descricao']}</div>
                    <div style="font-size:0.72rem;color:#7F8C8D">Vence em {venc_fmt}</div>
                  </div>
                  <span style="font-family:'JetBrains Mono',monospace;font-size:0.95rem;font-weight:700;color:{cor_val}">
                    R$ {r['valor']:.2f}
                  </span>
                </div>
                """, unsafe_allow_html=True)

                bc1, bc2, bc3 = st.columns(3)
                with bc1:
                    # Modificado para alternar definitivamente e sumir da lista atualizada ao recarregar
                    if st.button("✓ Marcar Pago" if not pago else "↩ Reabrir", key=f"st_{rid}", use_container_width=True):
                        novo_status = "PAGO" if not pago else "ABERTO"
                        gerenciar_parcela(rid, "STATUS", novo_status)
                        st.rerun()
                with bc2:
                    if st.button("✎ Editar", key=f"ed_{rid}", use_container_width=True):
                        st.session_state[f"edit_parc_{rid}"] = not st.session_state.get(f"edit_parc_{rid}", False)
                with bc3:
                    if st.button("✕ Excluir", key=f"ex_{rid}", use_container_width=True):
                        gerenciar_parcela(rid, "EXCLUIR")
                        st.rerun()