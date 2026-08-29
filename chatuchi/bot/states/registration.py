"""
Registration state machine states.
"""

from enum import Enum


class RegistrationState(Enum):
    """States for registration flow."""
    NONE = "none"
    WAITING_NAME = "waiting_name"
    WAITING_AGE = "waiting_age"
    WAITING_SEX = "waiting_sex"
    WAITING_CITY_PROVINCE = "waiting_city_province"
    WAITING_CITY = "waiting_city"
    WAITING_BIO = "waiting_bio"
