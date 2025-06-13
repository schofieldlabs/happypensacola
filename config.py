import os
import stripe

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
