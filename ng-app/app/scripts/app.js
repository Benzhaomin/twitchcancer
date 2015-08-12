'use strict';

/**
 * @ngdoc overview
 * @name twitchcancer
 * @description
 * # Live monitoring of Twitch chats cancer level via web-sockets.
 *
 * Main module of the application.
 */
angular
  .module('twitchcancer', [
    'ngAnimate',
    'ngCookies',
    'ngMessages',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch'
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl',
        controllerAs: 'main'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
