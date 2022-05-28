import os
import json
import requests

# get work keys through subject call
def get_work_keys():
    offset = 0
    nbr_works = 1000

    with open('work_keys.txt', "w") as outfile:
        while True:

            if offset >= nbr_works:
                return

            result = requests.get('https://openlibrary.org/subjects/science_fiction.json?offset=' + str(offset)).json()
            work_keys = [work["key"] for work in result["works"]]
            outfile.writelines("%s\n" % key for key in work_keys)
            offset += len(work_keys)

# get work data using stored work keys
def get_work_data(folder_name: str):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open('work_keys.txt', "r") as infile:
        for work_key in infile:
            book = {}
            work_key = work_key[:-1]
            result = requests.get('https://openlibrary.org' + work_key + ".json").json()

            book["key"] = result["key"] if "key" in result else ""
            book["title"] = result["title"] if "title" in result else ""
            book["covers"] = result["covers"] if "covers" in result else ""
            book["authors"] = result["authors"] if "authors" in result else ""
            book["subjects"] = result["subjects"] if "subjects" in result else ""
            book["description"] = result["description"] if "description" in result else ""

            file_path = os.path.join(folder_name, work_key[7:] + ".json")

            with open(file_path, "w") as outfile:
                json.dump(book, outfile)
                print(book["title"])
