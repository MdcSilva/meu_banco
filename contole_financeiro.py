import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from database import conn

# --- CONFIGURAÇÃO E ESTILO CORPORATIVO ---
st.set_page_config(page_title="Gestão Financeira", page_icon="🏦", layout="wide")

st.markdown("""
    <style>
    /* Paleta Corporativa */
    :root {
        --primary: #0F172A;
        --accent: #2563EB;
        --text-main: #1E293B;
        --bg-light: #F8FAFC;
    }
    
    .main { background-color: var(--bg-light); }
    
    /* Títulos e Tipografia */
    h1, h2, h3 { color: var(--primary); font-family: 'Inter', sans-serif; font-weight: 700; }
    
    /* Estilização de Cards e Métricas */
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #E2E8F0;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    /* Botões Customizados */
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    /* Status Labels */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
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
        cursor.execute("""
            INSERT INTO parcelas (vencimento, valor, status, descricao) 
            VALUES (?, ?, ?, ?)
        """, (str(venc), valor_unit, "ABERTO", f"{desc} [{i+1}/{parcelas_qtd}]"))
    conn.commit()

# --- CARREGAMENTO DE DADOS ---
df = pd.read_sql("SELECT * FROM lancamentos", conn)
parcelas = pd.read_sql("SELECT * FROM parcelas", conn)

if not df.empty:
    df["data"] = pd.to_datetime(df["data"])
    df["data_br"] = df["data"].dt.strftime('%d/%m/%Y')

# --- DASHBOARD SUPERIOR ---
st.title("🏦 Gestão Financeira Corporativa")
st.markdown("Monitoramento de ativos e passivos em tempo real.")

m1, m2, m3, m4 = st.columns(4)
rec_total = df[df["tipo"] == "Entrada"]["valor"].sum() if not df.empty else 0
des_total = df[df["tipo"] == "Saída"]["valor"].sum() if not df.empty else 0
pendente = parcelas[parcelas["status"] != "PAGO"]["valor"].sum() if not parcelas.empty else 0

m1.metric("Receita Acumulada", f"R$ {rec_total:,.2f}")
m2.metric("Despesa Operacional", f"R$ {des_total:,.2f}")
m3.metric("Fluxo de Caixa", f"R$ {(rec_total - des_total):,.2f}")
m4.metric("Passivo Futuro", f"R$ {pendente:,.2f}", delta="- Previsão", delta_color="inverse")

tab_lancar, tab_analise, tab_parcelas, tab_admin = st.tabs([
    "📥 Lançamentos", "📈 Dashboard", "🗓️ Contas Futuras", "⚙️ Histórico"
])

# --- ABA: NOVO LANÇAMENTO (LAYOUT image_e8e7dd.png) ---
with tab_lancar:
    col_l, col_r = st.columns([1.2, 2])
    with col_l:
        st.subheader("Registrar Movimentação")
        with st.container():
            tipo = st.selectbox("Categoria de Fluxo", ["Saída", "Entrada"])
            dt = st.date_input("Data do Evento", format="DD/MM/YYYY")
            cat = st.selectbox("Centro de Custo", ["Salário", "Operacional", "Impostos", "Logística", "Marketing", "Financeiro", "Outros"])
            val = st.number_input("Montante (R$)", min_value=0.0, format="%.2f")
            desc_l = st.text_input("Nota / Descritivo")
            f_pag = st.selectbox("Meio de Pagamento", ["Pix", "Transferência", "Cartão Corporate", "Espécie"])
            
            if st.button("Confirmar Registro", use_container_width=True, type="primary"):
                conn.cursor().execute("INSERT INTO lancamentos (data, tipo, categoria, forma, descricao, valor) VALUES (?,?,?,?,?,?)",
                                       (str(dt), tipo, cat, f_pag, desc_l, val))
                conn.commit()
                st.success("Transação registrada no Ledger.")
                st.rerun()

# --- ABA: CONTAS FUTURAS (GESTÃO AVANÇADA) ---
with tab_parcelas:
    col_menu, col_grid = st.columns([1, 3])
    
    with col_menu:
        st.write("**Estruturar Novo Parcelamento**")
        with st.expander("Abrir Formulário"):
            p_desc = st.text_input("Título do Contrato")
            p_total = st.number_input("Valor de Face", min_value=0.0)
            p_qtd = st.number_input("Ciclos (Meses)", min_value=1, value=12)
            p_data = st.date_input("Início do Cronograma")
            if st.button("Gerar Plano de Pagamento", use_container_width=True):
                gerar_plano_parcelamento(p_desc, p_total, p_qtd, p_data)
                st.rerun()

    with col_grid:
        if not parcelas.empty:
            filt = st.radio("Status do Portfólio", ["Em Aberto", "Pago", "Todos"], horizontal=True)
            
            p_view = parcelas.copy()
            if filt == "Em Aberto": p_view = p_view[p_view["status"] != "PAGO"]
            elif filt == "Pago": p_view = p_view[p_view["status"] == "PAGO"]
            
            for _, r in p_view.iterrows():
                with st.container():
                    c_info, c_val, c_venc, c_acao = st.columns([2, 1, 1, 1.5])
                    
                    status_icon = "🔴" if r['status'] != "PAGO" else "🟢"
                    c_info.write(f"{status_icon} **{r['descricao']}**")
                    c_val.write(f"R$ {r['valor']:.2f}")
                    c_venc.write(pd.to_datetime(r['vencimento']).strftime('%d/%m/%Y'))
                    
                    # Botões de Ação Rápida
                    col_btn1, col_btn2, col_btn3 = c_acao.columns(3)
                    
                    # Baixar / Estornar
                    if r['status'] == 'PAGO':
                        if col_btn1.button("🔄", key=f"re_{r['id']}", help="Estornar"):
                            gerenciar_parcela(r['id'], "STATUS", "ABERTO"); st.rerun()
                    else:
                        if col_btn1.button("✅", key=f"ok_{r['id']}", help="Liquidar Parcela"):
                            gerenciar_parcela(r['id'], "STATUS", "PAGO"); st.rerun()
                    
                    # Editar
                    if col_btn2.button("✏️", key=f"ed_{r['id']}", help="Editar detalhes"):
                        st.session_state[f"edit_mode_{r['id']}"] = True

                    # Excluir
                    if col_btn3.button("🗑️", key=f"del_{r['id']}", help="Excluir Parcela"):
                        gerenciar_parcela(r['id'], "EXCLUIR")
                        st.rerun()

                    # Área de Edição (Condicional)
                    if st.session_state.get(f"edit_mode_{r['id']}", False):
                        with st.form(f"f_edit_{r['id']}"):
                            ed_d = st.date_input("Vencimento", value=pd.to_datetime(r['vencimento']))
                            ed_v = st.number_input("Valor", value=float(r['valor']))
                            ed_s = st.text_input("Descrição", value=r['descricao'])
                            if st.form_submit_button("Atualizar"):
                                gerenciar_parcela(r['id'], "EDITAR", {'data': ed_d, 'valor': ed_v, 'desc': ed_s})
                                st.session_state[f"edit_mode_{r['id']}"] = False
                                st.rerun()
                st.divider()
        else:
            st.info("Nenhum compromisso futuro identificado.")

# --- ABA: ADMINISTRAÇÃO E HISTÓRICO ---
with tab_admin:
    st.subheader("Transações")
    if not df.empty:
        st.dataframe(df[["id", "data_br", "tipo", "categoria", "descricao", "valor"]].sort_values("id", ascending=False), use_container_width=True)
        if st.button("Limpar Histórico Completo", type="secondary"):
            st.warning("Ação restrita ao administrador.")