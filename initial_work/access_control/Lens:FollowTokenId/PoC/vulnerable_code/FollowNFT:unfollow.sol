/// @inheritdoc IFollowNFT
    function unfollow(uint256 unfollowerProfileId, address transactionExecutor) external override onlyHub {
        uint256 followTokenId = _followTokenIdByFollowerProfileId[unfollowerProfileId];
        if (followTokenId == 0) {
            revert NotFollowing();
        }
        address followTokenOwner = _unsafeOwnerOf(followTokenId);
        if (followTokenOwner == address(0)) {
            // Follow token is unwrapped.
            // Unfollowing and allowing recovery.
            _unfollow({unfollower: unfollowerProfileId, followTokenId: followTokenId});
            _followDataByFollowTokenId[followTokenId].profileIdAllowedToRecover = unfollowerProfileId;
        } else {
            // Follow token is wrapped.
            address unfollowerProfileOwner = IERC721(HUB).ownerOf(unfollowerProfileId);
            // Follower profile owner or its approved delegated executor must hold the token or be approved-for-all.
            if (
                (followTokenOwner != unfollowerProfileOwner) &&
                (followTokenOwner != transactionExecutor) &&
                !isApprovedForAll(followTokenOwner, transactionExecutor) &&
                !isApprovedForAll(followTokenOwner, unfollowerProfileOwner)
            ) {
                revert DoesNotHavePermissions();
            }
            _unfollow({unfollower: unfollowerProfileId, followTokenId: followTokenId});
        }
    }