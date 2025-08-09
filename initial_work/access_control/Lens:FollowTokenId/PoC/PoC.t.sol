// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import 'test/base/BaseTest.t.sol';
import 'contracts/interfaces/IFollowNFT.sol';

contract Unfollow_POC is BaseTest {
    address targetProfileOwner;
    address ALICE;
    address BOB;

    uint256 targetProfileId;
    uint256 aliceProfileId;
    uint256 bobProfileId;

    function setUp() public override {
        super.setUp();

        // Setup addresses for target, Alice and Bob
        targetProfileOwner = makeAddr("Target");
        ALICE = makeAddr("Alice");
        BOB = makeAddr("Bob");

        // Create profile for target, Alice and Bob 
        targetProfileId = _createProfile(targetProfileOwner);
        aliceProfileId = _createProfile(ALICE);
        bobProfileId = _createProfile(BOB);
    }

    function testCannotUnfollowWithoutFollowNFT() public {
        // Alice follows target
        vm.startPrank(ALICE);
        uint256 followTokenId = hub.follow(
            aliceProfileId,
            _toUint256Array(targetProfileId),
            _toUint256Array(0),
            _toBytesArray('')
        )[0];

        // Get followNFT contract created
        FollowNFT followNFT = FollowNFT(hub.getProfile(targetProfileId).followNFT);

        // Alice lets Bob follow using her followTokenId
        followNFT.wrap(followTokenId);
        followNFT.approveFollow(bobProfileId, followTokenId);
        vm.stopPrank();

        // Bob follows using her followTokenId        
        vm.startPrank(BOB);
        hub.follow(
            bobProfileId,
            _toUint256Array(targetProfileId),
            _toUint256Array(followTokenId),
            _toBytesArray('')
        );
        assertTrue(followNFT.isFollowing(bobProfileId));

        // After a while, Bob wants to unfollow. 
        // However, unfollow() reverts as he doesn't own the followNFT
        vm.expectRevert(IFollowNFT.DoesNotHavePermissions.selector);
        hub.unfollow(bobProfileId, _toUint256Array(targetProfileId));
        vm.stopPrank();
    }
}