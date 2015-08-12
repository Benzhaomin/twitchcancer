'use strict';

/**
 * @ngdoc function
 * @name twitchCancer.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the main view
 */
angular.module('twitchCancer')
  .controller('MainCtrl', function ($scope) {
    $scope.history = [2, 1, 3];
  });
