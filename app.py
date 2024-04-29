import random
from flask import Flask
import schedule
import time
import CF

app = Flask(__name__)
# Sample data: list of recommended jobs for each user_id

# def refresh_data():
#     # process_data()
#     # encode_data()
#     user_user_collaborative_filtering()
#     item_item_collaborative_filtering()
    
# Schedule the job function to run every 25 minutes
# schedule.every(25).minutes.do(refresh_data)

# Function to run the scheduler
# def run_scheduler():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
        
# @app.route('/recommendation/jobs/<string:user_id>', methods=['GET'])
# def get_recommendation_jobs_by_user_id(user_id):
#     list_job_recommend = get_recommendation_job_by_user(user_id)
#     return jsonify(list_job_recommend)

# @app.route('/recommendation/users/<string:job_id>', methods=['GET'])
# def get_recommendation_users_by_job_id(job_id):
#     list_user_recommend = get_recommendation_user_by_job(job_id)
#     return jsonify(list_user_recommend)

# @app.route('/recommendation/job_detail/<string:name>', methods=['GET'])
# def get_recommendation_job_detail(name):
#     return jsonify(recommend_detail_job(name, 10))

# #Hello
# @app.route('/', methods=['GET'])
# def hello():
#     return "Hello World"


import pandas as pd
import pandas
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import read_csv
from CF import CF
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pyodbc
import csv
import json

def get_course_index_by_title(course_pivot, course_id):
    try:
        index = course_pivot.columns.get_loc(course_id)
        return index
    except KeyError:
        print(f"The course with title '{course_id}' does not exist in course_pivot.")
        return -1


def get_dataframe_ratings_base(id):
    conn_str = (
        r"DRIVER={ODBC Driver 17 for SQL Server};"
        r"Server=abcdavid-knguyen.ddns.net,30009;"
        r"Database=es_mssql1;"
        r"TrustServerCertificate=Yes;"
        r"UID=SA;"
        r"PWD=Devopsnhucc?#@Quy69420;"
        r"MultipleActiveResultSets=Yes;"
    )
    try:
        # Connect to the database
        conn = pyodbc.connect(conn_str)
        sql_query = "SELECT * FROM Course"

        # Perform operations here, such as executing SQL queries

        # Don't forget to close the connection when done
        # SQL query to retrieve data
        courses_with_rate = pd.read_sql(sql_query, conn)
        courses_with_rate.rename(columns={'Id': 'course_id'}, inplace=True)
        courses_with_rate.rename(columns={'LearnerId': 'learner_id'}, inplace=True)

        sql_query = "SELECT * FROM Customer"

        # courses = pandas.read_csv('Courses.csv',usecols=[0, 1, 12] ,names=courses_cols,encoding='utf-8')
        users =  pd.read_sql(sql_query, conn)
        users.rename(columns={'Id': 'user_id'}, inplace=True)

        conn.close()
        print("Connection closed successfully.")
    except Exception as e:
        print("Error connecting to database:", e)
    


    print("Courses \n")
    print(courses_with_rate.info())
    print("user \n")
    print(users.head(5))
    print("rating before \n")


    num_rating = courses_with_rate.groupby(["learner_id", "course_id"])["Rate"].count().reset_index()
    num_rating.rename(columns={"Rate" : "num_of_rating"}, inplace=True)
    print("num_rating \n")
    print(num_rating.head())
    print(num_rating.info())

    final_rating = courses_with_rate.merge(num_rating, on="course_id")
    print("final_rating \n")
    print(final_rating.head())
    # final_rating = final_rating[final_rating["num_of_rating"] >= 50]
    # print("final_rating \n")
    # print(final_rating.head())

    final_rating.drop_duplicates(["course_id", "Title"], inplace=True)
    print(final_rating.info())

    course_pivot = final_rating.pivot_table(columns="learner_id_x",index="course_id", values = "Rate")
    # course_pivot = course_pivot.transpose()
    print("course_pivot \n")
    # with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
    print(course_pivot) 
    print(course_pivot.shape) 

    course_index = get_course_index_by_title(course_pivot, id)
    print(course_index)

    course_pivot.fillna(0, inplace=True)
    course_sparse = csr_matrix(course_pivot)
    print(course_sparse)

    model = NearestNeighbors(algorithm="brute")
    model.fit(course_sparse)
    distance, suggestion = model.kneighbors(course_pivot.iloc[course_index,:].values.reshape(1,-1), n_neighbors=9)
    suggestion_ids = []

    # print(distance)
    # print(suggestion)
    print(suggestion.tolist())

    for i in suggestion[0]:
        suggestion_ids.append(course_pivot.index[i])

    # for i in range(len(suggestion)):
    #     print(course_pivot.index[suggestion[i]])
    #     suggestion_ids.append(course_pivot.index[suggestion[i]])

    # print("Y_data after \n")
    # print(Y_data)
    print(suggestion_ids)
    return json.dumps(suggestion_ids)
 
# Y_data = get_dataframe_ratings_base()
# rs = CF(Y_data, k = 10, uuCF = 0)
# rs.normalize_matrix()
# rs.similarity()
# rs.print_recommendation()

# Read the main CSV file
# r_cols = ['user_id', 'rating', 'courseId']
# ratings = pd.read_csv("modified_rating_file.csv", usecols=[0, 1, 2], names=r_cols, header=None, encoding='utf-8')

# # Extract the IDs from the first column of the courses DataFrame

# # Shuffle the given IDs randomly

# # Replace the 'courseId' column with random IDs

# # Generate random ratings from 1 to 5
# ratings['rating'] = [random.randint(1, 5) for _ in range(len(ratings))]

# # Save the modified DataFrame back to CSV
# ratings.to_csv('modified_rating_file.csv', index=False)
 # more options can be specified also

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/get_recommended_course/<id>")
def get_recommended_courses(id):
    data = get_dataframe_ratings_base(id)
    return jsonify(data), 200

if __name__ == "__main__":
    app.run(debug=True)