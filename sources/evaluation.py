def get_precision_and_recall(retrieved_documents: list[str], relevant_documents: list[str]):
    relevant_retrieved_documents = []
    relevant_not_retrieved_documents = []
    non_relevant_retrieved_documents = []

    for doc in relevant_documents:
        if doc in retrieved_documents:
            relevant_retrieved_documents.append(doc)
        else: relevant_not_retrieved_documents.append(doc)

    for doc in retrieved_documents:
        if not doc in relevant_documents:
            non_relevant_retrieved_documents.append(doc)

    tp = len(relevant_retrieved_documents)
    fp = len(non_relevant_retrieved_documents)
    fn = len(relevant_not_retrieved_documents)

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)

    print("PRECISION & RECALL:", precision, recall)


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
