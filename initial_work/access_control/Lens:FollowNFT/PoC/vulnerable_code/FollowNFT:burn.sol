    function burn(uint256 followTokenId) public override {
        _unfollowIfHasFollower(followTokenId);
        super.burn(followTokenId);
    }