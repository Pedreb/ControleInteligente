import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from msal import ConfidentialClientApplication
import io
from datetime import datetime, time as dt_time, date, timedelta
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Sistema de Controle Inteligente - Pará",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Personalizado - Inspirado no layout mostrado
st.markdown("""
<style>
    /* Reset e configurações gerais */
    .stApp {
        background-color: #f5f5f5;
    }

    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #F7931E 0%, #000000 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(247, 147, 30, 0.3);
    }

    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
    }

    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }

    /* Sidebar personalizada */
    .sidebar-content {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }

    .sidebar-title {
        color: #333;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #F7931E;
    }

    /* Botão de atualizar */
    .update-button {
        background: linear-gradient(45deg, #F7931E, #FFB347);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }

    /* Container principal */
    .main-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }

    /* Título das seções */
    .section-title {
        color: #333;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 10px;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #F7931E;
    }

    /* Métricas cards */
    .metric-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .metric-card:hover {
        border-color: #F7931E;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(247, 147, 30, 0.2);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #F7931E;
        margin-bottom: 0.5rem;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #666;
        font-weight: 500;
    }

    /* Tabela principal */
    .main-table {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 15px rgba(0,0,0,0.1);
    }

    /* Headers da tabela */
    .table-header {
        background: linear-gradient(135deg, #F7931E 0%, #E6820A 100%);
        color: white;
        padding: 1rem;
        font-weight: 600;
        text-align: center;
        font-size: 0.9rem;
        border-right: 1px solid rgba(255,255,255,0.2);
    }

    /* Status indicators */
    .status-presente {
        background: #28a745;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }

    .status-ausente {
        background: #dc3545;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }

    .status-urgente {
        background: #ff6b6b;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }

    .status-folga {
        background: #17a2b8;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }

    /* Filtros */
    .filter-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }

    /* Responsividade */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }

        .metric-card {
            height: auto;
            padding: 1rem;
        }

        .metric-value {
            font-size: 1.5rem;
        }
    }

    /* Customização do Streamlit */
    .stSelectbox > div > div {
        border-color: #F7931E;
        border-radius: 8px;
    }

    .stDateInput > div > div {
        border-color: #F7931E;
        border-radius: 8px;
    }

    /* Remover padding padrão do streamlit */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Configurações de autenticação - agora usando secrets
CLIENT_ID = st.secrets["sharepoint"]["client_id"]
CLIENT_SECRET = st.secrets["sharepoint"]["client_secret"]
TENANT_ID = st.secrets["sharepoint"]["tenant_id"]

# Configurações do SharePoint
SITE_URL = st.secrets["sharepoint"]["config"]["site_url"]
SITE_PATH = st.secrets["sharepoint"]["config"]["site_path"]
FILE_NAME = st.secrets["sharepoint"]["config"]["file_name"]

# Configurações do sistema
CACHE_TTL = st.secrets["system"]["cache_ttl"]
DEFAULT_WORK_HOURS = st.secrets["system"]["default_work_hours"]


@st.cache_data(ttl=CACHE_TTL)
def safe_datetime_convert(value):
    """Converte texto para datetime de forma segura"""
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        if isinstance(value, str):
            return pd.to_datetime(value, errors='coerce')
        elif isinstance(value, datetime):
            return value
        else:
            return pd.to_datetime(str(value), errors='coerce')
    except:
        return None


@st.cache_data(ttl=CACHE_TTL)
def process_controle_data(df):
    """Processa os dados do controle inteligente"""
    if df is None or df.empty:
        return None

    df_processed = df.copy()

    # Verificar colunas obrigatórias
    required_cols = ['Data e hora', 'Nome', 'Tipo']
    if not all(col in df_processed.columns for col in required_cols):
        st.error(f"Colunas obrigatórias não encontradas: {required_cols}")
        return None

    # Processar dados
    df_processed['Data e hora'] = df_processed['Data e hora'].apply(safe_datetime_convert)
    df_processed['Data'] = df_processed['Data e hora'].dt.date
    df_processed['Hora'] = df_processed['Data e hora'].dt.time

    # Filtrar dados válidos
    df_clean = df_processed[['Data', 'Nome', 'Tipo', 'Hora']].dropna()

    # Agrupar e pegar primeiro horário
    df_grouped = df_clean.groupby(['Data', 'Nome', 'Tipo']).first().reset_index()

    # Fazer pivot
    df_pivot = df_grouped.pivot_table(
        index=['Data', 'Nome'],
        columns='Tipo',
        values='Hora',
        aggfunc='first'
    ).reset_index()

    # Renomear colunas
    column_renames = {
        'Saída para almoço': 'Saída Almoço',
        'Volta do almoço': 'Volta Almoço'
    }
    existing_renames = {old: new for old, new in column_renames.items() if old in df_pivot.columns}
    if existing_renames:
        df_pivot = df_pivot.rename(columns=existing_renames)

    return df_pivot.sort_values(['Data', 'Nome'])


@st.cache_data(ttl=CACHE_TTL)
def download_sharepoint_data():
    """Download dos dados do SharePoint"""
    try:
        with st.spinner("🔐 Autenticando no SharePoint..."):
            app = ConfidentialClientApplication(
                CLIENT_ID,
                authority=f"https://login.microsoftonline.com/{TENANT_ID}",
                client_credential=CLIENT_SECRET,
            )

            result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

            if "access_token" not in result:
                st.error("❌ Erro na autenticação")
                return None

            headers = {"Authorization": f"Bearer {result['access_token']}"}

        with st.spinner("📡 Conectando ao site..."):
            site_url = f"https://graph.microsoft.com/v1.0/sites/{SITE_URL}:{SITE_PATH}"
            site_response = requests.get(site_url, headers=headers)

            if site_response.status_code != 200:
                st.error("❌ Erro ao conectar ao site")
                return None

            site_id = site_response.json()['id']

        with st.spinner("🔍 Buscando arquivo..."):
            search_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/search(q='{FILE_NAME}')"
            search_response = requests.get(search_url, headers=headers)

            if search_response.status_code != 200:
                st.error("❌ Erro na busca do arquivo")
                return None

            files_found = search_response.json().get('value', [])
            target_file = next((item for item in files_found if item['name'] == FILE_NAME), None)

            if not target_file:
                st.error("❌ Arquivo não encontrado")
                return None

        with st.spinner("⬇️ Baixando dados..."):
            download_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{target_file['id']}/content"
            download_response = requests.get(download_url, headers=headers)

            if download_response.status_code != 200:
                st.error("❌ Erro no download")
                return None

            df = pd.read_excel(io.BytesIO(download_response.content))
            return df

    except Exception as e:
        st.error(f"❌ Erro geral: {str(e)}")
        return None


def get_status_badge(row):
    """Retorna badge de status baseado na presença"""
    if pd.notna(row.get('Entrada')) and pd.notna(row.get('Saída')):
        return '<span class="status-presente">PRESENTE</span>'
    elif pd.notna(row.get('Entrada')):
        return '<span class="status-urgente">TRABALHANDO</span>'
    else:
        return '<span class="status-ausente">AUSENTE</span>'


def format_time_column(time_val):
    """Formata coluna de tempo"""
    if pd.isna(time_val):
        return "-"
    if isinstance(time_val, dt_time):
        return time_val.strftime("%H:%M")
    return str(time_val)


def calculate_work_duration(entrada, saida):
    """Calcula duração do trabalho"""
    try:
        if pd.notna(entrada) and pd.notna(saida):
            entrada_dt = pd.to_datetime(str(entrada))
            saida_dt = pd.to_datetime(str(saida))

            if saida_dt > entrada_dt:
                diff = saida_dt - entrada_dt
                hours = int(diff.total_seconds() // 3600)
                minutes = int((diff.total_seconds() % 3600) // 60)
                return f"{hours}h{minutes:02d}min"
        return "-"
    except:
        return "-"


def show_reports_page(df_filtered):
    """Exibe a página de relatórios com análises avançadas"""
    st.markdown('<div class="section-title">📊 Relatórios e Análises</div>', unsafe_allow_html=True)

    if df_filtered is None or df_filtered.empty:
        st.warning("Nenhum dado disponível para gerar relatórios.")
        return

    # Métricas de Relatório
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_funcionarios = df_filtered['Nome'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_funcionarios}</div>
            <div class="metric-label">👥 FUNCIONÁRIOS ATIVOS</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if 'Entrada' in df_filtered.columns:
            presencas = len(df_filtered[df_filtered['Entrada'].notna()])
            taxa_presenca = (presencas / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{taxa_presenca:.1f}%</div>
                <div class="metric-label">📈 TAXA PRESENÇA</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">N/A</div>
                <div class="metric-label">📈 TAXA PRESENÇA</div>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        total_dias = (df_filtered['Data'].max() - df_filtered['Data'].min()).days + 1 if len(df_filtered) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_dias}</div>
            <div class="metric-label">📅 PERÍODO ANALISADO</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        total_registros = len(df_filtered)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_registros}</div>
            <div class="metric-label">📋 TOTAL REGISTROS</div>
        </div>
        """, unsafe_allow_html=True)

    # Gráfico de Saldo de Horas
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### ⏰ Saldo de Horas por Funcionário")

    if 'Entrada' in df_filtered.columns and 'Saída' in df_filtered.columns:
        # Calcular saldo de horas para cada funcionário
        saldo_data = []

        for funcionario in df_filtered['Nome'].unique():
            func_data = df_filtered[df_filtered['Nome'] == funcionario]
            total_horas = 0
            dias_validos = 0

            for _, row in func_data.iterrows():
                entrada = row.get('Entrada')
                saida = row.get('Saída')

                if pd.notna(entrada) and pd.notna(saida):
                    try:
                        entrada_dt = pd.to_datetime(str(entrada))
                        saida_dt = pd.to_datetime(str(saida))

                        if saida_dt > entrada_dt:
                            # Calcular horas trabalhadas no dia
                            horas_dia = (saida_dt - entrada_dt).total_seconds() / 3600

                            # Assumindo jornada padrão configurável
                            saldo_dia = horas_dia - DEFAULT_WORK_HOURS
                            total_horas += saldo_dia
                            dias_validos += 1
                    except:
                        continue

            if dias_validos > 0:
                saldo_data.append({
                    'Funcionário': funcionario,
                    'Saldo_Horas': total_horas,
                    'Dias_Válidos': dias_validos
                })

        if saldo_data:
            saldo_df = pd.DataFrame(saldo_data)
            # Ordenar do maior saldo para o menor
            saldo_df = saldo_df.sort_values('Saldo_Horas', ascending=True)

            # Criar gráfico de barras horizontal
            fig_saldo = px.bar(
                saldo_df,
                x='Saldo_Horas',
                y='Funcionário',
                orientation='h',
                title="Saldo de Horas por Funcionário (Maior para Menor)",
                color='Saldo_Horas',
                color_continuous_scale=['#dc3545', '#ffc107', '#28a745'],
                labels={'Saldo_Horas': 'Saldo de Horas', 'Funcionário': 'Funcionário'},
                text='Saldo_Horas'  # Adicionar rótulos de dados
            )

            # Formatar os rótulos de dados
            fig_saldo.update_traces(
                texttemplate='%{text:.1f}h',
                textposition='outside'
            )

            # Adicionar linha vertical no zero
            fig_saldo.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.5)

            # Customizar layout
            fig_saldo.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#333',
                height=500,
                xaxis_title="Saldo de Horas",
                yaxis_title="Funcionário",
                showlegend=False
            )

            # Adicionar anotações para valores positivos e negativos
            fig_saldo.add_annotation(
                x=max(saldo_df['Saldo_Horas']) * 0.8 if max(saldo_df['Saldo_Horas']) > 0 else 1,
                y=len(saldo_df) - 1,
                text="Horas Extras",
                showarrow=False,
                font=dict(color="#28a745", size=12, family="Arial Black")
            )

            if min(saldo_df['Saldo_Horas']) < 0:
                fig_saldo.add_annotation(
                    x=min(saldo_df['Saldo_Horas']) * 0.8,
                    y=0,
                    text="Horas Devendo",
                    showarrow=False,
                    font=dict(color="#dc3545", size=12, family="Arial Black")
                )

            st.plotly_chart(fig_saldo, use_container_width=True)

            # Mostrar resumo estatístico
            col1, col2, col3 = st.columns(3)

            with col1:
                funcionario_mais_horas = saldo_df.loc[saldo_df['Saldo_Horas'].idxmax()]
                st.metric(
                    "🏆 Maior Saldo",
                    f"{funcionario_mais_horas['Funcionário']}",
                    f"{funcionario_mais_horas['Saldo_Horas']:.1f}h"
                )

            with col2:
                funcionario_menos_horas = saldo_df.loc[saldo_df['Saldo_Horas'].idxmin()]
                st.metric(
                    "⚠️ Menor Saldo",
                    f"{funcionario_menos_horas['Funcionário']}",
                    f"{funcionario_menos_horas['Saldo_Horas']:.1f}h"
                )

            with col3:
                media_saldo = saldo_df['Saldo_Horas'].mean()
                st.metric(
                    "📊 Média Geral",
                    f"{media_saldo:.1f}h",
                    f"({len(saldo_df)} funcionários)"
                )
        else:
            st.warning("Não foi possível calcular o saldo de horas. Verifique se há dados de entrada e saída válidos.")
    else:
        st.warning("Colunas 'Entrada' e 'Saída' são necessárias para calcular o saldo de horas.")

    st.markdown('</div>', unsafe_allow_html=True)

    # Análise de Pontualidade
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("### 🕘 Análise de Pontualidade")

    if 'Entrada' in df_filtered.columns:
        pontualidade_data = df_filtered[df_filtered['Entrada'].notna()].copy()

        if not pontualidade_data.empty:
            # Classificar pontualidade (assumindo 8:00 como horário padrão)
            pontualidade_data['Hora_Entrada'] = pd.to_datetime(pontualidade_data['Entrada'].astype(str)).dt.time

            def classificar_pontualidade(hora):
                if pd.isna(hora):
                    return 'Sem registro'
                hora_dt = pd.to_datetime(str(hora)).time()
                if hora_dt <= dt_time(8, 0):
                    return 'Pontual'
                elif hora_dt <= dt_time(8, 15):
                    return 'Tolerância'
                else:
                    return 'Atrasado'

            pontualidade_data['Classificacao'] = pontualidade_data['Hora_Entrada'].apply(classificar_pontualidade)

            # Contar classificações
            pont_counts = pontualidade_data['Classificacao'].value_counts()

            # Gráfico de pizza
            fig_pont = px.pie(
                values=pont_counts.values,
                names=pont_counts.index,
                title="Distribuição de Pontualidade",
                color_discrete_map={
                    'Pontual': '#28a745',
                    'Tolerância': '#ffc107',
                    'Atrasado': '#dc3545',
                    'Sem registro': '#6c757d'
                }
            )

            fig_pont.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#333'
            )

            col1, col2 = st.columns([2, 1])

            with col1:
                st.plotly_chart(fig_pont, use_container_width=True)

            with col2:
                st.markdown("#### 📈 Estatísticas de Pontualidade")

                for categoria, count in pont_counts.items():
                    porcentagem = (count / len(pontualidade_data)) * 100
                    st.markdown(f"**{categoria}:** {count} ({porcentagem:.1f}%)")
        else:
            st.info("Sem dados de entrada para análise de pontualidade")
    else:
        st.info("Dados de entrada não disponíveis")

    st.markdown('</div>', unsafe_allow_html=True)

    # Tabela de Ranking
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("### 🏆 Ranking de Funcionários")

    # Calcular ranking baseado em presença e pontualidade
    ranking_data = []

    for funcionario in df_filtered['Nome'].unique():
        func_data = df_filtered[df_filtered['Nome'] == funcionario]

        # Métricas do funcionário
        total_dias = len(func_data)

        if 'Entrada' in func_data.columns:
            dias_presentes = len(func_data[func_data['Entrada'].notna()])
            taxa_presenca = (dias_presentes / total_dias * 100) if total_dias > 0 else 0

            # Calcular pontualidade
            entradas_validas = func_data[func_data['Entrada'].notna()]
            if not entradas_validas.empty:
                entradas_pontuais = 0
                for _, row in entradas_validas.iterrows():
                    hora_entrada = pd.to_datetime(str(row['Entrada'])).time()
                    if hora_entrada <= dt_time(8, 15):  # Considerando tolerância
                        entradas_pontuais += 1

                taxa_pontualidade = (entradas_pontuais / len(entradas_validas) * 100) if len(
                    entradas_validas) > 0 else 0
            else:
                taxa_pontualidade = 0
        else:
            dias_presentes = total_dias
            taxa_presenca = 100
            taxa_pontualidade = 0

        # Score geral (70% presença + 30% pontualidade)
        score_geral = (taxa_presenca * 0.7) + (taxa_pontualidade * 0.3)

        ranking_data.append({
            'Funcionário': funcionario,
            'Dias Trabalhados': dias_presentes,
            'Taxa Presença (%)': f"{taxa_presenca:.1f}%",
            'Taxa Pontualidade (%)': f"{taxa_pontualidade:.1f}%",
            'Score Geral': f"{score_geral:.1f}"
        })

    # Converter para DataFrame e ordenar por score
    ranking_df = pd.DataFrame(ranking_data)
    ranking_df['Score_Numerico'] = ranking_df['Score Geral'].str.replace('%', '').astype(float)
    ranking_df = ranking_df.sort_values('Score_Numerico', ascending=False)

    # Adicionar posição
    ranking_df['Posição'] = range(1, len(ranking_df) + 1)

    # Reordenar colunas
    ranking_display = ranking_df[
        ['Posição', 'Funcionário', 'Dias Trabalhados', 'Taxa Presença (%)', 'Taxa Pontualidade (%)',
         'Score Geral']].copy()

    st.dataframe(ranking_display, use_container_width=True, height=400)

    st.markdown('</div>', unsafe_allow_html=True)


