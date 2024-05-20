import pandas as pd
import pandas
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pyodbc
import schedule

def reconnectDb():
    global courses_with_rate, users, subjects, discovery, discoveries_with_subjects, discoveries_with_usrs, tutorMajor
    conn_str = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"Server=homelab-quy.duckdns.org,1433;"
    r"Database=es_mssql;"
    # r"TrustServerCertificate=Yes;"
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

        sql_query = "SELECT * FROM Subject"

        # courses = pandas.read_csv('Courses.csv',usecols=[0, 1, 12] ,names=courses_cols,encoding='utf-8')
        subjects =  pd.read_sql(sql_query, conn)
        sql_query = "SELECT * FROM Tutor"
        tutors = pd.read_sql(sql_query, conn)

        sql_query = "SELECT * FROM Discovery"
        discovery = pd.read_sql(sql_query, conn)

        sql_query = "SELECT * FROM DiscoverySubject"
        discoveries_with_subjects = pd.read_sql(sql_query, conn)

        sql_query = "SELECT * FROM DiscoveryUser"
        discoveries_with_usrs = pd.read_sql(sql_query, conn)

        sql_query = "SELECT * FROM TutorMajor"
        tutorMajor = pd.read_sql(sql_query, conn)

        conn.close()
        print("Connection closed successfully.")
        print("Courses \n")
        print(courses_with_rate.info())
        print("user \n")
        print(users.head(5))
        print("subject \n")
        print(subjects.head(5))
        print("discovery \n")
        print(discovery.head(5))
        print("discovery with user \n")
        print(discoveries_with_usrs.head(5))
        print("discovery with subject \n")
        print(discoveries_with_subjects.head(5))
        print("tutor \n")
        print(tutors.head(5))


    except Exception as e:
        print("Error connecting to database:", e)

def get_subject_index_by_title(course_pivot, course_id):
    id = pd.to_numeric(course_id, errors='coerce', downcast='integer')
    try:
        index = course_pivot.index.get_loc(id)
        return index
    except KeyError:
        print(f"The course with id '{id }' does not exist in course_pivot.")
        return -1
    
def get_rec_course_by_discovery_id(discovery_id):
    filtered_df = discoveries_with_subjects[discoveries_with_subjects['DiscoveryId'] == discovery_id].reset_index(drop=True)
    courseIds = []
    subjectIds = []
    
    for i, row in filtered_df.iterrows():
        subjectIds.append(row['SubjectId'])
        if(i == 2): break
    subjectIds = list(dict.fromkeys(subjectIds))

    for id in subjectIds:
        rec_ids = get_rec_subject_id_by_id(id)
        for subjectId in rec_ids:
            courses = courses_with_rate[(courses_with_rate['SubjectId'] == subjectId) & courses_with_rate['Status'] == 1].reset_index(drop=True)
            for _, course_row in courses.iterrows():
                courseIds.append(course_row['course_id'])
                if( _ == 2): break
  

    return courseIds

def get_rec_tutor_ids_by_discovery(discovery_id):
    filtered_df = discoveries_with_subjects[discoveries_with_subjects['DiscoveryId'] == discovery_id].reset_index(drop=True)
    tutorIds = []
    subjectIds = []
    for i, row in filtered_df.iterrows():
        subjectIds.append(row['SubjectId'])
        if(i == 2): break
    subjectIds = list(dict.fromkeys(subjectIds))

    for id in subjectIds:
        subjectIds = get_rec_subject_id_by_id(id)
        for subjectId in subjectIds:
            tutors = tutorMajor[tutorMajor['SubjectId'] == subjectId].reset_index(drop=True)
            for _, tutor_row in tutors.iterrows():
                tutorIds.append(tutor_row['TutorId'])
                if( _ == 2): break


    return tutorIds

def get_rec_course_ids_by_user(user_id):
    user_id = user_id.upper()
    filtered_df = discoveries_with_usrs[discoveries_with_usrs['UserId'] == user_id].sample(frac=1).reset_index(drop=True)
    suggestion_ids = []

    for index, row in filtered_df.iterrows():
        coursesIds = get_rec_course_by_discovery_id(row['DiscoveryId'])
        suggestion_ids.extend(coursesIds)
        if(index == 2): break
        
    suggestion_ids = list(dict.fromkeys(suggestion_ids))
    return suggestion_ids
    
def get_rec_tutor_ids_by_user(user_id):
    user_id = user_id.upper()
    filtered_df = discoveries_with_usrs[discoveries_with_usrs['UserId'] == user_id].sample(frac=1).reset_index(drop=True)
    suggestion_ids = []

    for index, row in filtered_df.iterrows():
        tutorsIds = get_rec_tutor_ids_by_discovery(row['DiscoveryId'])
        suggestion_ids.extend(tutorsIds)
        if(index == 2): break

    suggestion_ids = list(dict.fromkeys(suggestion_ids))
    return suggestion_ids

