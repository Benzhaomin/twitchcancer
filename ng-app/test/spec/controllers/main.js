'use strict';

describe('Controller: MainCtrl', function () {

  // load the controller's module
  beforeEach(module('twitchCancer'));

  var MainCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    MainCtrl = $controller('MainCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  /*it('should attach a cancer history to the scope', function () {
    expect(MainCtrl.history.length).toBe(3);
  });*/
});
