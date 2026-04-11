from fastapi import APIRouter
from pydantic import BaseModel
import mysql.connector
import spacy

router = APIRouter()
nlp = spacy.load("en_core_web_sm")

class Question(BaseModel):
    question: str

def extract_entities_and_generate_sql(question: str):
    doc = nlp(question.lower())

    tokens = [t.text for t in doc]

    if "revenue" in tokens or "money" in tokens or "total" in tokens:
        if "today" in tokens:
            return (
                "SELECT SUM(total_bill) as total FROM orders WHERE DATE(closing_time) = CURDATE();",
                "Today's total revenue is ${total}."
            )
        return (
            "SELECT SUM(total_bill) as total FROM orders WHERE closing_time IS NOT NULL;",
            "Total revenue collected is ${total}."
        )

    elif "unpaid" in tokens:
        return (
            "SELECT COUNT(*) as count FROM orders WHERE closing_time IS NULL;",
            "There are {count} unpaid orders."
        )

    elif "table" in tokens and "most" in tokens:
        return (
            "SELECT table_number, MAX(total_bill) as max_bill FROM orders;",
            "Table {table_number} had the highest bill: ${max_bill}."
        )

    elif "order" in tokens and "today" in tokens:
        return (
            "SELECT COUNT(*) as count FROM orders WHERE DATE(entry_time) = CURDATE();",
            "Today, there have been {count} orders."
        )

    elif "last" in tokens and "order" in tokens:
        return (
            "SELECT table_number, total_bill FROM orders ORDER BY entry_time DESC LIMIT 1;",
            "Last order was from table {table_number} with bill ${total_bill}."
        )

    return None, "Sorry, I couldn't understand the question."

@router.post("/nlp-query/")
def handle_nlp_query(q: Question):
    query, template = extract_entities_and_generate_sql(q.question)

    if not query:
        return {"answer": template}

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_mysql_password",
            database="restaurant"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return {"answer": template.format(**result)}
        return {"answer": "No data found."}
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}
