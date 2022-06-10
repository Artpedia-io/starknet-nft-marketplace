%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin, SignatureBuiltin
from src.utils import sum_func
from starkware.cairo.common.uint256 import (
    Uint256,
    uint256_check,
    uint256_eq,
    uint256_not,
    uint256_le,
    uint256_unsigned_div_rem,
    uint256_mul,
    uint256_sub,
    uint256_signed_lt,
)
# from src.exchange import Exchange

@external
func deployer{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
    alice : felt
):
    alloc_locals
    const public_key = 123
    local alice_address : felt
    %{ ids.alice_address = deploy_contract("./src/openzeppelin/account/Account.cairo", [ids.public_key]).contract_address %}
    return (alice_address)
end

@external
func test_constructor{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    # let (alice) = deployer()
    alloc_locals

    const alice_public_key = 123
    local alice_address : felt
    %{ ids.alice_address = deploy_contract("./src/openzeppelin/account/Account.cairo", [ids.alice_public_key]).contract_address %}

    const bob_public_key = 456
    local bob_address : felt
    %{ ids.bob_address = deploy_contract("./src/openzeppelin/account/Account.cairo", [ids.bob_public_key]).contract_address %}

    const dai_str = 4473161
    local dai_address : felt
    const erc20_decimals = 18

    %{ ids.dai_address = deploy_contract("./src/openzeppelin/token/erc20/ERC20.cairo", [ids.dai_str,ids.dai_str,18,1000,0,ids.alice_address]).contract_address %}

    const owner = 894122822122802080876
    const name = 2148280743873961096307
    local tubbycats_address : felt
    %{ ids.tubbycats_address = deploy_contract("./src/openzeppelin/token/erc721/ERC721_Mintable_Burnable.cairo", [ids.owner, ids.name, ids.bob_address]).contract_address %}

    local artpedia_address : felt
    %{ ids.artpedia_address = deploy_contract("./src/exchange/Exchange.cairo", [ids.alice_address, ids.dai_address, ids.alice_address, 2000, 0, 1000, 0]).contract_address %}

    let (user_tokens) = dai_address.balanceOf(dai_address, bob_address)

    assert user_tokens = Uint256(0, 0)
    return ()
end
