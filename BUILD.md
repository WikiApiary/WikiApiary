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

TODO: provide overview of what a bot task is.

### Extension

TODO: provide overview of what an extension task is.

### Farmer

TODO: provide overview of what a farm task is.

### Website

TODO: provide overview of what a website task is.

## Adding a new task

Great, so now you have an overview of the code structure, how celery works, what the ApiaryAPI is. What if you want to add a new dataset to WikiApiary? That's awesome, here is how you would do that.

### Slowly changing data

If the data you want to look at is slowly changing you should store it as Semantic MediaWiki data in WikiApiary itself. To do this, you will create a new subpage for the website. WikiApiary has page in the Website category for each website it monitors. The website page itself is only ever modified by human editors or Audit Bee. Edit frequency on the main wiki page should be relatively low to make watchlists more useful. Each data set is then stored on a subpage that is edited only by the bots. Current examples of subpages include:

* `WikiApiary/General` stores all values produced by siteinfo/general API call.
* `WikiApiary/Extensions` stores the list of all extensions used.
* `WikiApiary/Interwikimap` stores the interwikimap.

Each of these pages is created and maintained by a task. For the ones above they are `apiary/tasks/general.py`, `apiary/tasks/extensions.py` and `apiary/tasks/interwikimap.py`. The tasks themselves should by design do very little. They simply get the data, do any cleanup required of the data and then store it in the wiki. As much as possible keep the names of the data unmodified so it is easier to track data from the bot task into the wiki.

The data once stored in a wiki page is parsed using a template, and the template actually creates the Semantic MediaWiki data. None of that is done by the tasks. This keeps as much of the logic and capability directly in Semantic MediaWiki and limits the need for people to have to edit Python code to do new things.

#### Recipe

First, determine a proper name for your task and create a new file in one of the directories in `apiary/tasks` for your code. Use the right directory for the type of task you are writing. If it is new or unknown email the WikiApiary developer mailing list and ask for a recommendation. A blank task would look like this:

    """
    My great task worker to get amazing data!
    """

    from apiary.tasks import BaseApiaryTask
    import logging


    LOGGER = logging.getLogger()

    class GetAmazingDataTask(BaseApiaryTask):
        """Get amazing data"""

        def run(self):
            """Run my task"""
            pass

Now add a proper test for your task in the right directory of  `apiary/tests`. A blank test would look like:

    """
    Tests for the amazing data task!
    """

    import unittest
    if __name__ == "__main__" and __package__ is None:
        __package__ = "apiary.tests"
    from apiary.tasks.bot.amazing import DeleteBotLogsTask


    class Test GetAmazingDataTask(unittest.TestCase):
        """Run GetAmazingDataTask and make sure it worked"""

        def test_amazing_data(self):
            """One of the amazing test cases"""
            task = GetAmazingDataTask()
            assert task.run() >= 0

    if __name__ == '__main__':
        unittest.main()

Code your task up and make sure to run `nosetests` to make sure everything works. Once you are done, issue a pull request.

### Time-series data

Data that is quickly changing is a little more complicated. This data is stored outside of the WikiApiary wiki and managed directly in ApiaryDB, a MySQL database that holds millions of rows of data.

The process for adding this type of data set is similar to the one above, but you'll need a new database table to put that data in, or possibly modify an existing one.

The ApiaryDB is managed using database migrations using yoyo-migrations. You can see the migrations in the `migrations` directory. The filenames are important as they are executed in order. To add a new table, you would create a new file in the `migrations` directory and then describe both the apply and rollback methods for the table.

You then apply the migration using the same step you did above to initially setup the database. The database connection is established in the `connect_mysql.py` and is stored in a `apiary_db` in the BaseApiaryTask class. In your code you can access it directly as `self.apiary_db`.

You will need to add the proper SQL calls to your task worker to write the data. You can see `tasks/website/statistics.py` for an example of how to do this.

Data stored in MySQL is then exposed by the ApiaryAPI. After adding your data to the database via your tasks, you will then want to extend ApiaryAPI by adding additional routes and handlers in `apiary/ApiaryAPI/api.py`. This API is then used by templates in WikiApiary to draw graphs and expose other elements.

If you need a static Javascript library to display the data add that to the `www` directory. That is where the core dygraph.js library is stored.