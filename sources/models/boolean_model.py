def get_inverted_index_posting_list(books_data: list[dict]):
    posting_list: dict[str, list[tuple[int, int]]] = {}

    for index in range(len(books_data)):
        book_data = books_data[index]
        for token in book_data["tokens"]:
            if not token in posting_list:
                posting_list[token] = list()
            posting_list[token].append((index, book_data["tokens"][token]))

    return posting_list


def get_documents_from_terms(query_terms: list[str], words: list[str], posting_list: dict[str, list[tuple[int, int]]]):
    query_documents: list[tuple[int, int]] = []

    for term in query_terms:
        clean_term = term.strip().lower()
        if clean_term in words:
            for doc_index in posting_list[clean_term]:
                query_documents.append(doc_index)

    return query_documents


def get_query_bool_vector(query: str, words: list[str], posting_list: dict[str, list[tuple[int, int]]]):
    query_documents: list[tuple[int, int]] = []
    query_terms = query.lower().split(" ")
    query_len = len(query_terms)

    # AND only
    unranked_documents = get_documents_from_terms(query_terms, words, posting_list)
    unranked_doc_indexes = list(map(lambda item: item[0], unranked_documents))

    filtered_doc_indexes = list(set(filter(lambda item: unranked_doc_indexes.count(item) == query_len, unranked_doc_indexes)))
    filtered_documents = list(filter(lambda item: item[0] in filtered_doc_indexes, unranked_documents))

    cumuled_frequency_documents = {}

    for doc in filtered_documents:
        if not doc[0] in cumuled_frequency_documents:
            cumuled_frequency_documents[doc[0]] = 0
        cumuled_frequency_documents[doc[0]] += doc[1]

    sorted_frequency_documents = dict(sorted(cumuled_frequency_documents.items(), key=lambda item: item[1], reverse=True))

    for doc in sorted_frequency_documents:
        query_documents.append((doc, sorted_frequency_documents[doc]))

    return query_documents
