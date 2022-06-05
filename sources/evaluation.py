from numpy import log2

def get_mean_average_precision(retrieved_documents: list[str], relevant_documents: list[str]):
    cumul_precisions = []

    for index in range(len(retrieved_documents)):
        indexed_retrieved_docs = retrieved_documents[:(index + 1)]
        indexed_relevant_docs = relevant_documents[:(index + 1)]

        relevant_retrieved_documents = []
        non_relevant_retrieved_documents = []

        for doc in indexed_relevant_docs:
            if doc in indexed_retrieved_docs:
                relevant_retrieved_documents.append(doc)

        for doc in indexed_retrieved_docs:
            if not doc in indexed_relevant_docs:
                non_relevant_retrieved_documents.append(doc)

        tp = len(relevant_retrieved_documents)
        fp = len(non_relevant_retrieved_documents)
        cumul_precisions.append(tp / (tp + fp))

    mean_average_precision = sum(cumul_precisions) / len(cumul_precisions)
    print("MEAN AVERAGE PRECISION:", mean_average_precision)


def get_position_document_ranking(retrieved_documents: list[str], relevant_documents: list[str]) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
    ideal_documents = []
    ranked_documents = []
    document_amount = len(retrieved_documents)

    for index, value in enumerate(retrieved_documents):
        relevant_index = 0
        for rel_index, rel_value in enumerate(relevant_documents):
            if value == rel_value:
                relevant_index = rel_index

        ranked_documents.append((value, document_amount - relevant_index))

    for index, value in enumerate(relevant_documents):
        ideal_documents.append((value, document_amount - index))

    return ranked_documents, ideal_documents


def get_discounted_cumulative_gain(ranked_documents: list[tuple[str, int]]):
    discounted_cumulative_gain = []

    for index, value in enumerate(ranked_documents):
        numerator = 2 ** value[1] - 1
        denominator = log2(index + 2)
        score = numerator / denominator
        discounted_cumulative_gain.append(score)

    return sum(discounted_cumulative_gain)


def get_normalized_discounted_cumulative_gain(retrieved_documents: list[str], relevant_documents: list[str]):
    ranked_documents, ideal_documents = get_position_document_ranking(retrieved_documents, relevant_documents)
    discounted_cumulative_gain = get_discounted_cumulative_gain(ranked_documents)
    ideal_discounted_cumulative_gain = get_discounted_cumulative_gain(ideal_documents)
    normalized_discounted_cumulative_gain = discounted_cumulative_gain / ideal_discounted_cumulative_gain

    print("NORMALIZED DISCOUNTED CUMULATIVE GAIN:", normalized_discounted_cumulative_gain)
