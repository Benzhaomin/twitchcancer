$(document).ready(function() {
    $('form').submit(function(e) {
        e.preventDefault();

        $("#results").html('<img class="loading" src="img/loading.svg"/>');

        var channel = $('input[name="channel"]').val().replace("#", "");

        var margin = {top: 20, right: 20, bottom: 30, left: 50},
            width = $("#chart").width() - margin.left - margin.right,
            height = 500 - margin.top - margin.bottom;

        var parseDate = d3.time.format("%Y-%m-%d %H:%M:%S").parse;

        var x = d3.time.scale()
            .range([0, width]);

        var y = d3.scale.linear()
            .range([height, 0]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");

        var svg = d3.select("#chart").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        svg.append("text")
            .attr("x", (width / 2))
            .attr("y", 10)
            .attr("text-anchor", "middle")
            .attr("class", "title")
            .text("#"+channel);

        d3.json("http://localhost:8080/history/"+channel, function(error, json) {
            if (error) {
                $("#results").html('<h2 class="error">Request failed</h2>');
                return console.warn(error);
            }

            data = transform(json.history);

            console.log(data);

            x.domain(d3.extent(data, function(d) { return parseDate(d.date); }));
            y.domain([0, d3.max(data, function(d) { return d.total; })]);

            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis)
                .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 10)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text("Messages");

            var seriesData = ['cancer', 'sane'].map(function(name) {
              return {
                name: name,
                values: data.map(function(d) {
                  return {name: name, label: parseDate(d.date), value: +(name==='cancer' ? d[name] : d['total'] - d['cancer'])};
                })
              };
            });

            var stack = d3.layout.stack()
                .offset("zero")
                .values(function (d) { return d.values; })
                .x(function (d) { return x(d.label); })
                .y(function (d) { return d.value; });

            stack(seriesData);

            var area = d3.svg.area()
                .interpolate("cardinal")
                .x(function (d) { return x(d.label); })
                .y0(function (d) { return y(d.y0); })
                .y1(function (d) { return y(d.y0 + d.y); });

            var series = svg.selectAll(".series")
                .data(seriesData)
                .enter().append("g")
                .attr("class", "series");

            series.append("path")
                .attr("class", "streamPath")
                .attr("d", function(d) { return area(d.values); })
                .attr("class", function(d) { return d.name; });

            var points = svg.selectAll(".seriesPoints")
                .data(seriesData)
                .enter().append("g")
                .attr("class", "seriesPoints");

            points.selectAll(".point")
                .data(function (d) { return d.values; })
                .enter().append("circle")
                .attr("class", "point")
                .attr("cx", function (d) { return x(d.label); })
                .attr("cy", function (d) { return y(d.y0 + d.y); })
                .attr("r", "8px")
                .attr("title", function(d) { return d.y0 + d.y; })
                .on("mouseover", function (d) { showPopover.call(this, d); })
                .on("mouseout",  function (d) { removePopovers(); });


            function removePopovers() {

            }

            function showPopover(d) {
                console.log(d);

                $(this).qtip({
                    content: {
                        title: d.label.toLocaleString(),
                        text: d.y + " " + d.name + " messages"
                    },
                    show: {
                        solo: true,
                        ready: true
                    },
                    position: {
                        my: 'top left',
                        at: 'bottom right',
                        adjust: {
                            x: 20
                        },
                        target: $(this)
                    }
                });
            }
        });
    });

    $("a.preset").click(function(e) {
        e.preventDefault();
        e.stopPropagation();

        $('input[name="channel"]').val($(this).attr("href"));
        $('form').submit();
    });

    function transform(history) {
        var data = [];

        for (index in history) {
            var obj = history[index];
            var time = Object.keys(obj).pop();
            var point = {'date': time, 'cancer': obj[time]['cancer'], 'total': obj[time]['total']};
            data.push(point);
        }

        return data;
    }

    $('form').submit();
});
