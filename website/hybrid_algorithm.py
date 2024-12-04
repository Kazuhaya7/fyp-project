import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from .db_utils import load_car_data

# Load the dataset once globally
data = load_car_data()

def preprocess_data(df):
    # Implement your data preprocessing logic here
    # Example: dropping unnecessary columns, handling missing values, etc.
    processed_data = df.copy()
    processed_data = processed_data.drop(columns=['column_to_drop'])
    # Additional preprocessing steps as needed
    return processed_data

# Step 1: Content-Based Filtering
content_features = data[['brand', 'model', 'variant', 'segment','bodytype','engine', 'Horsepower', 'Torque', 'Fuel', 'Transmission', 'Driveline', 'Seats', 'Boot Space']]
content_features = content_features.fillna('')

content_features['combined'] = content_features.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(content_features['combined'])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Step 2: Item-Based Collaborative Filtering
rating_matrix = data.pivot_table(index='variant', columns='price', values=['exper_trating', 'owner_rating']).fillna(0)
item_similarity = cosine_similarity(rating_matrix)

# Step 3: Hybrid Filtering
def get_recommendations(variant, cosine_sim=cosine_sim, item_sim=item_similarity, hybrid_weight=0.5):
    try:
        idx = data[data['variant'] == variant].index[0]
    except IndexError:
        return f"Variant '{variant}' not found in the dataset."

    content_sim_scores = list(enumerate(cosine_sim[idx]))
    item_sim_scores = list(enumerate(item_sim[idx]))
    
    # Ensure item_sim_scores is the same length as content_sim_scores
    if len(item_sim_scores) < len(content_sim_scores):
        item_sim_scores.extend([(i, 0) for i in range(len(item_sim_scores), len(content_sim_scores))])
    
    hybrid_sim_scores = [(i, hybrid_weight * content_sim_scores[i][1] + (1 - hybrid_weight) * item_sim_scores[i][1]) for i in range(len(content_sim_scores))]
    hybrid_sim_scores = sorted(hybrid_sim_scores, key=lambda x: x[1], reverse=True)
    
    car_indices = [i[0] for i in hybrid_sim_scores[1:11]]
    return data.iloc[car_indices][['brand', 'model', 'variant','segment','bodytype', 'image_src', 'exper_trating', 'owner_rating', 'price']]
