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

window.my_graph = new Object();

function destroyOldGraph(targetDiv) {
  if (window.my_graph[targetDiv] != undefined) {
    console.log("Destroying previous graph: " + window.my_graph[targetDiv]);
    window.my_graph[targetDiv].destroy();
  }  
}

function notImpl() {
  alert ("Not implemented yet.");
}

function showArticleGraph(targetDiv, siteID) {
  console.log("Displaying article graph for " + siteID)
  destroyOldGraph(targetDiv);
  window.my_graph[targetDiv] = new Dygraph(
    document.getElementById(targetDiv),
    "http://wikiapiary.com/apiary/data/articles.php?id=" + siteID,
    {
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
      labelsDiv: document.getElementById("legend"),
      ylabel: 'Pages',
      yLabelWidth: 12,
      y2label: 'Articles',
      rightGap: 10
    }
    );
}

function showUsersGraph(targetDiv, siteID) {
  console.log("Displaying users graph for " + siteID)
  destroyOldGraph(targetDiv);
  window.my_graph[targetDiv] = new Dygraph(
    document.getElementById(targetDiv),
    "http://wikiapiary.com/apiary/data/users.php?id=" + siteID,
    {
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
      labelsDiv: document.getElementById("legend"),
      yLabelWidth: 12,
      rightGap: 10
    }
    );
}

function showJobsGraph(targetDiv, siteID) {
  console.log("Displaying jobs graph for " + siteID)  
  destroyOldGraph(targetDiv);
  window.my_graph[targetDiv] = new Dygraph(
    document.getElementById(targetDiv),
    "http://wikiapiary.com/apiary/data/jobs.php?id=" + siteID,
    {
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
      labelsDiv: document.getElementById("legend"),
      yLabelWidth: 12,
      fillGraph: true,
      includeZero: true,
      rightGap: 10
    }
    );
}

function showEditsGraph(targetDiv, siteID) {
  console.log("Displaying edits graph for " + siteID)
  destroyOldGraph(targetDiv);
  window.my_graph[targetDiv] = new Dygraph(
    document.getElementById(targetDiv),
    "http://wikiapiary.com/apiary/data/edits.php?id=" + siteID,
    {
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
      labelsDiv: document.getElementById("legend"),
      yLabelWidth: 12,
      fillGraph: true,
      includeZero: true,
      rightGap: 10
    }
    );
}


