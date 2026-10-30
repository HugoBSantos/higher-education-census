import duckdb

import os

from dotenv import load_dotenv

from pipe.bronze import create_bronze
from pipe.silver import create_silver


if __name__ == "__main__":
    
    create_bronze()
    
    load_dotenv()
    database_name = os.environ["DATABASE_NAME"]
    with duckdb.connect(f"md:{database_name}") as conn:
        create_silver(conn)