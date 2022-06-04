import os
import re
import json

from functools import reduce

REPLACE_SYMBOLS = [ ".", ",", ":", ";", "!", "?", "(", ")", "\"", "-", " - ", "--", "'", "*", "`", "=", "&", "_" ]

reg1 = re.compile(r"\[([^\(\)])+\]\(http([^\(\)])+\)")
reg2 = re.compile(r"\[([^\(\)])+\]: http([^\s])+\.html")
reg3 = re.compile(r"\(\[source\]\[1\]\)")
reg4 = re.compile(r"http([^\s])+")
reg5 = re.compile(r"…")



def get_string_tokens(string: str, stopwords: list[str]) -> list:
    lower_string = string.lower()
    for symbol in REPLACE_SYMBOLS:
        lower_string = lower_string.replace(symbol, " ")

    tokens = lower_string.split(" ")
    tokens = list(filter(lambda t: t.isalnum(), tokens))
    tokens = list(filter(lambda t: t not in stopwords, tokens))
    tokens = list(filter(lambda t: t != "", tokens))

    return tokens


def get_book_description_tokens(description: str, stopwords: list[str]) -> list:
    description = reg1.sub(" ", description)
    description = reg2.sub(" ", description)
    description = reg3.sub(" ", description)
    description = reg4.sub(" ", description)
    description = reg5.sub(" ", description)

    return get_string_tokens(description, stopwords)


def get_book_subjects_tokens(subjects: list[str], stopwords: list[str]) -> list:
    subjects = list(map(lambda a: a.lower(), subjects))
    subjects_str = reduce(lambda a, b: a + " " + b, subjects, "")

    return get_string_tokens(subjects_str, stopwords)


def get_book_title_tokens(title: str, stopwords: list[str]) -> list:
    return get_string_tokens(title, stopwords)


def get_book_tokens(book: dict, book_description: str, stopwords: list[str]) -> dict:
    book_tokens = {}

    book_description_tokens = get_book_description_tokens(book_description, stopwords)
    book_subjects_tokens = get_book_subjects_tokens(book["subjects"], stopwords)
    book_title_tokens = get_book_title_tokens(book["title"], stopwords)

    for token in book_description_tokens:
        if not token in book_tokens:
            book_tokens[token] = 1
        else: book_tokens[token] += 1

    for token in book_subjects_tokens:
        if not token in book_tokens:
            book_tokens[token] = 1
        else: book_tokens[token] += 1

    for token in book_title_tokens:
        if not token in book_tokens:
            book_tokens[token] = 1
        else: book_tokens[token] += 1

    return book_tokens


def get_clean_books_data(folder_name: str, stopwords: list[str], max_file_nbr: int) -> tuple[list[dict], list[str]]:
    books_data = []
    books_words = []

    files_name = os.listdir(folder_name)
    for index in range(len(files_name)):

        if index >= max_file_nbr:
            break

        file_path = os.path.join(folder_name, files_name[index])
        if os.path.isfile(file_path):
            with open(file_path, "r") as infile:
                book = json.load(infile)

                book_description: str = book["description"] \
                    if isinstance(book["description"], str) \
                    else book["description"]["value"]

                book_cover = book["covers"][0] if isinstance(book["covers"], list) else ""
                book_authors = [ author["author"]["key"] for author in book["authors"] ]
                book_tokens = get_book_tokens(book, book_description, stopwords)

                books_words += book_tokens.keys()

                books_data.append({
                    "key": book["key"],
                    "cover": book_cover,
                    "title": book["title"],
                    "authors": book_authors,
                    "subjects": book["subjects"],
                    "description": book_description,
                    "tokens": book_tokens
                })

    return books_data, sorted(set(books_words))
