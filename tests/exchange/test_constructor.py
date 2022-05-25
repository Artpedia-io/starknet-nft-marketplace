import pytest
from utils import to_uint


@pytest.mark.asyncio
async def test_constructor(factory):
    artpedia, tubbycats, dai, ust, alice, bob, charlie = factory
    dai_response = await artpedia.check_approved_tokens_as_payment(
        dai.contract_address
    ).invoke()
    assert dai_response.result.is_approved == 1

    ust_response = await artpedia.check_approved_tokens_as_payment(
        ust.contract_address
    ).invoke()
    assert ust_response.result.is_approved == 0
    import pdb

    pdb.set_trace()

    response = await artpedia.check_platform_fee().invoke()
    assert response.result.platform_fee == to_uint(2)
    assert response.result.decimals == to_uint(100)

    admin_response = await artpedia.get_admin().invoke()
    assert admin_response.result.admin == alice.contract_address
