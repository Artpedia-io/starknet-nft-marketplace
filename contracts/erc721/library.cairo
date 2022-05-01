# SPDX-License-Identifier: MIT
# OpenZeppelin Contracts for Cairo v0.1.0 (token/erc721/library.cairo)

%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin, SignatureBuiltin
from starkware.starknet.common.syscalls import get_caller_address
from starkware.cairo.common.math import assert_not_zero, assert_not_equal
from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.bool import TRUE, FALSE
from starkware.cairo.common.uint256 import Uint256, uint256_check


@storage_var
func ERC721_name() -> (name: felt):
end

@storage_var
func ERC721_symbol() -> (symbol: felt):
end

func ERC721_initializer{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
}(
    name: felt,
    symbol: felt,
): 
    ERC721_name.write(name)
    ERC721_symbol.write(symbol)
    return ()
end