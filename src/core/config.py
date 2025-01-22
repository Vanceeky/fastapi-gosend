from pydantic_settings import BaseSettings

from dotenv import load_dotenv
load_dotenv(override=True)

#import os

class Settings(BaseSettings):
    """
    Configuration class for loading application settings from environment variables.
    Inherits from `BaseSettings` to automatically load values from a `.env` file or environment variables.
    """
    secret: str # secret key for JWT
    algorithm: str # algorithm for JWT

    DATABASE_URL: str
    #DATABASE_URL: str = os.getenv("DATABASE_URL") # "mysql+aiomysql://root@localhost/gosend_db"


    # ITEXMO API Configuration
    itexmo_api_endpoint: str
    itexmo_api_email: str
    itexmo_api_password: str
    itexmo_api_code: str
    itexmo_sender_id: str

    # Additional Configuration
    tw_api_url: str
    tw_api_key: str
    tw_secret_key: str
    tw_motherwallet: str
    
    """
    The database connection URL. This is the connection string for connecting to the database,
    using the `mysql+aiomysql` protocol for asynchronous connections with MySQL.
    """

    class Config:
        """
        Configuration class to specify how settings should be loaded.
        In this case, it tells Pydantic to read the settings from the `.env` file.
        """
        env_file = ".env"


settings = Settings()
"""
Instantiate the `Settings` class, which will load configuration from environment variables or the `.env` file.
"""
