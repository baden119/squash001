<h1>SQuASH</h1>
<h2>Simple Quantative Analyzer of Submission History</h2>
<h2>https://squash001.herokuapp.com/</h2>
<h3>What is SQuASH:</h3>
<p>
SQuASH is a simple tool for counting and graphing reddit submissions.<br>
Enter a search term, a date range, and one or more subreddits to create a graph.<br>
SQuASH was made as a final project for <a href="https://www.edx.org/course/cs50s-introduction-to-computer-science">cs50</a>, an introductory course to computer programming.<br>
<br>
<h3>Problems:</h3>
<p>
SQuASH has a huge flaw! It turns out that querying the pushshift API can be a slow buisness.<br>
Each query can takes around 5 seconds to complete, and each period of time (day, week or month) needs its own query.<br>
I didn't think this was so big of a deal at first, but <a href="https://devcenter.heroku.com/articles/request-timeout">Heroku terminates any requests that take longer than 30 seconds to complete.</a><br>
This severly limits the usefulness of the app at this stage, in effect limiting any query to 6 or 7 individual time periods.<br>
Query times do often fluctuate, however, so if your request times out, maybe try your luck a second or third time!

</p>
<h3>History:</h3>
<p>
The intention behind this project was to create a tool to understand what the users of a particular subreddit thought about
a subject and how this thinking changed over time.<br>
<a href="static/Original Squash Home.png">The original design of SQuASH</a> was therefore based around searching a single subreddit
for one or more terms. So for instance you could graph a count of submissions to <a href="static/Original Squash NFL.png">/r/nfl that mention certain teams</a>, or submissions
to <a href="static/Original Squash cs50.png">/r/cs50 that mention certain problem sets</a>.
</p>
<p>
Unfortunatly, while this earlier version of SQuASH worked well enough running locally, once deployed to Heorku it became unstable. Identical
queries to the pushshift API would sometimes fail and sometimes not, without any aparent rhyme or reason.
</p>
<p>
Changing the way SQuASH queries the API, searching multiple subreddits for a single term rather than a single subreddit for multiple
terms, fixes this problem. In making these changes, however, SQuASH deviates somewhat from it's indended purpose and becomes less useful
than it might otherwise have been.
</p>
<h3>Looking Forward:</h3>
<p>
Despite it's considerable faults, I'm pretty happy with how SQuASH turned out. I feel it's a good
reflection of where i'm at in terms of programming ability after taking cs50.<br>
All going well I hope to take the follow-up CS50 web development course soon, and hopefully as I continue
to learn I will be able to improve SQuASH as well!
</p>
<h3>Support:</h3>
<p>
This project relies on the generous work of the folks over at <a href="https://pushshift.io/">pushshift.io</a>. It could not function without their publicly available
data.<br> <a href="https://pushshift.io/donations/">If you're feeling generous please support them.</a>
</p>
