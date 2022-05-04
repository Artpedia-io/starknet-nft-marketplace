# SPDX-License-Identifier: MIT
# OpenZeppelin Contracts for Cairo v0.1.0 (token/erc721/library.cairo)

%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin, SignatureBuiltin
from starkware.starknet.common.syscalls import get_caller_address
from starkware.cairo.common.math import assert_not_zero, assert_not_equal
from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.bool import TRUE, FALSE
from starkware.cairo.common.uint256 import Uint256, uint256_check
from contracts.erc721.library import ERC721

@constructor
func constructor{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    name : felt, symbol : felt
):
    ERC721.constructor(name, symbol)
    return ()
end

@view
func name{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (name : felt):
    let (name) = ERC721.name()
    return (name)
end

@view
func symbol{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (symbol : felt):
    let (symbol) = ERC721.symbol()
    return (symbol)
end

@external
func mint{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    to : felt, token_id : Uint256
) -> ():
    ERC721.mint(to, token_id)
    return ()
end

@view
func ownerOf{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    token_id : Uint256
) -> (owner : felt):
    let (owner) = ERC721.ownerOf(token_id)
    return (owner)
end
