from sqlalchemy import create_engine
import pandas as pd

DATABASE_URL = "mysql+pymysql://root:369369369@localhost/smartboardinghouse"

engine = create_engine(DATABASE_URL)

def run_query(query):
    return pd.read_sql(query, engine)