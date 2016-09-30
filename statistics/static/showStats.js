var stats_colors = ["#64DD17", "#FFEE58", "#FFA726", "#EF5350", "#dddddd"]

function readablizeNumber (number) {
  var units = ['', 'k', 'M', 'G', 'T', 'P'];
  var e = Math.floor(Math.log(number) / Math.log(1000));
  return (number / Math.pow(1000, e)).toFixed((e > 0) ? 2 : 0) + " " + units[e];
}

function preProcessData(data) {
    for (var i = 0; i < 4; i++) {
        detail = data.detailed[i]
        if (data.on_statuses.length === 0 || -1 !== $.inArray(detail.id, data.on_statuses)) {
            detail.graph_value = detail.value
        } else {
            detail.graph_value = 0
        }
    }
    // Avoid division by zero when there are no results.
    if (data.num_tot === 0)
        data.detailed.push({dummy: 1, value: 0, graph_value: 0})
}

function showStatsPie (data, target_id) {
    preProcessData(data)

    var detailed_data = data.detailed
    var w = 201, h = 111;
	var r = 100, mr = 30; // radii
    var color = d3.scale.ordinal().range(stats_colors);

	// Create the svg element

    var vis = d3.select("#"+target_id).select(".statspie_graph")
        .append("svg:svg")
            .attr("width", w)
            .attr("height", h)
        .append("svg:g")
            .attr("transform", "translate(" + r + "," + r + ")");    //move the center of the pie chart from 0, 0 to radius, radius

	var parts = vis.selectAll("g.chart")
		.data([detailed_data])
		.enter()
			.append("svg:g")
				.attr("class", "chart");

    var arc = d3.svg.arc()              //this will create <path> elements for us using arc data
        .outerRadius(r)
		.innerRadius(mr);

    var pie = d3.layout.pie()           //this will create arc data for us given a list of values
        .value(function(d) { return d.dummy || d.graph_value; }) //we must tell it out to access the value of each element in our data array
		.sort(null)
		.startAngle(-Math.PI/2)
		.endAngle(Math.PI/2);

    var arcs = d3.select(parts[0][0])
    var arcs = arcs.selectAll("g.slice")     //this selects all <g> elements with class slice (there aren't any yet)
    var arcs = arcs
        .data(pie)                          //associate the generated pie data (an array of arcs, each having startAngle, endAngle and value properties) 
        .enter()                            //this will create <g> elements for every "extra" data element that should be associated with a selection. The result is creating a <g> for every object in the data array
            .append("svg:g")                //create a group to hold each slice (we will have a <path> and a <text> element associated with each slice)
                .attr("class", "slice")    //allow us to style things in the slices (like text)
            .each(function(d) { this._current = d.value; });

    var paths = arcs.append("svg:path")
                .attr("fill", function(d, i) { return color(i); } ) //set the color for each slice to be chosen from the color function defined above
                .attr("d", arc);                                    //this creates the actual SVG path using the associated data (pie) with the arc drawing function

	// Outer labels
    function translateText(thisArc, d) {				
        //set the label's origin to the center of the arc
        //we have to make sure to set these before calling arc.centroid
        d.innerRadius = mr;
        d.outerRadius = r;
        return "translate(" + thisArc.centroid(d) + ")";//this gives us a pair of coordinates like [50, 50]
    }
    function textForLabel(d, i) {
         return (d.data.graph_value === 0 ? "" : readablizeNumber(d.data.graph_value));
    }
	var arcs_text = d3.select(parts[0][0]).selectAll("g.slicetext")
        .data(pie)
        .enter()
            .append("svg:g")
                .attr("class", "slicetext");
		
    arcs_text.append("svg:text")                                     //add a label to each slice
            .attr("transform", function(d) { return translateText(arc,d); })
            .attr("text-anchor", "middle")                          //center the text on it's origin
            .text(textForLabel);

	var captions = d3.select("#"+target_id).select(".statspie_caption");

    function updatePie(data) {
        preProcessData(data)

        var arcs = d3.select(parts[0][0]).datum(data.detailed)
        var selectArcs = function(elt) { return arcs.selectAll(elt).data(pie).transition() }

        selectArcs("path")
          .attr("d", arc);
        selectArcs("text")
          .attr("transform",function(d) { return translateText(arc,d) })
          .text(textForLabel);
        captions.datum(data.detailed).selectAll("span.detail")
            .data(pie)
            .transition()
		    .text(function(d) { return d.data.value; });
    }

    return updatePie;
}
