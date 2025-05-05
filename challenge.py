# Importando bibliotecas
import pandas as pd
import requests
import matplotlib.pyplot as plt


url = "https://apisidra.ibge.gov.br/values/t/7524/n1/all/v/29,1988/p/all/c12716/115236/c1835/72206"
 
response = requests.get(url)
data = response.json()


dados_limpos = data[1:]
df = pd.DataFrame(dados_limpos)
df.head()


# Tratando colunas
df['V'] = df['V'].astype(str)
df['V'] = df['V'].replace('-', pd.NA)

df['V'] = df['V'].replace('.', '').replace(',', '.')
df['V'] = pd.to_numeric(df['V'], errors='coerce')

print('Verificando valores nulos:',df.isna().sum())
print('\n Verificando tipos das colunas:\n')
df.info()


ovos = df[df['D2C'] == '29'][['D3C', 'V']].copy()
ovos.rename(columns={'V': 'ovos_incubados'}, inplace=True)

galinhas = df[df['D2C'] == '1988'][['D3C', 'V']].copy()
galinhas.rename(columns={'V': 'galinhas_poedeiras'}, inplace=True)

base = pd.merge(ovos, galinhas, on='D3C')

print("Datas com ovos:", ovos.shape[0])
print("Datas com galinhas:", galinhas.shape[0])

datas_comuns = pd.merge(ovos[['D3C']], galinhas[['D3C']], on='D3C')
print("Datas com ambos os dados:", datas_comuns.shape[0])

base = base.dropna()
base.head()

# Usando os dados trimestral
base_trimestral = base.copy()
yield_mensal = base_trimestral['ovos_incubados'] / base_trimestral['galinhas_poedeiras']
base_trimestral['yield'] = yield_mensal

base_trimestral['yield_ma12'] = base_trimestral['yield'].rolling(window=12).mean()
base_trimestral['ma_galinhas'] = base_trimestral['galinhas_poedeiras'].rolling(12).mean()

base_trimestral['D3C'] = pd.to_datetime(base_trimestral['D3C'], format='%Y%m')
base_trimestral['ano'] = base_trimestral['D3C'].dt.year

base_trimestral.head()

# Mudando os dados trimestres para mensal
min_date = pd.to_datetime(base['D3C'], format='%Y%m').min()
print(min_date)
max_date = pd.to_datetime(base['D3C'], format='%Y%m').max()
print(max_date)

df_meses = pd.DataFrame({'meses': pd.date_range(start=min_date, end=max_date, freq='MS')})
df_meses['D3C'] = df_meses['meses'].dt.year.astype(str) + '0' +df_meses['meses'].dt.to_period('Q').dt.quarter.astype(str)

base[['ovos_incubados', 'galinhas_poedeiras']] = base[['ovos_incubados', 'galinhas_poedeiras']] / 3
base['yield'] = base['ovos_incubados'] / base['galinhas_poedeiras']
base_monthly = base.merge(df_meses, how='left', on=['D3C'])

base_monthly.head()

# Gráfico de média móvel mensal
# MENSAL
base_monthly['ma_galinhas'] = base_monthly['galinhas_poedeiras'].rolling(12).mean().round(2)
ma_em_milhoes = base_monthly['ma_galinhas'] / 1_000_000

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(base_monthly['meses'], ma_em_milhoes, label='Moving average (12 months)', color='#E60000', linewidth=1.5)
ax.set_title('Chicken breeder herd over time – last 12 months moving average', fontsize=14, weight='bold')
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Number of Chicken breeder (millions)', fontsize=12)

ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.ticklabel_format(style='plain', axis='y')
ax.yaxis.get_offset_text().set_visible(False)

ax.legend()
plt.tight_layout()
#plt.show()

# Gerando gráfico média móvel trimestral
# TRIMESTRAL
base_trimestral['ma_galinhas'] = base_trimestral['galinhas_poedeiras'].rolling(12).mean().round(2)
ma_em_milhoes = base_trimestral['ma_galinhas'] / 1_000_000

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(base_trimestral['D3C'], ma_em_milhoes, label='Moving average (12 months)', color='#E60000', linewidth=1.5)
ax.set_title('Chicken breeder herd over time – last 12 months moving average', fontsize=14, weight='bold')
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Number of Chicken breeder (millions)', fontsize=12)

ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.ticklabel_format(style='plain', axis='y')
ax.yaxis.get_offset_text().set_visible(False)

ax.legend()
plt.tight_layout()
#plt.show()


# Gráfico móvel 12 meses
# MENSAL
base_monthly['galinhas_milhoes'] = base_monthly['galinhas_poedeiras'] / 1_000_000
base_monthly['ma_galinhas_milhoes'] = base_monthly['ma_galinhas'] / 1_000_000

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(base_monthly['meses'], base_monthly['galinhas_milhoes'], label='Monthly', color='#E60000', alpha=0.8)
ax.plot(base_monthly['meses'], base_monthly['ma_galinhas_milhoes'], label='Moving average (12 months)', color='gray', linewidth=1.5)

