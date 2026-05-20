from db import run_query

def login(phone, password):

    query = f"""
    SELECT *
    FROM users
    WHERE phone = '{phone}'
    AND password = '{password}'
    """

    result = run_query(query)

    if len(result) > 0:
        return result.iloc[0]

    return None