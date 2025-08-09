    function removeFollower(uint256 followTokenId) external override {
        address followTokenOwner = ownerOf(followTokenId);
        if (followTokenOwner == msg.sender || isApprovedForAll(followTokenOwner, msg.sender)) {
            _unfollowIfHasFollower(followTokenId);
        } else {
            revert DoesNotHavePermissions();
        }
    }