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

INITAL_SUPPLY = to_uint(20000)
AMOUNT = to_uint(1000)
AMOUNT2 = to_uint(10000)
ZERO_AMOUNT = to_uint(0)


@pytest.fixture(scope="module", autouse=True)
async def deployer():
    starknet = await Starknet.empty()

    account_def = get_contract_def("openzeppelin/account/Account.cairo")
    alice = await starknet.deploy(
        contract_def=account_def, constructor_calldata=[signer.public_key]
    )
    bob = await starknet.deploy(
        contract_def=account_def, constructor_calldata=[signer.public_key]
    )

    charlie = await starknet.deploy(
        contract_def=account_def, constructor_calldata=[signer.public_key]
    )

    erc20_def = get_contract_def("openzeppelin/token/erc20/ERC20_Mintable.cairo")
    dai = await starknet.deploy(
        contract_def=erc20_def,
        constructor_calldata=[
            str_to_felt("DAI"),
            str_to_felt("DAI"),
            18,
            *INITAL_SUPPLY,
            alice.contract_address,
            alice.contract_address,
        ],
    )

    ust = await starknet.deploy(
        contract_def=erc20_def,
        constructor_calldata=[
            str_to_felt("UST"),
            str_to_felt("UST"),
            18,
            *INITAL_SUPPLY,
            alice.contract_address,
            alice.contract_address,
        ],
    )

    erc721_def = get_contract_def(
        "openzeppelin/token/erc721/ERC721_Mintable_Burnable.cairo"
    )
    milady = await starknet.deploy(
        contract_def=erc721_def,
        constructor_calldata=[
            str_to_felt("Milady Maker"),  # name
            str_to_felt("MiladyMaker"),  # ticker
            bob.contract_address,  # owner
        ],
    )

    exchange_def = get_contract_def("exchange/Exchange.cairo")
    artpedia = await starknet.deploy(
        contract_def=exchange_def,
        constructor_calldata=[alice.contract_address, dai.contract_address],
    )

    return [starknet.state, artpedia, milady, dai, ust, alice, bob, charlie], [
        exchange_def,
        erc721_def,
        erc20_def,
        account_def,
    ]


@pytest.fixture
def factory(deployer):
    [starknet_state, artpedia, milady, dai, ust, alice, bob, charlie], [
        exchange_def,
        erc721_def,
        erc20_def,
        account_def,
    ] = deployer

    _state = starknet_state.copy()
    alice = cached_contract(_state, account_def, alice)
    bob = cached_contract(_state, account_def, bob)
    charlie = cached_contract(_state, account_def, charlie)
    artpedia = cached_contract(_state, exchange_def, artpedia)
    milady = cached_contract(_state, erc721_def, milady)
    dai = cached_contract(_state, erc20_def, dai)
    ust = cached_contract(_state, erc20_def, ust)
    return artpedia, milady, dai, ust, alice, bob, charlie


@pytest.fixture
async def milady_minted_to_bob(factory):
    artpedia, milady, dai, ust, alice, bob, charlie = factory
    for token in TOKENS:
        await signer.send_transaction(
            bob, milady.contract_address, "mint", [bob.contract_address, *token]
        )

    return artpedia, milady, dai, ust, alice, bob, charlie


@pytest.fixture
async def milady_0_is_listed_by_bob(factory):
    artpedia, milady, dai, ust, alice, bob, charlie = factory

    for token in TOKENS:
        await signer.send_transaction(
            bob, milady.contract_address, "mint", [bob.contract_address, *token]
        )

    # bob delegate TOKEN to Artpedia Exchange
    await signer.send_transaction(
        bob, milady.contract_address, "approve", [artpedia.contract_address, *TOKEN]
    )

    # list milady 0
    await signer.send_transaction(
        bob,
        artpedia.contract_address,
        "listing",
        [milady.contract_address, *TOKEN, dai.contract_address, *AMOUNT],
    )

    return artpedia, milady, dai, ust, alice, bob, charlie


@pytest.fixture
async def send_dai_to_bob_and_charlie(milady_0_is_listed_by_bob):
    artpedia, milady, dai, ust, alice, bob, charlie = milady_0_is_listed_by_bob

    # send to bob
    await signer.send_transaction(
        alice,
        dai.contract_address,
        "transfer",
        [
            bob.contract_address,
            *AMOUNT2,
        ],
    )

    # send to charlie
    await signer.send_transaction(
        alice,
        dai.contract_address,
        "transfer",
        [
            charlie.contract_address,
            *AMOUNT2,
        ],
    )

    return artpedia, milady, dai, ust, alice, bob, charlie


# @pytest.fixture(autouse=True)
# def isolation(fn_isolation):
#     pass
