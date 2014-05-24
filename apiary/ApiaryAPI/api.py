"""
Data API for WikiApiary
"""
# pylint: disable=C0301,C0103,W1201,W0622


from flask import Flask
from flask import request
from apiary.connect_mysql import apiary_db

app = Flask(__name__)

@app.route("/data/<int:site_id>", methods=['GET'])
def data(site_id):
    """Return data for a given site."""

    duration = request.args.get('duration')

    cur = apiary_db.cursor()
    # SELECT capture_date, articles, pages FROM statistics WHERE website_id = :id AND capture_date > :date_filter
    temp_sql = "SELECT capture_date, articles, pages FROM statistics WHERE website_id = %d" % site_id
    cur.execute(temp_sql)

    return_data = ""
    for row in cur:
        return_data += "%s,%d,%d\n" % row

    return return_data


if __name__ == "__main__":
    app.run()
