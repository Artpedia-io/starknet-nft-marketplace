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

TOKENS_BOB = [to_uint(5042), to_uint(793)]
TOKENS_CHARLIE = [to_uint(0), to_uint(1)]

SECONDS_IN_DAY = 86400
QUARTER_HOUR = int(SECONDS_IN_DAY / 24 / 4)


@pytest.mark.asyncio
async def test_positive_cancel_by_bidder(send_dai_to_bob_and_charlie):
    """
    5042 is listed by bob
    793 is minted to bob
    0 is minted to charlie
    1 is minted to charlie
    """
    artpedia, tubbycats, dai, ust, alice, bob, charlie = send_dai_to_bob_and_charlie

    AMOUNT = to_uint(10000)

    token_id = TOKENS_BOB[0]

    await signer.send_transaction(
        charlie, dai.contract_address, "approve", [artpedia.contract_address, *AMOUNT]
    )

    await signer.send_transaction(
        charlie,
        artpedia.contract_address,
        "bid",
        [
            tubbycats.contract_address,
            *token_id,
            dai.contract_address,
            *AMOUNT,
            QUARTER_HOUR,
        ],
    )

    response = await signer.send_transaction(
        charlie,
        artpedia.contract_address,
        "cancel_bid",
        [tubbycats.contract_address, *token_id],
    )

    assert_event_emitted(
        response,
        from_address=artpedia.contract_address,
        name="Bidding",
        data=[
            charlie.contract_address,
            tubbycats.contract_address,
            *token_id,
            0,
            *ZERO_AMOUNT,
            0,
        ],
    )

    response = await artpedia.get_bade_item(
        tubbycats.contract_address, token_id, charlie.contract_address
    ).invoke()

    assert response.result.payment_token == 0
    assert response.result.price_bid == ZERO_AMOUNT
    assert response.result.expire_time == 0


@pytest.mark.asyncio
async def test_negative_no_bid_for_this_item(send_dai_to_bob_and_charlie):
    """
    5042 is listed by bob
    793 is minted to bob
    0 is minted to charlie
    1 is minted to charlie
    """
    artpedia, tubbycats, dai, ust, alice, bob, charlie = send_dai_to_bob_and_charlie

    AMOUNT = to_uint(10000)

    token_id = TOKENS_BOB[0]

    await signer.send_transaction(
        charlie, dai.contract_address, "approve", [artpedia.contract_address, *AMOUNT]
    )

    await assert_revert(
        signer.send_transaction(
            charlie,
            artpedia.contract_address,
            "cancel_bid",
            [tubbycats.contract_address, *token_id],
        ),
        reverted_with="ArtpediaExchange: no bid for this token_id",
    )


@pytest.mark.asyncio
async def test_negative_caller_is_not_bidder(send_dai_to_bob_and_charlie):
    """
    5042 is listed by bob
    793 is minted to bob
    0 is minted to charlie
    1 is minted to charlie
    """
    artpedia, tubbycats, dai, ust, alice, bob, charlie = send_dai_to_bob_and_charlie

    AMOUNT = to_uint(10000)

    token_id = TOKENS_BOB[0]

    await signer.send_transaction(
        charlie, dai.contract_address, "approve", [artpedia.contract_address, *AMOUNT]
    )

    await signer.send_transaction(
        charlie,
        artpedia.contract_address,
        "bid",
        [
            tubbycats.contract_address,
            *token_id,
            dai.contract_address,
            *AMOUNT,
            QUARTER_HOUR,
        ],
    )

    await assert_revert(
        signer.send_transaction(
            alice,
            artpedia.contract_address,
            "cancel_bid",
            [tubbycats.contract_address, *token_id],
        ),
        reverted_with="ArtpediaExchange: no bid for this token_id",
    )
