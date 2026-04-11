import psycopg2, os
from datetime import datetime
from dotenv import load_dotenv
import psycopg2.extras

load_dotenv(dotenv_path=os.path.join("test_case_generator.env"))

CONNECTION_INFO = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PWD"),
    "host": os.getenv("DB_HOST"),
    "port": 5432,
}


def get_job_status(unique_id):
    query = """
        SELECT * FROM public.test_case_jobs_status
        WHERE job_id = %s
    """
    conn = None
    try:
        conn = psycopg2.connect(**CONNECTION_INFO)
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, (unique_id,))
                row = cur.fetchone()
                return dict(row) if row else None
    except Exception as e:
        print("Error:", e)
    finally:
        if conn:
            conn.close()


def create_job_status_in_db(unique_id):
    query = """
        INSERT INTO public.test_case_jobs_status (
  job_id, status, created_at, updated_at
) VALUES (%s,%s,%s,%s)
    """
    conn = None
    try:
        conn = psycopg2.connect(**CONNECTION_INFO)
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    query, (unique_id, "started", datetime.utcnow(), datetime.utcnow())
                )
    except Exception as e:
        print("Rge::", e)
    finally:
        conn.close()


def update_job_status_in_db(job_id: str, status: str):
    """
    Updates the status and updated_at for a given job_id in the test_case_jobs_status table.

    Args:
        job_id (str): UUID of the job.
        status (str): New status to set.
        conn_info (dict): Database connection info (host, dbname, user, password, port).

    Raises:
        ValueError: If job_id or status is invalid.
        Exception: If the update fails.
    """
    if not job_id or not status:
        raise ValueError("job_id and status are required.")

    query = """
        UPDATE public.test_case_jobs_status
        SET status = %s,
            updated_at = %s
        WHERE job_id = %s
    """

    try:
        conn = psycopg2.connect(**CONNECTION_INFO)
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, ("completed", datetime.utcnow(), job_id))
                if cur.rowcount == 0:
                    raise Exception(f"No record found with job_id {job_id}")
    finally:
        conn.close()
