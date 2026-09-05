import json

import requests
from bs4 import BeautifulSoup


def web_search():
    url = "https://holosen.net/courses/"
    response = requests.get(url, timeout=30)

    soup = BeautifulSoup(response.content, "html.parser")

    result = soup.select('.edu-course-area > div.container > div')[1]
    courses = result.find_all('div', recursive=False)
    course_list = []
    for course in courses:
        title = course.select_one("h2")
        price = course.select_one(".current-price")

        if title and price:
            title = title.text
            price = price.text
            course_list.append({
                "title": title.strip(),
                "price": price.strip()
            })

    return json.dumps(course_list, ensure_ascii=False)
