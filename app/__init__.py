from flask import Flask, render_template, request, send_from_directory
import requests
import json

app = Flask(__name__)

app.config.from_pyfile('../config/config.cfg')

ELASTIC_URL = app.config["ES_BASE_URL"]

DEFAULT_START = 1805
DEFAULT_END = 1864

with open('data/doc_filters/countries.json') as countries_file, \
        open('data/doc_filters/years.json') as years_file, \
        open('data/doc_filters/redactionToSource.json') as red_file, \
        open('data/doc_filters/sourceToRedaction.json') as src_file:

    countries_data = json.loads(countries_file.read())
    years_data = json.loads(years_file.read())
    red_src_data = json.loads(red_file.read())
    src_red_data = json.loads(src_file.read())

    country_list = sorted([x[0].upper() + x[1:]
                           for x in countries_data.keys()])
    country_docs = set([doc for sl in countries_data.values() for doc in sl])

    years_list = sorted([int(x) for x in years_data.keys()])
    years_count = {year: len(docs) for year, docs in years_data.iteritems()}


def search_doc_by_id(doc_id):
	print doc_id

	resp = requests.get(ELASTIC_URL + "/_search?q=id:{0}".format(doc_id)).json()

	return resp["hits"]["hits"][0]["_source"]


@app.route('/files/<path:path>', methods=["GET"])
def send_files(path):
    # files/documents/{{doc_id}}.nofoot.txt
    return send_from_directory('data', path)


@app.route('/', methods=["GET", "POST"])
def hello_world():
    def format_data(c_sl="", start=DEFAULT_START, end=DEFAULT_END, result=[]):
        return {
            "country_list": country_list,
            "years_list": years_list,
            "years_count": years_count,
            "countrySelected": c_sl,
            "result": result,
            "start-year": start,
            "end-year": end
        }

    def post(form):
        start = int(form['start-year'])
        end = int(form['end-year'])
        c_sl = form['countrySelect'].lower()

        year_range = [str(year) for year in range(start, end + 1)]

        year_doc_list = [years_data.get(year, []) for year in year_range]
        y_docs = set([doc for sl in year_doc_list for doc in sl])
        c_docs = country_docs if c_sl == 'all' else set(
            countries_data.get(c_sl, []))

        final = c_docs.intersection(y_docs)

        result = list(sorted(list(final)))

        return format_data(c_sl, start, end, result)

    data = post(request.form) if request.method == 'POST' else format_data()

    return render_template("index.html", data=data)


@app.route('/view/<int:doc_id>', methods=["GET", "POST"])
def view(doc_id):
    doc_id = str(doc_id)

    is_redact = doc_id in red_src_data.keys()

    results = red_src_data[doc_id] if is_redact else src_red_data[doc_id]
    result_text = [search_doc_by_id(res) for res in results]

    original = search_doc_by_id(doc_id)

    return render_template("docviewer.html", doc_id=doc_id,
                           is_redact=is_redact,
                           original=original,
                           result_text=result_text)