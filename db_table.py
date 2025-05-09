import sqlite3

def get_db_connection():
    conn = sqlite3.connect('users.db')  
    conn.row_factory = sqlite3.Row
    return conn

def print_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    print("\n=== Liste des utilisateurs ===")
    for user in users:
        print(f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}, "
              f"Gender: {user['gender']}, Age: {user['age']}, Location: {user['location']}")

if __name__ == '__main__':
    print_users()














# import sqlite3

# def create_table():
#     # Connexion à la base de données SQLite
#     conn = sqlite3.connect('database.db')  # Remplace par ton nom de fichier SQLite
#     cursor = conn.cursor()

#     # Création de la table 'users' si elle n'existe pas
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT NOT NULL,
#             email TEXT NOT NULL,
#             password TEXT NOT NULL,
#             age INTEGER,
#             location TEXT,
#             gender TEXT
#         );
#     ''')

#     # Sauvegarder les changements et fermer la connexion
#     conn.commit()
#     conn.close()
#     print("La base de données a été initialisée avec succès.")

# # Appeler la fonction pour créer la table
# create_table()

