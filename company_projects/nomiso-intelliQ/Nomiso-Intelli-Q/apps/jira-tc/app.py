import threading, os, requests, re, json, uuid
from flask import Flask, jsonify, request
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Get API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROJECT_KEY = "SCRUM"
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_API_KEY = os.getenv("JIRA_TOKEN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_KEY)
headers = {"Accept": "application/json", "Content-Type": "application/json"}

STATUS_FILE = "status.json"


@app.route("/", methods=["GET"])
def home():
    return "Testcase app is running!"


def background_job(story_id, desc, unique_id):
    try:
        generate_tests(story_id, desc, unique_id)
    except Exception as e:
        print("Error here::", str(e))
        pass


def create_test_case(summary):
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": summary}],
                    }
                ],
            },
            "issuetype": {"name": "Task"},
        }
    }
    try:
        print("zsum::", summary, payload)
        url = f"https://{JIRA_DOMAIN}/rest/api/3/issue"
        response = requests.post(url, headers=headers, auth=auth, json=payload)
        response.raise_for_status()
        created_issue = response.json()
        print(f"Test Case Created Successfully: {created_issue['key']}")
        return created_issue["key"]
    except requests.exceptions.RequestException as err:
        print(f"Error creating test case: {err}")
        print(f"Response content: {response.text}")
    return None


def generate_tests(story_id, desc, unique_id):
    # call openAI with specific prompt
    prompt = f"Generate test cases for the requirement. Make sure to give list of test cases only no input and output.{desc}"
    print("Prompt now::", prompt, story_id)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
    }
    # print("PLOAD", payload)

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )

    if response.status_code == 200:
        result = response.json()
        print("Result here::", result)
        reply = result["choices"][0]["message"]["content"]
        # print("The AI rep::", reply)
        # parse and split reply in run in loop
        lines = reply.split("\n")
        parsed_tcs = [
            re.sub(r"^\d+\.\s*", "", line).strip() for line in lines if line.strip()
        ]
        print("Lines here::", parsed_tcs)
        for test_case in parsed_tcs:
            # in loop create work item
            test_case_key = create_test_case(test_case)
            link_test_case_to_story(test_case_key, story_id)
        # now its done save it to a json file
        status = {"id": unique_id, "status": "completed"}
        write_contents_file(status)
        return "done"
    else:
        print("OpenAI API error:", response.text)


def link_test_case_to_story(test_case_key, story_key, link_type="Relates"):
    """
    Links the created test case to a user story.

    Args:
        test_case_key (str): The Jira key of the test case (e.g., TST-1).
        story_key (str): The Jira key of the story (e.g., TST-2).
        link_type (str): The type of link. Default is 'Relates'.
                        Common types: 'Relates', 'Blocks', 'Cloners', 'Duplicate', 'Tests'
    """
    print(
        f"Linking test case {test_case_key} to story {story_key} with link type '{link_type}'"
    )

    payload = {
        "type": {"name": link_type},
        "inwardIssue": {"key": story_key},
        "outwardIssue": {"key": test_case_key},
        "comment": {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Link created from automation between test case {test_case_key} and story {story_key}",
                            }
                        ],
                    }
                ],
            }
        },
    }

    try:
        url = f"https://{JIRA_DOMAIN}/rest/api/3/issueLink"
        response = requests.post(url, headers=headers, auth=auth, json=payload)
        if response.status_code != 201:
            print(
                f"Failed to link issues. Status Code: {response.status_code}, Response: {response.text}"
            )
        response.raise_for_status()
        print(f"Successfully linked test case {test_case_key} to story {story_key}")
    except requests.exceptions.RequestException as err:
        print(f"Error linking test case: {err}")


def read_contents_file() -> list:
    with open(STATUS_FILE, "r") as file:
        data = json.load(file)
        return data
    return []


def write_contents_file(content_dict):
    existing_data = read_contents_file()
    found = False
    for data in existing_data:
        if data["id"] == content_dict["id"]:
            data["status"] = content_dict["status"]
            found = True
            break
    if found == False:
        existing_data.append(content_dict)
    with open(STATUS_FILE, "w") as f:
        json.dump(existing_data, f, indent=4)


@app.route("/test-case-generator", methods=["POST"])
def generate_test_case():
    data = request.get_json()
    story_id = data.get("story_id")
    desc = data.get("description")
    if not story_id:
        return jsonify({"status": "error", "message": "Missing story_id"}), 400
    unique_id = str(uuid.uuid4())

    status = {"id": unique_id, "status": "started"}
    write_contents_file(status)
    thread = threading.Thread(target=background_job, args=(story_id, desc, unique_id))
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
    existing_data = read_contents_file()
    print("Existing", existing_data)
    for data in existing_data:
        if data["id"] == unique_id:
            return (
                jsonify(data),
                200,
            )
    return (
        jsonify({"status": "not-found", "id": unique_id}),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
