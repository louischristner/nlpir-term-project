from flask import Flask
from flask import request, render_template

import os
import concurrent.futures

from sources.stopwords import stopwords
from sources.collect_data import get_work_data
from sources.ir_models import get_clean_books_data
from sources.query_utils import query_is_valid, get_final_documents_rank
from sources.models.boolean_model import get_inverted_index_posting_list, get_query_bool_vector
from sources.models.vector_space_model import get_term_document_weight_matrix, get_vector_space_model_result

# models generation

MAX_FILE_NBR = 1000

if not os.path.isdir("books"):
    get_work_data("books")

books_data, words = get_clean_books_data("books", stopwords, MAX_FILE_NBR)
posting_list = get_inverted_index_posting_list(books_data)
documents = get_term_document_weight_matrix(books_data, words)

# Flask

app = Flask(__name__)

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