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


def create_announcement(course_id, title, message):
    url = f"https://{CANVAS_DOMAIN}/api/v1/courses/{course_id}/discussion_topics"
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
                static_link = f"https://github.com/K0e-jp"
                announcement_title = "おはようございます"
                announcement_message = """
                <p>Line 1</p>
                <p>Line 2 Line 2 Line 2 Line 2</p>
                <p>example on how to post the link: <a href="{static_link}" target="_blank">Link text</a></p>
                <p>Thank you for your support - k0e</p>"""

                print(f"Posting in {course_id}")
                result = create_announcement(course_id, announcement_title, announcement_message)
                print(f"Posted: {result.get('title')}")
            except Exception as e:
                print(f"Failed for course {course_id}: {e}")


if __name__ == "__main__":
    main()
