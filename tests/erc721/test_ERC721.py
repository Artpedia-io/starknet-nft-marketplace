import pytest
from starkware.starknet.testing.starknet import Starknet
from utils import Signer, get_contract_def, str_to_felt, cached_contract, to_uint

signer = Signer(123456789987654321)


# testing vars
NAME = str_to_felt("ERC721Demo")
SYMBOL = str_to_felt("ART")
TOKEN_ID = to_uint(0)


@pytest.fixture(scope="module")
async def erc721():
    erc721_def = get_contract_def("erc721/ERC721.cairo")
    starknet = await Starknet.empty()
    erc721 = await starknet.deploy(
        contract_def=erc721_def, constructor_calldata=[NAME, SYMBOL]
    )
    return erc721


@pytest.fixture(scope="module")
async def alice():
    account_def = get_contract_def("account/Account.cairo")
    starknet = await Starknet.empty()
    alice = await starknet.deploy(
        contract_def=account_def, constructor_calldata=[signer.public_key]
    )
    return alice


@pytest.fixture(scope="module")
async def bob():
    account_def = get_contract_def("account/Account.cairo")
    starknet = await Starknet.empty()
    bob = await starknet.deploy(
        contract_def=account_def, constructor_calldata=[signer.public_key]
    )
    return bob


@pytest.mark.asyncio
async def test_constructor(erc721):
    execution_info = await erc721.name().invoke()
    assert execution_info.result.name == NAME

    execution_info = await erc721.symbol().invoke()
    assert execution_info.result.symbol == SYMBOL


@pytest.mark.asyncio
async def test_minting(erc721, alice):
    await erc721.mint(alice.contract_address, TOKEN_ID).invoke()
    execution_info = await erc721.ownerOf(TOKEN_ID).invoke()
    assert execution_info.result.owner == alice.contract_address
