import requests


CANVAS_DOMAIN = "-"
ACCESS_TOKEN = "-"
TERMS = ["term name"]

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}


def get_term_ids():
    url = f"{CANVAS_DOMAIN}/api/v1/accounts/1/terms"
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
    url = f"{CANVAS_DOMAIN}/api/v1/accounts/1/courses?enrollment_term_id={term_id}&per_page=100"
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        courses.extend(response.json())
        url = response.links.get("next", {}).get("url")  # Handle pagination
    return courses


def update_course_settings(course_id):
    url = f"{CANVAS_DOMAIN}/api/v1/courses/{course_id}/settings"
    payload = {"hide_distribution_graphs": True}
    response = requests.put(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


def main():
    term_ids = get_term_ids()

    for term_name, term_id in term_ids.items():
        courses = get_courses(term_id)
        print(f"{len(courses)} courses in  '{term_name}'")

        for course in courses:
            course_id = course["id"]
            update_course_settings(course_id)
            print(f"Updated {course_id}")

    print("done")


if __name__ == "__main__":
    main()
