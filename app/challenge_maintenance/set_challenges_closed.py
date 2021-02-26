from datetime import datetime, timedelta

from sqlalchemy import text

from db import db


def update_challenges():
    sql = """
    UPDATE challenges SET status = 'CLOSED' WHERE 
        status not in ('COMPLETED', 'DISPUTED', 'FINISHED', 'SOLVED') and due_date <= :time_ago
    """
    time_ago = datetime.utcnow() - timedelta(days=1)
    db.engine.execute(text(sql), time_ago=time_ago)
