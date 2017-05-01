# Redactions Archive Frontend Version 2
New version of the old Redactions frontend

# Setup
Run [Spark-Redaction](https://github.com/declassengine/redactions/tree/spark-analysis) to get all the data. Then do the following


```bash
sh tif-to-jpeg.sh # converts all `TIFF` files into `jpeg`
pip install -r requirements.txt
python2 app.py
```
