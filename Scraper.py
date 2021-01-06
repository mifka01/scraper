import requests
from lxml import html
import pandas as pd
import pathlib
import json
import time


class Scraper:

    def __init__(self, products_filename = "products.json", import_filename="fields.json",export_filename = "export.csv", separator=";", fields_file = True, test=False):
        self.base_path = str(pathlib.Path(__file__).parent.absolute())
        self.test = test
        self.get_products(products_filename)
        self.wanted_fields = []
        self.separator = separator
        self.export_filename = export_filename
        self.import_filename = import_filename
        self.one_time = 2.66667
        self.fields_file = fields_file

    def get_products(self, filename):
        with open(f'{self.base_path}/{filename}') as f:
            self.products = json.load(f)
        if self.test == True:
            self.products = self.products[:10]
        print(f"Počet produktů: {len(self.products)}")

    def get(self, url):
        return requests.get(url).content

    def export(self, data):
        data = pd.DataFrame.from_records(data)
        data.to_csv(f"{self.base_path}/{self.export_filename}",sep=f"{self.separator}")

    def scrape(self, tree):
        data = {}
        for el in self.wanted_fields:
            if el["type"] == "str":
                val = self.clean("".join(tree.xpath(el["xpath"] + "//text()")))
            elif el["type"] == "links":
                val = self.list_to_string(self.remove_duplicates(tree.xpath(el["xpath"] + "/@href")))
            elif el["type"] == "list":
                val = self.list_to_string(self.remove_duplicates(tree.xpath(el["xpath"] + "//text()")))
            else:
                val = ""
            data[el["name"]] = val

        return data

    def clean(self, bloated_string) -> str:
        if type(bloated_string) != str:
            bloated_string = str(bloated_string)

        if "\n" in bloated_string:
            if bloated_string.startswith("\n"):
                bloated_string.replace("\n","")
            bloated_string.replace("\n","<br>")
        return " ".join(bloated_string.strip().split())

    def remove_duplicates(self, bloated_list: list) -> list:
        return list(set(bloated_list))

    def list_to_string(self, bloated_list: list) -> str:
        return ",".join(bloated_list)

    def set_fields(self):
        if self.fields_file:
            with open(f'{self.base_path}/{self.import_filename}') as f:
                self.wanted_fields = json.load(f)
        else:
            print("Zadej pole pro parser")
            print("1 pro konec 0 pro konec")
            while True:
                self.wanted_fields.append({
                    "name": input("Zadej nazev: "),
                    "type": input("Zadej typ [str, links, list]: "),
                    "xpath":input("Zadej xpath: ")
                })
                action = int(input("Akce: "))
                if action == 1:
                    continue
                else:
                    break

    def run(self):
        self.set_fields()
        data = []
        for i, product in enumerate(self.products):
            if i == 0:
                start_time = time.time()
            print("Progress {:2.1%}, Zbývající čas: {} min".format(i / len(self.products),round(self.one_time*len(self.products[i:len(self.products)])/60),0), end="\r")
            tree = html.fromstring(self.get(product))
            data.append(self.scrape(tree))
            if i == 0:
                self.one_time = time.time() - start_time
        self.export(data)

Scraper().run()
