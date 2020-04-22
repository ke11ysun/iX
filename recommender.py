from datetime import datetime
from typing import Dict, List

import numpy as np
import numpy.linalg as la


class Preference:

    def __init__(self, preferred_datetimes: List[datetime],
                 preferred_zipcode: int, extras: str, weight: int = 0):
        """
        :param preferred_datetimes: preferred list of date + time in the order
                                    of most preferred to least preferred
        :param preferred_zipcode: preferred areas ex. 10044
        :param extras: extra preferences in natural language
        :param weight: an optional weight for tie breakers. higher weight can
                       be taken into more consideration in all preferences
        """
        self.preferred_datetimes = preferred_datetimes
        self.preferred_zipcode = preferred_zipcode
        self.extras = extras
        self.weight = weight


class Event:

    def __init__(self, event_datetime: datetime, zipcode: int):
        self.event_datetime = event_datetime
        self.zipcode = zipcode


def get_ticket_recommendation(events: Dict[str, Event],
                              preferences: Dict[str, Preference]) -> List[str]:
    """
    :param events: event database as <event_id, event metadata>
    :param preferences: collected preferences as <user_id, user preference>
    :return: a list of event_id ordered from most recommended to least recommended
    """
    num_people = len(preferences)
    recommendations = list(events.keys())
    # TODO: filter events based on preferences

    return recommendations


def get_movie_recommendation(user_ratings: np.ndarray,
                             user_id: int) -> List[str]:
    u, sigma, vt = la.svd(user_ratings, full_matrices=False)
    v = vt.T
    user = user_ratings[user_id]
    user_genre_preference = user @ v
    recommendations = []

    return recommendations


np.set_printoptions(precision=2, suppress=True)
get_movie_recommendation(None, None)
