from numpy import dot
from math import log, log2
from numpy.linalg import norm

def get_term_document_weight_matrix(books_data: list[dict], words: list[str]):
    documents: list[list[float]] = []
    books_amount = len(books_data)
    words_amount = len(words)

    documents = [None] * books_amount

    for index in range(books_amount):
        documents[index] = [0.0] * words_amount
        for word_index in range(words_amount):
            tf, df = 0, 0
            word = words[word_index]
            book_tokens = books_data[index]["tokens"]

            if word in book_tokens:
                tf = 1 + log(book_tokens[word])

                for book_data in books_data:
                    if word in book_data["tokens"].keys():
                        df += 1

                weight = tf * log2(books_amount / df)
                documents[index][word_index] = weight

    return documents


def get_query_weight_vector(query: str, documents: list[list[float]], words: list[str], books_data: list[dict]) -> list[float]:
    words_amount = len(words)
    documents_amount = len(documents)

    query_terms = query.lower().split(" ")
    query_weight_vector = [0.0] * words_amount
    query_terms_frequencies: dict[str, int] = {}

    for query_term in query_terms:
        if not query_term in query_terms_frequencies:
            query_terms_frequencies[query_term] = 1
        else: query_terms_frequencies[query_term] += 1

    for word_index in range(words_amount):
        tf, df, = 0, 0
        word = words[word_index]

        if word in query_terms:
            tf = 1 + log(query_terms_frequencies[word])

            for book_data in books_data:
                if word in book_data["tokens"].keys():
                    df += 1

            weight = tf * log2(documents_amount / df)
            query_weight_vector[word_index] = weight

    return query_weight_vector


def cosine_similarity(vector1: list[float], vector2: list[float]):
    return dot(vector1, vector2) / (norm(vector1) * norm(vector2))


def get_ranked_documents(documents: list[list[float]], query_weight_vector: list[float]) -> dict[int, float]:
    documents_cos_sin: dict[str, float] = {}

    for doc_index in range(len(documents)):
        document = documents[doc_index]
        documents_cos_sin[doc_index] = cosine_similarity(document, query_weight_vector)

    return dict(sorted(documents_cos_sin.items(), key=lambda item: item[1], reverse=True))
