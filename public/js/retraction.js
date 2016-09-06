/* global d3, $ */

/**
 * updateGraph
 *
 * Update the graph with some new data and remove the old one.
 *
 * @newData: New tuples of data to update the graph with
 */
function updateGraph(newData) {
  var svg;
  var rects;
  var x = d3.scale.linear()
              .domain([0, d3.max(newData)])
              .range([0, 420]);

  /* Drop any existing SVG elements */
  Array.prototype.forEach.call(document.getElementsByClassName("chart"),
                               function dropInnerHTMLOf(element) {
                                 /* Drop everything inside this chart */
                                 element.innerHTML = "";  // eslint-disable-line no-param-reassign
                               });

  svg = d3.select("div.chart")
          .append("svg")
          .attr("class", "svgchart")
          .attr("width", 960)
          .attr("height", 500);

  rects = svg.selectAll("rect")
             .data(newData)
             .enter()
             .append("rect");

  rects.attr("width", function setWidthFromScale(d) {
    return x(d);
  })
  .attr("height", 20)
  .attr("y", function setYFromIndex(d, i) {
    return 30 * i;
  });
}

$.ajax({
  url: "/get_bar_chart",
  json: {
    name: "name"
  },
  success: function onAjaxSuccess(data) {
    updateGraph(data.map(function onEachDataElement(w) {
      return w.value;
    }));
  }
});

/**
 * updateSelection
 *
 * Get the new value from the graph selection and update the graph with it.
 */
function updateSelection() {
  var x = document.getElementById("graphs").value;
  updateGraph(values[x]); // adding string rather than selection and doesnt remove old selections
}

document.addEventListener("DOMContentLoaded", function onDOMContentLoad() {
  updateSelection(values.journalYear);
});
