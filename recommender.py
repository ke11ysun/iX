from typing import List, Dict

import numpy as np
from sklearn.utils.extmath import randomized_svd


def get_movie_recommendation(user_ratings: List[List[int]],
                             movie_db: List[Dict],
                             user_id: int,
                             num_genres: int = 5,
                             limit: int = 20) -> List[str]:
    """
    :param user_ratings: user rating matrix for all users and movies s.t.
                         user_ratings[i, j] = rating of user_id i for movie_id j
    :param user_id: current user to be recommended
    :param movie_db: movie database <movie_id, movie metadata>
    :param num_genres: predicted number of movie genres
    :param limit: max number of items in the recommended list
    :return: a list of recommended movies from movie_db for user_id,
             ordered from most recommended to least recommended
    """
    # model source: page 3 and 4 of
    # https://www.overleaf.com/project/5d754ab8d17be90001cf2a69
    user_ratings_np = np.array(user_ratings)
    U, s, VT = randomized_svd(user_ratings_np, num_genres)
    Sigma = np.diag(s)
    V = VT.T
    user_genre_preferences = U[user_id]  # TODO: unused for now
    user_movie_predicted_rating = user_ratings_np[user_id] @ V @ VT

    # filter movies that is showing in cinemas
    recommendations = list(
            filter(lambda movie_id: movie_db[movie_id]["is_showing"],
                   range(len(movie_db))))

    # sort by predicted user ratings (from the highest to the lowest)
    recommendations.sort(
            key=lambda movie_id: user_movie_predicted_rating[movie_id],
            reverse=True)
    # TODO: sort by movie length

    return recommendations[:limit]


if __name__ == '__main__':
    np.set_printoptions(precision=2, suppress=True)
    print(get_movie_recommendation([[10, 10, 10, 0, 0],
                                    [10, 9, 9, 1, 0],
                                    [0, 0, 0, 10, 8],
                                    [0, 0, 2, 10, 8],
                                    [0, 1, 1, 10, 10]],
                                   [{"is_showing": True, "length": 100},
                                    {"is_showing": False, "length": 105},
                                    {"is_showing": False, "length": 80},
                                    {"is_showing": True, "length": 100},
                                    {"is_showing": True, "length": 100}], 0, 2))
