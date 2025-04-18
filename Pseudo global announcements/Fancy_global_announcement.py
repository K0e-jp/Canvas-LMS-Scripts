import requests


CANVAS_DOMAIN = "-"
ACCESS_TOKEN = "-"
TERMS = ["term name1", "term name2"]


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


#fetches the id of the instructor for each course to post the announcement as the instructor

def get_primary_teacher_user_id(course_id):
    url = f"https://{CANVAS_DOMAIN}/api/v1/courses/{course_id}/users?enrollment_type=teacher&per_page=100"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    teachers = response.json()
    if not teachers:
        raise ValueError(f"No teacher found for course {course_id}")
    return teachers[0]["id"]

#fetches the id of a specific item for each course to generate a custom link in the announcement

def find_item_id(course_id):
    modules_url = f"https://{CANVAS_DOMAIN}/api/v1/courses/{course_id}/modules?per_page=100"
    modules_resp = requests.get(modules_url, headers=HEADERS)
    modules_resp.raise_for_status()
    modules = modules_resp.json()

    for module in modules:
        items_url = f"https://{CANVAS_DOMAIN}/api/v1/courses/{course_id}/modules/{module['id']}/items?per_page=100"
        items_resp = requests.get(items_url, headers=HEADERS)
        items_resp.raise_for_status()
        items = items_resp.json()

        for item in items:
            if item["title"].strip().lower() == "-": #plug here the name of the item you want to link to
                return item["id"]

    return None


def create_announcement_as_user(course_id, title, message, user_id):
    url = f"https://{CANVAS_DOMAIN}/api/v1/courses/{course_id}/discussion_topics?as_user_id={user_id}"
    payload = {
        "title": title,
        "message": message,
        "is_announcement": True
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


def main():
    term_ids = get_term_ids()
    for term_name, term_id in term_ids.items():
        print(f"\nProcessing term: {term_name}")
        courses = get_courses(term_id)
        for course in courses:
            course_id = course["id"]

            try:
                teacher_id = get_primary_teacher_user_id(course_id)
                item_id = find_item_id(course_id)

                if not item_id:
                    print(f"No item found in {course_id}")
                    continue

                custom_item_link = f"https://{CANVAS_DOMAIN}/courses/{course_id}/modules/items/{item_id}"
                announcement_title = "おはようございます"
                announcement_message = f"""
                <p>Line 1</p>
                <p>Line 2 Line 2 Line 2 Line 2</p>
                <p>example on how to post the link: <a href="{custom_item_link}" target="_blank">Link text</a></p>
                <p>You can also click on the module page of any of your Canvas courses and select the item link</p>
                <p>Thank you for your support- k0e</p>"""

                print(f"Posting as {teacher_id} in {course_id}")
                result = create_announcement_as_user(course_id, announcement_title, announcement_message, teacher_id)
                print(f"Posted: {result.get('title')}")
            except Exception as e:
                print(f"Failed for course {course_id}: {e}")


if __name__ == "__main__":
    main()
