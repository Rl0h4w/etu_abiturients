import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
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


class Universities:
    def __init__(self):
        self.abiturients = []
        self.__leti_url = r"https://abit.etu.ru/"
        self.__leti_sp_url = r"https://abit.etu.ru/ru/postupayushhim/bakalavriat-i-specialitet/konkursnye-spiski/?competitions=1-2"
        self.__spgu_url = r"https://priem2023.spmi.ru/data"
        self.__spgu_sp_url = r"https://priem2023.spmi.ru/data/ub.json"

    def add_leti(self):
        br = Browser()
        for i in filter(
            lambda x: len(x) == 4 and x[2] != "-",
            self.get_table(br.get_html(self.__leti_sp_url)),
        ):
            url = self.__leti_url + i[2]
            site = br.get_html(url)
            faculty = site.find("h2").text
            max_ab = site.find(
                "div",
                class_="col-md-3 d-flex justify-content-center align-items-center places-list",
            )
            max_ab = int(re.search(r"\d+", max_ab.text).group())
            for j in filter(
                lambda x: x and all(y.isdigit() for y in (x[0], x[2], *x[4:10])),
                self.get_table(site),
            ):
                j[1] = j[1].replace("-", "").replace(" ", "")
                self.abiturients.append(
                    Abiturient(
                        int(j[1]),
                        int(j[4]),
                        True if j[-2] == "Да" else False,
                        self.__leti_url,
                        faculty,
                        int(j[2]),
                    )
                )

    def add_spgu(self):
        br = Browser()
        for i in json.loads(br.get_html(self.__spgu_sp_url).text):
            faculty = i["okso_title"]
            url = self.__spgu_url + "/" + i["program_id"] + "1" + ".json"
            for j in json.loads(br.get_html(url).text):
                try:
                    num = int(j["snilsnumber_p"].replace("-", ""))
                    score = int(j["sum_ball"])
                    original = False if j["orig"] == "Копия" else True
                    priority = int(j["priority_p"])
                    self.abiturients.append(
                        Abiturient(
                            num, score, original, self.__spgu_url, faculty, priority
                        )
                    )
                except Exception as e:
                    print(j)

    @staticmethod
    def get_table(sp):
        return (
            [
                j.text if not j.find("a") else j.find("a").get("href")
                for j in i.find_all("td")
            ]
            for i in sp.find_all("tr")
        )


class Abiturient:
    def __init__(self, num, score, original, university, faculty, priority):
        self.num = num
        self.score = score
        self.original = original
        self.university = university
        self.faculty = faculty
        self.priority = priority

    def __str__(self):
        return f"NUM: {self.num}___SCORE: {self.score}___ORIGINAL: {self.original}___UNIVERSITY: {self.university}___FACULTY: {self.faculty}___PRIORITY: {self.priority}\n"


class Faculty:
    pass


if __name__ == "__main__":
    univ = Universities()
    univ.add_leti()
