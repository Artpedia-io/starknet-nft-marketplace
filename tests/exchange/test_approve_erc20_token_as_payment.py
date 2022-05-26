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
async def test_remove_approved_tokens_by_admin(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory
    response = await signer.send_transaction(
        alice,
        artpedia.contract_address,
        "approve_token_as_payment",
        [dai.contract_address, 0],
    )

    assert_event_emitted(
        response,
        from_address=artpedia.contract_address,
        name="ApproveTokenAsPayment",
        data=[dai.contract_address, 0],
    )

    response = await artpedia.is_approved_token_as_payment(
        dai.contract_address
    ).invoke()
    assert response.result.is_approved == 0


@pytest.mark.asyncio
async def test_positive_add_approval_to_new_erc20_token_by_admin(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory
    response = await signer.send_transaction(
        alice,
        artpedia.contract_address,
        "approve_token_as_payment",
        [ust.contract_address, 1],
    )

    assert_event_emitted(
        response,
        from_address=artpedia.contract_address,
        name="ApproveTokenAsPayment",
        data=[ust.contract_address, 1],
    )

    response = await artpedia.is_approved_token_as_payment(
        ust.contract_address
    ).invoke()
    assert response.result.is_approved == 1


@pytest.mark.asyncio
async def test_negative_remove_approved_tokens_by_non_admin(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory

    await assert_revert(
        signer.send_transaction(
            bob,
            artpedia.contract_address,
            "approve_token_as_payment",
            [dai.contract_address, 0],
        ),
        reverted_with="Ownable: caller is not the owner",
    )


@pytest.mark.asyncio
async def test_negative_approve_token_token_have_the_same_approval(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory
    await assert_revert(
        signer.send_transaction(
            alice,
            artpedia.contract_address,
            "approve_token_as_payment",
            [dai.contract_address, 1],
        ),
        reverted_with="ArtpediaExchange: ERC-20 token already has the same approval",
    )

    await assert_revert(
        signer.send_transaction(
            alice,
            artpedia.contract_address,
            "approve_token_as_payment",
            [ust.contract_address, 0],
        ),
        reverted_with="ArtpediaExchange: ERC-20 token already has the same approval",
    )
