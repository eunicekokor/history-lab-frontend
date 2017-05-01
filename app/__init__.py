import requests
import json

from os import listdir
from os.path import dirname, realpath, join
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)

app.config.from_pyfile("../config/config.cfg")

ELASTIC_URL = app.config["ES_BASE_URL"]

DEFAULT_START = 1805
DEFAULT_END = 1864

MONTHS = set(["january", "february", "march", "april", "may", "june",
              "july", "august", "september", "october", "november", "december"])

with open("data/countries.json") as countries_file, \
        open("data/years.json") as years_file, \
        open("data/writtenYears.json") as wyears_file, \
        open("data/publicationYears.json") as pyears_file, \
        open("data/redactionToSource.json") as red_file, \
        open("data/sourceToRedaction.json") as src_file, \
        open("data/location.json") as loc_file, \
        open("data/organization.json") as org_file, \
        open("data/person.json") as people_file, \
        open("data/date.json") as date_file:

    countries_data = json.loads(countries_file.read())

    years_data = json.loads(years_file.read())
    wyears_data = json.loads(wyears_file.read())
    pyears_data = json.loads(pyears_file.read())

    red_src_data = json.loads(red_file.read())
    src_red_data = json.loads(src_file.read())

    loc_data = json.loads(loc_file.read())
    org_data = json.loads(org_file.read())
    people_data = json.loads(people_file.read())
    date_data = json.loads(date_file.read())

    country_list = sorted(countries_data.keys())
    country_docs = set([doc for sl in countries_data.values() for doc in sl])

    years_list = sorted([int(x) for x in years_data.keys()])
    years_count = {year: len(docs) for year, docs in years_data.iteritems()}


def get_year_by_id(doc_id):
    return load_match(doc_id, years_data.iteritems())


def get_country_by_id(doc_id):
    return load_match(doc_id, countries_data.iteritems())


def get_loc_by_id(doc_id):
    return load_match(doc_id, loc_data.iteritems())


def load_match(doc_id, data):
    results = [k for k, vals in data if doc_id in vals]

    return results


def htmlify(a):
    return str(a).replace("\n", "<br>")


def firstLetterUpper(x):
	return x[0].upper() + x[1:]


def firstLetterLower(x):
	return x[0].lower() + x[1:]



def search_doc_by_id(doc_id):
    resp = requests.get(ELASTIC_URL + "/{0}".format(doc_id)).json()

    return resp["_source"] if "_source" in resp else ""


def get_images(doc_id):
    curr_dir = dirname(realpath(__file__))

    images_pre = listdir(join(curr_dir, "static/images/{0}".format(doc_id)))

    images = [i for i in images_pre if i.endswith("jpeg")]

    return ["images/{0}/{1}".format(doc_id, i) for i in images]


def format_date(dates):
    results = [date for date in dates if len(
        set(date.split(" ")).intersection(MONTHS)) > 0]


def format_res_data(result, c_sl="", start=DEFAULT_START, end=DEFAULT_END):
    return {
        "country_list": country_list,
        "years_list": years_list,
        "years_count": years_count,
        "country_selected": c_sl,
        "result": [str(r) for r in result],
        "start_year": start,
        "end_year": end
    }

@app.route("/", methods=["GET", "POST"])
def index(default_result=[]):
    def post(form):
        start = int(form["start-year"])
        end = int(form["end-year"])
        c_sl = form["country-select"].lower()

        year_range = [str(year) for year in range(start, end + 1)]

        year_doc_list = [years_data.get(year, []) for year in year_range]
        y_docs = set([doc for sl in year_doc_list for doc in sl])
        c_docs = country_docs if c_sl == "all" else set(
            countries_data.get(c_sl, []))

        final = c_docs.intersection(y_docs)

        result = sorted(list(final))

        return format_res_data(result, c_sl, start, end)

    if request.method == "POST":
    	return render_template("index.html", data=post(request.form))
    else:
    	data = format_res_data(result=default_result)

    	return render_template("index.html", data=data)


@app.route("/location/<string:loc>")
def get_loc(loc):
    c_docs = set(countries_data.get(loc, []) + loc_data.get(loc, []))
    data = format_res_data(result=c_docs, c_sl=loc)
    print data

    return render_template("index.html", data=data)


@app.route("/year/<int:year>")
def get_years(year):
	data = format_res_data(result=years_data.get(str(year), []))

	return render_template("index.html", data=data)


@app.route("/w_year/<int:year>")
def get_wyears(year):
	data = format_res_data(result=wyears_data.get(str(year), []))

	return render_template("index.html", data=data)


@app.route("/p_year/<int:year>")
def get_pyears(year):
	data = format_res_data(result=pyears_data.get(str(year), []))

	return render_template("index.html", data=data)


@app.route("/org/<string:org>")
def get_orgs(org):
	data = format_res_data(result=org_data.get(org, []))

	return render_template("index.html", data=data)


@app.route("/person/<string:name>")
def get_people(name):
	data = format_res_data(result=people_data.get(name, []))

	return render_template("index.html", data=data)


@app.route("/date/<string:date>")
def get_dates(date):
	data = format_res_data(result=date_data.get(date, []))

	return render_template("index.html", data=data)



@app.route("/view/<int:doc_id>", methods=["GET", "POST"])
def view(doc_id):
    def html_arr(arr):
        return [htmlify(a) for a in arr]

    doc_id = str(doc_id)

    is_redact = doc_id in red_src_data.keys()
    res_ids = red_src_data[doc_id] if is_redact else src_red_data[doc_id]

    try:
	    original = search_doc_by_id(doc_id)

	    entities = original["entityMap"]

	    locations = set(entities.get("LOCATION", []) + get_country_by_id(doc_id))

	    dates = format_date(entities.get("DATE", []) + get_year_by_id(doc_id))

	    result = [(rid, search_doc_by_id(rid)["pages"]) for rid in res_ids]

	    f_res = [r for r in result if r[1] != ""]

	    return render_template("docviewer.html", doc_id=doc_id,
	                           is_redact=is_redact,
	                           title=str(original["title"]),
	                           original_pages=html_arr(original["pages"]),
	                           result_pages={str(i): html_arr(p)
	                                         for i, p in f_res},
	                           year_written=original["yearWritten"],
	                           year_published=original["yearPublished"],
	                           locations=locations,
	                           orgs=entities.get("ORGANIZATION", []),
	                           people=entities.get("PERSON", []),
	                           dates=dates
	                           )
    except:
        return abort(404)

@app.route("/raw/<int:doc_id>")
def view_rat(doc_id):
    try:
	    images = get_images(doc_id)

	    return render_template("rawView.html", doc_id=doc_id,
	                           images=images)
    except:
    	return abort(404)
