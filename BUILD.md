Thank you for your interest in contributing to WikiApiary. This document is intended to help get you started off in the right direction and provide an overall understanding of the codebase.

Before diving in, you might want to also subscribe to the [WikiApiary development mailing list](http://lists.thingelstad.com/cgi-bin/mailman/listinfo/wikiapiary-dev) as well as the [general WikiApiary mailing list](http://lists.thingelstad.com/cgi-bin/mailman/listinfo/wikiapiary-l). These mailing lists are the right place to ask for various questions about how WikiApiary.

The WikiApiary repository contains:

* `apiary` is the location where the Python source is.
* `apiary/ApiaryAPI` is the Flask-based API for communicating directly with the ApiaryDB and bots.
* `apiary/tasks` contain the various tasks that are executed by Celery.
* `apiary/tests` contain the unit tests.
* `apiary/celery.py` defines the Celery application. This is also where the Celery scheduled tasks are defined.
* `apiary/connect_*.py` sets up connections to various services that the codebase needs.
* `config` holds the configuration file. **This file is not included in the repository. This is where passwords are stored.**
* `migrations` contains the database migrations to setup and modify the MySQL database structure.
* `www` contains static assets that should be served directly via a web server.

WikiApiary uses Travis-CI for building and running unit tests. Travis-CI will send build notification to the WikiApiary developer mailing list. Github also sends notifications to the developer mailing list. Code coverage is tracked on Coveralls. Code quality analysis is done by Landscape.io.

## Running Locally

For development purposes you will want to clone the repository locally. 

### Required Services

You must have `mysqld` and `redis-server` running to work on the bots. If you are using Ubuntu these are easily installed with your package manager. On a Mac it is easiest to use brew to get these setup. The code is setup to run without a configuration file for unittests.

#### Creating MySQL Database

You must have a local database named `apiary` in MySQL. Apply the database migrations from the `migrations` directory:

`yoyo-migrate apply ./migrations`.

### Celery

Start the worker locally by making sure you are in the `WikiApiary` directory and running:

`celery --beat --app=apiary worker -l info`.

## ApiaryAPI

The ApiaryAPI is a module and Python doesn't like to run modules directly. The easiest way around this is to go to the `WikiApiary` directory and run

`python -c "from apiary.ApiaryAPI.api import app; app.run()"`

This invokes Python, loads the ApiaryAPI as a module and runs the Flask application.

## Tasks

The heart of WikiApiary bots are the [Celery](http://www.celeryproject.org) tasks that do all the work. If you are unfamiliar with Celery you should definitely take a moment review before diving into creating new tasks. If you can’t be bothered, know that:

> Celery is an asynchronous task queue/job queue based on distributed message passing.  It is focused on real-time operation, but supports scheduling as well.

> The execution units, called tasks, are executed concurrently on a single or more worker servers using multiprocessing. Tasks can execute asynchronously (in the background) or synchronously (wait until ready).

By using Celery we don't have to worry about tasks blocking other tasks. Additionally, scaling out to collect more data from more wikis is straightforward by adding more celery worker processes.

All components of WikiApiary collectors are tasks, including the components that determine what to collect. The tasks are divided into four logical groupings, each in their own directory.

### Bot

### Extension

### Farmer

### Website

