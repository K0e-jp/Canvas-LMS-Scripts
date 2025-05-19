import requests
#from datetime import datetime, timedelta

CANVAS_DOMAIN = "-"
TOKEN = "-"
TERMS = ["-"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
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
        url = response.links.get("next", {}).get("url")
    return courses

def create_calendar_event(course_id):
    url = f"https://{CANVAS_DOMAIN}/api/v1/calendar_events"

    event_payload = {
        "calendar_event": {
            "context_code": f"course_{course_id}",
            "title": "Eventi Title",
            "description": "Event description ex: National holiday, no classes held",
            "start_at": "yyyy-MM-ddThh:mm:ss",
            "end_at": "yyyy-MM-ddThh:mm:ss",
            #"all_day": "true",
            #"location_name": "In Person"
        }
    }

    response = requests.post(url, headers=HEADERS, json=event_payload)
    if response.status_code != 201:
        print(f"Error creating calendar event in course {course_id}: {response.status_code}")
        print(response.text)
    response.raise_for_status()
    event = response.json()
    print(f"Created calendar event in course {course_id}: Event ID {event['id']}")


def main():
    term_ids = get_term_ids()

    for term_name, term_id in term_ids.items():
        courses = get_courses(term_id)
        print(f"Processing {len(courses)} courses in '{term_name}'")

        for course in courses:
            course_id = course["id"]
            create_calendar_event(course_id)

    print("Finished creating calendar events.")

if __name__ == "__main__":
    main()
