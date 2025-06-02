FROM mongo:latest

# Copie le script d'import et le fichier CSV
COPY ../Food_Products.csv /import/Food_Products.csv
COPY import.sh /docker-entrypoint-initdb.d/import.sh

# Donner les bons droits au script
RUN chmod +x /docker-entrypoint-initdb.d/import.sh


