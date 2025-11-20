import requests


CANVAS_DOMAIN = "-"
ACCESS_TOKEN = "-"
TERMS = ["Term Name"]

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

ANNOUNCEMENT_TITLE = "match with previous script"

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

def get_announcements(course_id):
    announcements = []
    url = f"https://{CANVAS_DOMAIN}/api/v1/courses/{course_id}/discussion_topics?only_announcements=true&per_page=100"

    while url:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        announcements.extend(resp.json())
        url = resp.links.get("next", {}).get("url", None)

    return announcements


def delete_announcement(course_id, announcement_id):
    url = f"https://{CANVAS_DOMAIN}/api/v1/courses/{course_id}/discussion_topics/{announcement_id}"
    resp = requests.delete(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.status_code == 204


def delete_script_announcements(course_id):
    announcements = get_announcements(course_id)

    for ann in announcements:
        if ann.get("title", "").strip() == ANNOUNCEMENT_TITLE:
            ann_id = ann["id"]
            print(f"Deleting announcement {ann_id} in course {course_id}...")
            delete_announcement(course_id, ann_id)


def main():
    term_ids = get_term_ids()

    for term_name, term_id in term_ids.items():
        print(f"\nProcessing term: {term_name}")
        courses = get_courses(term_id)

        for course in courses:
            course_id = course["id"]
            try:
                delete_script_announcements(course_id)
            except Exception as e:
                print(f"Failed for course {course_id}: {e}")


if __name__ == "__main__":
    main()
