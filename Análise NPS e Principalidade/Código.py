# ==============================================================================
# SCRIPT DE ANÁLISE ESTRATÉGICA: NPS VS PRINCIPALIDADE
# Autor: Gemini Advanced (Baseado na solicitação do usuário)
# Data: 04/12/2025
# ==============================================================================

# --- 1. IMPORTAÇÃO DE BIBLIOTECAS ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

# Configuração de Estilo dos Gráficos
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# --- 2. CARREGAMENTO E SANEAMENTO DE DADOS ---

def clean_float(x):
    """Converte strings de porcentagem (ex: '45,5%') para float (45.5)."""
    if isinstance(x, str):
        return float(x.replace('%', '').replace(',', '.').strip())
    return x

def load_data():
    """Carrega os arquivos CSV tentando diferentes encodings."""
    try:
        df_n = pd.read_csv('NPS.csv', sep=';', encoding='utf-8')
        df_p = pd.read_csv('Principalidade.csv', sep=';', encoding='utf-8')
    except UnicodeDecodeError:
        df_n = pd.read_csv('NPS.csv', sep=';', encoding='latin1')
        df_p = pd.read_csv('Principalidade.csv', sep=';', encoding='latin1')
    return df_n, df_p

print(">>> Carregando e limpando dados...")
df_nps, df_princ = load_data()

# Limpeza NPS
df_nps = df_nps.dropna(subset=['Agência'])
# Remove linhas de totais
df_nps = df_nps[~df_nps['Agência'].str.contains('Total', case=False, na=False)] 
cols_nps = ['NPS', '% Detrator', '% Promotor', '% Neutro']
for col in cols_nps:
    if col in df_nps.columns:
        df_nps[col] = df_nps[col].apply(clean_float)

# Limpeza Principalidade
df_princ = df_princ.dropna(subset=['Agência'])
cols_princ = ['GERAL', 'PF', 'PJ', 'AGRO']
for col in cols_princ:
    if col in df_princ.columns:
        df_princ[col] = df_princ[col].apply(clean_float)

# Merge (Junção das tabelas)
df = pd.merge(df_nps[['Agência', 'NPS', '% Detrator', 'Pesquisados']], 
              df_princ[['Agência', 'GERAL', 'PF', 'PJ', 'AGRO']], 
              on='Agência', how='inner')

# Filtro de Robustez (Remove agências sem pesquisas)
df = df[df['Pesquisados'] > 0]
print(f"Base final pronta: {len(df)} agências analisadas.\n")

# ==============================================================================
# 3. ANÁLISES ESTATÍSTICAS E HIPÓTESES
# ==============================================================================

# --- H1: Correlação Geral (NPS x Principalidade) ---
r_spearman, p_val_h1 = stats.spearmanr(df['GERAL'], df['NPS'])
model_ols = sm.OLS(df['NPS'], sm.add_constant(df['GERAL'])).fit()

print(f"--- H1: CORRELAÇÃO GERAL ---")
print(f"Coeficiente Spearman: {r_spearman:.4f}")
print(f"P-Valor: {p_val_h1:.4f}")
print(f"R2 (Regressão): {model_ols.rsquared:.4f}")

# Gráfico H1
plt.figure()
sns.regplot(data=df, x='GERAL', y='NPS', line_kws={'color':'red', 'linestyle':'--'})
plt.title(f'H1: Dispersão NPS vs Principalidade (R={r_spearman:.2f})')
plt.xlabel('Principalidade Geral (%)')
plt.ylabel('NPS')
plt.tight_layout()
plt.savefig('analise_h1_dispersao.png')
print("Gráfico H1 salvo como 'analise_h1_dispersao.png'")

# --- H2: Análise de Detratores ---
median_princ = df['GERAL'].median()
df['Nivel_Princ'] = np.where(df['GERAL'] >= median_princ, 'Alta', 'Baixa')
detratores_alta = df[df['Nivel_Princ']=='Alta']['% Detrator'].mean()
detratores_baixa = df[df['Nivel_Princ']=='Baixa']['% Detrator'].mean()

print(f"\n--- H2: DETRATORES ---")
print(f"Média Detratores (Baixa Princ): {detratores_baixa:.2f}%")
print(f"Média Detratores (Alta Princ): {detratores_alta:.2f}%")

# Gráfico H2
plt.figure()
sns.barplot(x=['Baixa Principalidade', 'Alta Principalidade'], 
            y=[detratores_baixa, detratores_alta], palette='viridis')
plt.title('H2: Impacto do Vínculo Financeiro na Insatisfação')
plt.ylabel('% Média de Detratores')
plt.tight_layout()
plt.savefig('analise_h2_detratores.png')

# --- H3: Impacto por Segmento (Random Forest) ---
X = df[['PF', 'PJ', 'AGRO']]
y = df['NPS']
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X, y)
importances = pd.Series(rf.feature_importances_, index=X.columns)

print(f"\n--- H3: SEGMENTAÇÃO (Feature Importance) ---")
print(importances.sort_values(ascending=False).to_string())

# Correlações individuais
print("Correlações de Spearman por Segmento:")
print(df[['PF', 'PJ', 'AGRO', 'NPS']].corr(method='spearman')['NPS'])

