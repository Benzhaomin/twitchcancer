'use strict';

/**
 * @ngdoc overview
 * @name twitchprofile
 * @description
 * # Twitch.tv profiles loading and formatting.
 *
 * Util module.
 */
angular
  .module('twitchProfile', [
    'ui.bootstrap'
  ])
  .factory('twitch_profiles', function($http) {
    var profiles = {}

    var _load_channel = function(channel) {
      $http.jsonp('https://api.twitch.tv/kraken/channels/'+channel.replace('#', '')+'?callback=JSON_CALLBACK').then(function(response) {

        profiles[channel] = response.data;

        console.log('[jsonp] finished loading ' + channel);
      }, function(err) {
        console.log('[jsonp] failed loading ' + channel);

        delete profiles[channel];
      });
    };

    return {
      'load': function(channel) {
        if (!(channel in profiles)) {
          profiles[channel] = null;
          _load_channel(channel);
        }
        return profiles[channel];
      }
    };
  })
  .directive('twitchprofile', function($http, twitch_profiles) {
    return {
      restrict: 'E',
      replace: false,
      scope: {channel: '@'},
      templateUrl : 'views/twitch_profile.html',
      link: function (scope, element, attrs) {
        //console.log(scope.profiles);
        scope.$watch(function() {
            return twitch_profiles.load(scope.channel)
          },
          function(newValue, oldValue) {
            if (newValue) {
              //console.log('[directive] profile loaded ' + scope.channel);
              scope.profile = twitch_profiles.load(scope.channel);
            }
          }
        )
      }
    };
  });
