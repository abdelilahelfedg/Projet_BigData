import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient

# Créer le client Mongodb
client = MongoClient("mongodb://localhost:27017/")

# Accéder à la base et à la collection
db = client["food_db"]
collection = db["products"]

# Charger les documents MongoDB dans un DataFrame pandas
data = list(collection.find())  # retourne une liste de dictionnaires
df = pd.DataFrame(data)

# Supprimer l'_id automatique si nécessaire
if '_id' in df.columns:
    df = df.drop(columns=['_id'])

# Nettoyer les données : on garde les lignes non nulles
df = df.dropna(subset=['product_name', 'ingredients_main_text_only', 'countrie'])

# Préparation du texte
df['ingredients_main_text_only'] = df['ingredients_main_text_only'].astype(str).str.lower()
df['countrie'] = df['countrie'].astype(str).str.lower()

# Fonction de recommandation prenant en compte le pays
def recommend_recipes(user_ingredients, country='maroc', top_n=5):
    country = country.lower()
    filtered_df = df[df['countrie'] == country]
    if filtered_df.empty:
        # Si aucun produit pour ce pays, on retourne les meilleurs produits tous pays confondus
        filtered_df = df

    # Recalcule le TF-IDF pour le sous-ensemble filtré
    vectorizer = TfidfVectorizer(stop_words='english')
    filtered_tfidf_matrix = vectorizer.fit_transform(filtered_df['ingredients_main_text_only'])
    user_input = ' '.join(user_ingredients).lower()
    user_vector = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_vector, filtered_tfidf_matrix).flatten()
    top_indices = similarities.argsort()[-top_n:][::-1]

    recommendations = filtered_df.iloc[top_indices][['product_name', 'ingredients_main_text_only', 'countrie']]
    recommendations['similarity'] = similarities[top_indices]
    return recommendations

def nettoyer_ingredients(texte):
    texte = texte.replace(";", ",").replace(".", ",")
    tokens = [t.strip().lower() for t in texte.split(",") if t.strip()]
    uniques = list(dict.fromkeys(tokens))
    return ", ".join(uniques)