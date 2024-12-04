# db_utils.py

import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Database configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'fyp'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def load_car_data():
    conn = get_db_connection()
    query = "SELECT * FROM carbase"
    car_data = pd.read_sql(query, conn)
    conn.close()
    return car_data

def concatenate_user_preferences(user_preferences):
    preferences_str = ""
    for key, value in user_preferences.items():
        if value:
            preferences_str += f"{value} "
    return preferences_str.strip()
