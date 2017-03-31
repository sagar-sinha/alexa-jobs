from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
from lib.github import Github
from datetime import datetime
import requests
import urllib
import json
import re

app = Flask(__name__)
ask = Ask(app, "/alexa")


def _get_job_object(job):
    return {
        'company': job['company'],
        'title': job['title'],
        'how_to_apply': job['how_to_apply'],
        'url': job['url']
    }


@ask.launch
def new_ask():
    welcome = render_template('welcome')
    reprompt = render_template('reprompt_welcome')
    return question(welcome) \
        .reprompt(reprompt)

@ask.intent('SearchJobsIntent')
def search_jobs(role, city):
    jobs = Github.get_jobs(query=role, location=city)

    if len(jobs) == 0:
        if city:
            response = render_template(
                'no_jobs_found_city',
                role=role,
                city=city
            )
            return statement(response)
        else:
            response = render_template(
                'no_jobs_found',
                role=role
            )
            return response
    response = render_template('search_job_response', number=len(jobs))

    job_objects = map(_get_job_object, jobs)

    session.attributes['jobs'] = job_objects
    session.attributes['index'] = 0
    return question(response)


@ask.intent('AMAZON.YesIntent')
def next_job():
    # assuming we have saved jobs
    # TODO: handle case where we do not have jobs
    current_job = session.attributes['jobs'][session.attributes['index']]
    # increment job index
    session.attributes['index'] += 1

    role = current_job['title']
    company = current_job['company']

    return question(
        render_template(
            'job_listing',
            role=role,
            company=company
        )
    )


if __name__ == '__main__':
    app.run(debug=True)
