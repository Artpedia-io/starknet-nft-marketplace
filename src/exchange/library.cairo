# SPDX-License-Identifier: MIT

%lang starknet

from starkware.starknet.common.syscalls import (
    get_caller_address,
    get_contract_address,
    get_block_number,
    get_block_timestamp,
)

from starkware.cairo.common.cairo_builtins import HashBuiltin, SignatureBuiltin
from starkware.cairo.common.math import assert_not_zero, assert_lt, assert_not_equal
from starkware.cairo.common.bool import TRUE, FALSE
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

from openzeppelin.token.erc721.interfaces.IERC721 import IERC721

from openzeppelin.token.erc20.interfaces.IERC20 import IERC20

@event
func Listing(
    maker : felt,
    nft_collection : felt,
    token_id : Uint256,
    payment_token : felt,
    listing_price : Uint256,
):
end

@event
func Bidding(
    sender : felt,
    nft_collection : felt,
    token_id : Uint256,
    payment_token : felt,
    bidding_price : Uint256,
    expire_time : felt,
):
end

@event
func ApproveTokenAsPayment(token : felt, is_approved : felt):
end

@event
func OrdersMatched(
    sender : felt,
    receiver : felt,
    nft_collection : felt,
    token_id : Uint256,
    payment_token : felt,
    price_matched : Uint256,
):
end

struct User:
    member address : felt
    member balance : felt
end

struct ListingInformation:
    member nft_collection : felt
    member token_id : Uint256
end

struct PricingInformation:
    member is_on_sale : felt
    member payment_token : felt
    member listing_price : Uint256
end

struct BidInfo:
    member payment_token : felt
    member price_bid : Uint256
    member expire_time : felt
end

@storage_var
func listing_information(nft_collection : felt, token_id : Uint256) -> (
    pricing_information : PricingInformation
):
end

@storage_var
func bid_information(nft_collection : felt, token_id : Uint256, bidder : felt) -> (
    bid_information : BidInfo
):
end

@storage_var
func platform_fee() -> (amount : Uint256):
end

@storage_var
func multiplier() -> (amount : Uint256):
end

@storage_var
func treasury() -> (address : felt):
end

@storage_var
func approved_token_as_payment(erc20 : felt) -> (is_approved : felt):
end

