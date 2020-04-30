import os
import sys
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics.pairwise import cosine_similarity
from scipy import linalg

## collaborative_filter for getting total ratings using user-user similarity
class collaborative_filter:
    def __init__(self,df_rating,save_path):
        """
       Parameters:
         :df_rating: dataframe of user_rating matrix include column 'user_id'
         :save_path: path to save the results
        """
        self.df_rating = df_rating
        self.ratings = df_rating.iloc[:,1:] # ratings:exclude 'user_id'
        self.save_path = save_path

    ##  The user - user recommender system.
    def user_user_recommender(self, verbose=0):
        """
        Parameters:
          :self.ratings: dataframe of the ratings matrix
          :verbose: flag to print details,defalut 0 not to print.
        Returns:
          :df_all_scores: a datafrme, contains movies and similarity scores for  
                          all users and movies that appear in orders.     
        """
        ratings = self.ratings
        if verbose:print('ratings:\n',ratings)
            
        # normalize ratings
        df_normalized = (ratings.T - ratings.T.mean()).T
        if verbose: print('df_normalized:\n',df_normalized)

        # cosine similarity between users:
        sim_all_users = cosine_similarity(df_normalized)

        # predict scores of all item
        all_scores = sim_all_users.dot(df_normalized)
        df_all_scores = pd.DataFrame(all_scores, columns=ratings.columns)

        # add the mean back to ratings
        df_all_scores = df_all_scores.add(ratings.mean(axis=1), axis='index')
        
        # add column 'user_id' 
        df_all_scores.insert(0,'user_id',self.df_rating['user_id'])
        if verbose:print('df_all_scores:\n',df_all_scores)
        
        # save the results 
        pickle.dump(df_all_scores,open(self.save_path+'df_all_scores.sav', 'wb'))
                 
        return df_all_scores
    
## getting UserID list, MovieID list,and a dataframe containing user_id,movie_id 
## and the corresponding score
def user_movie_ordered(df_order,df_show,df_movie):
    """
    Parameters:
      :df_order: dataframe of the orders
      :df_show:  dataframe of the shows
      :df_movies: dataframe of the movies
    Returns:
      :df_user_movie_ordered: a datafrme, contains user_id corresponding to 
                              each order and the movie_id and score of that order.
      :UserID:  list of user_id who has orders.
      :MovieID: list of movie_id which has ever been ordered.
                      
    """
    def showId_to_movieId(show_id):
        movie_id = df_show.loc[df_show['show_id']==show_id,'movie_id'].values[0]
        return movie_id

    df = df_order.loc[:,['user_id','score','show_id']]
    df['movie_id'] = df['show_id'].apply(showId_to_movieId)
    df = df.drop(['show_id'],axis=1)
    df = df.loc[:,['user_id','movie_id','score']]
    df = df.drop_duplicates(['user_id','movie_id'])
    
    UserID = np.sort(df.user_id.unique())
    MovieID = np.sort(df.movie_id.unique())    
    return df, UserID, MovieID       
    
## getting rating dataframe,each row contains UserID and ratings of a user in orders   
def get_rating(df_order,df_show,df_movie):
    """
    Parameters:
      :df_order: dataframe of the orders
      :df_show:  dataframe of the shows
      :df_movies: dataframe of the movies
    Returns:
      :df_rating: a datafrme, contains user_id of user and his/her rating scores 
                  for each movie that he/she has ordered.
    """
    df, UserID, MovieID = user_movie_ordered(df_order,df_show,df_movie)
    df_rating = pd.DataFrame(columns=['user_id',*MovieID])
    for user_id in UserID:
        df_temp = df[df['user_id']==user_id].sort_values(by = 'movie_id')       
        MovieID_no_rating = [x for x in MovieID if x not in \
                                    df_temp['movie_id'].values]

        rating_missing = np.full_like(MovieID_no_rating,0)
      
        uid_missing = np.full_like(MovieID_no_rating,user_id)
        
        user_no_rating = np.vstack((uid_missing,
                                    MovieID_no_rating,
                                    rating_missing)).T   
       
        user_rating = np.vstack((df_temp.values,user_no_rating))
        
        df_user_rating = pd.DataFrame(user_rating,columns=df_temp.columns)
        
        df_user_rating = df_user_rating.sort_values('movie_id')
        
        rating_temp = df_user_rating['score'].values
        
        rating_temp = np.hstack((user_id,rating_temp))
        
        df_rating_temp = pd.DataFrame(rating_temp.reshape(1,-1),
                                       columns=df_rating.columns)
        df_rating = df_rating.append(df_rating_temp,ignore_index=True)
    return df_rating

