from datetime import datetime
from typing import Dict, List


class Preference:

    def __init__(self,
                 preferred_datetimes: datetime,
                 preferred_zipcode: int,
                 extras: str,
                 # an optional weight for each preference as a tie breaker
                 weight: int = 0):
        self.preferred_datetimes = preferred_datetimes
        self.preferred_zipcode = preferred_zipcode
        self.extras = extras
        self.weight = weight


def get_recommendation(movies: Dict[str, Dict],
                       preferences: Dict[str, Preference]) -> List[str]:
    """
    :param movies: movie database as <movie_id, movie_metadata>
    :param preference: collected preferences as <user_id, preference>
    :return: a list of movie_id ordered from most recommended to least recommended
    """
    recommendations = []

    num_people = len(preferences)

    return recommendations
