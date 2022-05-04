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
func ERC721_name() -> (name : felt):
end

@storage_var
func ERC721_symbol() -> (symbol : felt):
end

@storage_var
func ERC721_id_to_owner(token_id : Uint256) -> (owner : felt):
end

namespace ERC721:
    func constructor{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        name : felt, symbol : felt
    ):
        ERC721_name.write(name)
        ERC721_symbol.write(symbol)
        return ()
    end

    func name{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (name : felt):
        let (name) = ERC721_name.read()
        return (name)
    end

    func symbol{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
        symbol : felt
    ):
        let (symbol) = ERC721_symbol.read()
        return (symbol)
    end

    func mint{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        to : felt, token_id : Uint256
    ) -> ():
        ERC721_id_to_owner.write(token_id, to)
        return ()
    end

    func ownerOf{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        token_id : Uint256
    ) -> (owner : felt):
        let (owner) = ERC721_id_to_owner.read(token_id)
        return (owner)
    end
end
