import datetime as dt; from dateutil.relativedelta import *
from flask import Flask, jsonify, render_template, request
import json
import matplotlib.pyplot as plt, mpld3
from matplotlib.ticker import MaxNLocator
import numpy as np
import requests

app = Flask(__name__)

def term_counter(current_query, before, after, sub):
    # Accepts datetime before and after, and string query and sub. converts datetime to timestamp, feeds all info to pushshift and
    # returns a count of occurances of the query in the sub over that time.
    before = int(before.timestamp())
    after = int(after.timestamp())
    url = 'https://api.pushshift.io/reddit/search/submission/?title='+str(current_query)+'&after='+str(after)+'&before='+str(before)+'&subreddit='+str(sub)+'&fields=title'+'&size=1000'
    r = requests.get(url)
    if not r:
        print ("Termchecker error.")
        return render_template("error.html")
    data = json.loads(r.text)
    return len(data['data'])

@app.route('/', methods = ["GET", "POST"])

def index():

    if request.method == "POST":

        # Get inputs from HTML and declare some lists
        term_period = request.form.get("term_period")
        start_date = dt.datetime.strptime(request.form.get("start_date"), '%Y-%m-%d')
        end_date = dt.datetime.strptime(request.form.get("end_date"), '%Y-%m-%d')
        sub = request.form.get("subreddit")
        period_data = []
        period_lables = []
        queries = []
        query_count = 0

        # For testing
        print ('XxX Heroku Log Test XxX')

        # Create queries list from HTML
        query = request.form.get('searchTerm'+str(query_count))

        # Error checking
        if not query or not sub or not start_date or not end_date or (end_date < start_date):
            return render_template("error.html")


        while query:
            queries.append(query)
            period_data.append([])
            query_count += 1
            query = request.form.get('searchTerm'+str(query_count))

        # Gathering data for graphing. Some vairables dependant on day/week/month periods requested by user.
        if term_period == ('day'):
            xlabel = "Date."
            end_date = end_date + relativedelta(days=+1)
            current_start = start_date
            current_end = current_start + relativedelta(days=+1)
            while (current_end <= end_date):
                period_lables.append(str(current_start.day) + '/' + str(current_start.month))
                for i in range(len(queries)):
                    period_data[i].append(term_counter(current_query = queries[i], before = current_end, after = current_start, sub = sub))
                current_start = current_end
                current_end = current_start + relativedelta(days=+1)

        if term_period == ('week'):
            xlabel = "Week Beginning:"
            #Adjusting start and end dates to beginning and ending of selected weeks.
            while (start_date.weekday() != 0):
                start_date -= relativedelta(days=1)
            while (end_date.weekday() != 6):
                end_date += relativedelta(days=1)
            current_start = start_date
            current_end = current_start + relativedelta(days=+7)
            while (current_end <= end_date):
                period_lables.append(str(current_start.day) + '/' + str(current_start.month))
                for i in range(len(queries)):
                    period_data[i].append(term_counter(current_query = queries[i], before = current_end, after = current_start, sub = sub))
                current_start = current_end
                current_end = current_start + relativedelta(days=+7)

        if term_period ==('month'):
            xlabel = "Month / Year."
            #Adjusting start and end dates to beginning and ending of selected months.
            start_date -= relativedelta(day=1)
            end_date += relativedelta(day=31)
            current_start = start_date
            current_end = current_start + relativedelta(day=31)
            while (current_end <= end_date):
                period_lables.append(str(current_start.month) + '/' + str(current_start.year))
                for i in range(len(queries)):
                    period_data[i].append(term_counter(current_query = queries[i], before = current_end, after = current_start, sub = sub))
                current_start += relativedelta(months=+1)
                current_end += relativedelta(months=+1)
                current_end += relativedelta(day=31)

        # Graphing Data
        xpos = np.arange(len(period_lables))

        # Setting graph size and background colour
        fig = plt.figure(figsize=(10,6))
        ax = plt.axes()
        ax.set_facecolor("#fff44f")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Dynamically set width of bars depending on number of queries
        number_of_bars = len(queries)
        bar_width = round(0.9 / number_of_bars, 3)
        xpos_current = (round(- 0.4 + (bar_width / 2), 3))
        width_values = []
        width_values.append(xpos_current)

        for bar in range(number_of_bars - 1):
            xpos_current = round((xpos_current + bar_width), 3)
            width_values.append(xpos_current)

        # Plot data from Pushshift API
        for i in range(number_of_bars):
            plt.bar(xpos+ width_values[i], period_data[i], width = bar_width, label = queries[i])

        # Labelling axis
        plt.xticks(xpos, period_lables)
        plt.xlabel(xlabel)
        plt.ylabel("Post Submissions")
        plt.title('Subreddit:\n/r/' + sub)
        plt.legend()


        html_graph = mpld3.fig_to_html(fig, template_type='simple')

        return render_template('squash.html', html_graph = html_graph)

    else:
        return render_template("index.html")

@app.route("/check", methods=["GET"])
def check():

    start_date = dt.datetime.strptime(request.args.get("start_date"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("end_date"), '%Y-%m-%d')
    field_count = request.args.get("field_count")
    term_period = request.args.get("term_period")
    period_count = 0
    #Pushift query process time (in seconds) determined after rigerous testing.
    query_process = 1.3

    if term_period == ('day'):
        end_date = end_date + relativedelta(days=+1)
        current_start = start_date
        current_end = current_start + relativedelta(days=+1)
        while (current_end <= end_date):
            period_count += 1
            current_start = current_end
            current_end = current_start + relativedelta(days=+1)

    if term_period == ('week'):
        #Adjusting start and end dates to beginning and ending of selected weeks.
        while (start_date.weekday() != 0):
            start_date -= relativedelta(days=1)
        while (end_date.weekday() != 6):
            end_date += relativedelta(days=1)
        current_start = start_date
        current_end = current_start + relativedelta(days=+7)
        while (current_end <= end_date):
            period_count += 1
            current_start = current_end
            current_end = current_start + relativedelta(days=+7)

    if term_period ==('month'):
        #Adjusting start and end dates to beginning and ending of selected months.
        start_date -= relativedelta(day=1)
        end_date += relativedelta(day=31)
        current_start = start_date
        current_end = current_start + relativedelta(day=31)
        while (current_end <= end_date):
            period_count += 1
            current_start += relativedelta(months=+1)
            current_end += relativedelta(months=+1)
            current_end += relativedelta(day=31)

    query_in_seconds = (period_count * query_process * int(field_count))

    query_in_datetime = dt.timedelta(seconds=query_in_seconds)

    if (query_in_datetime.seconds <= 10):
        return jsonify(False)

    elif ((query_in_datetime.seconds > 10) and (query_in_datetime.seconds <= 30)):
        return ("SQuASH process time estimated at under 30sec.")

    elif ((query_in_datetime.seconds > 30) and (query_in_datetime.seconds <= 60)):
        return ("SQuASH process time estimated at under 1min.")

    elif ((query_in_datetime.seconds > 60) and (query_in_datetime.seconds <= 180)):
        return ("SQuASH process time estimated at under 3min.")

    else:
        return ("Long wait time expected, consider re-evaluating request.    "  + (str(query_in_datetime)))


@app.route('/documentation', methods = ["GET"])

def docs():

    return render_template("documentation.html")


if __name__ == '__main__':
    app.run()
