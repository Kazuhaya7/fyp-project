# popularcar.py
import pandas as pd
from .db_utils import load_car_data

def get_top_10_cars():
    # Load the dataset from the database
    car_data = load_car_data()

    # List of specified brands
    specified_brands = ['Perodua', 'Proton', 'Toyota', 'Honda', 'Mitsubishi']

    # Filter the dataset for the specified brands
    filtered_cars = car_data[car_data['brand'].isin(specified_brands)]

    # Filter out cars with missing owner ratings
    rated_filtered_cars = filtered_cars.dropna(subset=['owner_rating'])

    # Sort the cars based on owner_rating in descending order
    sorted_filtered_cars = rated_filtered_cars.sort_values(by='owner_rating', ascending=False)

    # Select the top 10 cars
    top_10_filtered_cars = sorted_filtered_cars.head(14)

    # Verify and update column names if necessary
    columns_to_display = ['brand', 'model', 'variant', 'monthly', 'price', 'image_src','segment','bodytype','engine','Capacity']  # Make sure these match exactly
    top_10_filtered_cars_selected = top_10_filtered_cars[columns_to_display]

    return top_10_filtered_cars_selected.to_dict(orient='records')
