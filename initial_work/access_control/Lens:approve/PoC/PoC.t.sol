// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import 'forge-std/Test.sol';
import '../contracts/namespaces/LensHandles.sol';

contract TokenGuardian_POC is Test {
    LensHandles lensHandles;

    address ALICE;
    address BOB;
    uint256 tokenId;

    function setUp() public {
        // Setup LensHandles contract
        lensHandles = new LensHandles(address(this), address(0), 0);

        // Setup Alice and Bob addresses
        ALICE = makeAddr("Alice");
        BOB = makeAddr("Bob");

        // Mint "alice.lens" to Alice
        tokenId = lensHandles.mintHandle(ALICE, "alice");
    }
    
    function testCanApproveWhileTokenGuardianEnabled() public {
        // Alice disables tokenGuardian to set Bob as an approved operator
        vm.startPrank(ALICE);
        lensHandles.DANGER__disableTokenGuardian();
        lensHandles.setApprovalForAll(BOB, true);

        // Alice re-enables tokenGuardian
        lensHandles.enableTokenGuardian();
        vm.stopPrank();

        // Bob disables tokenGuardian for himself
        vm.startPrank(BOB);
        lensHandles.DANGER__disableTokenGuardian();

        // Alice still has tokenGuardian enabled
        assertEq(lensHandles.getTokenGuardianDisablingTimestamp(ALICE), 0);

        // However, Bob can still set approvals for Alice's handle
        lensHandles.approve(address(0x1337), tokenId);
        vm.stopPrank();
        assertEq(lensHandles.getApproved(tokenId), address(0x1337));
    }
}