# --- H4: Gap de Monetização (Análise Inversa) ---
df['Faixa_NPS'] = pd.cut(df['NPS'], bins=[-1, 50, 75, 101], labels=['Crítico', 'Neutro', 'Excelência'])
monetizacao = df.groupby('Faixa_NPS', observed=False)['GERAL'].mean()

print(f"\n--- H4: GAP DE MONETIZAÇÃO ---")
print(monetizacao.to_string())

# Gráfico H4
plt.figure()
sns.boxplot(data=df, x='Faixa_NPS', y='GERAL', palette='Oranges')
plt.title('H4: Principalidade Média por Nível de Satisfação')
plt.ylabel('Principalidade Geral (%)')
plt.tight_layout()
plt.savefig('analise_h4_gap.png')

# ==============================================================================
# 4. CLUSTERIZAÇÃO ESTRATÉGICA (MATRIZ K-MEANS)
# ==============================================================================

print(f"\n--- CLUSTERIZAÇÃO DE AGÊNCIAS ---")
# Normalização dos dados
scaler = StandardScaler()
X_cluster = scaler.fit_transform(df[['GERAL', 'NPS']])

# K-Means com 4 clusters
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X_cluster)

# Lógica para nomear os clusters dinamicamente baseada nos centróides
summary = df.groupby('Cluster')[['GERAL', 'NPS']].mean()
global_nps = df['NPS'].mean()
global_princ = df['GERAL'].mean()

def nomear_cluster(row):
    if row['NPS'] > global_nps and row['GERAL'] > global_princ: return 'OURO (Alto NPS/Alta Princ)'
    if row['NPS'] > global_nps and row['GERAL'] <= global_princ: return 'POTENCIAL (Alto NPS/Baixa Princ)'
    if row['NPS'] <= global_nps and row['GERAL'] > global_princ: return 'RISCO (Baixo NPS/Alta Princ)'
    return 'CRÍTICO (Baixo NPS/Baixa Princ)'

mapa_nomes = {i: nomear_cluster(summary.iloc[i]) for i in range(4)}
df['Grupo_Estrategico'] = df['Cluster'].map(mapa_nomes)

# Gráfico da Matriz
plt.figure(figsize=(12, 8))
sns.scatterplot(data=df, x='GERAL', y='NPS', hue='Grupo_Estrategico', style='Grupo_Estrategico', 
                s=150, palette='deep', alpha=0.9)
plt.axhline(global_nps, color='gray', linestyle='--')
plt.axvline(global_princ, color='gray', linestyle='--')
plt.title('Matriz Tática de Agências (Clusters)')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('analise_matriz_clusters.png')
print("Gráfico da Matriz salvo como 'analise_matriz_clusters.png'")

# Exportar lista final
df_export = df[['Agência', 'Grupo_Estrategico', 'NPS', 'GERAL', 'PF', 'PJ', 'AGRO']].sort_values(['Grupo_Estrategico', 'Agência'])
df_export.to_csv('Resultado_Analise_Agencias.csv', index=False, sep=';', encoding='utf-8-sig')
print("Arquivo final exportado: 'Resultado_Analise_Agencias.csv'")

# Exibir prévia do Grupo de Risco
print("\n>>> AGÊNCIAS EM GRUPO DE RISCO (Prioridade):")
print(df[df['Grupo_Estrategico'].str.contains('RISCO')][['Agência', 'NPS', 'GERAL']].to_string(index=False))

# ==============================================================================
# COMPLEMENTO: TESTES DE VALIDAÇÃO ESTATÍSTICA (P-VALORES)
# Cole este trecho no seu script para gerar os números de confiabilidade
# ==============================================================================

print("\n>>> RODANDO TESTES DE VALIDAÇÃO ESTATÍSTICA (Significância)...")

# 1. TESTE T DE STUDENT (Para H2 - Detratores)
# Valida se a diferença de detratores entre Alta e Baixa Principalidade é real
grupo_alta = df[df['Nivel_Princ'] == 'Alta']['% Detrator']
grupo_baixa = df[df['Nivel_Princ'] == 'Baixa']['% Detrator']

# O teste assume variâncias diferentes (Welch's t-test)
t_stat, p_val_ttest = stats.ttest_ind(grupo_baixa, grupo_alta, equal_var=False)

print(f"   [H2] Teste T (Detratores): P-Valor = {p_val_ttest:.4f}")
if p_val_ttest < 0.10:
    print("   -> Resultado: A diferença é estatisticamente relevante (confiável).")
else:
    print("   -> Resultado: A diferença pode ser obra do acaso (não significativa).")

# 2. ANOVA ONE-WAY (Para H4 - Monetização)
# Valida se existe diferença real de dinheiro entre os grupos de NPS
grupo_critico = df[df['Faixa_NPS'] == 'Crítico']['GERAL']
grupo_neutro = df[df['Faixa_NPS'] == 'Neutro']['GERAL']
grupo_excelencia = df[df['Faixa_NPS'] == 'Excelência']['GERAL']

f_stat, p_val_anova = stats.f_oneway(grupo_critico, grupo_neutro, grupo_excelencia)

print(f"   [H4] ANOVA (Monetização): P-Valor = {p_val_anova:.4f}")
if p_val_anova < 0.10:
    print("   -> Resultado: Os grupos têm níveis de principalidade diferentes.")
else:
    print("   -> Resultado: Não há prova estatística de que o NPS muda a principalidade (Gap confirmado).")
print("==============================================================================\n")
