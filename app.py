from flask import Flask, render_template,request
import json
app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def hello_world():
    start = 1801
    end = 1803
    countries_data=open('countries.json').read()
    years_data=open('years.json').read()

    countrySel = ""
    countries = json.loads(countries_data)
    years = json.loads(years_data)

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
      "start-year": int(start)
    }
    # print(data['taiwan'])
    return render_template("index.html", data=data)

# @app.route('/search/<input>')

if __name__ == "__main__":
    app.debug = True
    app.run(port=8000)

