from flask import Flask, render_template,request,send_from_directory
import json
app = Flask(__name__)

@app.route('/files/<path:path>', methods=["GET"])
def send_files(path):
  # files/documents/{{doc_id}}.nofoot.txt
  return send_from_directory('data', path)

@app.route('/', methods=["GET", "POST"])
def hello_world():
    # default
    start = 1805
    end = 1864
    countries_data=open('data/doc_filters/countries.json').read()
    years_data=open('data/doc_filters/years.json').read()

    countrySel = ""
    countries = json.loads(countries_data)
    years = json.loads(years_data)

    years_count = {}

    for year,docs in years.iteritems():
        years_count[year] = len(docs)

    print years_count

    countryList = countries.keys()
    countryDocs = set([])
    for c in countryList:
      docsAssociated = countries[c]
      for doc in docsAssociated:
        countryDocs.add(doc)
    countryList = [x[0].upper() + x[1:] for x in countryList]
    countryList.sort()

    yearsList = years.keys()
    yearsList = [int(x) for x in yearsList]
    yearsList.sort()
    results = []

    if request.method == 'POST':
      end = request.form['end-year']
      start = request.form['start-year']
      countrySelected = request.form['countrySelect']
      year_range = range(int(start), int(end) + 1)
      print year_range
      years_needed = set([])
      for year in year_range:
        temp = years.get(str(year),None)
        if temp:
          for t in temp:
            years_needed.add(t)

      print "years so far {}".format(years_needed)

      if countrySelected == 'all':
        results = set(countries)
        # country_docs =
      else:
        countrySel = countrySelected
        countrySelected = countrySelected.lower()
        results = set(countries.get(countrySelected,None))
        countryDocs = set(countries.get(countrySelected,None))
      # print countryDocs
      if countrySelected =="all":
        final = years_needed
      else:
        final = countryDocs.intersection(years_needed)
      results = list(final)
      results.sort()

    data = {
      "countries":countries,
      "years": years,
      "countryList": countryList,
      "yearsList": yearsList,
      "countrySelected": countrySel,
      "results": list(results),
      "end-year": int(end),
      "start-year": int(start),
      "years_count": years_count
    }
    # print(data['taiwan'])
    return render_template("index.html", data=data)

@app.route('/view/<doc_id>', methods=["GET", "POST"])
def view(doc_id):
  doc_id = str(doc_id)
  redact=open('data/doc_filters/redactionToSource.json').read()
  source=open('data/doc_filters/sourceToRedaction.json').read()
  redactSource = json.loads(redact)
  sourceRedact = json.loads(redact)

  if doc_id in redactSource.keys():
    results = redactSource[doc_id]

  if doc_id in sourceRedact.keys():
    results = sourceRedact[doc_id]

  results = list(set(results))
  result_text  = []

  for d_id in results:
     result_text.append(getText(d_id))
  original_text = getText(doc_id)


  # # for each doc id, read the text file
  data = {
  "doc_id": str(doc_id),
  "result_text": result_text,
  "original_text": original_text
  }
  # print data['result_text']
  # data = "data"
  # print getText("205403")
  return render_template("docviewer.html", data=data)

def getText(doc_id):
  with open('data/documents/' + doc_id + '.nofoot.txt') as f:
    text = f.readlines()
  text_arr = text
  text_blob = " ".join(text)
  return {"arr": text_arr, "blob": text_blob}


if __name__ == "__main__":
    app.debug = True
    app.run(port=8000)

