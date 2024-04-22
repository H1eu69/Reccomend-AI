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
  
def get_course_index_by_title(course_pivot, title):
    try:
        index = course_pivot.index.get_loc(title)
        return index
    except KeyError:
        print(f"The course with title '{title}' does not exist in course_pivot.")
        return -1


def get_dataframe_ratings_base():
  """
  đọc file base của movilens, lưu thành dataframe với 3 cột user id, item id, rating
  """
  courses_cols = ['courseId', 'title', "subject_id"]
  courses = pandas.read_csv('Courses.csv',usecols=[0, 1, 12] ,names=courses_cols,encoding='utf-8')
  users = pandas.read_csv('Customers.csv', encoding='utf-8')
  r_cols = ['user_id', 'rating', 'courseId']
  ratings = pandas.read_csv("modified_rating_file.csv", usecols=[0, 1, 2], names=r_cols, header=None, encoding='utf-8')

  print("Courses \n")
  print(courses.head(5))
  print("user \n")
  print(users.head(5))
  print("rating before \n")
  print(ratings.head(5))
  print(ratings.shape)
  
  ratings_with_courses = ratings.merge(courses, on="courseId")
  print("ratings_with_courses \n")
  print(ratings_with_courses.head(5))
  
  num_rating = ratings_with_courses.groupby("title")["rating"].count().reset_index()
  num_rating.rename(columns={"rating" : "num_of_rating"}, inplace=True)
  print("num_rating \n")
  print(num_rating.head())
  
  final_rating = ratings_with_courses.merge(num_rating, on="title")
  print("final_rating \n")
  print(final_rating.head())
  # final_rating = final_rating[final_rating["num_of_rating"] >= 50]
  # print("final_rating \n")
  # print(final_rating.head())
  
  final_rating.drop_duplicates(["user_id", "title"], inplace=True)
  print(final_rating.shape)
  
  course_pivot = final_rating.pivot_table(columns="user_id",index="title", values = "rating")
  # course_pivot = course_pivot.transpose()
  print("course_pivot \n")
  # with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
  print(course_pivot) 
  print(course_pivot.shape) 

  course_title_to_find = "Python Test"
  course_index = get_course_index_by_title(course_pivot, course_title_to_find)
  print(course_index)
 
  course_pivot.fillna(0, inplace=True)
  course_sparse = csr_matrix(course_pivot)
  print(course_sparse)

  model = NearestNeighbors(algorithm="brute")
  model.fit(course_sparse)
  distance, suggestion = model.kneighbors(course_pivot.iloc[course_index,:].values.reshape(1,-1), n_neighbors=10)
  
  print(distance)
  print(suggestion)

  for i in range(len(suggestion)):
    print(course_pivot.index[suggestion[i]])

  Y_data = ratings.values
  # print("Y_data after \n")
  # print(Y_data)
  return Y_data
 

 # more options can be specified also
Y_data = get_dataframe_ratings_base()
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

def __pred(self, u, i,):
    """ 
    predict the rating of user u for item i (normalized)
    if you need the un
    """
    # Step 1: find all users who rated i
    ids = np.where(self[:, 1] == i)[0].astype(np.int32)
    # Step 2: 
    users_rated_i = (self[ids, 0]).astype(np.int32)
    # Step 3: find similarity btw the current user and others 
    # who already rated i
    sim = self.S[u, users_rated_i]
    # Step 4: find the k most similarity users
    a = np.argsort(sim)[-self.k:] 
    # and the corresponding similarity levels
    nearest_s = sim[a]
    # How did each of 'near' users rated item i
    r = self.Ybar[i, users_rated_i[a]]
    # add a small number, for instance, 1e-8, to avoid dividing by 0
    return (r*nearest_s)[0]/(np.abs(nearest_s).sum() + 1e-8)

