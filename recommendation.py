# from collaborative_filtering import CFF
# from content_base_intl import ContentBasedRecommender
# from handle_data import get_data, fecth_all_job
# import pandas as pd 
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# def user_user_collaborative_filtering():
#     data = get_data('data_after')
#     ratings = data[['user_id_encoded','job_id_encoded','rating']]
#     ratings.columns = ['user_id', 'job_id', 'rating']
#     Y_data = ratings.values
#     rs = CFF(Y_data, k = 10, uuCF = 1)
#     rs.fit()
#     rs.print_recommendation()
    
# # user_user_collaborative_filtering()
# def item_item_collaborative_filtering():
#     data = get_data('data_after')
#     ratings = data[['user_id_encoded','job_id_encoded','rating']]
#     ratings.columns = ['user_id', 'job_id', 'rating']
#     Y_data = ratings.values
#     rs = CF(Y_data, k = 10, uuCF = 0)
#     rs.fit()
#     rs.print_recommendation()
# # item_item_collaborative_filtering()    
# def get_recommendation_user_by_job(job_id):
#     db_mongo = connect_to_mongodb()
#     collection = db_mongo['recommendations_user_by_job']
#     query = {'job_id': job_id}
#     result = collection.find_one(query)
#     if result:
#         return result['recommended_users']
#     else:
#         return []

# def get_recommendation_job_by_user(user_id):
#     db_mongo = connect_to_mongodb()
#     collection = db_mongo['recommendations_job_by_user']
#     query = {'user_id': user_id}
#     result = collection.find_one(query)
#     if result:
#         return result['recommended_items']
#     else:
#         return []
# # print(get_recommendation_job_by_user('09c52577-c39c-4340-affa-e52c4c4947e9'))

# def getuser_by_job():
#     db_mongo = connect_to_mongodb()
#     collection = db_mongo['recommendations_job_by_user']
#     query = {'recommended_items': {'$ne': []}}
#     print(list(collection.find(query)))

# def getjob_by_user():
#     db_mongo = connect_to_mongodb()
#     collection = db_mongo['recommendations_user_by_job']
#     query = {'recommended_users': {'$ne': []}}
#     print(list(collection.find(query)))
    
# # getuser_by_job()
# # getjob_by_user()

# def recommend_detail_job(name_job, number_suggest):
#     fecth_all_job()
#     job_df = pd.read_csv('data_sql.csv')  
#     job_df['name'] = job_df['name'].str.replace(r'\n', '')
#     tfidf = TfidfVectorizer(analyzer='word', stop_words='english')
#     lyrics_matrix = tfidf.fit_transform(job_df['name'])
#     cosine_similarities = cosine_similarity(lyrics_matrix) 
#     similarities = {}
#     for i in range(len(cosine_similarities)):
#         # Now we'll sort each element in cosine_similarities and get the indexes of the songs. 
#         similar_indices = cosine_similarities[i].argsort()[:-50:-1] 
#         # After that, we'll store in similarities each name of the 50 most similar songs.
#         # Except the first one that is the same song.
#         similarities[job_df['name'].iloc[i]] = [(cosine_similarities[i][x], job_df['name'][x],job_df['job_id'][x], job_df['position_position_id'][x]) for x in similar_indices][1:]
#     recommedations = ContentBasedRecommender(similarities)

#     # recommendation = {
#     # "job": name_job,
#     # "number": number_suggest}

#     recommendation = {
#     "job": job_df['name'].iloc[13],
#     "number": 100
#     }   

#     return recommedations.recommend(recommendation)

        
