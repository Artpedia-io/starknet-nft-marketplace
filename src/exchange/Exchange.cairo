# SPDX-License-Identifier: MIT

%lang starknet

from starkware.starknet.common.syscalls import get_caller_address, get_contract_address
from starkware.cairo.common.cairo_builtins import HashBuiltin, SignatureBuiltin
from starkware.cairo.common.math import assert_not_zero, assert_lt
from starkware.cairo.common.bool import TRUE, FALSE
from starkware.cairo.common.uint256 import (
    Uint256,
    uint256_check,
    uint256_eq,
    uint256_not,
    uint256_unsigned_div_rem,
    uint256_mul,
)

from openzeppelin.token.erc721.interfaces.IERC721 import IERC721
from src.exchange.library import Exchange
from src.openzeppelin.access.ownable import (
    Ownable_initializer,
    Ownable_only_owner,
    Ownable_get_owner,
    Ownable_transfer_ownership,
)

@constructor
func constructor{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    admin : felt, erc20_token : felt, treasury_address, platform_fee : Uint256, multiplier : Uint256
):
    Ownable_initializer(admin)
    # TODO: approve arrays of erc20 tokens

    Exchange.initializer(erc20_token, treasury_address, platform_fee, multiplier)
    return ()
end

@view
func get_admin{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
    admin : felt
):
    let (admin) = Ownable_get_owner()
    return (admin)
end

@view
func is_owner_or_operator{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    nft_collection : felt, token_id : Uint256
) -> (result : felt):
    let (result) = Exchange.is_owner_or_operator(nft_collection, token_id)
    return (result)
end

@view
func is_listed_item{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    nft_collection : felt, token_id : Uint256
) -> (is_on_sale : felt, payment_token : felt, listing_price : Uint256):
    let (is_listed_item) = Exchange.is_listed_item(nft_collection, token_id)
    return (is_listed_item.is_on_sale, is_listed_item.payment_token, is_listed_item.listing_price)
end

@view
func is_approved_token_as_payment{
    syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr
}(erc20_token : felt) -> (is_approved : felt):
    let (is_approved) = Exchange.is_approved_token_as_payment(erc20_token)
    return (is_approved)
end

@view
func get_platform_fee{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
    platform_fee : Uint256, multiplier : Uint256
):
    let (platform_fee, multiplier) = Exchange.get_platform_fee()
    return (platform_fee, multiplier)
end

@view
func get_token_allocation{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    amount : Uint256
) -> (platform_allocation : Uint256, seller_allocation : Uint256):
    let (platform_allocation, seller_allocation) = Exchange.get_token_allocation(amount)
    return (platform_allocation, seller_allocation)
end

@external
func listing{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    nft_collection : felt, token_id : Uint256, payment_token : felt, listing_price : Uint256
):
    Exchange.listing(nft_collection, token_id, payment_token, listing_price)
    return ()
end

@external
func delisting{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    nft_collection : felt, token_id : Uint256
):
    Exchange.delisting(nft_collection, token_id)
    return ()
end

@external
func approve_token_as_payment{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    erc20_token : felt, is_approved : felt
):
    Ownable_only_owner()
    Exchange.approve_token_as_payment(erc20_token, is_approved)
    return ()
end

@external
func buy{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    nft_collection : felt, token_id : Uint256, data_len : felt, data : felt*
):
    Exchange.buy(nft_collection, token_id, data_len, data)
    return ()
end

@external
func bid{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    nft_collection : felt,
    token_id : Uint256,
    payment_token : felt,
    price_bid : Uint256,
    expire_time : felt,
):
    Exchange.bid(nft_collection, token_id, payment_token, price_bid, expire_time)
    return ()
end

@external
func set_treasury_address{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    treasury_address : felt
):
    Ownable_only_owner()
    Exchange.set_treasury_address(treasury_address)
    return ()
end

@view
func get_treasury_address{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
    treasury_address : felt
):
    let (treasury_address) = Exchange.get_treasury_address()
    return (treasury_address)
end

@view
func get_bade_item{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    nft_collection : felt, token_id : Uint256, bidder : felt
) -> (payment_token : felt, price_bid : Uint256, expire_time : felt):
    let (bid_info) = Exchange.get_bade_item(nft_collection, token_id, bidder)
    return (bid_info.payment_token, bid_info.price_bid, bid_info.expire_time)
end

@external
func cancel_bid{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    nft_collection : felt, token_id : Uint256, bidder : felt
):
    Exchange.cancel_bid(nft_collection, token_id, bidder)
    return ()
end

@external
func accept_bid{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    nft_collection : felt,
    token_id : Uint256,
    payment_token : felt,
    minimum_price : Uint256,
    bidder : felt,
    data_len : felt,
    data : felt*,
):
    Exchange.accept_bid(
        nft_collection, token_id, payment_token, minimum_price, bidder, data_len, data
    )
    return ()
end
