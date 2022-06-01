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
DATA = []
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
INITIAL_BALANCE = to_uint(10000)
ZERO_AMOUNT = to_uint(0)
ETH_TO_WEI = 1e18


@pytest.mark.asyncio
async def test_negative_buyer_is_owner(tubbycats_0_is_listed_by_bob):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = tubbycats_0_is_listed_by_bob

    await assert_revert(
        signer.send_transaction(
            bob,
            artpedia.contract_address,
            "buy",
            [tubbycats.contract_address, *TOKEN, len(DATA), *DATA],
        ),
        reverted_with="ArtpediaExchange: caller is ERC-721 owner",
    )


@pytest.mark.asyncio
async def test_negative_buy_unlisted_item(tubbycats_0_is_listed_by_bob):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = tubbycats_0_is_listed_by_bob

    await assert_revert(
        signer.send_transaction(
            charlie,
            artpedia.contract_address,
            "buy",
            [tubbycats.contract_address, *TOKEN1, len(DATA), *DATA],
        ),
        reverted_with="ArtpediaExchange: item not listed",
    )


@pytest.mark.asyncio
async def test_negative_insufficient_allowance_while_buying(
    send_dai_to_bob_and_charlie,
):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = send_dai_to_bob_and_charlie
    await assert_revert(
        signer.send_transaction(
            charlie,
            artpedia.contract_address,
            "buy",
            [tubbycats.contract_address, *TOKEN, len(DATA), *DATA],
        ),
        reverted_with="ERC20: insufficient allowance",
    )


@pytest.mark.asyncio
async def test_negative_not_enough_balance_while_buying(send_dai_to_bob_and_charlie):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = send_dai_to_bob_and_charlie

    await signer.send_transaction(
        alice,
        dai.contract_address,
        "approve",
        [artpedia.contract_address, *INITIAL_BALANCE],
    )

    await assert_revert(
        signer.send_transaction(
            alice,
            artpedia.contract_address,
            "buy",
            [tubbycats.contract_address, *TOKEN, len(DATA), *DATA],
        ),
        reverted_with="ERC20: transfer amount exceeds balance",
    )


@pytest.mark.asyncio
async def test_positive_buy_1000_wei(send_dai_to_bob_and_charlie):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = send_dai_to_bob_and_charlie

    response = await tubbycats.ownerOf(TOKEN).invoke()
    assert response.result == (bob.contract_address,)

    response = await dai.balanceOf(alice.contract_address).invoke()
    assert response.result.balance == ZERO_AMOUNT

    response = await dai.balanceOf(bob.contract_address).invoke()
    assert response.result.balance == INITIAL_BALANCE

    response = await dai.balanceOf(charlie.contract_address).invoke()
    assert response.result.balance == INITIAL_BALANCE

    # delegate artpedia with buyer's ERC20 token
    await signer.send_transaction(
        charlie,
        dai.contract_address,
        "approve",
        [artpedia.contract_address, *INITIAL_BALANCE],
    )

    response = await dai.allowance(
        charlie.contract_address, artpedia.contract_address
    ).invoke()

    assert response.result.remaining == INITIAL_BALANCE

    response_buy = await signer.send_transaction(
        charlie,
        artpedia.contract_address,
        "buy",
        [tubbycats.contract_address, *TOKEN, len(DATA), *DATA],
    )

    assert_event_emitted(
        response_buy,
        from_address=artpedia.contract_address,
        name="OrdersMatched",
        data=[
            charlie.contract_address,
            bob.contract_address,
            tubbycats.contract_address,
            *TOKEN,
            dai.contract_address,
            *AMOUNT,
        ],
    )

    response = await tubbycats.ownerOf(TOKEN).invoke()
    assert response.result == (charlie.contract_address,)

    response = await dai.balanceOf(charlie.contract_address).invoke()
    assert response.result.balance == to_uint(9000)

    response = await dai.balanceOf(bob.contract_address).invoke()
    assert response.result.balance == to_uint(10980)

    response = await dai.balanceOf(alice.contract_address).invoke()
    assert response.result.balance == to_uint(20)
