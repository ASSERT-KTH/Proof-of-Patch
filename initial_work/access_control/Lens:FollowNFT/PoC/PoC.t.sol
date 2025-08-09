// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import 'test/base/BaseTest.t.sol';

contract Unfollow_POC is BaseTest {
    address targetProfileOwner;
    uint256 targetProfileId;
    FollowNFT targetFollowNFT;

    address follower;
    uint256 followerProfileId;
    uint256 followTokenId;

    function setUp() public override {
        super.setUp();

        // Create profile for target
        targetProfileOwner = makeAddr("Target");
        targetProfileId = _createProfile(targetProfileOwner);

        // Create profile for follower
        follower = makeAddr("Follower");
        followerProfileId = _createProfile(follower);

        // Follower follows target
        vm.prank(follower);
        followTokenId = hub.follow(
            followerProfileId,
            _toUint256Array(targetProfileId),
            _toUint256Array(0),
            _toBytesArray('')
        )[0];
        targetFollowNFT = FollowNFT(hub.getProfile(targetProfileId).followNFT);
    }

    function testCanUnfollowWhilePaused() public {
        // Governance pauses system
        vm.prank(governance);
        hub.setState(Types.ProtocolState.Paused);
        assertEq(uint8(hub.getState()), uint8(Types.ProtocolState.Paused));

        // unfollow() reverts as system is paused
        vm.startPrank(follower);
        vm.expectRevert(Errors.Paused.selector);
        hub.unfollow(followerProfileId, _toUint256Array(targetProfileId));

        // However, follower can still unfollow through FollowNFT contract 
        targetFollowNFT.wrap(followTokenId);
        targetFollowNFT.removeFollower(followTokenId);        
        vm.stopPrank();

        // follower isn't following anymore
        assertFalse(targetFollowNFT.isFollowing(followerProfileId));
    }
}