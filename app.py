import pandas as pd
import pandas
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pyodbc

conn_str = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"Server=homelab-quy.duckdns.org,1433;"
    r"Database=es_mssql;"
    r"TrustServerCertificate=Yes;"
    r"UID=SA;"
    r"PWD=1q2w3E**;"
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
    print("Courses \n")
    print(courses_with_rate.info())
    print("user \n")
    print(users.head(5))
    print("rating before \n")
except Exception as e:
    print("Error connecting to database:", e)



def get_course_index_by_title(course_pivot, course_id):
    id = course_id.upper()
    try:
        index = course_pivot.index.get_loc(course_id)
        return index
    except KeyError:
        print(f"The course with id '{course_id}' does not exist in course_pivot.")
        return -1


def get_dataframe_ratings_base(id):

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
        return suggestion_ids


from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/get_recommend/<id>")
def get_recommended_courses(id):
    data = get_dataframe_ratings_base(id)
    return jsonify(data), 200

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

# app.run(debug=True,host="0.0.0.0",port=8001)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)