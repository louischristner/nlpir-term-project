import os
import json
import logging
import requests
import threading

# get work keys through subject call
def get_work_keys(nbr_works: int):
    offset = 0

    with open('work_keys.txt', "w") as outfile:
        while True:

            if offset >= nbr_works:
                return

            try:
                result = requests.get('https://openlibrary.org/subjects/science_fiction.json?offset=' + str(offset)).json()
                work_keys = [work["key"] for work in result["works"]]
                outfile.writelines("%s\n" % key for key in work_keys)
                offset += len(work_keys)
            except requests.exceptions.JSONDecodeError:
                offset += 1

# get book data from work key
def get_book_data(work_key: str, folder_name: str):
    try:
        book = {}
        result = requests.get('https://openlibrary.org' + work_key + ".json").json()

        book["key"] = result["key"] if "key" in result else ""
        book["title"] = result["title"] if "title" in result else ""
        book["covers"] = result["covers"] if "covers" in result else ""
        book["authors"] = result["authors"] if "authors" in result else ""
        book["subjects"] = result["subjects"] if "subjects" in result else ""
        book["description"] = result["description"] if "description" in result else ""

        file_path = os.path.join(folder_name, work_key[7:] + ".json")

        with open(file_path, "w") as outfile:
            logging.info(book["title"])
            json.dump(book, outfile)
    except:
        pass

# get work data using stored work keys
def get_work_data(folder_name: str):
    threads: list[threading.Thread] = []

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open('work_keys.txt', "r") as infile:
        for work_key in infile:
            x = threading.Thread(target=get_book_data, args=(work_key[:-1], folder_name))
            threads.append(x)
            x.start()

    for thread in threads:
        thread.join()
