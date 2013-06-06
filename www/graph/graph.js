window.Chart = function(targetDiv, id, defaultGraph) {
  var _id = id;
  var _defaultGraph = defaultGraph;
  var _parentDiv = $(targetDiv)[0],
    _targetDiv = $(targetDiv+" .graph")[0],
    _legendDiv = $(targetDiv+" .legend")[0],
    _navDiv = $(targetDiv+" .nav")[0],
    _selectedGraph;

  var _durations = [
      {
        name: "1 week",
        param: "1w"
      },
      {
        name: "1 month",
        param: "1m"
      },
      {
        name: "2 months",
        param: "2m"
      },
      {
        name: "3 months",
        param: "3m"
      },
      {
        name: "1 year",
        param: "1y"
      }
    ];

  var _graphs = [
    {
      id: "pages",
      name: "Pages",
      freq: ["raw", "weekly", "daily"],
      type: "basic",
      dygraphOpts: {
        labels: [ 'Date', 'Articles', 'Pages'],
        'Pages': {
          strokeWidth: 2
        },
        'Articles': {
          axis: {
          }
        },
        axes: {
          y: {
            labelsKMB: true
          },
          y2: {
            labelsKMB: true
          }
        },
        axisLabelFontSize: 10,
        maxNumberWidth: 12,
        title: 'Pages and Articles',
        labelsDiv: _legendDiv,
        ylabel: 'Pages',
        yLabelWidth: 12,
        y2label: 'Articles',
        rightGap: 10
      },
      path: "http://wikiapiary.com/apiary/data/articles.php?id=" + _id
    },
    {
      id: "edits",
      name: "Edits",
      freq: ["raw", "weekly", "daily"],
      type: "basic",
      dygraphOpts: {
        labels: [ 'Date', 'Edits'],
        axes: {
          y: {
            labelsKMB: true
          }
        },
        ylabel: 'Edits',
        axisLabelFontSize: 10,
        maxNumberWidth: 12,
        title: 'Edit Count',
        labelsDiv: _legendDiv,
        yLabelWidth: 12,
        fillGraph: true,
        rightGap: 10
      },
      path: "http://wikiapiary.com/apiary/data/edits.php?id=" + _id
    },
    {
      id: "users",
      name: "Users",
      freq: ["raw", "weekly", "daily"],
      type: "basic",
      dygraphOpts: {
        labels: [ 'Date', 'Users', 'Active Users'],
        'Users': {
          axis: {
          }
        },
        'Active Users': {
          fillGraph: true
        },
        axes: {
          y: {
            labelsKMB: true
          },
          y2: {
            labelsKMB: true
          }
        },
        ylabel: 'Active Users',
        y2label: 'Users',
        axisLabelFontSize: 10,
        maxNumberWidth: 12,
        title: 'Active Users and Users',
        labelsDiv: _legendDiv,
        yLabelWidth: 12,
        rightGap: 10
      },
      path: "http://wikiapiary.com/apiary/data/users.php?id=" + _id
    },
    {
      id: "jobs",
      name: "Jobs",
      freq: ["raw", "weekly", "daily"],
      type: "basic",
      dygraphOpts: {
        labels: [ 'Date', 'Jobs'],
        axes: {
          y: {
            labelsKMB: true
          }
        },
        ylabel: 'Jobs',
        axisLabelFontSize: 10,
        maxNumberWidth: 12,
        title: 'Job Queue',
        labelsDiv: _legendDiv,
        yLabelWidth: 12,
        fillGraph: true,
        includeZero: true,
        rightGap: 10
      },
      path: "http://wikiapiary.com/apiary/data/jobs.php?id=" + _id
    },
    {
      id: "response-time",
      name: "Response Time",
      freq: ["raw", "weekly", "daily"],
      type: "basic",
      dygraphOpts: {
        labels: [ 'Date', 'Response Time'],
        axes: {
          y: {
            labelsKMB: true
          }
        },
        ylabel: 'Response Time (sec)',
        axisLabelFontSize: 10,
        maxNumberWidth: 12,
        title: 'Response Time',
        labelsDiv: _legendDiv,
        yLabelWidth: 12,
        includeZero: true,
        rightGap: 10
      },
      path: "http://wikiapiary.com/apiary/data/response_timer.php?id=" + _id
    }

    ];

  var _my_graph;

  function _destroyOldGraph() {
    if (_my_graph !== undefined) {
      console.log("Destroying previous graph: " + _targetDiv);
      _my_graph.destroy();
    }
  }

  this.notImpl = function () {
    alert ("Not implemented yet.");
  };

  function _displayGraph(path, opts) {
    _destroyOldGraph();
    _my_graph = new Dygraph(_targetDiv, path, opts);
  }

  function _showSelected(event) {
        var opt = _dataChoiceNav[0].options[_dataChoiceNav[0].selectedIndex];
        _selectedGraph = opt.graph;
        var dur = _getSelectedDuration();
        _displayGraph(_selectedGraph.path + "&duration=" + dur.param, _selectedGraph.dygraphOpts);
        _updateFrequencyNav();
  }

  function _getSelectedDuration() {
    var opt = _durationChoiceNav[0].options[_durationChoiceNav[0].selectedIndex];
    return opt.duration;
  }

  function _showSelectedFrequency(event) {
    var frequency = _selectedGraph.freq[_frequencyChoiceNav[0].selectedIndex];
    var dur = _getSelectedDuration();
    _displayGraph(_selectedGraph.path + "&freq=" + frequency + "&duration=" + dur.param, _selectedGraph.dygraphOpts);
  }

  var _frequencyChoiceNav = $("<select id='freq_choice_" + id + "'></select>");
  var _durationChoiceNav = $("<select id='dur_choice_" + id + "'></select>");

  function _updateFrequencyNav() {
      _frequencyChoiceNav.empty();
      var i=0,
      glen = _selectedGraph.freq.length;
      for(i=0;i<glen;i++) {
        var opt = $("<option>" + _selectedGraph.freq[i] + "</option>");
        opt.appendTo(_frequencyChoiceNav);
      }
  }

  var i=0,
  glen = _durations.length;
  for(i=0;i<glen;i++) {
    var opt = $("<option>" + _durations[i].name + "</option>");
    opt[0].duration = _durations[i];
    opt.appendTo(_durationChoiceNav);
  }

  var _dataChoiceNav = $("<select id='data_choice_" + id + "'></select>");
  glen = _graphs.length;
  for(i=0;i<glen;i++) {
    var graph = _graphs[i];
    // TODO: check the type of the graph and see if it should be displayed for this website
    // if (graph.type == 'foo')
    var opt = $("<option>" + graph.name + "</option>");
    if(_defaultGraph==graph.id) {
      opt.attr("selected", "true");
    }
    opt[0].graph = graph;
    opt.appendTo(_dataChoiceNav);
  }

  $("<label>Data</label>").appendTo(_navDiv);
  _dataChoiceNav.appendTo(_navDiv);
  _dataChoiceNav.on("change", _showSelected);
  $("<label>Frequency</label>").appendTo(_navDiv);
  _frequencyChoiceNav.appendTo(_navDiv);
  _frequencyChoiceNav.on("change", _showSelectedFrequency);
  $("<label>Duration</label>").appendTo(_navDiv);
  _durationChoiceNav.appendTo(_navDiv);
  _durationChoiceNav.on("change", _showSelected);
  _showSelected();

};


var QueryString = function () {
  // This function is anonymous, is executed immediately and
  // the return value is assigned to QueryString!
  var query_string = {};
  var query = window.location.search.substring(1);
  var vars = query.split("&");
  for (var i=0;i<vars.length;i++) {
    var pair = vars[i].split("=");
      // If first entry with this name
    if (typeof query_string[pair[0]] === "undefined") {
      query_string[pair[0]] = pair[1];
      // If second entry with this name
    } else if (typeof query_string[pair[0]] === "string") {
      var arr = [ query_string[pair[0]], pair[1] ];
      query_string[pair[0]] = arr;
      // If third or later entry with this name
    } else {
      query_string[pair[0]].push(pair[1]);
    }
  }
    return query_string;
} ();
