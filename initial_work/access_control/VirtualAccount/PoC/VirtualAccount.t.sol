//SPDX-License-Identifier: AGPL-3.0-only
pragma solidity ^0.8.0;

import {VirtualAccount} from "@omni/VirtualAccount.sol";
import {PayableCall} from "@omni/interfaces/IVirtualAccount.sol";

import {ERC20} from "solmate/tokens/ERC20.sol";

import "./helpers/ImportHelper.sol";


contract VirtualAccountTest is Test {

    address public alice;
    address public bob;

    VirtualAccount public vAcc;

    function setUp() public {
        alice = makeAddr("Alice");
        bob = makeAddr("Bob");

        // create new VirtualAccount for user Alice and this test contract as mock local port
        vAcc = new VirtualAccount(alice, address(this));
    }

    function testWithdrawERC20_AliceSuccess() public {
        vm.prank(alice);
        vAcc.withdrawERC20(address(this), 1); // caller is authorized
    }

    function testWithdrawERC20_BobFailure() public {
        vm.prank(bob);
        vm.expectRevert();
        vAcc.withdrawERC20(address(this), 1); // caller is not authorized
    }

    function testWithdrawERC20_BobBypassSuccess() public {
        PayableCall[] memory calls = new PayableCall[](1);
        calls[0].target = address(this);
        calls[0].callData = abi.encodeCall(ERC20.transfer, (bob, 1));

        vm.prank(bob);
        vAcc.payableCall(calls); // caller is not authorized but it does't matter
    }


    // mock VirtualAccount call to local port
    function isRouterApproved(VirtualAccount _userAccount, address _router) external returns (bool) {
        return false;
    }
    
    // mock ERC20 token transfer
    function transfer(address to, uint256 value) external returns (bool) {
        console2.log("Transferred %s from %s to %s", value, msg.sender, to);
        return true;
    }
}