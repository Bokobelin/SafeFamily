"""Extensions initialization for the SafeFamily application."""

import json
import logging

import psycopg2
import pytz
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from config.settings import settings
from src.safe_family.utils.constants import TIMEZONE

logger = logging.getLogger(__name__)
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
local_tz = pytz.timezone(TIMEZONE)


def get_db_connection():
    """Establish a new database connection using psycopg2."""
    config_dict = json.loads(settings.DB_PARAMS)
    return psycopg2.connect(**config_dict)
