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
async def test_positive_listing_by_owner(milady_minted_to_bob):
    artpedia, milady, dai, ust, alice, bob, charlie = milady_minted_to_bob

    response = await artpedia.check_listed_items(
        milady.contract_address, TOKEN
    ).invoke()
    assert response.result.is_on_sale == 0
    assert response.result.payment_token == 0
    assert response.result.listing_price == ZERO_AMOUNT

    for token in TOKENS:
        response = await milady.ownerOf(token).invoke()
        assert response.result == (bob.contract_address,)

    # bob delegate TOKEN to Artpedia Exchange
    await signer.send_transaction(
        bob, milady.contract_address, "approve", [artpedia.contract_address, *TOKEN]
    )

    # execute listing transaction
    response = await signer.send_transaction(
        bob,
        artpedia.contract_address,
        "listing",
        [milady.contract_address, *TOKEN, dai.contract_address, *AMOUNT],
    )

    # check
    assert_event_emitted(
        response,
        from_address=artpedia.contract_address,
        name="Listing",
        data=[
            bob.contract_address,
            milady.contract_address,
            *TOKEN,
            dai.contract_address,
            *AMOUNT,
        ],
    )

    response = await artpedia.check_listed_items(
        milady.contract_address, TOKEN
    ).invoke()
    assert response.result.is_on_sale == 1
    assert response.result.payment_token == dai.contract_address
    assert response.result.listing_price == AMOUNT


@pytest.mark.asyncio
async def test_positive_listing_by_operator(milady_minted_to_bob):
    artpedia, milady, dai, ust, alice, bob, charlie = milady_minted_to_bob

    response = await artpedia.check_listed_items(
        milady.contract_address, TOKEN
    ).invoke()
    assert response.result.is_on_sale == 0
    assert response.result.payment_token == 0
    assert response.result.listing_price == ZERO_AMOUNT

    for token in TOKENS:
        response = await milady.ownerOf(token).invoke()
        assert response.result == (bob.contract_address,)

    # delegate bob's token to charlie
    await signer.send_transaction(
        bob,
        milady.contract_address,
        "setApprovalForAll",
        [charlie.contract_address, TRUE],
    )

    # charlie delegate TOKEN to Artpedia Exchange
    await signer.send_transaction(
        charlie, milady.contract_address, "approve", [artpedia.contract_address, *TOKEN]
    )

    # execute listing transaction
    response = await signer.send_transaction(
        charlie,
        artpedia.contract_address,
        "listing",
        [milady.contract_address, *TOKEN, dai.contract_address, *AMOUNT],
    )

    # check
    assert_event_emitted(
        response,
        from_address=artpedia.contract_address,
        name="Listing",
        data=[
            charlie.contract_address,
            milady.contract_address,
            *TOKEN,
            dai.contract_address,
            *AMOUNT,
        ],
    )

    response = await artpedia.check_listed_items(
        milady.contract_address, TOKEN
    ).invoke()
    assert response.result.is_on_sale == 1
    assert response.result.payment_token == dai.contract_address
    assert response.result.listing_price == AMOUNT


@pytest.mark.asyncio
async def test_negative_listing_listed_item(milady_0_is_listed_by_bob):
    artpedia, milady, dai, ust, alice, bob, charlie = milady_0_is_listed_by_bob

    response = await artpedia.check_listed_items(
        milady.contract_address, TOKEN
    ).invoke()
    assert response.result.is_on_sale == 1
    assert response.result.payment_token == dai.contract_address
    assert response.result.listing_price == AMOUNT

    await assert_revert(
        signer.send_transaction(
            bob,
            artpedia.contract_address,
            "listing",
            [milady.contract_address, *TOKEN, dai.contract_address, *AMOUNT2],
        ),
        reverted_with="ArtpediaExchange: item already listed",
    )


@pytest.mark.asyncio
async def test_negative_listing_without_approval(milady_minted_to_bob):
    artpedia, milady, dai, ust, alice, bob, charlie = milady_minted_to_bob

    await assert_revert(
        signer.send_transaction(
            bob,
            artpedia.contract_address,
            "listing",
            [milady.contract_address, *TOKEN, dai.contract_address, *AMOUNT],
        ),
        reverted_with="ArtpediaExchange: exchange is not approved yet",
    )
