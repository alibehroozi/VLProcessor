module xor_gate(input i1, input i2, output out);

wire mid1 = i1 & ~i2;
wire mid2 = ~i1 & i2;

out = mid1 | mid2;

endmodule
