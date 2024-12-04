# views.py

from flask import Flask, redirect, render_template, request, Blueprint, url_for
from .db_utils import get_db_connection, load_car_data
from .hybrid_algorithm import preprocess_data, preprocess_data  ,get_recommendations
import mysql.connector
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
from .popularcar import get_top_10_cars
from .affordable_car import get_affordable_cars


views = Blueprint('views', __name__)
data = load_car_data()

@views.route('/')
def home():
    top_10_cars = get_top_10_cars()
    return render_template('home.html', cars=top_10_cars)

@views.route('/affordable_cars')
def affordable_cars():
    # Call the function to get affordable cars
    cars = get_affordable_cars()
    # Render the template with the list of affordable cars
    return render_template('affordable_cars.html', cars=cars)

def get_cars_by_brand(brand):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM carbase WHERE brand = %s", (brand,))
    cars = cursor.fetchall()
    cursor.close()  # Close cursor after fetching results
    conn.close()    # Close connection after cursor is closed
    return cars

@views.route('/perodua')
def perodua():
    cars = get_cars_by_brand('Perodua')
    return render_template('car page/perodua.html', cars=cars)

@views.route('/proton')
def proton():
    cars = get_cars_by_brand('Proton')
    return render_template('car page/proton.html', cars=cars)

@views.route('/toyota')
def toyota():
    cars = get_cars_by_brand('Toyota')
    return render_template('car page/toyota.html', cars=cars)

@views.route('/honda')
def honda():
    cars = get_cars_by_brand('Honda')
    return render_template('car page/honda.html', cars=cars)

@views.route('/mazda')
def mazda():
    cars = get_cars_by_brand('Mazda')
    return render_template('car page/mazda.html', cars=cars)

@views.route('/mitsubishi')
def mitsubishi():
    cars = get_cars_by_brand('Mitsubishi')
    return render_template('car page/mitsubishi.html', cars=cars)

@views.route('/mercedes_benz')
def mercedes_benz():
    cars = get_cars_by_brand('Mercedes-Benz')
    return render_template('car page/mercedes_benz.html', cars=cars)

@views.route('/bmw')
def bmw():
    cars = get_cars_by_brand('BMW')
    return render_template('car page/bmw.html', cars=cars)

@views.route('/nissan')
def nissan():
    cars = get_cars_by_brand('Nissan')
    return render_template('car page/nissan.html', cars=cars)

@views.route('/isuzu')
def isuzu():
    cars = get_cars_by_brand('Isuzu')
    return render_template('car page/isuzu.html', cars=cars)

@views.route('/filter', methods=['GET', 'POST'])
def filter_cars():
    if request.method == 'POST':
        # Retrieve user preferences from form data
        brand = request.form.get('brand')
        price_range = request.form.get('price')
        car_type = request.form.get('bodytype')
        fuel = request.form.get('fuel')
        transmission = request.form.get('transmission')
        arrangement = request.form.get('arrangement')

        # Build SQL query dynamically based on selected preferences
        query = "SELECT * FROM carbase WHERE 1=1"
        params = []

        if brand:
            query += " AND brand = %s"
            params.append(brand)
        if price_range:
            price_min, price_max = map(int, price_range.split('-'))
            query += " AND price BETWEEN %s AND %s"
            params.extend([price_min, price_max])
        if car_type:
            query += " AND bodytype = %s"
            params.append(car_type)
        if fuel:
            query += " AND fuel = %s"
            params.append(fuel)
        if transmission:
            query += " AND transmission = %s"
            params.append(transmission)
        if arrangement:
            query += " AND arrangement = %s"
            params.append(arrangement)

        # Execute the SQL query to fetch filtered cars
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        filtered_cars = cursor.fetchall()
        cursor.close()  # Close cursor after fetching results
        conn.close()    # Close connection after cursor is closed

        # Render results.html with filtered cars
        return render_template('filtered_cars.html', cars=filtered_cars)

    # If it's a GET request, just render the filter form
    return render_template('filter.html')

@views.route('/search')
def search():
    query = request.args.get('query')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM carbase WHERE brand LIKE %s OR model LIKE %s", ('%' + query + '%', '%' + query + '%'))
    search_results = cursor.fetchall()
    cursor.close()  # Close cursor after fetching results
    conn.close()    # Close connection after cursor is closed
    return render_template('search_results.html', cars=search_results)

@views.route('/car/<int:car_spec>')
def car_details(car_spec):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM fullspecs WHERE Id = %s"
        cursor.execute(query, (car_spec,))
        car = cursor.fetchone()
        
        # Close cursor after fetching results
        cursor.close()
        
        # Close connection after cursor is closed
        conn.close()
        
        return render_template('car_details.html', car=car)
    
    except mysql.connector.Error as err:
        print(f"Error fetching car details: {err}")
        return redirect(url_for('views.home'))
    

      

@views.route('/similar_cars/<car_model>', methods=['GET', 'POST'])
def similar_cars(car_model):
    # Fetch car details for the selected car model
    selected_car = data[data['model'] == car_model].iloc[0]

    # Check if selected_car is empty (no matching model found)
    if selected_car.empty:
        return redirect(url_for('views.home'))
    
    # Get user preferences based on the selected car's features
    user_preferences = {
        'brand': selected_car['brand'],
        'model': selected_car['model'],
        'variant': selected_car['variant'],
        'image_src': selected_car['image_src'],
        'exper_trating': selected_car['exper_trating'],
        'owner_rating': selected_car['owner_rating'],
        'price': selected_car['price'],
        'monthly': selected_car['monthly'],
        'segment': selected_car['segment'],
        'bodytype': selected_car['bodytype'],
        'engine': selected_car['engine'],
        'Capacity': selected_car['Capacity'],
        'Arrangement': selected_car['Arrangement'],
        'Timing Type': selected_car['Timing Type'],
        'Horsepower': selected_car['Horsepower'],
        'Torque': selected_car['Torque'],
        'Fuel': selected_car['Fuel'],
        'Compression Ratio': selected_car['Compression Ratio'],
        'Transmission': selected_car['Transmission'],
        'Driveline': selected_car['Driveline'],
        'Seats': selected_car['Seats'],
        'Boot Space': selected_car['Boot Space'],
        'Fuel Tank': selected_car['Fuel Tank'],
        'Tyre Front': selected_car['Tyre Front'],
        'Tyre Rear': selected_car['Tyre Rear'],
        'Front Brakes': selected_car['Front Brakes'],
        'Rear Brakes': selected_car['Rear Brakes'],
        'Airbags': selected_car['Airbags'],
        'Headlamps': selected_car['Headlamps'],
        'Taillamps': selected_car['Taillamps'],
        'Seats Front': selected_car['Seats Front'],
        'Seats Rear': selected_car['Seats Rear'],
        'Audio': selected_car['Audio'],
        'Parking Brake': selected_car['Parking Brake']
    }
    
    
        # Get recommendations based on the selected car model
    recommendations = get_recommendations(selected_car['variant'])
        
    return render_template('similar_cars.html', selected_car=selected_car, cars=recommendations.to_dict(orient='records'))
    
    
