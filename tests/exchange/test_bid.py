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


@pytest.mark.asyncio
async def test_positive_maxbid_listed_item(send_dai_to_bob_and_charlie):
    """
    5042 is listed by bob
    793 is minted to bob
    0 is minted to charlie
    1 is minted to charlie
    """
    artpedia, tubbycats, dai, ust, alice, bob, charlie = send_dai_to_bob_and_charlie

    AMOUNT = to_uint(10000)

    await signer.send_transaction(
        charlie, dai.contract_address, "approve", [artpedia.contract_address, *AMOUNT]
    )

    response = await signer.send_transaction(
        charlie,
        artpedia.contract_address,
        "bid",
        [tubbycats.contract_address, *TOKENS_BOB[0], dai.contract_address, *AMOUNT],
    )

    assert_event_emitted(
        response,
        from_address=artpedia.contract_address,
        name="Bidding",
        data=[
            charlie.contract_address,
            tubbycats.contract_address,
            *TOKENS_BOB[0],
            dai.contract_address,
            *AMOUNT,
            0,
        ],
    )


@pytest.mark.asyncio
async def test_negative_bid_zero_price(send_dai_to_bob_and_charlie):
    """
    5042 is listed by bob
    793 is minted to bob
    0 is minted to charlie
    1 is minted to charlie
    """
    artpedia, tubbycats, dai, ust, alice, bob, charlie = send_dai_to_bob_and_charlie

    await assert_revert(
        signer.send_transaction(
            charlie,
            artpedia.contract_address,
            "bid",
            [
                tubbycats.contract_address,
                *TOKENS_BOB[0],
                dai.contract_address,
                *ZERO_AMOUNT,
            ],
        ),
        reverted_with="ArtpediaExchange: amount must be more than zero",
    )


@pytest.mark.asyncio
async def test_negative_owner_have_insufficient_erc20_token(
    send_dai_to_bob_and_charlie,
):
    """
    5042 is listed by bob
    793 is minted to bob
    0 is minted to charlie
    1 is minted to charlie
    """
    artpedia, tubbycats, dai, ust, alice, bob, charlie = send_dai_to_bob_and_charlie

    AMOUNT = to_uint(10001)

    await assert_revert(
        signer.send_transaction(
            charlie,
            artpedia.contract_address,
            "bid",
            [
                tubbycats.contract_address,
                *TOKENS_BOB[0],
                dai.contract_address,
                *AMOUNT,
            ],
        ),
        reverted_with="ArtpediaExchange: buyer does not have enough ERC-20 Tokens",
    )


@pytest.mark.asyncio
async def test_negative_owner_have_insufficient_erc20_allowance(
    send_dai_to_bob_and_charlie,
):
    """
    5042 is listed by bob
    793 is minted to bob
    0 is minted to charlie
    1 is minted to charlie
    """
    artpedia, tubbycats, dai, ust, alice, bob, charlie = send_dai_to_bob_and_charlie

    AMOUNT = to_uint(10000)

    await assert_revert(
        signer.send_transaction(
            charlie,
            artpedia.contract_address,
            "bid",
            [
                tubbycats.contract_address,
                *TOKENS_BOB[0],
                dai.contract_address,
                *AMOUNT,
            ],
        ),
        reverted_with="ArtpediaExchange: insufficient allowance",
    )