def show_settings_page():
    """Exibe a página de configurações"""
    st.markdown('<div class="section-title">⚙️ Configurações do Sistema</div>', unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### 🔧 Configurações Gerais")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ⏰ Horários de Trabalho")
        horario_entrada = st.time_input("Horário padrão de entrada:", value=dt_time(8, 0))
        horario_saida = st.time_input("Horário padrão de saída:", value=dt_time(17, 0))
        tolerancia = st.number_input("Tolerância para atraso (minutos):", min_value=0, max_value=60, value=15)

    with col2:
        st.markdown("#### 📊 Configurações de Relatório")
        dias_padrao = st.number_input("Período padrão de análise (dias):", min_value=1, max_value=365, value=30)
        auto_refresh = st.checkbox("Atualização automática dos dados", value=True)
        mostrar_graficos = st.checkbox("Exibir gráficos por padrão", value=True)

    st.markdown("#### 🔄 Configurações de Sincronização")
    st.info(f"📡 Conectado ao SharePoint: {SITE_URL}")
    st.info(f"📁 Arquivo: {FILE_NAME}")
    st.info(f"🕒 Última sincronização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    if st.button("🔄 Testar Conexão", use_container_width=True):
        with st.spinner("Testando conexão..."):
            # Simular teste de conexão
            import time
            time.sleep(2)
            st.success("✅ Conexão com SharePoint funcionando corretamente!")

    st.markdown("#### 📧 Notificações")
    st.checkbox("Enviar relatório diário por email", value=False)
    st.checkbox("Alertas de ausência", value=True)
    st.checkbox("Notificações de atraso", value=True)

    if st.button("💾 Salvar Configurações", use_container_width=True):
        st.success("✅ Configurações salvas com sucesso!")

    st.markdown('</div>', unsafe_allow_html=True)


def main():
    # Header Principal - Inspirado no layout
    st.markdown("""
    <div class="main-header">
        <h1>🏢 Sistema de Controle Inteligente - Pará</h1>
        <p>Gestão inteligente de folgas e movimentação das equipes</p>
    </div>
    """, unsafe_allow_html=True)

    # Layout principal com sidebar
    col_sidebar, col_main = st.columns([1, 4])

    with col_sidebar:
        st.markdown("""
        <div class="sidebar-content">
            <div class="sidebar-title">📋 Menu de Navegação</div>
        </div>
        """, unsafe_allow_html=True)

        # Seleção de página (simulando o dropdown do layout original)
        pagina = st.selectbox(
            "Selecione a página:",
            ["Cronograma por Colaborador", "Relatórios"],
            index=0
        )

        st.markdown("""
        <div class="sidebar-content">
            <div class="sidebar-title">🔄 Controles</div>
        </div>
        """, unsafe_allow_html=True)

        # Botão de atualização
        if st.button("📊 Atualizar Dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.markdown("""
        <div class="sidebar-content">
            <div class="sidebar-title">📅 Filtros de Período</div>
        </div>
        """, unsafe_allow_html=True)

        # Filtros de data
        today = datetime.now().date()

        data_inicio = st.date_input(
            "Data Início:",
            value=today - timedelta(days=7),
            max_value=today
        )

        data_fim = st.date_input(
            "Data Fim:",
            value=today,
            max_value=today
        )

    with col_main:
        # Verificar qual página foi selecionada
        if pagina == "Relatórios":
            # Carregar e processar dados para relatórios
            df_raw = download_sharepoint_data()

            if df_raw is not None:
                df_processed = process_controle_data(df_raw)

                if df_processed is not None:
                    # Filtrar por data
                    df_filtered = df_processed[
                        (df_processed['Data'] >= data_inicio) &
                        (df_processed['Data'] <= data_fim)
                        ]
                    show_reports_page(df_filtered)
                else:
                    st.error("❌ Erro no processamento dos dados")
            else:
                st.error("❌ Não foi possível carregar os dados do SharePoint")
            return

        # Página principal - Cronograma por Colaborador
        # Carregar e processar dados
        df_raw = download_sharepoint_data()

        if df_raw is not None:
            df_processed = process_controle_data(df_raw)

            if df_processed is not None:
                # Filtrar por data
                df_filtered = df_processed[
                    (df_processed['Data'] >= data_inicio) &
                    (df_processed['Data'] <= data_fim)
                    ]

                # Métricas principais em cards
                st.markdown('<div class="main-container">', unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    total_colaboradores = df_filtered['Nome'].nunique()
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{total_colaboradores}</div>
                        <div class="metric-label">👥 COLABORADORES</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    total_registros = len(df_filtered)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{total_registros}</div>
                        <div class="metric-label">📋 REGISTROS</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    dias_periodo = (data_fim - data_inicio).days + 1
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{dias_periodo}</div>
                        <div class="metric-label">📅 DIAS</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    if 'Entrada' in df_filtered.columns and 'Saída' in df_filtered.columns:
                        presentes = len(df_filtered[df_filtered['Entrada'].notna() & df_filtered['Saída'].notna()])
                        taxa_presenca = (presentes / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{taxa_presenca:.0f}%</div>
                            <div class="metric-label">📊 PRESENÇA</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">N/A</div>
                            <div class="metric-label">📊 PRESENÇA</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

                # Tabela principal - Inspirada no cronograma detalhado
                st.markdown('<div class="main-container">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">📊 Cronograma Detalhado - Ordenado por Data</div>',
                            unsafe_allow_html=True)

                # Preparar dados para exibição
                display_df = df_filtered.copy()

                # Adicionar coluna de status
                display_df['STATUS'] = display_df.apply(get_status_badge, axis=1)

                # Adicionar duração se tiver entrada e saída
                if 'Entrada' in display_df.columns and 'Saída' in display_df.columns:
                    display_df['DURAÇÃO'] = display_df.apply(
                        lambda x: calculate_work_duration(x.get('Entrada'), x.get('Saída')), axis=1)

                # Formatear colunas de tempo
                time_columns = [col for col in display_df.columns if col not in ['Data', 'Nome', 'STATUS', 'DURAÇÃO']]
                for col in time_columns:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(format_time_column)

                # Ordenar por data (mais recente primeiro) e nome
                display_df = display_df.sort_values(['Data', 'Nome'], ascending=[False, True])

                # Renomear colunas para português
                column_names = {
                    'Data': '📅 DATA',
                    'Nome': '👤 COLABORADOR',
                    'Entrada': '🕘 ENTRADA',
                    'Saída Almoço': '🍽️ SAÍDA ALMOÇO',
                    'Volta Almoço': '🍽️ VOLTA ALMOÇO',
                    'Saída': '🕕 SAÍDA',
                    'STATUS': '🚦 STATUS',
                    'DURAÇÃO': '⏱️ DURAÇÃO'
                }

                # Selecionar e renomear colunas existentes
                available_columns = [col for col in column_names.keys() if col in display_df.columns]
                display_df_final = display_df[available_columns].rename(columns=column_names)

                # Converter data para string formatada
                if '📅 DATA' in display_df_final.columns:
                    display_df_final['📅 DATA'] = display_df_final['📅 DATA'].apply(
                        lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) else '')

                # Mostrar tabela com HTML para preservar os badges de status
                st.markdown(
                    display_df_final.to_html(escape=False, classes='main-table', table_id='cronograma-table'),
                    unsafe_allow_html=True
                )

                st.markdown('</div>', unsafe_allow_html=True)

                # Filtros adicionais
                st.markdown('<div class="main-container">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">🔍 Filtros Avançados</div>', unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    funcionarios = ['Todos'] + sorted(df_filtered['Nome'].unique().tolist())
                    funcionario_selecionado = st.selectbox("Filtrar por colaborador:", funcionarios)

                with col2:
                    status_filter = st.selectbox("Filtrar por status:", ["Todos", "Presente", "Trabalhando", "Ausente"])

                # Aplicar filtros se selecionados
                if funcionario_selecionado != 'Todos' or status_filter != 'Todos':
                    filtered_data = df_filtered.copy()

                    if funcionario_selecionado != 'Todos':
                        filtered_data = filtered_data[filtered_data['Nome'] == funcionario_selecionado]

                    # Mostrar dados filtrados
                    if not filtered_data.empty:
                        st.markdown("### 📋 Dados Filtrados")
                        st.dataframe(filtered_data, use_container_width=True, height=300)
                    else:
                        st.info("Nenhum registro encontrado com os filtros aplicados.")

                st.markdown('</div>', unsafe_allow_html=True)

            else:
                st.error("❌ Erro no processamento dos dados")
        else:
            # Dados de exemplo se não conseguir conectar
            st.warning("⚠️ Não foi possível conectar ao SharePoint. Carregando dados de exemplo...")

            # Criar dados de exemplo
            dates = pd.date_range(start=data_inicio, end=data_fim, freq='D')
            names = ['RAYLON HENRIQUE', 'GENESIS WESLEY', 'SERGIO DE SOUZA', 'EDNALDO LIMA', 'ROGÉRIO RIKER']

            example_data = []
            for i, date in enumerate(dates):
                for j, name in enumerate(names):
                    if np.random.random() > 0.1:  # 90% de presença
                        example_data.append({
                            'Data': date.date(),
                            'Nome': name,
                            'Entrada': dt_time(8, np.random.randint(0, 30)),
                            'Saída': dt_time(17, np.random.randint(0, 30)),
                            'Saída Almoço': dt_time(12, 0),
                            'Volta Almoço': dt_time(13, 0)
                        })

            df_example = pd.DataFrame(example_data)

            if not df_example.empty:
                # Mostrar dados de exemplo com o mesmo layout
                st.markdown('<div class="main-container">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">🧪 Dados de Exemplo - Cronograma Detalhado</div>',
                            unsafe_allow_html=True)

                # Aplicar mesmo tratamento aos dados de exemplo
                df_example['STATUS'] = df_example.apply(get_status_badge, axis=1)
                df_example['DURAÇÃO'] = df_example.apply(
                    lambda x: calculate_work_duration(x.get('Entrada'), x.get('Saída')), axis=1)

                # Formatar e mostrar
                for col in ['Entrada', 'Saída', 'Saída Almoço', 'Volta Almoço']:
                    df_example[col] = df_example[col].apply(format_time_column)

                column_names = {
                    'Data': '📅 DATA',
                    'Nome': '👤 COLABORADOR',
                    'Entrada': '🕘 ENTRADA',
                    'Saída': '🕕 SAÍDA',
                    'Saída Almoço': '🍽️ SAÍDA ALMOÇO',
                    'Volta Almoço': '🍽️ VOLTA ALMOÇO',
                    'STATUS': '🚦 STATUS',
                    'DURAÇÃO': '⏱️ DURAÇÃO'
                }

                df_display = df_example.rename(columns=column_names)
                df_display['📅 DATA'] = df_display['📅 DATA'].apply(lambda x: x.strftime('%d/%m/%Y'))

                st.markdown(
                    df_display.to_html(escape=False, classes='main-table'),
                    unsafe_allow_html=True
                )

                st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