namespace Internal:
    func is_owner_or_operator{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt, token_id : Uint256
    ) -> (result : felt):
        alloc_locals
        let (caller) = get_caller_address()
        let (owner) = IERC721.ownerOf(contract_address=nft_collection, tokenId=token_id)
        let (is_operator) = IERC721.isApprovedForAll(
            contract_address=nft_collection, owner=owner, operator=caller
        )
        local is_owner = 0
        if caller == owner:
            local is_owner = 1
            return (is_owner)
        end

        let result = is_owner + is_operator
        return (result=result)
    end
    func assert_caller_not_owner{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt, token_id : Uint256
    ):
        let (caller) = get_caller_address()
        let (owner) = IERC721.ownerOf(contract_address=nft_collection, tokenId=token_id)
        with_attr error_message("ArtpediaExchange: caller is ERC-721 owner"):
            assert_not_equal(caller, owner)
        end
        return ()
    end

    func assert_token_owner_or_operator{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr
    }(nft_collection : felt, token_id : Uint256):
        let (owner_or_operator) = is_owner_or_operator(nft_collection, token_id)
        with_attr error_message("ArtpediaExchange: caller is not owner nor operators"):
            assert owner_or_operator = 1
        end
        return ()
    end

    func assert_bidder_have_enough_erc20_token{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr
    }(erc20_token : felt, item_price : Uint256, bidder : felt):
        alloc_locals
        # buyer must have enough token

        let (balance) = IERC20.balanceOf(contract_address=erc20_token, account=bidder)

        # erc20 balance (rhs) must be more than the item price
        local syscall_ptr : felt* = syscall_ptr
        let (is_enough_erc20_token) = uint256_le(item_price, balance)
        with_attr error_message("ArtpediaExchange: buyer does not have enough ERC-20 Tokens"):
            assert is_enough_erc20_token = 1
        end
        return ()
    end

    func assert_bidder_delegate_enough_erc20_to_exchange{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr
    }(erc20_token : felt, item_price : Uint256, bidder):
        alloc_locals
        let (exchange) = get_contract_address()
        let (allowance) = IERC20.allowance(
            contract_address=erc20_token, owner=bidder, spender=exchange
        )
        local syscall_ptr : felt* = syscall_ptr
        let (is_enough_allowance) = uint256_le(item_price, allowance)
        with_attr error_message("ArtpediaExchange: insufficient allowance"):
            assert is_enough_allowance = 1
        end
        return ()
    end
    func assert_listed_item{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt, token_id : Uint256
    ):
        let (pricing_information) = listing_information.read(nft_collection, token_id)
        with_attr error_message("ArtpediaExchange: item not listed"):
            assert pricing_information.is_on_sale = 1
        end
        return ()
    end

    func assert_listed_token_as_payment{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr
    }(erc20_token : felt):
        let (is_approved) = approved_token_as_payment.read(erc20_token)
        with_attr error_message("ArtpediaExchange: not an approved ERC-20 on Artpedia"):
            assert is_approved = 1
        end
        return ()
    end

    func assert_unlisted_items{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt, token_id : Uint256
    ):
        let (pricing_information) = listing_information.read(nft_collection, token_id)
        with_attr error_message("ArtpediaExchange: item already listed"):
            assert pricing_information.is_on_sale = 0
        end
        return ()
    end

    func assert_exchange_approved_for_erc721{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr
    }(nft_collection : felt, token_id : Uint256):
        let (exchange_address) = get_contract_address()
        let (approved_contract) = IERC721.getApproved(
            contract_address=nft_collection, tokenId=token_id
        )
        with_attr error_message("ArtpediaExchange: exchange is not approved yet"):
            assert exchange_address = approved_contract
        end
        return ()
    end

    func assert_uint256_not_zero{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        amount : Uint256
    ):
        # TODO: listing price assertion
        let one = Uint256(1, 0)
        # return 1 if amount (left) is lesser than one
        let (is_zero) = uint256_signed_lt(amount, one)

        with_attr error_message("ArtpediaExchange: amount must be more than zero"):
            assert is_zero = 0
        end
        return ()
    end

    func assert_bid_not_expired{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        expire_time : felt
    ):
        let (block_timestamp) = get_block_timestamp()
        let is_not_expired = uint256_signed_lt(block_timestamp, expire_time)

        with_attr error_message("ArtpediaExchange: bid has expired"):
            assert is_not_expired = 1
        end
        return ()
    end

    func get_bade_item{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt, token_id : Uint256, bidder : felt
    ) -> (bid_info : BidInfo):
        let (bid_info) = bid_information.read(nft_collection, token_id, bidder)
        return (bid_info)
    end

    func assert_bid_exists{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt, token_id : Uint256, bidder : felt
    ):
        let (bid_info) = get_bade_item(nft_collection, token_id, bidder)

        # bid must exist
        with_attr error_message("ArtpediaExchange: no bid for this token_id"):
            assert_not_zero(bid_info.payment_token)
        end

        with_attr error_message("ArtpediaExchange: no bid for this token_id"):
            Internal.assert_uint256_not_zero(bid_info.price_bid)
        end

        with_attr error_message("ArtpediaExchange: no bid for this token_id"):
            assert_not_zero(bidder)
        end

        return ()
    end
end

