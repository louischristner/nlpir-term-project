from flask import Flask
from flask import request, render_template

import os
import concurrent.futures

from sources.stopwords import stopwords
from sources.collect_data import get_work_data
from sources.ir_models import get_clean_books_data
from sources.query_utils import query_is_valid, get_final_documents_rank
from sources.evaluation import get_mean_average_precision, get_normalized_discounted_cumulative_gain

from sources.models.boolean_model import get_inverted_index_posting_list, get_query_bool_vector
from sources.models.vector_space_model import get_term_document_weight_matrix, get_vector_space_model_result

# models generation

MAX_FILE_NBR = 2000

if not os.path.isdir("books"):
    get_work_data("books")

books_data, words = get_clean_books_data("books", stopwords, MAX_FILE_NBR)
posting_list = get_inverted_index_posting_list(books_data)
documents = get_term_document_weight_matrix(books_data, words)

# evaluate models

RELEVANT_DOCUMENTS = [
    "Fragment",
    "Miss Peregrine's Home for Peculiar Children",
    "Letters from Atlantis",
    "L'\u00cele myst\u00e9rieuse",
    "An Antarctic Mystery",
    "Island of Dr. Moreau",
    "R.U.R",
    "The Island Stallion Races",
    "Concrete island",
    "The sandcastle empire",
    "The Outsider",
    "Green boy",
    "Envy",
    "A grey moon over China",
    "Broken Crowns (Internment Chronicles)",
    "The Overlord Protocol",
    "The fountains of paradise",
    "The Survivors Club",
    "The Island Of Excess Love"
]

def evaluate_model_result(documents_rank: list, relevant_documents: list[str]):
    retrieved_documents = [ books_data[doc[0]]["title"] for doc in documents_rank ]
    get_mean_average_precision(retrieved_documents, relevant_documents)
    get_normalized_discounted_cumulative_gain(retrieved_documents, relevant_documents)

def evaluate_models(query: str, relevant_documents: list[str]):
    bool_query_docs = get_query_bool_vector(query, words, posting_list)
    documents_cos_sin = get_vector_space_model_result(query, documents, words, books_data)
    documents_cos_sin_filtered = list(filter(lambda x: x[1] > 0.0, documents_cos_sin.items()))
    documents_rank = get_final_documents_rank(bool_query_docs, documents_cos_sin)

    print("-- BOOLEAN MODEL --")
    evaluate_model_result(bool_query_docs, relevant_documents)
    print("-- VECTOR SPACE MODEL --")
    evaluate_model_result(documents_cos_sin_filtered, relevant_documents)
    print("-- COMBINED MODELS --")
    evaluate_model_result(documents_rank, relevant_documents)

evaluate_models("island", RELEVANT_DOCUMENTS)

# Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev")

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/", methods=["POST", "GET"])
    def index():
        books_infos = []

        if request.method == "POST":
            query = request.form["query"]

            if query_is_valid(query, words):
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    bool_thread_result = executor.submit(get_query_bool_vector, query, words, posting_list)
                    vect_thread_result = executor.submit(get_vector_space_model_result, query, documents, words, books_data)

                    bool_query_docs = bool_thread_result.result()
                    documents_cos_sin = vect_thread_result.result()

                    documents_rank = get_final_documents_rank(bool_query_docs, documents_cos_sin)

                    for doc in documents_rank:
                        books_infos.append(books_data[doc[0]])

        return render_template('index.html', books_infos=books_infos)

    return app