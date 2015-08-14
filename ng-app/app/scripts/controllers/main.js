'use strict';

/**
 * @ngdoc function
 * @name twitchCancer.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the main view
 */
angular.module('twitchCancer')
  .controller('MainCtrl', function ($scope, $http, $interval) {
    $scope.cancer = [];

    var update = function() {
      $http.get('http://localhost:8080/live').success(function(data) {
        $scope.cancer = data.channels.sort(function(a, b) {
          return b.cancer - a.cancer;
        }).slice(0,10);
      })
    };

    update();
    $interval(update, 5000);
  })
  .directive('barsChart', function () {
    return {
      restrict: 'E',
      replace: false,
      scope: {data: '=chartData'},
      link: function (scope, element, attrs) {
        var chart = d3.select(element[0]).append("div").attr("class", "chart");
        var x = d3.scale.linear().range([10,99]);

        scope.$watch('data', function() {

          x.domain(d3.extent(scope.data, function(d) {
            return d.cancer;
          }));

          //console.log(scope.data);
          var div = chart.selectAll('div')
            .data(scope.data);

          div.attr("class", "update")
            .transition().ease("elastic");

          div.enter().append("div")
            .attr("class", "enter");


          div.style("width", function(d) { return x(d.cancer) + "%"; })
            .text(function(d) { return d.channel + ": " + d.cancer; })
        });
      }
    };
   });
