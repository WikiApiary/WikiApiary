# WikiApiary

[WikiApiary](http://wikiapiary.com/) is a wiki that tracks the performance and activity on hundreds of other MediaWiki websites. WikiApiary is largely powered by MediaWiki itself along with Semantic MediaWiki and dozens of related extensions. Additionally, there are bots that work in conjunction with the wiki to provide all of the additional services.

[![Build Status](https://travis-ci.org/thingles/WikiApiary.png)](https://travis-ci.org/thingles/WikiApiary) [![Coverage Status](https://coveralls.io/repos/thingles/WikiApiary/badge.png?branch=refactor-class)](https://coveralls.io/r/thingles/WikiApiary?branch=refactor-class) [![Code Quality](https://landscape.io/github/thingles/WikiApiary/refactor-class/landscape.png)](https://landscape.io/github/thingles/WikiApiary/refactor-class)

## Bots

There are multiple bots powering WikiApiary.

### Bumble Bee

[Bumble Bee](http://wikiapiary.com/wiki/User:Bumble_Bee) is the bot that collects statistics and general configuration information from the wikis in WikiApiary. Bumble Bee selects the wikis it will collect information from WikiApiary and stores the metrics in a separate MySQL database. This database is then pulled directly for charting metrics.

General information on versions and extensions being used are pulled and recorded directly into wiki pages in WikiApiary.

### Audit Bee

### Notify Bee

Bot that handles email notifications.

Jamie Thingelstad <jamie@thingelstad.com>
http://wikiapiary.com/wiki/User:Thingles
http://thingelstad.com/