ax.set_title('Chicken breeder herd over time – last 12 months moving average', fontsize=14, weight='bold')
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Number of Chicken breeder (millions)', fontsize=12)

ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.ticklabel_format(style='plain', axis='y')
ax.yaxis.get_offset_text().set_visible(False)
ax.legend()

plt.savefig('mensal_chiken_breeder.png', dpi=300, bbox_inches='tight')
plt.tight_layout()
#plt.show()

# Gráfico móvel 12 meses trimestral
# TRIMESTRAL
base_trimestral['galinhas_milhoes'] = base_trimestral['galinhas_poedeiras'] / 1_000_000
base_trimestral['ma_galinhas_milhoes'] = base_trimestral['ma_galinhas'] / 1_000_000

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(base_trimestral['D3C'], base_trimestral['galinhas_milhoes'], label='Mensal', color='#E60000', alpha=0.8)
ax.plot(base_trimestral['D3C'], base_trimestral['ma_galinhas_milhoes'], label='Média Móvel (12 meses)', color='gray', linewidth=1.5)

ax.set_title('Galinhas Poedeiras – Série Mensal e Média Móvel de 12 Meses', fontsize=14, weight='bold')
ax.set_xlabel('Ano', fontsize=12)
ax.set_ylabel('Número de Galinhas Poedeiras (milhões)', fontsize=12)

ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.ticklabel_format(style='plain', axis='y')
ax.yaxis.get_offset_text().set_visible(False)
ax.legend()

plt.tight_layout()
#plt.show()

# Crescimento YoY mensal
# Year-over-Year Growth of Hatching Egg Production
tabela_yield_monthly = base_monthly[['D3C', 'ovos_incubados', 'galinhas_poedeiras', 'yield']].copy()

tabela_yield_monthly['ovos_incubados'] = tabela_yield_monthly['ovos_incubados'].round(0).astype('Int64')
tabela_yield_monthly['galinhas_poedeiras'] = tabela_yield_monthly['galinhas_poedeiras'].round(0).astype('Int64')
tabela_yield_monthly['yield'] = (tabela_yield_monthly['yield'] * 100).round(2)

tabela_yield_monthly.columns = ['D3C', 'Ovos Incubados', 'Galinhas Poedeiras', 'Yield (%)']
tabela_yield_monthly

# Figure 1 - Year-over-Year Growth of Hatching Egg Production
ovos_por_ano = base_trimestral.groupby('ano')['ovos_incubados'].sum().reset_index()

ovos_por_ano['crescimento_yoy'] = ovos_por_ano['ovos_incubados'].pct_change() * 100
ovos_por_ano['crescimento_yoy'] = ovos_por_ano['crescimento_yoy'].round(2)

fig, ax = plt.subplots(figsize=(12, 5))

ax.bar(ovos_por_ano['ano'], ovos_por_ano['crescimento_yoy'], color='#E60000', alpha=0.8)
ax.axhline(0, color='#D3D3D3', linestyle='--')

ax.set_title('YoY Growth of Hatching Egg Production', fontsize=14, weight='bold')
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Growth YoY (%)', fontsize=12)

ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.ticklabel_format(style='plain', axis='y')
ax.yaxis.get_offset_text().set_visible(False)

for i, row in ovos_por_ano.iterrows():
    valor = row['crescimento_yoy']
    if pd.notnull(valor):
        ax.text(row['ano'], valor, f'{valor:.1f}%', ha='center', va='bottom', fontsize=10)

plt.savefig('yoy_growth_production.png', dpi=300, bbox_inches='tight')
plt.tight_layout()
#plt.show()


# Média móvel yield
base_monthly['yield_pct'] = base_monthly['yield'] * 100
base_monthly['yield_ma12'] = base_monthly['yield'].rolling(window=12).mean()
base_monthly['yield_ma12_pct'] = base_monthly['yield_ma12'] * 100

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(base_monthly['meses'], base_monthly['yield_pct'], label='Monthly Yield (%)', color='gray', alpha=0.4)
ax.plot(base_monthly['meses'],base_monthly['yield_ma12_pct'],label='Moving average (12 months)',color='#C8102E',linewidth=2)

ax.set_title('The last 12 months moving average of yield per breeder', fontsize=14, weight='bold')
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Yield (%)', fontsize=12)

ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.ticklabel_format(style='plain', axis='y')
ax.yaxis.get_offset_text().set_visible(False)
ax.legend()

plt.savefig('moving_average_yield.png', dpi=300, bbox_inches='tight')
plt.tight_layout()
plt.show()