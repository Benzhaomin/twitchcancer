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

    $interval(function() {
      $http.get('http://localhost:8080/cancer/forsenlol|amazhs|massansc|savjz?horizon=1').success(function(data) {
        $scope.cancer = data.channels.map(function(channel) {
          return Object.keys(channel).map(function(name) {
            return {'key': name, 'value': Math.round(channel[name]*100*100) / 100};
          })[0];
        });
      });
    }, 5000);

    // {"channels": [{"amazhs": 0.8132028625675478}]}
  })
  .directive('barsChart', function () {
    return {
      restrict: 'E',
      replace: false,
      scope: {data: '=chartData'},
      link: function (scope, element, attrs) {
        var chart = d3.select(element[0]).append("div").attr("class", "chart");

        scope.$watch('data', function() {

          //console.log(scope.data);
          var div = chart.selectAll('div')
            .data(scope.data);

          div.attr("class", "update")
            .transition().ease("elastic");

          div.enter().append("div")
            .attr("class", "enter");

          div.style("width", function(d) { return d.value + "%"; })
            .text(function(d) { return d.key + " " + d.value + "%"; })
        });
      }
    };
   });
