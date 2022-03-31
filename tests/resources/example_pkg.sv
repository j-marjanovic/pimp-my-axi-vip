
// this line will stay

// enterprise-grade code
`define VALUE_0 0
`define VALUE_1 1
`define VALUE_2 2

package example_pkg;

  function logic [31:0] add_one(logic [31:0] a);
    // add one to the input value
    logic [31:0] tmp;
    tmp = a + 1;
    return tmp;
  endfunction

  function bit [31:0] add_two(bit [31:0] b);
    return b + `VALUE_2;
  endfunction

  // adding a couple of lines here to verify the patcher
  // more lines here

endpackage
