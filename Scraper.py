import requests
from lxml import html
import pandas as pd
import pathlib
import json
import time


class Scraper:

    def __init__(self, products_filename="products.json",
                 import_filename="fields.json",
                 export_filename="export.csv",
                 separator=";", fields_file=True,
                 test=False, login=False,
                 with_categories=False):
        self.base_path = str(pathlib.Path(__file__).parent.absolute())
        self.test = test
        self.get_products(products_filename)
        self.wanted_fields = []
        self.separator = separator
        self.export_filename = export_filename
        self.import_filename = import_filename
        self.one_time = 2.66667
        self.fields_file = fields_file
        self.start_time = None
        self.login = login
        self.with_categories = with_categories
        if self.login:
            self.logme()

    def get_products(self, filename):
        with open(f'{self.base_path}/resources/{filename}') as f:
            self.products = json.load(f)
        if self.test:
            self.products = self.products[:10]
        print(f"Počet produktů: {len(self.products)}")

    def logme(self):
        with open(f'{self.base_path}/resources/login_data.json') as f:
            login_data = json.load(f)
        with requests.Session() as session:
            session.post(login_data["url"], data=login_data["data"])
            self.session = session

    def get(self, url):
        if self.login:
            return self.session.get(url).content
        return requests.get(url).content

    def export(self, data, errors):
        data = pd.DataFrame.from_records(data)
        data.to_csv(
            f"{self.base_path}/output/{self.export_filename}", sep=f"{self.separator}")
        with open(f'{self.base_path}/output/errors.json', 'w') as f:
            json.dump(errors, f)
        print("Process finished --- %s seconds ---" %
              (time.time() - self.start_time))

    def scrape(self, tree):
        data = {}
        for el in self.wanted_fields:
            val = None
            if el["type"] == "str":
                if len(el["replace"][0]) > 0:
                    for replace in el["replace"]:
                        if val is None:
                            val = self.clean(self.clean(
                            "".join(tree.xpath(el["xpath"] + "//text()"))).replace(replace[0],replace[1]))
                        else:
                            val = self.clean(val.replace(replace[0],replace[1]))
                else:
                    val = self.clean(
                        "".join(tree.xpath(el["xpath"] + "//text()")))
                if len(el["split"][0]) > 0:
                    for split in el["split"]:
                        if val is None:
                            val = self.clean(self.clean(
                                "".join(tree.xpath(el["xpath"] + "//text()"))).split(split[0])[split[1]:split[2]])
                        else:
                            val = self.clean(val.split(split[0])[split[1]:split[2]])
                else:
                    if val is None:
                        val = self.clean(
                            "".join(tree.xpath(el["xpath"] + "//text()")))
            elif el["type"] == "str_list":
                val = self.list_to_string(
                    tree.xpath(el["xpath"] + "//text()"), delimiter="~")
            elif el["type"] == "links":
                val = self.list_to_string(self.remove_duplicates(
                    tree.xpath(el["xpath"] + "/@href")))
            elif el["type"] == "raw":
                val = html.tostring(tree.xpath(el["xpath"])[0], encoding="unicode")
            elif el["type"] == "imgs":
                val = self.list_to_string(self.remove_duplicates(
                    tree.xpath(el["xpath"] + "/@src")))
            elif el["type"] == "cat":
                val = self.list_to_string(tree.xpath(
                    el["xpath"] + "//text()"), delimiter="/")
            else:
                val = ""
            data[el["name"]] = val
            if self.with_categories:
                data["cat"] = self.category
        return data

    def clean(self, bloated_string) -> str:
        if type(bloated_string) != str:
            if type(bloated_string) == list:
                bloated_string = "/".join(bloated_string)
            else:
                bloated_string = str(bloated_string)

        if "\n" in bloated_string:
            if bloated_string.startswith("\n"):
                bloated_string.replace("\n", "")
            bloated_string.replace("\n", "<br>")
        return " ".join(bloated_string.strip().split())

    def remove_duplicates(self, bloated_list: list) -> list:
        return list(dict.fromkeys(bloated_list))

    def list_to_string(self, bloated_list, delimiter=",") -> str:
        return delimiter.join(bloated_list)

    def set_fields(self):
        if self.fields_file:
            with open(f'{self.base_path}/resources/{self.import_filename}') as f:
                self.wanted_fields = json.load(f)
        else:
            print("Zadej pole pro parser")
            print("1 pro další 0 pro konec")
            while True:
                self.wanted_fields.append({
                    "name": input("Zadej nazev: "),
                    "type": input("Zadej typ [str, links, list, imgs]: "),
                    "xpath": input("Zadej xpath: ")
                })
                action = int(input("Akce: "))
                if action == 1:
                    continue
                break

    def run(self):
        self.set_fields()
        self.start_time = time.time()
        data = []
        errors = []
        for i, product in enumerate(self.products):
            if i == 0:
                start_time = time.time()
            print("Průběh {:2.1%}, Zbývající čas: {} min".format(i / len(self.products),
                                                      round(self.one_time*len(self.products[i:len(self.products)])/60), 0), end="\r")
            if self.with_categories:
                self.category = product["cat"]
                tree = html.fromstring(self.get(product["url"]))
            else:
                tree = html.fromstring(self.get(product))
            try:
                data.append(self.scrape(tree))
            except:
                errors.append(product)

            if i == 0:
                self.one_time = time.time() - start_time
        self.export(data, errors)


Scraper().run()
