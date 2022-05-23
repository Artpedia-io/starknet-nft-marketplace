import pytest
from starkware.starknet.testing.starknet import Starknet
from utils import (
    Signer,
    str_to_felt,
    ZERO_ADDRESS,
    TRUE,
    FALSE,
    assert_revert,
    INVALID_UINT256,
    assert_event_emitted,
    get_contract_def,
    cached_contract,
    to_uint,
    sub_uint,
    add_uint,
)


signer = Signer(123456789987654321)

NONEXISTENT_TOKEN = to_uint(999)
# random token IDs
TOKENS = [to_uint(5042), to_uint(793)]
# test token
TOKEN = TOKENS[0]
# test token 1
TOKEN1 = TOKENS[1]
# random user address
RECIPIENT = 555
# random data (mimicking bytes in Solidity)
DATA = [0x42, 0x89, 0x55]
# random URIs
SAMPLE_URI_1 = str_to_felt("mock://mytoken.v1")
SAMPLE_URI_2 = str_to_felt("mock://mytoken.v2")

# selector ids
IERC165_ID = 0x01FFC9A7
IERC721_ID = 0x80AC58CD
IERC721_METADATA_ID = 0x5B5E139F
INVALID_ID = 0xFFFFFFFF
UNSUPPORTED_ID = 0xABCD1234

INITAL_SUPPLY = to_uint(1000)
AMOUNT = to_uint(1000)
AMOUNT2 = to_uint(10000)
ZERO_AMOUNT = to_uint(0)


@pytest.mark.asyncio
async def test_positive_delist_item_by_owner(milady_0_is_listed_by_bob):
    artpedia, milady, dai, ust, alice, bob, charlie = milady_0_is_listed_by_bob
    tx_exec_info = await signer.send_transaction(
        bob, artpedia.contract_address, "delisting", [milady.contract_address, *TOKEN]
    )
    response = await artpedia.check_listed_items(
        milady.contract_address, TOKEN
    ).invoke()
    assert response.result.is_on_sale == 0
    assert response.result.payment_token == 0
    assert response.result.listing_price == ZERO_AMOUNT

    assert_event_emitted(
        tx_exec_info=tx_exec_info,
        from_address=artpedia.contract_address,
        name="Listing",
        data=[bob.contract_address, milady.contract_address, *TOKEN, 0, *ZERO_AMOUNT],
    )


@pytest.mark.asyncio
async def test_positive_delist_item_by_operator(milady_0_is_listed_by_bob):
    artpedia, milady, dai, ust, alice, bob, charlie = milady_0_is_listed_by_bob

    # delegate bob's token to charlie
    await signer.send_transaction(
        bob,
        milady.contract_address,
        "setApprovalForAll",
        [charlie.contract_address, TRUE],
    )

    tx_exec_info = await signer.send_transaction(
        charlie,
        artpedia.contract_address,
        "delisting",
        [milady.contract_address, *TOKEN],
    )

    response = await artpedia.check_listed_items(
        milady.contract_address, TOKEN
    ).invoke()
    assert response.result.is_on_sale == 0
    assert response.result.payment_token == 0
    assert response.result.listing_price == ZERO_AMOUNT

    assert_event_emitted(
        tx_exec_info=tx_exec_info,
        from_address=artpedia.contract_address,
        name="Listing",
        data=[
            charlie.contract_address,
            milady.contract_address,
            *TOKEN,
            0,
            *ZERO_AMOUNT,
        ],
    )


@pytest.mark.asyncio
async def test_delist_by_non_operator(milady_0_is_listed_by_bob):
    artpedia, milady, dai, ust, alice, bob, charlie = milady_0_is_listed_by_bob

    await assert_revert(
        signer.send_transaction(
            alice,
            artpedia.contract_address,
            "delisting",
            [milady.contract_address, *TOKEN],
        ),
        reverted_with="ArtpediaExchange: caller is not owner nor approved(including operators)",
    )

    await assert_revert(
        signer.send_transaction(
            charlie,
            artpedia.contract_address,
            "delisting",
            [milady.contract_address, *TOKEN],
        ),
        reverted_with="ArtpediaExchange: caller is not owner nor approved(including operators)",
    )


@pytest.mark.asyncio
async def test_negative_delist_unlisted_item(milady_minted_to_bob):
    artpedia, milady, dai, ust, alice, bob, charlie = milady_minted_to_bob

    await assert_revert(
        signer.send_transaction(
            bob,
            artpedia.contract_address,
            "delisting",
            [milady.contract_address, *TOKEN],
        ),
        reverted_with="ArtpediaExchange: item not listed",
    )
