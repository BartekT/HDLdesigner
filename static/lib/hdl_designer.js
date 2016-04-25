var app = angular.module('designer', ['ui.codemirror', 'ui.bootstrap', 'ngFileSaver']);

function svgSaveCtrl(FileSaver, Blob) {
  var vm = this;

  vm.download = function(text) {
    var data = new Blob([text], { type: 'image/svg+xml' });
    FileSaver.saveAs(data, 'diagram.svg');
  };
}

app.controller('menuCtrl', function ($scope, $uibModal) {
  $scope.actvPanel = 'HDL';

  $scope.items = ['item1', 'item2', 'item3'];

  $scope.open = function (size) {

    var modalInstance = $uibModal.open({
      animation: $scope.animationsEnabled,
      templateUrl: 'myModalContent.html',
      controller: 'ModalInstanceCtrl',
      size: size,
      resolve: {
        items: function () {
          return $scope.items;
        }
      }
    });

    modalInstance.result.then(function (selectedItem) {
      $scope.selected = selectedItem;
    }, function () {
      $log.info('Modal dismissed at: ' + new Date());
    });
  };

  $scope.toggleAnimation = function () {
    $scope.animationsEnabled = !$scope.animationsEnabled;
  };
});

app.controller('svgSaveCtrl', ['FileSaver', 'Blob', svgSaveCtrl]);

app.controller('HDLctrl', function ($http, $scope, $uibModal, $log, $timeout) {

  $scope.form = {};
  $scope.form["searchText"] = null;

  $scope.oneAtATime = true;

  $scope.progress_state = false;
  $scope.parsing_error = false;

  $scope.animationsEnabled = true;

  $scope.codeChange = function() {
    $http.post('//localhost:5000/_parse_code', { "data": $scope.code }).success(function(response) {
	$scope.fsms = response.fsms;
	$scope.outputs = response.outputs;
	$scope.$broadcast('rebuild:me');
	$scope.parsing_error = response.parsing_error;
	$scope.progress_state = false;
	});
    $scope.code_refresh = 0;
  };

  $scope.isArr = function(arr) {
    return Array.isArray(arr);
  };

  $scope.isObj = function(obj) {
    return angular.isObject(obj);
  };

  $scope.code = "------------------------------------------\n-- This is an example FSM code\n------------------------------------------\n\nlibrary IEEE;\nuse IEEE.std_logic_1164.all;\nuse IEEE.std_logic_arith.all;\nuse IEEE.std_logic_unsigned.all;\n\nentity fsm is\n    port(\trst, clk, proceed: in std_logic;\n\t\tcomparison: in std_logic_vector( 1 downto 0 );\n\t\tenable, xsel, ysel, xld, yld: out std_logic\n    );\nend fsm;\n\narchitecture fsm_arc of fsm is\n\n    type states is ( init, s0, s1, s2, s3, s4, s5 );\n    signal nState, cState: states;\n\nbegin\n    process( rst, clk )\n    begin\n\tif( rst = '1' ) then \n\t    cState <= init;\n\telsif( clk'event and clk = '1' ) then \n\t    cState <= nState;\n\tend if;\n    end process;\n\n    process( proceed, comparison, cState )\n    begin\n\tcase cState is \n\t\t\n\twhen init =>\tif( proceed = '0' ) then \n\t\t\t    nState <= init;\n\t\t\telse \n\t\t\t    nState <= s0;\n\t\t\tend if;\n\t\t\t\n\twhen s0 =>\tenable <= '0';\n\t\t\txsel <= '0';\n\t\t\tysel <= '0';\n\t\t\txld <= '0';\n\t\t\tyld <= '0';\n\t\t\tnState <= s1;\n\t\n\twhen s1 =>\tenable <= '0';\n\t\t\txsel <= '0';\n\t\t\tysel <= '0';\n\t\t\txld <= '1';\n\t\t\tyld <= '1';\n\t\t\tnState <= s2;\n\t\t\n\twhen s2 =>\txld <= '0';\n\t\t\tyld <= '0';\n\t\t\tif( comparison = \"10\" ) then \n\t\t\t    nState <= s3;\n\t\t\telsif( comparison = \"01\" ) then \n\t\t\t    nState <= s4; \t\n\t\t\telsif( comparison = \"11\" ) then \n\t\t\t    nState <= s5;   \t\n\t\t\tend if;\n\t\t\n\twhen s3 =>\tenable <= '0';\n\t\t\txsel <= '1';\n\t\t\tysel <= '0';\n\t\t\txld <= '1';\n\t\t\tyld <= '0';\n\t\t\tnState <= s2;\n\t\n\twhen s4 =>\tenable <= '0';\n\t\t\txsel <= '0';\n\t\t\tysel <= '1';\n\t\t\txld <= '0';\n\t\t\tyld <= '1';\n\t\t\tnState <= s2;\n\n\twhen s5 =>\tenable <= '1';\n\t\t\txsel <= '1';\n\t\t\tysel <= '1';\n\t\t\txld <= '1';\n\t\t\tyld <= '1';\n\t\t\tnState <= s0;\n\t\t\t\n\twhen others =>\tnState <= s0;\n\t\t\t\n        end case;\n\t\n    end process;\n\t\nend fsm_arc;";
  $scope.codeChange();

  $scope.timeoutCodeChange = function() {
    if(!$scope.code_refresh)
    {
	$scope.progress_state = true;
	$scope.parsing_error = false;
	$scope.code_refresh = 1;
	$timeout($scope.codeChange, 3000);
    }
  };

});

// Please note that $uibModalInstance represents a modal window (instance) dependency.
// It is not the same as the $uibModal service used above.

app.controller('ModalInstanceCtrl', function ($scope, $uibModalInstance, items) {

  $scope.items = items;
  $scope.selected = {
    item: $scope.items[0]
  };

  $scope.ok = function () {
    $uibModalInstance.close($scope.selected.item);
  };

  $scope.cancel = function () {
    $uibModalInstance.dismiss('cancel');
  };
});

app.directive('resize', ['$window', function($window) {
	    return {
	        link: function(scope, elem, attrs) {
	            scope.onResize = function() {
	                var padding = 34,
			    offset = elem.prop('offsetTop'),
	                    height = $window.innerHeight - offset - padding;
	                elem.css({height: height + 'px'});
			console.log(height);
	            }
	            scope.onResize();
	                angular.element($window).bind('resize', function() {
	                scope.onResize();
	            })
	        }
	    }
	}]);

app.directive('svgImg', function() {
    return {
	scope: { content:'@' },
	link: function(scope, elem, attrs) {
	    scope.$watch("content",function(newValue,oldValue) {
		elem.html(newValue);
	    });
	    elem.html(attrs.content);
    }
    };
});
