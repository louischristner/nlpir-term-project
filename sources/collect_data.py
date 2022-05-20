import json
import requests

MAX_NBR_WORKS = 1000

# get work keys through subject call
def get_work_keys():
    offset = 0
    nbr_works = 16432 if 16432 < MAX_NBR_WORKS else MAX_NBR_WORKS

    with open('work_keys.txt', "w") as outfile:
        while True:

            if offset >= nbr_works:
                return

            result = requests.get('https://openlibrary.org/subjects/science_fiction.json?offset=' + str(offset)).json()
            work_keys = [work["key"] for work in result["works"]]
            outfile.writelines("%s\n" % key for key in work_keys)
            offset += len(work_keys)

# get work data using stored work keys
def get_work_data():
    index = 0

    with open('work_keys.txt', "r") as infile:
        while True:
            book = {}
            work_key = infile.readline()
            work_key = work_key[:-1]
            result = requests.get('https://openlibrary.org' + work_key + ".json").json()

            book["key"] = result["key"] if "key" in result else ""
            book["title"] = result["title"] if "title" in result else ""
            book["covers"] = result["covers"] if "covers" in result else ""
            book["authors"] = result["authors"] if "authors" in result else ""
            book["subjects"] = result["subjects"] if "subjects" in result else ""
            book["description"] = result["description"] if "description" in result else ""

            with open('books/' + work_key[7:] + '.json', "w") as outfile:
                json.dump(book, outfile)

            index += 1

if __name__ == "__main__":
    # get_work_keys()
    get_work_data()