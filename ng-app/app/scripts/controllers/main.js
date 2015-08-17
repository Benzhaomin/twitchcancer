'use strict';

/**
 * @ngdoc function
 * @name twitchCancer.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the main view
 */
angular.module('twitchCancer')
  .controller('MainCtrl', function ($scope, $http, $websocket) {
    var socket = $websocket('ws://localhost:8080');

    socket.onMessage(function(message) {
      var json = JSON.parse(message.data);

      if (json['topic'] === "twitchcancer.live") {
        $scope.live = json['data'].map(function(value) {
          // compute cancer per message
          value['cpm'] = Math.round(value.cancer / value.messages * 100)/100;
          return value;
        });
      }
      else if (json['topic'] === "twitchcancer.leaderboards") {
        $scope.leaderboards = json['data'];
      }
    });

    socket.onOpen(function() {
      console.log('socket opened');

      socket.send('{"subscribe": "twitchcancer.live"}');
      socket.send('{"subscribe": "twitchcancer.leaderboards"}');
    });

    socket.onClose(function() {
      console.warn('socket closed');

      $scope.$apply(function() {
        $scope.live = []
        $scope.leaderboards = []
      });
    });

    socket.onError(function(error) {
      console.error(error);
    });
  })
  .directive('barsChart', function() {
    return {
      restrict: 'E',
      replace: false,
      scope: {data: '=chartData', field: '@chartField'},
      link: function (scope, element, attrs) {
        var chart = d3.select(element[0]).append("div").attr("class", "chart");
        var x = d3.scale.linear().range([0,99]);

        scope.$watch('data', function() {

          if (typeof scope.data === 'undefined') {
            //chart.text("Loading...");
            return;
          }
          /*else {
            chart.text('');
          }*/

          if (scope.data.len == 0) {
            chart.text("No data");
            return;
          }

          x.domain(d3.extent(scope.data, function(d) {
            return d[scope.field];
          }));

          var data = scope.data.sort(function(a, b) {
            return b[scope.field] - a[scope.field];
          }).slice(0,10);

          var div = chart.selectAll('div')
            .data(data);

          div.attr("class", "update")
            .transition().ease("elastic");

          div.enter().append("div")
            .attr("class", "enter");

          div.style("width", function(d) { return x(d[scope.field]) + "%"; })
            .text(function(d) { return d.channel + ": " + d[scope.field]; })
        });
      }
    };
   })
  .directive('leaderboard', function() {
    return {
      restrict: 'E',
      replace: false,
      templateUrl : 'views/leaderboard.html',
      scope: {records: '=boardData', boardType: '@'}
    };
   });
;
