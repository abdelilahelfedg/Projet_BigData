from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from backend.recSys import recommend_recipes, nettoyer_ingredients # Importer la fonction de recommandation

app = Flask(__name__)
CORS(app)  

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

@app.route('/')
def index():
    """Servir la page principale"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal pour le chat"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        ingredients = data.get('ingredients')
        
        if not user_message and not ingredients:
            return jsonify({'error': 'Message vide et aucun ingrédient fourni'}), 400
        
        if not ingredients and user_message:
            ingredients = nettoyer_ingredients(user_message)
        
        if ingredients:
            recommendations_df = recommend_recipes(ingredients)
            # Conversion du DataFrame en liste de dictionnaires
            recommendations = recommendations_df.to_dict(orient='records')
            suggestions = ""
            for rec in recommendations[:5]:
                suggestions += f"🥣 {rec['product_name']}\n" + "-" * 60 + "\n"
            bot_response = (
                f"""Voici {len(recommendations)} produits recommandés pour vous ! Vous pouvez les utiliser pour préparer vos plats. Voici quelques suggestions : """)
            
        else:
            recommendations = []
            bot_response = "Je n'ai pas pu identifier d'ingrédients spécifiques. Pouvez-vous me dire quels ingrédients vous avez ? Par exemple : 'J'ai des tomates, du basilic et de l'ail'."
        
        return jsonify({
            # 'bot_response': bot_response,
            # 'ingredients': ingredients,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        import traceback
        print("Erreur dans /api/chat :", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)