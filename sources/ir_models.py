import os
import re
import sys
import json

from functools import reduce
from stopwords import stopwords

from models.boolean_model import get_inverted_index_posting_list, get_query_bool_vector
from models.vector_space_model import get_term_document_weight_matrix, get_query_weight_vector, get_ranked_documents


MAX_FILE_NBR = 100
REPLACE_SYMBOLS = [ ".", ",", ":", ";", "!", "?", "(", ")", "\"", "-", " - ", "--", "'", "*", "`", "=", "&", "_" ]

reg1 = re.compile(r"\[([^\(\)])+\]\(http([^\(\)])+\)")
reg2 = re.compile(r"\[([^\(\)])+\]: http([^\s])+\.html")
reg3 = re.compile(r"\(\[source\]\[1\]\)")
reg4 = re.compile(r"http([^\s])+")
reg5 = re.compile(r"…")



def get_string_tokens(string: str) -> list:
    lower_string = string.lower()
    for symbol in REPLACE_SYMBOLS:
        lower_string = lower_string.replace(symbol, " ")

    tokens = lower_string.split(" ")
    tokens = list(filter(lambda t: t.isalnum(), tokens))
    tokens = list(filter(lambda t: t not in stopwords, tokens))
    tokens = list(filter(lambda t: t != "", tokens))

    return tokens


def get_book_description_tokens(description: str) -> list:
    description = reg1.sub(" ", description)
    description = reg2.sub(" ", description)
    description = reg3.sub(" ", description)
    description = reg4.sub(" ", description)
    description = reg5.sub(" ", description)

    return get_string_tokens(description)


def get_book_subjects_tokens(subjects: list[str]) -> list:
    subjects = list(map(lambda a: a.lower(), subjects))
    subjects_str = reduce(lambda a, b: a + " " + b, subjects, "")

    return get_string_tokens(subjects_str)


def get_book_tokens(book: dict, book_description: str) -> dict:
    book_tokens = {}

    book_description_tokens = get_book_description_tokens(book_description)
    book_subjects_tokens = get_book_subjects_tokens(book["subjects"])

    for token in book_description_tokens:
        if not token in book_tokens:
            book_tokens[token] = 1
        else: book_tokens[token] += 1

    for token in book_subjects_tokens:
        if not token in book_tokens:
            book_tokens[token] = 1
        else: book_tokens[token] += 1

    return book_tokens


def get_clean_books_data(folder_name: str) -> tuple[list[dict], list[str]]:
    books_data = []
    books_words = []

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
                book_tokens = get_book_tokens(book, book_description)

                books_words += book_tokens.keys()

                books_data.append({
                    "key": book["key"],
                    "title": book["title"],
                    "authors": book_authors,
                    "subjects": book["subjects"],
                    "description": book_description,
                    "tokens": book_tokens
                })

    return books_data, sorted(set(books_words))


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        folder_name = sys.argv[1]
        books_data, words = get_clean_books_data(folder_name)
        posting_list = get_inverted_index_posting_list(books_data)
        documents = get_term_document_weight_matrix(books_data, words)

        bool_query_docs = get_query_bool_vector("dinosaurs", words, posting_list)

        query_weight_vector = get_query_weight_vector("dinosaurs", documents, words, books_data)
        documents_cos_sin = get_ranked_documents(documents, query_weight_vector)

        print(bool_query_docs)
        for doc_name in documents_cos_sin:
            if documents_cos_sin[doc_name] > 0.0:
                print(doc_name, documents_cos_sin[doc_name])

