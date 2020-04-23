#!/usr/bin/env python
# coding: utf-8

# In[5]:


import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics.pairwise import cosine_similarity

class collaborative_filtering:

    def __init__(self, ratings, movies, user_id, recommend_number):
        """
       Parameters:
         :ratings: user_rating matrix
         :user_id: user id
         :recommend_number: number of movies needs to be recommended
        """
        self.ratings = ratings
        self.movies = movies
        self.user_id = user_id
        self.recommend_number = recommend_number
    
    ## Normalize ratings
    def normalize_ratings(self, mode=0, axis=0):
        """
       Parameters:
         :ratings: DataFrame, to be normalized
         :mode: 0(default),account for zeroes; 1, not count zeroes.
         :axis: 1: normalize ratings by row.
                0: normalize ratings by column.
        """
        def normalize_skipna(x):
            x = x.where(x!=0)
            mean_x = x.mean(skipna=True)
            x_normalized = (x - mean_x).fillna(0)
            return x_normalized   
        x = self.ratings
        if axis == 1:
            x = df.T        
        if mode == 0:
            x = x - x.mean()
        elif mode == 1:
            x = normalize_skipna(x)    
        if axis == 1:
            x = x.T    
        return x

    ##  Mean Match

    ##  The user - user recommender system.
    def user_user_recommender(self, normalize_mode=None, verbose=0):
        """
        Parameters:
          :df_ratings: dataframe of the ratings matrix
          :df_shows: dataframe of shows names
          :recommend_range: List of movie IDs of which the user has not seen
          :normalize_mode: None(default): do not normalize,
                           0: count all the items including all zeros that maybe blank items,
                           1: count only non-zeros.
          :verbose: flag to print details,defalut 0 not to print.
        Returns:
          :df_result_user_2_user: a datafrme, 
                                  contains movies and similarity scores for recommendation,
                                  sorted descendingly by similarity scores.       
        """
        # normalize ratings
        df_normalized = self.ratings
        if normalize_mode != None:
            df_normalized = normalize_ratings(self.ratings, mode=normalize_mode, axis=1)

        # cosine similarity between users:
        sim_all_users = cosine_similarity(df_normalized)

        # predict scores of all item
        all_scores = sim_all_users.dot(df_normalized)
        df_all_scores = pd.DataFrame(all_scores, columns=df_ratings.columns)

        # add the mean back to ratings
        if normalize_mode == 0:
            df_all_scores = df_all_scores.add(df_ratings.mean(axis=1), axis='index')
        elif normalize_mode == 1:
            df_all_scores = df_all_scores + mean_match(df_ratings, axis=1)

        return df_all_scores


    def movie_not_ordered(self, df_order, df_show, df_movie):
        show_id_ordered = df_order[df_order['user_id'] == user_id].show_id
        movie_id_ordered = df_show[df_show['show_id'] == show_id_ordered].movie_id
        movie_not_ordered = df_movie[df_movie['movie_id']!= movie_id_ordered]
        movie_not_ordered = movie_not_ordered.movie_id.to_list()
        return movie_not_ordered


    def movies_for_uid(self, df_all_scores, df_order, df_show, df_movie):
        """
        Parameters:
          :df_all_scores: dataframe of the ratings matrix for all users
          :self.user_id: the user to recommend to
          :self.recommend_number: number of movies needs to be recommended
        Returns:
          :df_result_user_2_user: a datafrme, 
                                  contains movies and similarity scores for recommendation,
                                  sorted descendingly by similarity scores.  
        """

        # list of movies to recommend    
        S = movie_not_ordered(df_order, df_show, df_movie, self.user_id)

        # scores of item in S for user_id:    
        df_scores_S_uid = df_all_scores.loc[self.user_id, S]

        # results of user–user recommender system:
        df_result_user_2_user = pd.DataFrame(index = S)
        df_result_user_2_user['similarity_scores'] = df_scores_S_uid
        df_result_user_2_user = df_result_user_2_user.sort_values('similarity_scores', ascending=False)
        df_result_user_2_user['shows'] = df_shows.loc[df_result_user_2_user.index]   
        df_result_user_2_user = df_result_user_2_user.iloc[0:self.recommend_number]
        return df_result_user_2_user

