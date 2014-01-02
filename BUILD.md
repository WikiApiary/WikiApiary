# Building WikiApiary

Thank you for your interest in contributing to the WikiApiary codebase. This document is intended to provide an overview of the project structure to make it easier for others to contibute.

## Running Locally

You must have `mysqld` and `redis-server` running to work on the bots.

## Data collection bots

### Classes

#### bot.py

The Bot class holds utility functions that all bots need to talk to the WikiApiary website and to the Apiary MySQL database.

#### farm.py

The Farm class mirrors the Farm category in WikiApiary. Farming bots that automatically add new wikis from various farms should inherit from this class. The Farm class provides base functionality to make farmer bots easier to write and maintain.

#### website.py

The Website class mirrors the Website category in the wiki. This class is the primary class that interfaces with the websites being monitored by WikiApiary.

## Web tools

The `www` directory contains a collection of PHP scripts to accessing the MySQL database that stores the data collected by the bots.