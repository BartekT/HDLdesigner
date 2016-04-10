app.controller('cpu_ctrl', function($scope, $http) {
    $scope.opcode_matrix = [];
    $scope.opcode_matrix_short = [];
    $scope.hexitems = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F' ];
    $scope.decitems = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ];

    $scope.loadTable = function() {
	$http.get("//localhost:5000/_load_instr").then(function (response) {
	    $scope.opcode_matrix = response.data.opcode_matrix;
	    $scope.opcode_matrix_short = response.data.opcode_matrix_short;
	    $scope.opcode_cycle = response.data.opcode_cycle;
	    $scope.max_signal_lengths = response.data.max_signal_lengths;
	    $scope.max_states = response.data.max_states;
	});
    };

    $scope.show_cycles = function(id) {
	$scope.sel_instr = $scope.opcode_matrix[id >> 4][id % 16];
	$scope.sel_opcode = ("0"+(Number(id).toString(16))).slice(-2).toUpperCase();
	$scope.opis = $scope.opcode_cycle[$scope.sel_opcode];
	$scope.max_signal_length = $scope.max_signal_lengths[$scope.sel_opcode];
	$scope.max_state = $scope.max_states[$scope.sel_opcode];
    };

    $scope.hide_cycles = function() {
	$scope.opis = 0;
	$scope.sel_opcode = '';
    };

    $scope.range = function( max ) {
	var values = [];
	for(var i = 0; i < max; i++) {
	    values.push(i);
	}
	return values;
    };

    $scope.loadTable();
});
