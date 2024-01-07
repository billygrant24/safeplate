from motor.motor_asyncio import AsyncIOMotorClient


def get_db_connection(uri: str, db_name: str) -> AsyncIOMotorClient:
    """Return a connection to the database."""
    return AsyncIOMotorClient(uri).get_database(db_name)
