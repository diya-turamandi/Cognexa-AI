from sqlalchemy import text
from app.core.database import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))
        print("DATABASE CONNECTED SUCCESSFULLY!")
        print(result.scalar())
except Exception as error:
    print("DATABASE CONNECTION FAILED:")
    print(error)