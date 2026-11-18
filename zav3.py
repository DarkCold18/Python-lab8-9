import string
import nltk
import matplotlib.pyplot as plt
from nltk.corpus import gutenberg, stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer
resources = ["gutenberg", "punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"]
for res in resources:
    nltk.download(res, quiet=True)
print("Доступні тексти в архіві Project Gutenberg:")
print(gutenberg.fileids())
file_id = "milton-paradise.txt"
raw_text = gutenberg.raw(file_id)
# Токенізація тексту за допомогою word_tokenize()
tokens = word_tokenize(raw_text)
#КІЛЬКІСТЬ СЛІВ ТА УНІКАЛЬНИХ СЛІВ (ПОРІВНЯННЯ)
total_tokens = len(tokens)
unique_tokens = len(set(tokens))
words_only = [w.lower() for w in tokens if w.isalpha()]
total_words = len(words_only)
unique_words = len(set(words_only))
ttr_ratio = (unique_words / total_words) * 100
avg_repeats = total_words / unique_words
print(f"\n--- Статистика тексту '{file_id}' ---")
print(f"Загальна кількість токенів (разом із пунктуацією): {total_tokens}")
print(f"Кількість унікальних токенів: {unique_tokens}")
print(f"Загальна кількість слів (лише буквені слова): {total_words}")
print(f"Кількість унікальних слів (без урахування регістру): {unique_words}")
print(f"Порівняння: унікальні слова становлять {ttr_ratio:.2f}% від загальної кількості слів.")
print(f"У середньому кожне унікальне слово повторюється в тексті {avg_repeats:.2f} раза.")
#10 НАЙБІЛЬШ УЖИВАНИХ СЛІВ (ДО ОЧИЩЕННЯ) ТА ДІАГРАМА
fdist_raw = FreqDist(tokens)
top_10_raw = fdist_raw.most_common(10)
print("\n10 найбільш уживаних токенів у початковому тексті:")
for word, count in top_10_raw:
    print(f"  {word!r}: {count}")
words_raw, counts_raw = zip(*top_10_raw)
plt.figure(figsize=(10, 5))
bars1 = plt.bar(words_raw, counts_raw, color="#4C72B0", edgecolor="black")
plt.title(f"Топ-10 найбільш уживаних токенів у '{file_id}' (до очищення)", fontsize=12)
plt.xlabel("Токени / слова", fontsize=11)
plt.ylabel("Частота вживання", fontsize=11)
plt.grid(axis="y", linestyle="--", alpha=0.6)
for bar in bars1:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 50, str(yval), ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.savefig("top10_raw_milton.png", dpi=150)
plt.show()
#ВИДАЛЕННЯ СТОП-СЛІВ І ПУНКТУАЦІЇ ТА ДІАГРАМА
stop_words = set(stopwords.words("english"))
table = str.maketrans("", "", string.punctuation)
cleaned_words = [
    word.translate(table).lower()
    for word in tokens
]
cleaned_words = [
    word for word in cleaned_words
    if word.isalpha() and word not in stop_words
]
fdist_clean = FreqDist(cleaned_words)
top_10_clean = fdist_clean.most_common(10)
print("\n10 найбільш уживаних слів після видалення стоп-слів та пунктуації:")
for word, count in top_10_clean:
    print(f"  {word!r}: {count}")
words_clean, counts_clean = zip(*top_10_clean)
plt.figure(figsize=(10, 5))
bars2 = plt.bar(words_clean, counts_clean, color="#55A868", edgecolor="black")
plt.title(f"Топ-10 найбільш уживаних слів у '{file_id}' (без стоп-слів і пунктуації)", fontsize=12)
plt.xlabel("Слова", fontsize=11)
plt.ylabel("Частота вживання", fontsize=11)
plt.grid(axis="y", linestyle="--", alpha=0.6)
for bar in bars2:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 5, str(yval), ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.savefig("top10_clean_milton.png", dpi=150)
plt.show()
#ЛЕМАТИЗАЦІЯ СЛІВ ТА 10 НАЙБІЛЬШ УЖИВАНИХ СЛІВ
lemmatizer = WordNetLemmatizer()
lemmatized_words = [lemmatizer.lemmatize(word) for word in cleaned_words]
fdist_lemma = FreqDist(lemmatized_words)
top_10_lemma = fdist_lemma.most_common(10)
print("\n10 найбільш уживаних слів після лематизації:")
for word, count in top_10_lemma:
    print(f"  {word!r}: {count}")