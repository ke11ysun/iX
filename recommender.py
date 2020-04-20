from datetime import datetime
from typing import Dict, List


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

    def __init__(self):
        pass


def get_recommendation(events: Dict[str, Event],
                       preferences: Dict[str, Preference]) -> List[str]:
    """
    :param events: event database as <event_id, event metadata>
    :param preferences: collected preferences as <user_id, user preference>
    :return: a list of event_id ordered from most recommended to least recommended
    """
    recommendations = []

    num_people = len(preferences)


    return recommendations
