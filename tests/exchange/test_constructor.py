import pytest
from utils import to_uint


@pytest.mark.asyncio
async def test_constructor(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory
    dai_response = await artpedia.is_approved_token_as_payment(
        dai.contract_address
    ).invoke()
    assert dai_response.result.is_approved == 1

    ust_response = await artpedia.is_approved_token_as_payment(
        ust.contract_address
    ).invoke()
    assert ust_response.result.is_approved == 0

    response = await artpedia.get_platform_fee().invoke()
    assert response.result.platform_fee == to_uint(2000)
    assert response.result.multiplier == to_uint(1000)

    response = await artpedia.get_treasury_address().invoke()
    assert response.result.treasury_address == alice.contract_address

    admin_response = await artpedia.get_admin().invoke()
    assert admin_response.result.admin == alice.contract_address
