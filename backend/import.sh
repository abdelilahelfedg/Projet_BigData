#!/bin/bash

echo "⏳ Importation des produits dans la base MongoDB..."

mongoimport \
  --db food_db \
  --collection products \
  --type csv \
  --file Food_Products.csv \
  --headerline

echo "✅ Importation terminée."
