import requests


CANVAS_DOMAIN = "-"
ACCESS_TOKEN = "-"
TERMS = ["Term name"]

# Headers
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def get_term_ids():
    url = f"https://{CANVAS_DOMAIN}/api/v1/accounts/1/terms"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    terms = response.json()["enrollment_terms"]

    term_ids = {}
    for term in terms:
        if term["name"] in TERMS:
            term_ids[term["name"]] = term["id"]

    if not term_ids:
        raise ValueError(f"No matching terms found for {TERMS}.")

    return term_ids

def get_courses(term_id):
    courses = []
    url = f"https://{CANVAS_DOMAIN}/api/v1/accounts/1/courses?enrollment_term_id={term_id}&per_page=100"
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        courses.extend(response.json())
        url = response.links.get("next", {}).get("url", None)
    return courses

def get_roll_call_assignment(course_id):
    url = f"https://{CANVAS_DOMAIN}/api/v1/courses/{course_id}/assignments"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    assignments = response.json()

    for assignment in assignments:
        if "Roll Call Attendance" in assignment["name"]:
            print(f"Found Roll Call assignment '{assignment['name']}' (ID: {assignment['id']}) in course {course_id}")
            return assignment["id"]

    print(f"No Roll Call assignment found in course {course_id}")
    return None

def verify_assignment_exists(course_id, assignment_id):
    url = f"https://{CANVAS_DOMAIN}/api/v1/courses/{course_id}/assignments/{assignment_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        response.raise_for_status()


def update_assignment(course_id, assignment_id, access_token):
    url = f"https://{CANVAS_DOMAIN}/api/v1/courses/{course_id}/assignments/{assignment_id}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "assignment": {
            "omit_from_final_grade": True
        }
    }

    response = requests.put(url, json=data, headers=headers)

    if response.status_code == 200:
        print("Assignment updated successfully.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

def main():
    term_ids = get_term_ids()

    for term_name, term_id in term_ids.items():
        courses = get_courses(term_id)
        print(f"{len(courses)} courses in '{term_name}'")

        for course in courses:
            course_id = course["id"]
            assignment_id = get_roll_call_assignment(course_id)
            if assignment_id:
                try:
                    update_assignment(course_id, assignment_id, ACCESS_TOKEN)
                    print(f"Updated Roll Call assignment {assignment_id} in course {course_id}")
                except requests.exceptions.HTTPError as e:
                    print(f"Failed to update assignment {assignment_id} in course {course_id}: {e}")


    print("done")

if __name__ == "__main__":
    main()
