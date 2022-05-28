def query_is_valid(query: str, words: list[str]):
    query_is_valid = False
    query_words = query.lower().split(" ")

    for query_word in query_words:
        if query_word in words:
            query_is_valid = True

    return query_is_valid

def get_final_documents_rank(bool_query_docs, documents_cos_sin):
    documents_rank = []

    bool_max_value = 0
    for query_doc in bool_query_docs:
        if query_doc[1] > bool_max_value:
            bool_max_value = query_doc[1]

    vector_max_value = 0.0
    for doc_index in documents_cos_sin:
        if documents_cos_sin[doc_index] > vector_max_value:
            vector_max_value = documents_cos_sin[doc_index]

    for query_doc in bool_query_docs:
        doc_bool_rank = query_doc[1] / bool_max_value
        doc_vect_rank = documents_cos_sin[query_doc[0]] / vector_max_value
        documents_rank.append((query_doc[0], doc_bool_rank * doc_vect_rank))

    return sorted(documents_rank, key=lambda doc: doc[1], reverse=True)