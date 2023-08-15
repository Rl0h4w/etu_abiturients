from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import asyncio

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

    def add_faculty(self, faculty, priority, ):
        self.faculty_priority[priority] = faculty


class Faculty:
    def __init__(self, name, max_ab):
        self.name = name
        self.max_ab = max_ab
        self.__array = []

    def add(self, obj):
        self.__array.append(obj)

    def __str__(self) -> str:
        return f"Name: {self.name}  MAX: {self.max_ab}"


class University:
    def __init__(self, faculties):
        self.faculties = faculties


def get_table(sp):
    return ([j.text if not j.find("a") else j.find("a").get("href") for j in i.find_all("td")] for i in sp.find_all("tr"))


def leti():
    abiturients = set()
    faculties = set()
    browser = Browser()
    url_lists = r"https://abit.etu.ru/ru/postupayushhim/bakalavriat-i-specialitet/konkursnye-spiski/?competitions=1-2"
    url_base = r"https://abit.etu.ru/"
    for i in filter(
        lambda x: len(x) == 4 and x[2] != "-", get_table(browser.get_html(url_lists))
    ):
        url_faculty = url_base + i[2]
        site = browser.get_html(url_faculty)
        faculty_str = site.find("h2").text
        max_abiturients = site.find(
            "div",
            class_="col-md-3 d-flex justify-content-center align-items-center places-list",
        )
        max_abiturients = int(re.search(r"\d+", max_abiturients.text).group())
        for j in filter(
            lambda x: x and all(y.isdigit() for y in (x[0], x[2], *x[4:10])),
            get_table(site),
        ):
            num = int(''.join(re.findall('\d', j[1])))
            priority = int(j[2])
            score = int(j[4])
            admission = True if j[-3] == 'Да' else False
            original = True if j[-2] == 'Да' else False
            if original:
                searched = [i for i in filter(lambda x: x.num == num, abiturients)]
                if searched is None:
                    abiturient = Abiturient(num, score=score if not admission else 300)
                    abiturients.add(abiturient)
                else:
                    searched[0].add_faculty(faculty_str, priority)
            
            print(*abiturients, sep='\n')
                    
                

if __name__ == "__main__":
    leti()
