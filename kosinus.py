from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Örnek metinler
texts = ["Python dili güçlüdür",
         "Python programlama dili"]

# TF-IDF vektörizerini özelleştirerek boş sonuçları önleme
tfidf_vectorizer = TfidfVectorizer(min_df=1, max_df=1.0, stop_words=None)
tfidf_matrix = tfidf_vectorizer.fit_transform(texts)

# TF-IDF matrisini ve kosinüs benzerliğini kontrol etme
print("TF-IDF Matrisinin Şekli:", tfidf_matrix.shape)
print("TF-IDF Matrisinin İçeriği:")
print(tfidf_matrix.toarray())

cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
print("İki metin arasındaki kosinüs benzerliği:", cosine_similarities[0][0])
