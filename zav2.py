import glob
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use("ggplot")
plt.rcParams["figure.figsize"] = (12, 5)
csv_files = glob.glob("*2017*.csv")
if not csv_files:
    raise FileNotFoundError(
        "CSV-файл за 2017 рік не знайдено! Завантажте його з donnees.montreal.ca у папку зі скриптом."
    )
file_path = csv_files[0]
print(f"Використовується файл: {file_path}")
try:
    df = pd.read_csv(file_path, sep=None, engine="python", encoding="utf-8")
except UnicodeDecodeError:
    df = pd.read_csv(file_path, sep=None, engine="python", encoding="latin1")
df = df.dropna(axis=1, how="all")
#ПЕРВИННИЙ АНАЛІЗ ОТРИМАНОГО DATAFRAME
print("\n--- Перші 5 рядків (df.head()) ---")
print(df.head())
print("\n--- Інформація про структуру DataFrame (df.info()) ---")
print(df.info())
print("\n--- Описова статистика (df.describe()) ---")
print(df.describe())
#ПІДГОТОВКА ДАТИ ТА ФІЛЬТРАЦІЯ ЗА 2017 РІК
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, format="mixed")
df_2017 = df[df["Date"].dt.year == 2017].copy()
bike_paths = df_2017.select_dtypes(include="number").columns.tolist()
#ОБРОБЛЕННЯ ОДЕРЖАНИХ ДАНИХ
total_by_path = df_2017[bike_paths].sum().sort_values(ascending=False)
total_all_2017 = int(total_by_path.sum())
print("\n--- Кількість велосипедистів за 2017 рік по кожній велодоріжці ---")
print(total_by_path.astype(int))
print(f"\nЗагальна кількість велосипедистів на всіх велодоріжках за 2017 рік: {total_all_2017:,}")
df_2017["Month"] = df_2017["Date"].dt.month
month_names = {
    1: "Січень", 2: "Лютий", 3: "Березень", 4: "Квітень",
    5: "Травень", 6: "Червень", 7: "Липень", 8: "Серпень",
    9: "Вересень", 10: "Жовтень", 11: "Листопад", 12: "Грудень"
}
preferred_paths = ["Berri1", "Maisonneuve_2", "Parc"]
selected_three = [p for p in preferred_paths if p in bike_paths]
if len(selected_three) < 3:
    selected_three = bike_paths[:3]
monthly_three = df_2017.groupby("Month")[selected_three].sum()
print("\n--- Найбільш популярний місяць для трьох обраних велодоріжок (2017 р.) ---")
for path in selected_three:
    best_month_num = int(monthly_three[path].idxmax())
    best_month_count = int(monthly_three[path].max())
    print(
        f"• {path}: {month_names[best_month_num]} "
        f"(місяць №{best_month_num}) — {best_month_count:,} велосипедистів"
    )
chosen_path = selected_three[0]  # наприклад, Berri1
monthly_dynamics = df_2017.groupby("Month")[chosen_path].agg(
    Загальна_кількість="sum",
    Середнє_за_день="mean",
    Максимум_за_день="max",
    Мінімум_за_день="min",
    Кількість_днів="count"
).round(1)
monthly_dynamics["Зміна_до_попер_міс_%"] = (
    monthly_dynamics["Загальна_кількість"].pct_change() * 100
).round(1)
monthly_dynamics.index = [month_names[m] for m in monthly_dynamics.index]
print(f"\n--- Динаміка використання велодоріжки '{chosen_path}' за місяцями 2017 року ---")
print(monthly_dynamics)
#ПОБУДОВА ГРАФІКА ЗА МІСЯЦЯМИ
monthly_counts = df_2017.groupby("Month")[chosen_path].sum()
labels = [month_names[m] for m in monthly_counts.index]
fig, ax = plt.subplots(figsize=(12, 5))
bars = ax.bar(labels, monthly_counts.values, color="#2b8cbe", edgecolor="black", alpha=0.85, label="Кількість за місяць")
ax.plot(labels, monthly_counts.values, color="#d95f0e", marker="o", linewidth=2, label="Тренд зміни")
for bar in bars:
    height = bar.get_height()
    ax.annotate(
        f"{int(height):,}",
        xy=(bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, 4),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=9
    )
ax.set_title(f"Динаміка кількості велосипедистів на велодоріжці '{chosen_path}' за місяцями (2017 рік)", fontsize=13)
ax.set_xlabel("Місяць", fontsize=11)
ax.set_ylabel("Кількість велосипедистів", fontsize=11)
ax.legend()
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig("cyclists_2017_monthly.png", dpi=150)
plt.show()