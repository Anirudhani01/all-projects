import threading, uuid
from flask import Flask, jsonify, request

from jira.jira_list_story_manager import JiraManager
from list_test_case import OpenAITestCaseGenerator
from database.db import create_job_status_in_db, get_job_status

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "Testcase app is running!"


def background_job(story_id, unique_id):
    try:
        jira_manager = JiraManager(story_id)
        create_job_status_in_db(unique_id)
        OpenAITestCaseGenerator(jira_manager.userStories, unique_id)
    except Exception as e:
        print("The error::", e)
        pass


@app.route("/test-case-generator", methods=["POST"])
def generate_test_case():
    data = request.get_json()
    story_id = data.get("story_id")

    if not story_id:
        return jsonify({"status": "error", "message": "Missing story_id"}), 400

    unique_id = str(uuid.uuid4())
    thread = threading.Thread(target=background_job, args=(story_id, unique_id))
    thread.start()

    return (
        jsonify(
            {
                "status": "accepted",
                "message": "Test case generation started.",
                "id": unique_id,
            }
        ),
        202,
    )


@app.route("/get-status/<unique_id>", methods=["GET"])
def get_status_id(unique_id):
    data = get_job_status(unique_id)
    return (
        jsonify(data),
        200,
    )


# @app.route('/test-case-generator', methods=['GET'])
# def test_case_generator():
#     story_id = request.args.get('story_id', default=None, type=str)
#     jira_manager = JiraManager(story_id)

#     try:
#         OpenAITestCaseGenerator(jira_manager.userStories)
#     except Exception as e:
#         print("error", e)
#         return jsonify({"status": "error", "message": str(e)}), 500
#     print("Done")
#     return jsonify({"status": "done", "story_id": story_id, "message": "Test cases generated successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
