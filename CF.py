import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse

class CF(object):
    """
    class Collaborative Filtering, hệ thống đề xuất dựa trên sự tương đồng
    giữa các users với nhau, giữa các items với nhau
    """
    def __init__(self, data_matrix, k, dist_func=cosine_similarity, uuCF=1):
        """
        Khởi tạo CF với các tham số đầu vào:
            data_matrix: ma trận Utility, gồm 3 cột, mỗi cột gồm 3 số liệu: user_id, item_id, rating.
            k: số lượng láng giềng lựa chọn để dự đoán rating.
            uuCF: Nếu sử dụng uuCF thì uuCF = 1 , ngược lại uuCF = 0. Tham số nhận giá trị mặc định là 1.
            dist_f: Hàm khoảng cách, ở đây sử dụng hàm cosine_similarity của klearn.
            limit: Số lượng items gợi ý cho mỗi user. Mặc định bằng 10.
        """
        self.uuCF = uuCF 
        self.Y_data = data_matrix 
        # if uuCF else data_matrix[:, [1, 0, 2]]
        self.k = k
        self.dist_func = dist_func
        self.Ybar_data = None
        self.Y_data = np.nan_to_num(self.Y_data)
        # Counting the total number of unique user IDs
        self.n_users = len(np.unique(self.Y_data[:, 0]))
        self.n_items = len(np.unique(self.Y_data[:, 1]))

    def normalize_matrix(self):
        """
        Tính similarity giữa các items bằng cách tính trung bình cộng ratings giữa các items.
        Sau đó thực hiện chuẩn hóa bằng cách trừ các ratings đã biết của item cho trung bình cộng
        ratings tương ứng của item đó, đồng thời thay các ratings chưa biết bằng 0.
        """
        users = self.Y_data[:, 0]
        self.Ybar_data = self.Y_data.copy()
        self.mu = {}

        unique_user_ids = np.unique(users)
        for user_id in unique_user_ids:
            ids = np.where(users == user_id)[0]
            item_ids = self.Y_data[ids, 1]
            ratings = self.Y_data[ids, 2]
            # take mean
            m = np.mean(ratings)
            if np.isnan(m):
                m = 0  # để tránh mảng trống và nan value
            self.mu[user_id] = m
            # chuẩn hóa
            self.Ybar_data[ids, 2] = ratings - self.mu[user_id]
        
        # Creating sparse matrix
        # print ("TYPE 2: " + str(self.Ybar_data[:, 2]))
        # print ("TYPE 1: " + self.Ybar_data[:, 1])
        # print ("TYPE 0: " + self.Ybar_data[:, 0])

        self.Ybar = sparse.coo_matrix((self.Ybar_data[:, 2],
                                    (self.Ybar_data[:, 1], self.Ybar_data[:, 0])), (self.n_items, self.n_users))
        self.Ybar = self.Ybar.tocsr()

        # hàm nằm trong class CF
    def __pred(self, u, i, normalized=1):
        """
        Dự đoán ra ratings của các users với mỗi items.
        """
        # tìm tất cả user đã rate item i
        ids = np.where(self.Y_data[:, 1] == i)[0].astype(np.int32)
        users_rated_i = (self.Y_data[ids, 0]).astype(np.int32)
        sim = self.S[u, users_rated_i]
        a = np.argsort(sim)[-self.k:]
        nearest_s = sim[a]
        r = self.Ybar[i, users_rated_i[a]]
        if normalized:
            # cộng với 1e-8, để tránh chia cho 0
            return (r * nearest_s)[0] / (np.abs(nearest_s).sum() + 1e-8)

        return (r * nearest_s)[0] / (np.abs(nearest_s).sum() + 1e-8) + self.mu[u]

    def pred(self, u, i, normalized=1):
        """
        Xét xem phương pháp cần áp dùng là uuCF hay iiCF
        """
        if self.uuCF: return self.__pred(u, i, normalized)
        return self.__pred(i, u, normalized)
    
    def print_recommendation(self):
        print ('Recommendation: ')
        for u in range(self.n_users):
            recommended_items = self.recommend(u)
            if self.uuCF:
                print ('    Recommend item(s):', recommended_items, 'for user', u)
            else: 
                print ('    Recommend item', u, 'for user(s) : ', recommended_items)

# ở phần khởi tạo class, ta đã gái: dist_func=cosine_similarity
    def similarity(self):
        """
        Tính độ tương đồng giữa các user và các item
        """
        eps = 1e-6
        self.S = self.dist_func(self.Ybar.T, self.Ybar.T)
