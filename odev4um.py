import sqlite3

connection = sqlite3.connect("kullani_metinler.db")

with connection:
    connection.execute("""
    CREATE TABLE IF NOT EXISTS metinler (
        id INTEGER PRIMARY KEY,
        metin TEXT
    )
    """)

metin1 = input("Birinci metni girin: ")
metin2 = input("İkinci metni girin: ")

with connection:
    connection.execute("INSERT INTO metinler (metin) VALUES (?)", (metin1,))
    connection.execute("INSERT INTO metinler (metin) VALUES (?)", (metin2,))

with connection:
    result = connection.execute("SELECT * FROM metinler").fetchall()

print("Eklenen metinler:")
for row in result:
    print(f"ID: {row[0]}, Metin: {row[1]}")

uzunluk_farki = abs(len(metin1) - len(metin2))

# Uzun olan diziye uygun hale getirmek için kısa diziyi uzatın
if len(metin1) > len(metin2):
    # İkinci diziyi boşluklarla uzatın
    metin2 += " " * uzunluk_farki
else:
    # Birinci diziyi boşluklarla uzatın
    metin1 += " " * uzunluk_farki

hatalar = 0
for karakter_1, karakter_2 in zip(metin1, metin2):
    if karakter_1 != karakter_2:
        hatalar += 1

if len(metin1) > len(metin2):
    uzun_metni_sec = metin1
else:
    uzun_metni_sec = metin2

benzerlik_orani=(len(uzun_metni_sec)-hatalar)/len(uzun_metni_sec)

print("Benzerlik Oranı:", benzerlik_orani)

with open("benzerlik_durumu.txt", "w") as dosya:
    # Benzerlik oranını dosyaya yaz
    dosya.write(f"Benzerlik Oranı: {benzerlik_orani:.2f}")

