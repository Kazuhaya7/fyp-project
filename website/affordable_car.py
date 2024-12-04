import pandas as pd
from .db_utils import load_car_data

def get_affordable_cars():
    # Load the dataset from the database
    car_data = load_car_data()

    # List of specified brands
    specified_brands = ['Perodua', 'Proton', 'Toyota', 'Honda', 'Mitsubishi']

    # Filter the dataset for the specified brands
    affordable_cars = car_data[car_data['brand'].isin(specified_brands)]

    # Sort the affordable cars based on price (ascending)
    affordable_cars_sorted = affordable_cars.sort_values(by='price')

    # Select columns to display
    columns_to_display = ['brand', 'model', 'variant', 'monthly', 'price', 'image_src', 'segment', 'bodytype', 'engine', 'Capacity']

    # Return the top affordable cars
    top_affordable_cars = affordable_cars_sorted.head(12)[columns_to_display].to_dict(orient='records')

    return top_affordable_cars