def get_rec_subject_id_by_id(id):

        num_rating = courses_with_rate.groupby(["learner_id", "SubjectId"])["Rate"].count().reset_index()
        num_rating.rename(columns={"Rate" : "num_of_rating"}, inplace=True)
        print("num_rating \n")
        print(num_rating.head())

        final_rating = courses_with_rate.merge(num_rating, on="SubjectId")
        print("final_rating \n")
        print(final_rating.head())
        # final_rating = final_rating[final_rating["num_of_rating"] >= 50]
        # print("final_rating \n")
        # print(final_rating.head())

        final_rating.drop_duplicates(["SubjectId", "Title"], inplace=True)

        course_pivot = final_rating.pivot_table(columns="learner_id_x",index="SubjectId", values = "Rate")
        # course_pivot = course_pivot.transpose()
        print("course_pivot \n")
        # with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
        print(course_pivot)
        print(course_pivot.shape)
        course_pivot.fillna(0, inplace=True)

        course_index = get_subject_index_by_title(course_pivot, id)
        print(course_index)

        course_sparse = csr_matrix(course_pivot)
        print(course_sparse)

        model = NearestNeighbors(algorithm="brute")
        model.fit(course_sparse)
        distance, suggestion = model.kneighbors(course_pivot.iloc[course_index,:].values.reshape(1,-1), n_neighbors=3)
        suggestion_ids = []
        for i in suggestion[0]:
            suggestion_ids.append(course_pivot.index[i])

        # print("Y_data after \n")
        # print(Y_data)
        print(suggestion_ids)

        return suggestion_ids

def get_rec_subject_by_id(id):

        num_rating = courses_with_rate.groupby(["learner_id", "SubjectId"])["Rate"].count().reset_index()
        num_rating.rename(columns={"Rate" : "num_of_rating"}, inplace=True)
        print("num_rating \n")
        print(num_rating.head())
        print(num_rating.info())

        final_rating = courses_with_rate.merge(num_rating, on="SubjectId")
        print("final_rating \n")
        print(final_rating.head())
        # final_rating = final_rating[final_rating["num_of_rating"] >= 50]
        # print("final_rating \n")
        # print(final_rating.head())

        final_rating.drop_duplicates(["SubjectId", "Title"], inplace=True)
        print(final_rating.info())

        course_pivot = final_rating.pivot_table(columns="learner_id_x",index="SubjectId", values = "Rate")
        # course_pivot = course_pivot.transpose()
        print("course_pivot \n")
        # with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
        print(course_pivot)
        print(course_pivot.shape)
        course_pivot.fillna(0, inplace=True)

        course_index = get_subject_index_by_title(course_pivot, id)
        print(course_index)

        course_sparse = csr_matrix(course_pivot)
        print(course_sparse)

        model = NearestNeighbors(algorithm="brute")
        model.fit(course_sparse)
        distance, suggestion = model.kneighbors(course_pivot.iloc[course_index,:].values.reshape(1,-1), n_neighbors=course_pivot.shape[0])
        suggestion_ids = []

        print(distance)
        print(suggestion)

        for i in suggestion[0]:
            suggestion_ids.append(course_pivot.index[i])

        # print("Y_data after \n")
        # print(Y_data)
        print(suggestion_ids)

        suggestion_subject_names = [subjects.loc[subjects['Id'] == id, 'Name'].iloc[0] for id in suggestion_ids]

        print(suggestion_subject_names)

        return suggestion_subject_names


from flask import Flask, request, jsonify

app = Flask(__name__)
reconnectDb()
schedule.every(15).minutes.do(reconnectDb)

@app.route("/get_recommend_tutors/<id>")
def get_recommended_tutors(id):
    data = get_rec_tutor_ids_by_user(id)
    page = request.args.get('page', 1, type=int)
    perPage = 9
    start = (page - 1) * perPage
    end = start + perPage
    totalPage = (len(data) + perPage - 1) // perPage
    # data = [int(x) for x in data]

    items_on_page = data[start:end]
    response = {
        "data": items_on_page,
        "total_pages": totalPage,
        "current_page": page
    }
    return jsonify(response), 200

@app.route("/get_recommend_courses/<id>")
def get_recommended_courses     (id):
    data = get_rec_course_ids_by_user(id)
    page = request.args.get('page', 1, type=int)
    perPage = 9
    start = (page - 1) * perPage
    end = start + perPage
    totalPage = (len(data) + perPage - 1) // perPage
    # data = [int(x) for x in data]

    items_on_page = data[start:end]
    response = {
        "data": items_on_page,
        "total_pages": totalPage,
        "current_page": page
    }
    return jsonify(response), 200

@app.route("/get_recommend_subject/<id>")
def get_recommended_subject(id):
    data = get_rec_subject_by_id(id)
    page = request.args.get('page', 1, type=int)
    perPage = 9
    start = (page - 1) * perPage
    end = start + perPage
    totalPage = (len(data) + perPage - 1) // perPage
    # data = [int(x) for x in data]

    items_on_page = data[start:end]
    response = {
        "data": items_on_page,
        "total_pages": totalPage,
        "current_page": page
    }
    return jsonify(response), 200

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

# app.run(debug=True,host="0.0.0.0",port=8001)

def run_scheduler():
    # Run the pending jobs once to execute the scheduled job for the first time
    while True:
        schedule.run_pending()
        
if __name__ == "__main__":
    import threading
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
