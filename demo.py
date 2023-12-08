import os
import sqlite3
import requests
import json
import numpy as np
import matplotlib.pyplot as plt

# Rename and establish database connection and path
database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DEM_DB206.db')
conn = sqlite3.connect(database_path)
cur = conn.cursor()

def initialize_database():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Ratings (
            unique_id INTEGER PRIMARY KEY,
            stars FLOAT,
            totalReviews INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Names (
            unique_id INTEGER PRIMARY KEY,
            restaurantName TEXT
        )
    """)
    conn.commit()

    list_names = []
    list_ratings = []
    list_reviews = []

    index = 0
    unique_ids = []
    unique_id = 0
    for i in range(5):
        api_url = f"https://api.yelp.com/v3/businesses/search?category=restaurants&location=AnnArbor&limit=25&offset={index * 25}"
        headers = {'Authorization': 'Bearer m9q9Y_aDsWdZu8RFrlxsQa3RGlSYTRSomLLMKGjYFJz_cHnSuw73xwA39zf9MzUNvhbkYVhIeFUtxmWrTCetxHPEt2Mwnzg9nweizth5172T4KvBRTuPI767yGdyZXYx'}
        response = requests.get(api_url, headers=headers)
        data = response.json()

        for restaurant in data["businesses"]:
            list_names.append(restaurant['name'])
            list_ratings.append(restaurant['rating'])
            list_reviews.append(restaurant['review_count'])
            unique_ids.append(unique_id)
            unique_id += 1

        index += 1

    inserted_count = 0
    for idx, id in enumerate(unique_ids):
        if inserted_count == 25:
            break
        cur.execute("INSERT OR IGNORE INTO Names (unique_id, restaurantName) VALUES (?, ?)", (id, list_names[idx]))
        cur.execute("INSERT OR IGNORE INTO Ratings (unique_id, stars, totalReviews) VALUES (?, ?, ?)", (id, list_ratings[idx], list_reviews[idx]))
        if cur.rowcount == 1:
            inserted_count += 1
            print(list_names[idx])

    conn.commit()
    conn.close()


def generate_pie_chart():
    db_connection = sqlite3.connect(database_path)
    db_cursor = db_connection.cursor()
    
    # Querying and categorizing ratings
    db_cursor.execute("SELECT stars FROM Ratings WHERE stars >= 3.5 AND stars < 4")
    category_35_to_4 = len(db_cursor.fetchall())

    db_cursor.execute("SELECT stars FROM Ratings WHERE stars >= 4 AND stars < 4.5")
    category_4_to_45 = len(db_cursor.fetchall())

    db_cursor.execute("SELECT stars FROM Ratings WHERE stars >= 4.5")
    category_above_45 = len(db_cursor.fetchall())

    categories = ['4.5 - 5.0', '4.0 - 4.5', '3.5 - 4.0']
    rating_data = [category_above_45, category_4_to_45, category_35_to_4]

    # Pie chart properties
    explode = (0.1, 0.05, 0.0)
    colors = ("red", "green", "blue")
    wedge_properties = {'linewidth': 1, 'edgecolor': "black"}
    
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 7))
    wedges, labels, autopct_labels = ax.pie(rating_data, autopct='%1.1f%%', explode=explode, labels=categories, colors=colors, startangle=140, wedgeprops=wedge_properties)
    
    # Legend and title
    ax.legend(wedges, categories, title="Ratings", loc="best")
    plt.title("Distribution of Restaurant Ratings")
    plt.show()

    db_connection.close()
def combined_data():
    db_connection = sqlite3.connect(database_path)
    db_cursor = db_connection.cursor()

    # Creating the new table
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS CombinedData (
            unique_id INTEGER PRIMARY KEY,
            restaurantName TEXT,
            stars FLOAT,
            totalReviews INTEGER
        )
    """)

    # SQL query to join the two tables and insert into the new table
    join_and_insert_query = """
    INSERT INTO CombinedData (unique_id, restaurantName, stars, totalReviews)
    SELECT 
        Names.unique_id, 
        Names.restaurantName, 
        Ratings.stars, 
        Ratings.totalReviews 
    FROM 
        Names 
    JOIN 
        Ratings ON Names.unique_id = Ratings.unique_id
    """

    db_cursor.execute(join_and_insert_query)
    db_connection.commit()
    db_connection.close()

    print("Combined data table created and populated successfully.")
def main():
    initialize_database()
    #generate_pie_chart() 
    combined_data()

if __name__ == "__main__":
    main()
