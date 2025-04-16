import requests


CANVAS_DOMAIN = "-"
TOKEN = "-"
TERMS = ["Term Name"]

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



def create_module(course_id):
    url = f"{CANVAS_DOMAIN}/api/v1/courses/{course_id}/modules"
    payload = {
        "module": {
            "name": "-",
            "position": 1
            #"published": True
        }
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Error creating module for course {course_id}: {response.status_code}")
        print(response.text)
    response.raise_for_status()  # Will raise an error if the request fails
    module = response.json()
    module_id = module["id"]

    #publish
    publish_url = f"{CANVAS_DOMAIN}/api/v1/courses/{course_id}/modules/{module_id}"
    publish_payload = {"module": {"published": True}}
    publish_resp = requests.put(publish_url, headers=HEADERS, json=publish_payload)
    publish_resp.raise_for_status()

    return response.json()


def add_external_tool_to_module(course_id, module_id, url):
    module_item_url = f"{CANVAS_DOMAIN}/api/v1/courses/{course_id}/modules/{module_id}/items"
    payload = {
        "module_item": {
            "title": "-",
            "type": "ExternalTool",
            "position": 1,
            "external_url": url,
            "new_tab": True
            #"published": True
        }
    }

    response = requests.post(module_item_url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Error adding external tool to module in course {course_id}: {response.status_code}")
        print(response.text)
    response.raise_for_status()
    item = response.json()
    item_id = item["id"]

    #publish
    publish_item_url = f"{CANVAS_DOMAIN}/api/v1/courses/{course_id}/modules/{module_id}/items/{item_id}"
    publish_payload = {"module_item": {"published": True}}
    publish_resp = requests.put(publish_item_url, headers=HEADERS, json=publish_payload)
    publish_resp.raise_for_status()


def unhide_modules_tab(course_id):
    url = f"{CANVAS_DOMAIN}/api/v1/courses/{course_id}/tabs/modules"
    payload = {
        "hidden": False
    }

    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Error unhiding Modules tab for course {course_id}: {response.status_code}")
        print(response.text)
    response.raise_for_status()


def main():

    term_ids = get_term_ids()

    for term_name, term_id in term_ids.items():
        courses = get_courses(term_id)
        print(f"Processing {len(courses)} courses in '{term_name}'")

        for course in courses:
            course_id = course["id"]
            url = "-"

            module = create_module(course_id)
            module_id = module["id"] 
            print(f"Created new module with ID {module_id} for course {course_id}")

            add_external_tool_to_module(course_id, module_id, url)
            print(f"Added external tool to the new module in course {course_id}")

            unhide_modules_tab(course_id)
            print(f"Unhid Modules tab in course {course_id}")

    print("Finished adding external tools and modules.")


if __name__ == "__main__":
    main()
