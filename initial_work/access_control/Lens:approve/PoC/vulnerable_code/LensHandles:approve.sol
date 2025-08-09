    function approve(address to, uint256 tokenId) public override(IERC721, ERC721) {
        // We allow removing approvals even if the wallet has the token guardian enabled
        if (to != address(0) && _hasTokenGuardianEnabled(msg.sender)) {
            revert HandlesErrors.GuardianEnabled();
        }
        super.approve(to, tokenId);
    }