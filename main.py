import io
import socket
import urllib.request
import zipfile
import pandas as pd
old_getaddrinfo = socket.getaddrinfo
def ipv4_only_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [r for r in responses if r[0] == socket.AF_INET]
socket.getaddrinfo = ipv4_only_getaddrinfo
try:
    df = pd.read_csv("world_bank_inflation.csv")
    print("Файл 'world_bank_inflation.csv' успішно завантажено.")
except FileNotFoundError:
    print("Помилка: файл 'world_bank_inflation.csv' не знайдено.")
    exit()
def load_wb_csv_indicator(indicator_code, col_name):
    url = f"https://api.worldbank.org/v2/en/indicator/{indicator_code}?downloadformat=csv"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            zip_bytes = io.BytesIO(response.read())

        with zipfile.ZipFile(zip_bytes) as zf:
            csv_name = [n for n in zf.namelist() if n.startswith("API_") and n.endswith(".csv")][0]
            with zf.open(csv_name) as f:
                raw_df = pd.read_csv(f, skiprows=4)
        year_cols = [str(y) for y in range(2010, 2020) if str(y) in raw_df.columns]
        long_df = raw_df.melt(
            id_vars=["Country Name"],
            value_vars=year_cols,
            var_name="Year",
            value_name=col_name
        ).rename(columns={"Country Name": "Country"})
        long_df["Year"] = long_df["Year"].astype(int)
        long_df[col_name] = pd.to_numeric(long_df[col_name], errors="coerce")
        print(f"Показник '{col_name}' успішно завантажено.")
        return long_df
    except Exception as e:
        print(f"Помилка завантаження {col_name}: {e}")
        return None
df_gdp = load_wb_csv_indicator("NY.GDP.PCAP.CD", "GDP_per_capita")
df_unemp = load_wb_csv_indicator("SL.UEM.TOTL.ZS", "Unemployment_rate")
if df_gdp is None or df_unemp is None:
    print("Не вдалося завантажити дані. Перевірте, чи не блокує антивірус/фаєрвол доступ Python до мережі.")
    exit()
df = df.merge(df_gdp, on=["Country", "Year"], how="left")
df = df.merge(df_unemp, on=["Country", "Year"], how="left")
df.to_csv("world_bank_inflation_extended.csv", index=False)
#БАЗОВИЙ АНАЛІЗ ОДЕРЖАНИХ ДАНИХ
print("\n--- Початкові дані ---")
print(df)
print("\n--- Перші 3 рядки DataFrame (df.head(3)) ---")
print(df.head(3))
print("\n--- Типи даних у стовпцях (df.dtypes) ---")
print(df.dtypes)
print("\n--- Кількість рядків і стовпців (df.shape) ---")
print(df.shape)
print("\n--- Описова статистика для числових даних (df.describe()) ---")
print(df.describe())
#ПОПЕРЕДНЄ ОБРОБЛЕННЯ ДАНИХ
df["Year"] = df["Year"].astype(int)
df_clean = df.dropna(subset=["Inflation_annual_percent"]).copy()
df_clean["Misery_index"] = (
    df_clean["Inflation_annual_percent"] + df_clean["Unemployment_rate"]
).round(2)
print("\n--- DataFrame з новим розрахунковим стовпцем (Misery_index) ---")
print(df_clean.head(5))
filtered_df = df_clean[df_clean["Inflation_annual_percent"] > 10].copy()
print(f"\n--- Результат фільтрації (Інфляція > 10%, записів: {len(filtered_df)}) ---")
print(filtered_df.head(10))
sorted_df = filtered_df.sort_values(
    by="Inflation_annual_percent",
    ascending=False
)
print("\n--- Результат сортування (Топ-10 за найвищою інфляцією) ---")
print(sorted_df.head(10))
#АНАЛІЗ ДАНИХ ЗА ДОПОМОГОЮ ГРУПУВАННЯ
grouped_df = df_clean.groupby("Country").agg(
    Mean_Inflation=("Inflation_annual_percent", "mean"),
    Min_Inflation=("Inflation_annual_percent", "min"),
    Max_Inflation=("Inflation_annual_percent", "max"),
    Mean_GDP_per_capita=("GDP_per_capita", "mean"),
    Mean_Misery_Index=("Misery_index", "mean")
).round(2).reset_index()
print("\n--- Результат групування за країнами (перші 10) ---")
print(grouped_df.head(10))
print(f"\nКількість унікальних країн/регіонів: {df_clean['Country'].nunique()}")
print(f"Кількість унікальних років: {df_clean['Year'].nunique()}")
grouped_df.to_csv("inflation_analysis_results.csv", index=False)
print("\nРезультати успішно збережено у файл 'inflation_analysis_results.csv'.")