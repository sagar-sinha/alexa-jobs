from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
from lib.github import Github
from datetime import datetime
import requests
import urllib
import re

app = Flask(__name__)
ask = Ask(app, "/alexa")

@ask.launch
def new_ask():
    welcome = render_template('welcome')
    reprompt = render_template('reprompt_welcome')
    return question(welcome) \
        .reprompt(reprompt)


@ask.intent('SearchJobsIntent')
def search_jobs(role):
    jobs = Github.get_jobs(query=role)
    response = render_template('search_job_response', number=len(jobs))
    return statement(response)

if __name__ == '__main__':
    app.run(debug=True)
