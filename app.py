from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
from lib.github import Github
from settings import TECHNOLOGIES
from datetime import datetime
import requests
import urllib
import json
import re

app = Flask(__name__)
ask = Ask(app, "/")


def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)


def _get_job_object(job):
    description = job['description'].lower()
    technologies = _get_technologies(description)
    experience = _get_experience(description)
    return {
        'company': job['company'],
        'title': job['title'],
        # 'how_to_apply': job['how_to_apply'],
        # 'url': job['url'],
        'experience': strip_non_ascii(experience),
        'technologies': technologies,
    }


def _get_technologies(description):
    technologies = []
    for technology in TECHNOLOGIES:
        if description.find(technology) != -1:
            technologies.append(technology)
    return ', '.join(technologies)

def _get_experience(description):
    matches = re.findall(
        r'([0-9]\+? years [a-zA-Z0-9\ -]{,})',
        strip_non_ascii(description)
    )
    if matches:
        return ', '.join(matches)
    else:
        return 'No experience information is listed for this job'

def _parse_description(description):
    technologies = _get_technologies(description)
    if technologies:
        experience = _get_experience(description)
        return (experience, technologies)
    else:
        return 'I Could not find any list of technologies for this job'

@ask.launch
def new_ask():
    welcome = render_template('welcome')
    reprompt = render_template('reprompt_welcome')
    return question(welcome) \
        .reprompt(reprompt)

@ask.intent('SearchJobsIntent')
def search_jobs(role, city):
    print city
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
def first_job():
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


@ask.intent('NextJobIntent')
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



@ask.intent('ExperienceIntent')
def show_experience():
    current_job = session.attributes['jobs'][session.attributes['index']]
    response = render_template(
        'show_experience',
        experience=current_job['experience']
    )
    return question(response)


@ask.intent('TechnologiesIntent')
def show_technologies():
    current_job = session.attributes['jobs'][session.attributes['index']]
    print current_job
    response = render_template(
        'show_technologies',
        technologies=current_job['technologies']
    )
    return question(response)


@ask.intent('AMAZON.StopIntent')
def stop():
    response = render_template('bye')
    return statement(response)


@ask.intent('AMAZON.HelpIntent')
def help():
    response = render_template('help')
    return question(response)

if __name__ == '__main__':
    app.run(debug=True)
