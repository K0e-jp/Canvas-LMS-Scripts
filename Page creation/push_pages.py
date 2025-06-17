import requests

CANVAS_DOMAIN = "-"
TOKEN = "-"
TERMS = ["Term Name"]
SAMPLE_COURSE_ID = "ID of the course the page is copied from"
SAMPLE_PAGE_NAME = "URL friendly name of the page to be copied"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
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
        url = response.links.get("next", {}).get("url")
    return courses


def get_sample_page():
    url = f"{CANVAS_DOMAIN}/api/v1/courses/{SAMPLE_COURSE_ID}/pages/{SAMPLE_PAGE_NAME}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error fetching sample page: {response.status_code}")
        print(response.text)
    response.raise_for_status()
    return response.json()


def create_page(course_id, page_data):
    url = f"{CANVAS_DOMAIN}/api/v1/courses/{course_id}/pages"
    payload = {
        "wiki_page": {
            "title": page_data["title"],
            "body": page_data["body"],
            "published": True
        }
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Error creating page in course {course_id}: {response.status_code}")
        print(response.text)
    response.raise_for_status()
    return response.json()


def create_redirect_app(course_id):
    url = f"{CANVAS_DOMAIN}/api/v1/courses/{course_id}/external_tools"

    payload = {
        "name": "Name for redirect tool",
        "privacy_level": "public",
        "consumer_key": "not_needed",
        "shared_secret": "not_needed",
        "config_type": "manual_entry",
        "tool_id": "redirect",
        "url": "https://www.edu-apps.org/redirect",
        "custom_fields": {
            "url": f"{CANVAS_DOMAIN}/courses/{course_id}/pages/policies-and-procedures"
        },
        "course_navigation": {
            "enabled": True,
            "text": "name shown on navigation bar",
            "visibility": "public"
        }
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Error creating redirect app in course {course_id}: {response.status_code}")
        print(response.text)
    response.raise_for_status()
    return response.json()



def move_tab_to_position(course_id, tab_id, position=3):
    url = f"{CANVAS_DOMAIN}/api/v1/courses/{course_id}/tabs/{tab_id}"
    payload = {
        "position": position
    }

    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Error moving tab {tab_id} in course {course_id}: {response.status_code}")
        print(response.text)
    response.raise_for_status()
    return response.json()


def main():
    sample_page = get_sample_page()
    term_ids = get_term_ids()

    for term_name, term_id in term_ids.items():
        courses = get_courses(term_id)
        print(f"Processing {len(courses)} courses in '{term_name}'")

        for course in courses:
            course_id = course["id"]
            course_page = create_page(course_id, sample_page)
            print(f"Created page '{course_page['title']}' in course {course_id}")

            tool_response = create_redirect_app(course_id)
            print(f"Created redirect tool in course {course_id}")

            tab_id = f"context_external_tool_{tool_response['id']}"
            move_tab_to_position(course_id, tab_id)
            print(f"Moved tab to position in course {course_id}")

    print("Finished creating pages and redirect tools in all courses.")


if __name__ == "__main__":
    main()