## generating total rating similarity scores using user-user system.
def generate_all_scores(df_rating,save_path=None):
    if save_path==None:
        save_path = './data/recommend/'
    cf = collaborative_filter(df_rating,save_path)
    df_all_scores = cf.user_user_recommender()
    return df_all_scores

## getting list of MovieID that have not been ordered by the user with user_id
def movie_not_ordered(df_order,df_show,df_movie,user_id,verbose=0):
    """
    Parameters:
      :df_order: dataframe of orders
      :df_show: dataframe of shows
      :df_movie: dataframe of movies
      :user_id: user_id of the user to recommend to
    Returns:
       list of MovieID that have not been ordered by the user
    """
    
    def showId_to_movieId(show_id):
        movie_id = df_show.loc[df_show['show_id']==show_id,'movie_id'].values[0]
        return movie_id
    
    show_id_ordered = df_order[df_order['user_id'] == user_id].show_id
    if verbose:print('show_id_ordered:\n',show_id_ordered)
    
    movie_id_ordered = show_id_ordered.apply(showId_to_movieId)
    if verbose:print('movie_id_ordered:\n',movie_id_ordered)
    
    _ , UserID, MovieID = user_movie_ordered(df_order,df_show,df_movie)
    movie_not_ordered =  set(MovieID) - set(movie_id_ordered)
    return list(movie_not_ordered)

## getting dataframe of movie_id and movie_name from the total similariy scores
def movies_for_uid(df_all_scores,df_order,df_show,df_movie,user_id,
                   recommend_range=None,recommend_number=None):
    """
    Parameters:
      :df_all_scores: dataframe of the ratings matrix for all users
      :df_order: dataframe of orders
      :df_show: dataframe of shows
      :df_movie: dataframe of movies
      :user_id: user_id of the user to recommend to
      :recommend_range:list of movie_id in which to rencommend,default None.
      :recommend_number: number of movies needs to be recommended,default None.
    Returns:
      :df_result_user_2_user: a datafrme, contains movies and similarity scores 
                    for recommendation,sorted descendingly by similarity scores.  
    """

    # list of movies to recommend 
    if recommend_range==None:
        S = movie_not_ordered(df_order, df_show, df_movie, user_id)
    else:
        S = recommend_range
        
    # scores of item in S for user_id:    
    df_scores_S_uid = df_all_scores.loc[df_all_scores.user_id==user_id,S]

    # results of user–user recommender system:
    df_result_u2u = pd.DataFrame(index = S)
    df_result_u2u['similarity_scores'] = df_scores_S_uid.iloc[0,:]
    df_result_u2u = df_result_u2u.sort_values('similarity_scores',ascending=False)
    df_result_u2u['movie_id'] = df_result_u2u.index
    df_result_u2u['movie_name'] = df_movie.loc[df_result_u2u.movie_id].Name 
    df_result_u2u =df_result_u2u.reset_index(drop=True)[['movie_id','movie_name']]
    if recommend_number !=None:
        df_result_u2u = df_result_u2u.iloc[:recommend_number]
    return df_result_u2u

## API to other modules
def recommend_movie(user_id,recommend_range=None,recommend_number=None,load_path=None,**kwargs):
    """
    Parameters:
      :user_id: the user to recommend to
      :recommend_range:list of movie_id in which to rencommend,default None.
      :recommend_number: number of movies needs to be recommended,default None
      :load_path: path to load the dataset
      :**kwargs:other parameters passed with the form key=value,for future use
    Returns:
      :df_result_u2u: a datafrme, contains movies and similarity scores for recommendation,
       sorted descendingly by similarity scores.  
    """ 
    if load_path == None:
        load_path = './data/recommend/'
    try: 
        df_all_scores = pickle.load(open(load_path + 'df_all_scores.sav', 'rb'))   
        df_order = pickle.load(open(load_path + 'df_order.sav', 'rb'))
        df_show = pickle.load(open(load_path + 'df_show.sav', 'rb'))
        df_movie = pickle.load(open(load_path + 'df_movie.sav', 'rb'))
    except Exception as e:
        print(e)
        return None
    else:
        df_result_u2u = movies_for_uid(df_all_scores,
                             df_order,
                             df_show,
                             df_movie,
                             user_id,
                             recommend_range,
                             recommend_number)
        return df_result_u2u
    
if __name__ == '__main__':
#     recommend_movie = recommend_movie(user_id=0,
#                            recommend_range=None,
#                            recommend_number=None)

#     recommend_movie = recommend_movie(user_id=0,
#                            recommend_range=None,
#                            recommend_number=5)

    recommend_movie = recommend_movie(user_id=0,
                           recommend_range=[12,15,30,107],
                           recommend_number=None)

#     recommend_movie = recommend_movie(user_id=1,
#                            recommend_range=None,
#                            recommend_number=None)
    print('recommend movies:\n',recommend_movie)
    
    