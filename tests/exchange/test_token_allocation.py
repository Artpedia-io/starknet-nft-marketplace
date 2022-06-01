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
async def test_token_allocation_50_wei(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory
    listing_price = to_uint(49)
    response = await artpedia.get_token_allocation(listing_price).invoke()
    assert response.result.platform_allocation == to_uint(0)
    assert response.result.seller_allocation == to_uint(49)


@pytest.mark.asyncio
async def test_token_allocation_50_wei(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory
    listing_price = to_uint(50)
    response = await artpedia.get_token_allocation(listing_price).invoke()
    assert response.result.platform_allocation == to_uint(1)
    assert response.result.seller_allocation == to_uint(49)


@pytest.mark.asyncio
async def test_token_allocation_100_wei(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory
    listing_price = to_uint(100)
    response = await artpedia.get_token_allocation(listing_price).invoke()
    assert response.result.platform_allocation == to_uint(2)
    assert response.result.seller_allocation == to_uint(98)


@pytest.mark.asyncio
async def test_token_allocation_1000_wei(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory
    listing_price = to_uint(1000)
    response = await artpedia.get_token_allocation(listing_price).invoke()
    assert response.result.platform_allocation == to_uint(20)
    assert response.result.seller_allocation == to_uint(980)


@pytest.mark.asyncio
async def test_token_allocation_zero_point_1_eth(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory
    listing_price = to_uint(int(ETH_TO_WEI))
    response = await artpedia.get_token_allocation(listing_price).invoke()
    assert response.result.platform_allocation == to_uint(int(2 * 1e16))
    assert response.result.seller_allocation == to_uint(int(98 * 1e16))


@pytest.mark.asyncio
async def test_token_allocation_10_eth(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory
    listing_price = to_uint(int(ETH_TO_WEI * 10))
    response = await artpedia.get_token_allocation(listing_price).invoke()
    assert response.result.platform_allocation == to_uint(int(2 * 1e17))
    assert response.result.seller_allocation == to_uint(int(98 * 1e17))


@pytest.mark.asyncio
async def test_token_allocation_100_eth(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory
    listing_price = to_uint(int(ETH_TO_WEI * 100))
    response = await artpedia.get_token_allocation(listing_price).invoke()
    assert response.result.platform_allocation == to_uint(int(2 * 1e18))
    assert response.result.seller_allocation == to_uint(int(98 * 1e18))


@pytest.mark.asyncio
async def test_token_allocation_1000_eth(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory
    listing_price = to_uint(int(ETH_TO_WEI * 1000))
    response = await artpedia.get_token_allocation(listing_price).invoke()
    assert response.result.platform_allocation == to_uint(int(2 * 1e19))
    assert response.result.seller_allocation == to_uint(int(98 * 1e19))
