import os
import re
import sys
import json

from functools import reduce
from stopwords import stopwords



MAX_FILE_NBR = 10
REPLACE_SYMBOLS = [ ".", ",", ":", ";", "!", "?", "(", ")", "\"", "-", " - ", "--", "'", "*", "`" ]

reg1 = re.compile(r"\[([^\(\)])+\]\(http([^\(\)])+\)")
reg2 = re.compile(r"\[([^\(\)])+\]: http([^\s])+\.html")
reg3 = re.compile(r"\(\[source\]\[1\]\)")
reg4 = re.compile(r"…")



def get_string_tokens(string: str) -> list:
    lower_string = string.lower()
    for symbol in REPLACE_SYMBOLS:
        lower_string = lower_string.replace(symbol, " ")

    tokens = lower_string.split(" ")
    tokens = list(filter(lambda t: t not in stopwords, tokens))
    tokens = list(filter(lambda t: t != "", tokens))

    return tokens


def get_book_description_tokens(description: str) -> list:
    description = reg1.sub(" ", description)
    description = reg2.sub(" ", description)
    description = reg3.sub(" ", description)
    description = reg4.sub(" ", description)

    return get_string_tokens(description)


def get_book_subjects_tokens(subjects: list[str]) -> list:
    subjects = list(map(lambda a: a.lower(), subjects))
    subjects_str = reduce(lambda a, b: a + " " + b, subjects, "")

    return get_string_tokens(subjects_str)


def get_clean_books_data(folder_name: str) -> list[dict]:
    books_data = []

    files_name = os.listdir(folder_name)

    for index in range(len(files_name)):

        if index >= MAX_FILE_NBR:
            break

        file_path = os.path.join(folder_name, files_name[index])
        if os.path.isfile(file_path):
            with open(file_path, "r") as infile:
                book = json.load(infile)

                book_description: str = book["description"] \
                    if isinstance(book["description"], str) \
                    else book["description"]["value"]

                book_authors = [ author["author"]["key"] for author in book["authors"] ]
                book_description_tokens = get_book_description_tokens(book_description)
                book_subjects_tokens = get_book_subjects_tokens(book["subjects"])

                books_data.append({
                    "key": book["key"],
                    "title": book["title"],
                    "authors": book_authors,
                    "subjects": book["subjects"],
                    "description": book_description,
                    "tokens": book_description_tokens + book_subjects_tokens
                })

    return books_data


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        folder_name = sys.argv[1]
        books_data = get_clean_books_data(folder_name)

        for book in books_data:
            print(book["title"], book["authors"])
            for token in book["tokens"]:
                print(token)

