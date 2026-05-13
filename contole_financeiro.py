import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from database import conn

# --- CONFIGURAÇÃO E ESTILO DARK ---
st.set_page_config(page_title="Gestão Financeira", page_icon="🏦", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    .stApp { background-color: #0B0E1B; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #FFFFFF !important; font-weight: 700; }
    div[data-testid="stMetric"] {
        background-color: #161B30;
        border: 1px solid #242B45;
        padding: 1.5rem;
        border-radius: 15px;
    }
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.8rem !important; }
    [data-testid="metric-container"]:first-child {
        background: linear-gradient(135deg, #FF6B00 0%, #FF3D00 100%) !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] { background-color: #2563EB !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE NEGÓCIO ---
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

def gerar_plano_parcelamento(desc, total, parcelas_qtd, data_ini):
    valor_unit = total / parcelas_qtd
    cursor = conn.cursor()
    for i in range(parcelas_qtd):
        venc = data_ini + timedelta(days=30 * i)
        cursor.execute("INSERT INTO parcelas (vencimento, valor, status, descricao) VALUES (?, ?, ?, ?)", 
                       (str(venc), valor_unit, "ABERTO", f"{desc} [{i+1}/{parcelas_qtd}]"))
    conn.commit()

# --- CARREGAMENTO DE DADOS ---
df = pd.read_sql("SELECT * FROM lancamentos", conn)
parcelas = pd.read_sql("SELECT * FROM parcelas", conn)

if not df.empty:
    df["data"] = pd.to_datetime(df["data"])
    df["data_br"] = df["data"].dt.strftime('%d/%m/%Y')
    df["mes_ano"] = df["data"].dt.to_period('M').astype(str)

# --- HEADER ---
st.markdown("### Dashboard Finanças Pessoais")

m1, m2, m3 = st.columns(3)
rec_total = df[df["tipo"] == "Entrada"]["valor"].sum() if not df.empty else 0
des_total = df[df["tipo"] == "Saída"]["valor"].sum() if not df.empty else 0

m1.metric("Saldo Atual", f"R$ {rec_total - des_total:,.2f}")
m2.metric("Entradas Totais", f"R$ {rec_total:,.2f}")
m3.metric("Despesas Totais", f"R$ {des_total:,.2f}")

tab_lancar, tab_analise, tab_parcelas, tab_admin = st.tabs([
    "📥 Lançamentos", "📈 Dashboard", "🗓️ Contas Futuras", "⚙️ Histórico"
])

# --- ABA: NOVO LANÇAMENTO ---
with tab_lancar:
    col_l, col_r = st.columns([1.2, 2])
    with col_l:
        st.subheader("Registrar Movimentação")
        with st.container():
            tipo = st.selectbox("Categoria de Fluxo", ["Saída", "Entrada"])
            dt = st.date_input("Data do Evento", format="DD/MM/YYYY")
            cat = st.selectbox("Centro de Custo", ["Salário", "Terceiros", "Empréstimo", "Alimentação", "Delivery", "Lazer", "Aluguel", "Água, Luz e Gás", "Pets", "Shopee", "Saúde", "Compras"])
            val = st.number_input("Montante (R$)", min_value=0.0, format="%.2f")
            desc_l = st.text_input("Nota / Descritivo")
            f_pag = st.selectbox("Meio de Pagamento", ["Pix", "Crédito", "Débito", "Espécie"])
            
            if st.button("Confirmar Registro", use_container_width=True):
                conn.cursor().execute("INSERT INTO lancamentos (data, tipo, categoria, forma, descricao, valor) VALUES (?,?,?,?,?,?)",
                                       (str(dt), tipo, cat, f_pag, desc_l, val))
                conn.commit()
                st.success("Transação registrada.")
                st.rerun()
    
    with col_r:
        if not df.empty:
            df_evolucao = df.groupby('data')['valor'].sum().reset_index()
            fig = px.area(df_evolucao, x='data', y='valor', title="Volume de Transações por Dia", color_discrete_sequence=['#2563EB'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=350)
            st.plotly_chart(fig, use_container_width=True)

# --- ABA: DASHBOARD FUNCIONAL ---
with tab_analise:
    if not df.empty:
        # Filtros de Período
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            data_inicio = st.date_input("De:", value=df["data"].min())
        with col_f2:
            data_fim = st.date_input("Até:", value=df["data"].max())
        
        mask = (df["data"] >= pd.Timestamp(data_inicio)) & (df["data"] <= pd.Timestamp(data_fim))
        df_filtrado = df.loc[mask]

        st.divider()
        
        # Gráficos Principais
        c1, c2 = st.columns(2)
        
        with c1:
            # Evolução Mensal Comparativa
            df_mensal = df_filtrado.groupby(['mes_ano', 'tipo'])['valor'].sum().reset_index()
            fig_bar = px.bar(df_mensal, x='mes_ano', y='valor', color='tipo', barmode='group',
                             title="Entradas vs Saídas por Mês",
                             color_discrete_map={'Entrada': '#10B981', 'Saída': '#EF4444'})
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            # Maiores Despesas por Categoria
            df_despesas = df_filtrado[df_filtrado["tipo"] == "Saída"].groupby('categoria')['valor'].sum().reset_index()
            fig_pie = px.pie(df_despesas, values='valor', names='categoria', hole=.4,
                             title="Maiores Gastos por Categoria",
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        # Tabela de Maiores Saídas Individuais (Análise de Pareto)
        st.subheader("Top 5 Maiores Saídas no Período")
        top_saidas = df_filtrado[df_filtrado["tipo"] == "Saída"].nlargest(5, 'valor')
        st.dataframe(top_saidas[["data_br", "categoria", "descricao", "valor"]], use_container_width=True)
    else:
        st.info("Aguardando dados para gerar análises.")

# --- ABA: CONTAS FUTURAS ---
with tab_parcelas:
    col_menu, col_grid = st.columns([1, 3])
    with col_menu:
        st.write("**Novo Parcelamento**")
        with st.expander("Formulário"):
            p_desc = st.text_input("Título")
            p_total = st.number_input("Valor Total", min_value=0.0)
            p_qtd = st.number_input("Parcelas", min_value=1, value=12)
            p_data = st.date_input("Início")
            if st.button("Gerar", use_container_width=True):
                gerar_plano_parcelamento(p_desc, p_total, p_qtd, p_data)
                st.rerun()

    with col_grid:
        if not parcelas.empty:
            filt = st.radio("Filtro", ["Em Aberto", "Pago", "Todos"], horizontal=True)
            p_view = parcelas.copy()
            if filt == "Em Aberto": p_view = p_view[p_view["status"] != "PAGO"]
            elif filt == "Pago": p_view = p_view[p_view["status"] == "PAGO"]
            
            for _, r in p_view.iterrows():
                with st.container():
                    c_info, c_val, c_venc, c_acao = st.columns([2, 1, 1, 1.5])
                    st.write(f"{'🔴' if r['status'] != 'PAGO' else '🟢'} **{r['descricao']}** | R$ {r['valor']:.2f} | Venc: {pd.to_datetime(r['vencimento']).strftime('%d/%m/%Y')}")
                    if st.button("Trocar Status", key=f"st_{r['id']}"):
                        novo_st = "PAGO" if r['status'] == "ABERTO" else "ABERTO"
                        gerenciar_parcela(r['id'], "STATUS", novo_st)
                        st.rerun()
                st.divider()

# --- ABA: ADMINISTRAÇÃO ---
with tab_admin:
    st.subheader("Histórico Geral")
    if not df.empty:
        st.dataframe(df[["id", "data_br", "tipo", "categoria", "valor", "descricao"]].sort_values("id", ascending=False), use_container_width=True)