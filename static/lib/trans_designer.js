app.controller('Transctrl', function ($http, $scope) {

  $scope.codeChange = function() {
    $http.post('//localhost:5000/_translate', { "data": $scope.code }).success(function(response) {
	$scope.trans_code = response.trans_code;
	});
  };

  $scope.code = "library IEEE;\nuse IEEE.std_logic_1164.all;\nuse IEEE.std_logic_arith.all;\nuse IEEE.std_logic_unsigned.all;\n\nentity fsm is\n    port(\trst, clk, proceed: in std_logic;\n\t\tcomparison: in std_logic_vector( 1 downto 0 );\n\t\tenable, xsel, ysel, xld, yld: out std_logic\n    );\nend fsm;\n\narchitecture fsm_arc of fsm is\n\n    type states is ( init, s0, s1, s2, s3, s4, s5 );\n    signal nState, cState: states;\n\nbegin\n    process( rst, clk )\n    begin\n\tif( rst = '1' ) then \n\t    cState <= init;\n\telsif( clk'event and clk = '1' ) then \n\t    cState <= nState;\n\tend if;\n    end process;\n\n    process( proceed, comparison, cState )\n    begin\n\tcase cState is \n\t\t\n\twhen init =>\tif( proceed = '0' ) then \n\t\t\t    nState <= init;\n\t\t\telse \n\t\t\t    nState <= s0;\n\t\t\tend if;\n\t\t\t\n\twhen s0 =>\tenable <= '0';\n\t\t\txsel <= '0';\n\t\t\tysel <= '0';\n\t\t\txld <= '0';\n\t\t\tyld <= '0';\n\t\t\tnState <= s1;\n\t\n\twhen s1 =>\tenable <= '0';\n\t\t\txsel <= '0';\n\t\t\tysel <= '0';\n\t\t\txld <= '1';\n\t\t\tyld <= '1';\n\t\t\tnState <= s2;\n\t\t\n\twhen s2 =>\txld <= '0';\n\t\t\tyld <= '0';\n\t\t\tif( comparison = \"10\" ) then \n\t\t\t    nState <= s3;\n\t\t\telsif( comparison = \"01\" ) then \n\t\t\t    nState <= s4; \t\n\t\t\telsif( comparison = \"11\" ) then \n\t\t\t    nState <= s5;   \t\n\t\t\tend if;\n\t\t\n\twhen s3 =>\tenable <= '0';\n\t\t\txsel <= '1';\n\t\t\tysel <= '0';\n\t\t\txld <= '1';\n\t\t\tyld <= '0';\n\t\t\tnState <= s2;\n\t\n\twhen s4 =>\tenable <= '0';\n\t\t\txsel <= '0';\n\t\t\tysel <= '1';\n\t\t\txld <= '0';\n\t\t\tyld <= '1';\n\t\t\tnState <= s2;\n\n\twhen s5 =>\tenable <= '1';\n\t\t\txsel <= '1';\n\t\t\tysel <= '1';\n\t\t\txld <= '1';\n\t\t\tyld <= '1';\n\t\t\tnState <= s0;\n\t\t\t\n\twhen others =>\tnState <= s0;\n\t\t\t\n        end case;\n\t\n    end process;\n\t\nend fsm_arc;";
  $scope.codeChange();

});
