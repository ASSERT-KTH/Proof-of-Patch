// SPDX-License-Identifier: BUSL 1.1
pragma solidity =0.8.22;

import "../../dev/Deployment.sol";
import "./TestCallReceiver.sol";


contract TestDAO is Deployment
	{
	// User wallets for testing
    address public constant alice = address(0x1111);
    address public constant bob = address(0x2222);


	constructor()
		{
		// If $COVERAGE=yes, create an instance of the contract so that coverage testing can work
		// Otherwise, what is tested is the actual deployed contract on the blockchain (as specified in Deployment.sol)
		if ( keccak256(bytes(vm.envString("COVERAGE" ))) == keccak256(bytes("yes" )))
			initializeContracts();

		grantAccessAlice();
		grantAccessBob();
		grantAccessCharlie();
		grantAccessDeployer();
		grantAccessDefault();

		finalizeBootstrap();

		vm.prank(address(daoVestingWallet));
		salt.transfer(DEPLOYER, 15000000 ether);

		// Mint some USDS to the DEPLOYER and alice
		vm.startPrank( address(collateralAndLiquidity) );
		usds.mintTo( DEPLOYER, 2000000 ether );
		usds.mintTo( alice, 1000000 ether );
		vm.stopPrank();

		vm.prank( DEPLOYER );
		salt.transfer( alice, 10000000 ether );

		// Allow time for proposals
		vm.warp( block.timestamp + 45 days );
		}


    function setUp() public
    	{
    	vm.startPrank( DEPLOYER );
    	usds.approve( address(dao), type(uint256).max );
    	salt.approve( address(staking), type(uint256).max );
    	usds.approve( address(proposals), type(uint256).max );
    	vm.stopPrank();

    	vm.startPrank( alice );
    	usds.approve( address(dao), type(uint256).max );
    	salt.approve( address(staking), type(uint256).max );
    	usds.approve( address(proposals), type(uint256).max );
    	vm.stopPrank();
    	}

	function testTeamRewardIsLockedInUpkeep() public {
		uint releasableAmount = teamVestingWallet.releasable(address(salt));
		uint upKeepBalance = salt.balanceOf(address(upkeep));
		uint mainWalletBalance = salt.balanceOf(address(managedTeamWallet.mainWallet()));
		//@audit-info a certain amount of SALT is releasable
		assertTrue(releasableAmount != 0);
		//@audit-info there is no SALT in upkeep
		assertEq(upKeepBalance, 0);
		//@audit-info there is no SALT in mainWallet
		assertEq(mainWalletBalance, 0);
		//@audit-info call release() before performUpkeep()
		teamVestingWallet.release(address(salt));
		upkeep.performUpkeep();
		
		upKeepBalance = salt.balanceOf(address(upkeep));
		mainWalletBalance = salt.balanceOf(address(managedTeamWallet.mainWallet()));
		//@audit-info all released SALT is locked in upKeep
		assertEq(upKeepBalance, releasableAmount);
		//@audit-info development team receive nothing
		assertEq(mainWalletBalance, 0);
  	}

}