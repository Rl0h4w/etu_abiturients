from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import multiprocessing

class Abiturient:
    def __init__(self, num, score):
        self.num = num
        self.score = score
        self.faculty_priority = dict()

    def __str__(self) -> str:
        return f"Num: {self.num}    Score: {self.score}"

    def add_faculty(self, faculty, priority, ):
        self.faculty_priority[priority] = faculty


def get_table(sp):
    return ([j.text if not j.find("a") else j.find("a").get("href") for j in i.find_all("td")] for i in sp.find_all("tr"))


def request(url):
    options = Options()
    options.add_argument('--headless')
    with webdriver.Chrome(options=options) as browser:
        browser.get(url)
        return browser.page_source



if __name__=="__main__":
    scorelists_url = r"https://abit.etu.ru/ru/postupayushhim/bakalavriat-i-specialitet/konkursnye-spiski/?competitions=1-2"
    base_url = r"https://etu.ru/en/university/"
    faculties_arr = get_table(BeautifulSoup(request(scorelists_url), 'lxml'))
    scorelists_faculties = [base_url + i[-1] for i in faculties_arr if i]
    with multiprocessing.Pool() as pool:
        pool.map(request, scorelists_faculties)

