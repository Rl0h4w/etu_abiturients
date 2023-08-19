from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import json


class Browser:
    def __init__(self):
        self.__options = Options()
        self.__options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.__options)

    def get_html(self, url):
        self.driver.get(url)
        return BeautifulSoup(self.driver.page_source, "lxml")

    def __del__(self):
        self.driver.quit()


class Abiturient:
    def __init__(self, num, score):
        self.num = num
        self.score = score
        self.faculty_priority = dict()

    def __str__(self) -> str:
        return f"Num: {self.num}    Score: {self.score}"

    def add_faculty(self, faculty, priority):
        self.faculty_priority[priority] = faculty


class Faculty:
    def __init__(self, name, max_ab):
        self.name = name
        self.max_ab = max_ab
        self.array = []

    def add(self, obj):
        self.array.append(obj)
        

    def __str__(self) -> str:
        return f"Name: {self.name}  MAX: {self.max_ab}"


    def show(self):
        print(*self.__array, self.max_ab, sep='\n')




def get_table(sp):
    return ([j.text if not j.find("a") else j.find("a").get("href") for j in i.find_all("td")] for i in
            sp.find_all("tr"))


def leti():
    raw_dct = dict()
    faculties = dict()
    abiturients = dict()
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
            raw_dct['abiturients'] = data['abiturients']
            raw_dct['faculties'] = data['faculties']

    except FileNotFoundError:
        with open('data.json', 'w') as file:
            browser = Browser()
            url_lists = r"https://abit.etu.ru/ru/postupayushhim/bakalavriat-i-specialitet/konkursnye-spiski/?competitions=1-2"
            url_base = r"https://abit.etu.ru/"
            faculties_raw = dict()
            abiturients_raw = []

            for i in filter(
                    lambda x: len(x) == 4 and x[2] != "-", get_table(browser.get_html(url_lists))
            ):

                url_faculty = url_base + i[2]
                site = browser.get_html(url_faculty)
                faculty_str = str(site.find("h2").text)
                max_abiturients = site.find(
                    "div",
                    class_="col-md-3 d-flex justify-content-center align-items-center places-list",
                )
                max_abiturients = int(re.search(r"\d+", max_abiturients.text).group())
                if faculty_str not in faculties_raw:
                    faculties_raw[faculty_str] = max_abiturients

                for j in filter(
                        lambda x: x and all(y.isdigit() for y in (x[0], x[2], *x[4:10])),
                        get_table(site),
                ):
                    num = int(''.join(re.findall('\d', j[1])))
                    priority = int(j[2])
                    score = int(j[4])
                    admission = True if j[-3] == 'Да' else False
                    original = True if j[-2] == 'Да' else False
                    abiturients_raw.append({'num': num, 'faculty': faculty_str, 'priority': priority,
                                            'score': 300 if score < 300 and admission else score,
                                            'admission': admission, 'original': original})

            raw_dct['abiturients'] = abiturients_raw
            raw_dct['faculties'] = faculties_raw
            json.dump(raw_dct, file)
    for faculty_str, max_abiturients in raw_dct['faculties'].items():
        faculties[faculty_str] = Faculty(faculty_str, max_abiturients)
    for abiturient_dct in raw_dct['abiturients']:
        if abiturient_dct['original']:
            if abiturient_dct['num'] not in abiturients:
                ab = Abiturient(abiturient_dct['num'], abiturient_dct['score'])
                ab.add_faculty(abiturient_dct['faculty'], abiturient_dct['priority'])
                abiturients[abiturient_dct['num']] = ab
            else:
                abiturients[abiturient_dct['num']].add_faculty(abiturient_dct['faculty'], abiturient_dct['priority'])

    for ab in sorted(abiturients.values(), key=lambda x: [x.score, list(x.faculty_priority.values())], reverse=True):
        for priority, faculty_str in ab.faculty_priority.items():
            faculty = faculties[faculty_str]
            if len(faculty.array) < faculty.max_ab:
                faculty.add(ab)
                break
            elif len(faculty.array) == faculty.max_ab:
                    if ab in faculty.array:
                        next
                    else:
                        break
    
    for s, n in faculties.items():
        print(s)
        print(*n.array, sep='\n')
        print('************************************')
    


if __name__ == "__main__":
    leti()
