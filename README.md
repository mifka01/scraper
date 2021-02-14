# Scraper

Scraper is an universal website scraper that works on the basis of xpath.
It works on the vast majority of websites.
## Settings
* test -> Test run for 10 products.
* login -> If your website needs to login before you can see products. (then you have to fill in **login_data.json** file too)
* fields_file -> Turn this on when you dont want to fill in the **fields.json** file. It will trigger console helper to fill it for you.
* with_categories -> If you already have categories scraped.
#### Filenames settings
* products_filename="products.json"
* import_filename="fields.json"
* export_filename="export.csv"
* separator=";"
## Usage

First of all you must upload **products.json** file into resources folder.

If with_categories setting is **False** (recommanded, by default)
```python
Scraper().run()
```
#### products.json

```javascript
[
"url_path_to_product",
"url_path_to_product",
"url_path_to_product",
...
]
```
If with_categories setting is **True**
```python
Scraper(with_categories=True).run()
```
#### products.json

```javascript
[
    {
        "cat":"Category/for/product",
        "url":"url_path_to_product",
    },
    {
        "cat":"Category/for/product",
        "url":"url_path_to_product",
    },
...
]
```

If fields_file setting is **True** you will just follow console helper. 
**Usage** section ends for you here with this setting on.
```python
Scraper(fields_file=False).run()
```
If ts set to **True** (recommanded, set by default)
```python
Scraper().run()
```
Then you must fill in the fields.json file in resources folder.
#### fields.json
```javascript
[
 {
  "name":"name",
  "type":"str",
  "xpath":"xpath_to_element",
  "split":[["/",0,3],[",",1,2]],
  "replace":[["#","hastag"],["...","!"]]
  },
...
]
```
#### Fields
* name(string) -> name of field in export file (csv)
* type(string) -> output type of element
    * str -> clean text(string)
    * links -> return all urls(href) from *a* element in *url,url* format
    * imgs -> return all urls(src) from *img* element in *url,url* format
    * rawn -> return raw html in string format
    * cat -> if you are using with_categories=True

#### Only used with str type according to example above 

* split(matrix)
```python
str.split("/")[:3].split(",")[1:2]
```
* replace(matrix)
```python
str.replace("#","hastag").replace("...","!")
```


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)