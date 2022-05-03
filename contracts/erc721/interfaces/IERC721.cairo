%lang starknet

from starkware.cairo.common.uint256 import Uint256

@contract_interface
namespace IERC721:
    func ownerOf(_tokenId : Uit256) -> (owner : felt):
    end

    func transferFrom(_from : felt, _to : felt, tokenId : Uint256) -> (success : felt):
    end

    func safeTransferFrom(
        _from : felt, _to : felt, tokenId : Uint256, data_len : felt, data : felt*
    ) -> (success : felt):
    end

    func approve(approved : felt, tokenId : Uint256):
    end

    func setApprovalForAll(operator : felt, approved : felt):
    end

    func getApproved(approved : felt, tokenId : Uint256) -> (approved : felt):
    end

    func isApprovedForAll(owner : felt, operator : felt) -> (isApproved : felt):
    end
end
