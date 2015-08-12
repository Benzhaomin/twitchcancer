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
    $scope.history = [];

    /*$http.get('http://localhost:8080/history/forsenlol').success(function(data) {
      $scope.history = transform(data.history);
    });*/

    $interval(function() {
      $scope.history = [
        {'key': 'a', 'value': Math.round(Math.random()*10+20) },
        {'key': 'b', 'value': Math.round(Math.random()*8+10) },
        {'key': 'c', 'value': Math.round(Math.random()*30+69) }
      ];
    }, 1000);

    function transform(json) {
      var data = [];

      for (var index in json) {
        var obj = json[index];
        var time = Object.keys(obj).pop();
        var point = {'date': time, 'cancer': obj[time]['cancer'], 'total': obj[time]['total']};
        data.push(point);
      }

      return data;
    }
  })
  .directive('barsChart', function () {
    return {
      restrict: 'E',
      replace: false,
      scope: {data: '=chartData'},
      link: function (scope, element, attrs) {
        var chart = d3.select(element[0]).append("div").attr("class", "chart");

        scope.$watch('data', function() {
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