namespace Exchange:
    func initializer{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        erc20_token : felt, treasury_address : felt, platform_fee : Uint256, multiplier : Uint256
    ):
        approve_token_as_payment(erc20_token, 1)
        set_platform_fee(platform_fee, multiplier)
        treasury.write(treasury_address)
        return ()
    end

    func set_treasury_address{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        treasury_address : felt
    ):
        treasury.write(treasury_address)
        return ()
    end

    func get_treasury_address{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        ) -> (treasury_address : felt):
        let (treasury_address) = treasury.read()
        return (treasury_address)
    end

    func set_platform_fee{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        _platform_fee : Uint256, _multiplier : Uint256
    ):
        platform_fee.write(_platform_fee)
        multiplier.write(_multiplier)
        return ()
    end

    func get_platform_fee{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
        _platform_fee : Uint256, _multiplier : Uint256
    ):
        let (_platform_fee) = platform_fee.read()

        let (_multiplier) = multiplier.read()
        return (_platform_fee, _multiplier)
    end

    func is_owner_or_operator{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt, token_id : Uint256
    ) -> (result : felt):
        let (result) = Internal.is_owner_or_operator(nft_collection, token_id)
        return (result=result)
    end

    func get_token_allocation{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        amount : Uint256
    ) -> (treasury_allocation : Uint256, seller_allocation : Uint256):
        alloc_locals
        let (_platform_fee, _multiplier) = get_platform_fee()
        local syscall_ptr : felt* = syscall_ptr
        let (quotient, _) = uint256_mul(_platform_fee, amount)
        let (divisor, _) = uint256_mul(Uint256(100, 0), _multiplier)
        let (treasury_allocation, _) = uint256_unsigned_div_rem(quotient, divisor)
        let seller_allocation = uint256_sub(amount, treasury_allocation)

        return (treasury_allocation, seller_allocation.res)
    end

    func send_erc20_token{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        payment_token : felt, sender : felt, recipient : felt, amount : Uint256
    ):
        # TODO: prevent reentrant
        alloc_locals
        let (treasury_address) = get_treasury_address()
        local treasury_address = treasury_address

        let (treasury_allocation, seller_allocation) = get_token_allocation(amount)

        IERC20.transferFrom(
            contract_address=payment_token,
            sender=sender,
            recipient=recipient,
            amount=seller_allocation,
        )

        IERC20.transferFrom(
            contract_address=payment_token,
            sender=sender,
            recipient=treasury_address,
            amount=treasury_allocation,
        )

        return ()
    end

    func is_listed_item{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt, token_id : Uint256
    ) -> (pricing_information : PricingInformation):
        let (pricing_information) = listing_information.read(nft_collection, token_id)
        return (pricing_information)
    end

    func is_approved_token_as_payment{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr
    }(erc20_token : felt) -> (is_approved : felt):
        let (is_approved) = approved_token_as_payment.read(erc20_token)
        return (is_approved)
    end

    func approve_token_as_payment{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr
    }(erc20_token : felt, is_approved : felt):
        alloc_locals
        let (approval) = approved_token_as_payment.read(erc20_token)

        if approval == 0:
            with_attr error_message("ArtpediaExchange: ERC-20 token already has the same approval"):
                assert is_approved = 1
            end
        else:
            with_attr error_message("ArtpediaExchange: ERC-20 token already has the same approval"):
                assert is_approved = 0
            end
        end

        # write to blockchain
        approved_token_as_payment.write(erc20_token, is_approved)

        # emit events
        ApproveTokenAsPayment.emit(erc20_token, is_approved)
        return ()
    end

    func listing{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt, token_id : Uint256, payment_token : felt, listing_price : Uint256
    ):
        # check if caller is owner or operator
        Internal.assert_token_owner_or_operator(nft_collection, token_id)

        # check if exchange have approval or not
        Internal.assert_exchange_approved_for_erc721(nft_collection, token_id)

        # check if payment token has been approved
        Internal.assert_listed_token_as_payment(payment_token)

        # check if token have been listed or not
        Internal.assert_unlisted_items(nft_collection, token_id)

        # check if not zero
        with_attr error_message("ArtpediaExchange: invalid ERC721 address"):
            assert_not_zero(nft_collection)
        end

        Internal.assert_uint256_not_zero(listing_price)

        # write to blockchain
        let pricing_information = PricingInformation(
            is_on_sale=1, payment_token=payment_token, listing_price=listing_price
        )
        listing_information.write(nft_collection, token_id, pricing_information)

        # emit events
        let (caller) = get_caller_address()
        Listing.emit(caller, nft_collection, token_id, payment_token, listing_price)
        return ()
    end

    func delisting{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt, token_id : Uint256
    ):
        # cancel caller must be owner or operator
        Internal.assert_token_owner_or_operator(nft_collection, token_id)

        # item must be listed
        Internal.assert_listed_item(nft_collection, token_id)

        # delisting
        let pricing_information = PricingInformation(
            is_on_sale=0, payment_token=0, listing_price=Uint256(0, 0)
        )
        listing_information.write(nft_collection, token_id, pricing_information)

        # emit event
        let (caller) = get_caller_address()
        Listing.emit(caller, nft_collection, token_id, 0, Uint256(0, 0))
        return ()
    end

    func buy{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt, token_id : Uint256, data_len : felt, data : felt*
    ):
        alloc_locals
        let (buyer) = get_caller_address()
        let (seller) = IERC721.ownerOf(contract_address=nft_collection, tokenId=token_id)

        let (pricing_information) = is_listed_item(nft_collection, token_id)
        let item_price = pricing_information.listing_price
        let payment_token = pricing_information.payment_token

        # item must be listed
        Internal.assert_listed_item(nft_collection, token_id)

        # buyer must not be ERC721 owner
        local pedersen_ptr : HashBuiltin* = pedersen_ptr
        Internal.assert_caller_not_owner(nft_collection, token_id)

        # buyer must have enough erc20 token
        # currently handled by ERC20 interface
        # assert_bidder_have_enough_erc20_token(payment_token, item_price)

        # exchange must have enough allowance for ERC20 transfer
        # currently handled by ERC20 interface
        # assert_bidder_delegate_enough_erc20_to_exchange(payment_token, item_price)

        # exchange must be approved for ERC721 transfer
        # currently handled by ERC721 interface
        # assert_exchange_approved_for_erc721(nft_collection, token_id)

        # send ERC721 from seller to buyer
        # TODO: prevent reentrant
        IERC721.safeTransferFrom(
            contract_address=nft_collection,
            from_=seller,
            to=buyer,
            tokenId=token_id,
            data_len=data_len,
            data=data,
        )

        # send ERC20 from buyer to seller
        send_erc20_token(payment_token, buyer, seller, item_price)

        # emit event
        OrdersMatched.emit(buyer, seller, nft_collection, token_id, payment_token, item_price)

        # delist item
        delisting(nft_collection, token_id)

        return ()
    end

    func bid{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt,
        token_id : Uint256,
        payment_token : felt,
        price_bid : Uint256,
        expire_time : felt,
    ):
        alloc_locals

        let (block_timestamp) = get_block_timestamp()
        let bid_expiry = block_timestamp + expire_time

        let (bidder) = get_caller_address()

        # bid must be greater than 0
        Internal.assert_uint256_not_zero(price_bid)

        # bidder must have enough token
        Internal.assert_bidder_have_enough_erc20_token(payment_token, price_bid, bidder)

        # bidder must have enough ERC20 allowance
        Internal.assert_bidder_delegate_enough_erc20_to_exchange(payment_token, price_bid, bidder)

        # bidder must not be ERC721 owner
        Internal.assert_caller_not_owner(nft_collection, token_id)

        # write to blockchain
        bid_information.write(
            nft_collection, token_id, bidder, BidInfo(payment_token, price_bid, bid_expiry)
        )

        # emit events
        let (bidder) = get_caller_address()
        Bidding.emit(bidder, nft_collection, token_id, payment_token, price_bid, bid_expiry)
        return ()
    end

    func get_bade_item{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt, token_id : Uint256, bidder : felt
    ) -> (bid_info : BidInfo):
        let (bid_info) = Internal.get_bade_item(nft_collection, token_id, bidder)
        return (bid_info)
    end

    func cancel_bid{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt, token_id : Uint256
    ):
        let (bidder) = get_caller_address()

        # bid must exist
        Internal.assert_bid_exists(nft_collection, token_id, bidder)

        let payment_token = 0
        let price_bid = Uint256(0, 0)
        let bid_expiry = 0

        # write to db
        let (bidder) = get_caller_address()
        bid_information.write(
            nft_collection, token_id, bidder, BidInfo(payment_token, price_bid, bid_expiry)
        )

        # emit event
        let (bidder) = get_caller_address()
        Bidding.emit(bidder, nft_collection, token_id, payment_token, price_bid, bid_expiry)

        return ()
    end

    func accept_bid{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        nft_collection : felt,
        token_id : Uint256,
        payment_token : felt,
        minimum_price : Uint256,
        bidder : felt,
        data_len : felt,
        data : felt*,
    ):
        alloc_locals
        let (seller) = get_caller_address()

        # caller must be owner or operator(s)
        Internal.assert_token_owner_or_operator(nft_collection, token_id)

        # bid must exist
        Internal.assert_bid_exists(nft_collection, token_id, bidder)

        # bid must not expired

        # bidding price must be at least the same as minimum_price
        let (bid_info) = Internal.get_bade_item(nft_collection, token_id, bidder)
        let (is_mev_detected) = uint256_le(minimum_price, bid_info.price_bid)
        with_attr error_message("ArtpediaExchange: bid frontrunning detected"):
            assert is_mev_detected = 1
        end

        # TODO: currently handled by ERC721 transferFrom
        # exchange must be approved for ERC721 transfer

        # send ERC721 from seller(ERC721 owner) to buyer(bidder)
        # TODO: prevent reentrant
        IERC721.safeTransferFrom(
            contract_address=nft_collection,
            from_=seller,
            to=bidder,
            tokenId=token_id,
            data_len=data_len,
            data=data,
        )

        # send ERC20 from bidder to seller (ERC721 owner)
        # TODO: prevent reentrant
        send_erc20_token(payment_token, bidder, seller, minimum_price)

        # emit events
        local syscall_ptr : felt* = syscall_ptr
        let (seller) = get_caller_address()
        OrdersMatched.emit(bidder, seller, nft_collection, token_id, payment_token, minimum_price)

        return ()
    end
end
