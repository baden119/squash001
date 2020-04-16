import datetime as dt; from dateutil.relativedelta import *
from flask import Flask, jsonify, render_template, request
import json
import matplotlib.pyplot as plt, mpld3
from matplotlib.ticker import MaxNLocator
import numpy as np
import requests
# For testing only
import time

app = Flask(__name__)

def term_counter(subs_string, before, after, search_term, sub_count):
    # Accepts datetime before and after, list of subs and a search term. Passes this info to pushshift API and
    # returns a list of the number of occurances of the search term in each sub over that time period.
    t0 = time.time()
    term_count = []
    url = 'https://api.pushshift.io/reddit/submission/search/?subreddit='+subs_string+'&aggs=subreddit&q='+ search_term +'&size=0&after='+str(after)+'&before='+str(before)
    r = requests.get(url)
    if not r:
        print ("Termchecker error.")
        return False
    data = json.loads(r.text)
    t1 = time.time()
    data = data['aggs']['subreddit']

    # Creating a list of 0 values if API returns no data.
    if (len(data)) == 0:
        for i in range(sub_count):
            term_count.append(0)

    # Adding 0 values to list if API only returns partial data.
    elif ((len(data) > 0) and (len(data) != sub_count)):
        subs_list = subs_string.split(",")
        for i in range(len(subs_list)):
            matched = False
            for j in range(len(data)):
                if ((subs_list[i]).lower() == (data[j]['key']).lower()):
                    term_count.append(data[j]['doc_count'])
                    matched = True
                    break
            if matched == False:
                term_count.append(0)

    # Adding data to a list if API retuens all data.
    else:
        for i in range(len(data)):
            term_count.append(data[i]['doc_count'])

    print ("{0:.2f}".format(t1 - t0))
    return(term_count)

@app.route('/', methods = ["GET", "POST"])

def index():

    if request.method == "POST":

        # Get inputs from HTML and declare some lists
        term_period = request.form.get("term_period")
        start_date = dt.datetime.strptime(request.form.get("start_date"), '%Y-%m-%d')
        end_date = dt.datetime.strptime(request.form.get("end_date"), '%Y-%m-%d')
        search_term = request.form.get("searchTerm")
        period_data = []
        period_lables = []
        subs = []
        sub_count = 0
        sub_data = []

        # Creating a list of Subreddits from HTML form, number of subs requested by user.``
        sub = request.form.get('subreddit'+str(sub_count))
        while sub:
            subs.append(sub)
            sub_count += 1
            sub = request.form.get('subreddit'+str(sub_count))
        subs_string  = ','.join(map(str, subs))

        # Error checking HTML Inputs. Most should be caught by JavaScript.
        if not subs_string or not search_term or not start_date or not end_date or (end_date < start_date):
            return render_template("error.html", error="Invalid inputs detected.")

        # Gathering data for graphing. Some vairables dependant on day/week/month periods requested by user.
        if term_period == ('day'):
            xlabel = "Date."
            end_date = end_date + relativedelta(days=+1)
            current_start = start_date
            current_end = current_start + relativedelta(days=+1)
            while (current_end <= end_date):
                period_lables.append(str(current_start.day) + '/' + str(current_start.month))
                push_data = (term_counter(subs_string = subs_string, before = current_end, after = current_start, search_term = search_term, sub_count = sub_count))
                if not push_data:
                    return render_template("error.html", error="Invalid Subreddit.")
                else: sub_data.append(push_data)
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
                push_data = (term_counter(subs_string = subs_string, before = current_end, after = current_start, search_term = search_term, sub_count = sub_count))
                if not push_data:
                    return render_template("error.html", error="Invalid Subreddit.")
                else: sub_data.append(push_data)
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
                push_data = (term_counter(subs_string = subs_string, before = current_end, after = current_start, search_term = search_term, sub_count = sub_count))
                if not push_data:
                    return render_template("error.html", error="Invalid Subreddit.")
                else: sub_data.append(push_data)
                current_start += relativedelta(months=+1)
                current_end += relativedelta(months=+1)
                current_end += relativedelta(day=31)

        # Rearranging data for graphing
        for i in range(len(subs)):
            period_data.append([])

        for i in range(len(sub_data)):
            for j in range(len(period_data)):
                period_data[j].append(sub_data[i][j])


        ### Graphing Data ###

        xpos = np.arange(len(period_lables))

        # Setting graph size and background colour
        fig = plt.figure(figsize=(10,6))
        ax = plt.axes()
        ax.set_facecolor("#fff44f")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Dynamically set width of bars depending on number of subs
        number_of_bars = len(subs)
        bar_width = round(0.9 / number_of_bars, 3)
        xpos_current = (round(- 0.4 + (bar_width / 2), 3))
        width_values = []
        width_values.append(xpos_current)

        for bar in range(number_of_bars - 1):
            xpos_current = round((xpos_current + bar_width), 3)
            width_values.append(xpos_current)

        # Plot data from Pushshift API
        for i in range(number_of_bars):
            plt.bar(xpos+ width_values[i], period_data[i], width = bar_width, label = subs[i])

        # Labelling axis
        plt.xticks(xpos, period_lables)
        plt.xlabel(xlabel)
        plt.ylabel("Post Submissions")
        plt.title('Search Term:\n' + search_term)
        plt.legend()

        html_graph = mpld3.fig_to_html(fig, template_type='simple')

        return render_template('squash.html', html_graph = html_graph)
    else:
        return render_template("index.html")

@app.route("/check", methods=["GET"])
# Route for AJAX check to warn if process time will result in a timeout error.
def check():

    start_date = dt.datetime.strptime(request.args.get("start_date"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("end_date"), '%Y-%m-%d')
    term_period = request.args.get("term_period")
    period_count = 0

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

    if (period_count <= 7):
        return jsonify(False)

    else:
        return ("Unfortunatly, SQuASH processing time for this\nrequest is such that timeout failure very likley.\n      Continue?")


@app.route('/documentation', methods = ["GET"])
# Route for Documentation page.
def docs():
    return render_template("documentation.html")

if __name__ == '__main__':
    app.run()
