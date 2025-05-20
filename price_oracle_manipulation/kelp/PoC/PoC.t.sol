// SPDX-License-Identifier: UNLICENSED

pragma solidity 0.8.21;

import { BaseTest } from "./BaseTest.t.sol";
import { LRTDepositPool } from "src/LRTDepositPool.sol";
import { RSETHTest, ILRTConfig, UtilLib, LRTConstants } from "./RSETHTest.t.sol";
import { ILRTDepositPool } from "src/interfaces/ILRTDepositPool.sol";

import { TransparentUpgradeableProxy } from "@openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol";
import { ProxyAdmin } from "@openzeppelin/contracts/proxy/transparent/ProxyAdmin.sol";

import "forge-std/console.sol";

contract LRTOracleMock {

    uint256 assetPrice = 1e18;

    function setAssetPrice(uint256 newPrice) external {
        assetPrice = newPrice;
    }

    function getAssetPrice(address) external view returns (uint256) {
        return assetPrice;
    }

    function getRSETHPrice() external pure returns (uint256) {
        return 1e18;
    }
}

contract MockNodeDelegator {
    function getAssetBalance(address) external pure returns (uint256) {
        return 1e18;
    }
}

contract LRTDepositPoolTest is BaseTest, RSETHTest {
    LRTDepositPool public lrtDepositPool;
    LRTOracleMock public mockOracle;

    function setUp() public virtual override(RSETHTest, BaseTest) {
        super.setUp();

        // deploy LRTDepositPool
        ProxyAdmin proxyAdmin = new ProxyAdmin();
        LRTDepositPool contractImpl = new LRTDepositPool();
        TransparentUpgradeableProxy contractProxy = new TransparentUpgradeableProxy(
            address(contractImpl),
            address(proxyAdmin),
            ""
        );

        lrtDepositPool = LRTDepositPool(address(contractProxy));
        mockOracle = new LRTOracleMock();

        // initialize RSETH. LRTCOnfig is already initialized in RSETHTest
        rseth.initialize(address(admin), address(lrtConfig));
        vm.startPrank(admin);
        // add rsETH to LRT config
        lrtConfig.setRSETH(address(rseth));
        // add oracle to LRT config
        lrtConfig.setContract(LRTConstants.LRT_ORACLE, address(mockOracle));

        // add minter role for rseth to lrtDepositPool
        rseth.grantRole(rseth.MINTER_ROLE(), address(lrtDepositPool));

        vm.stopPrank();
    }
}

contract LRTDepositPoolDepositAsset is LRTDepositPoolTest {
    address public rETHAddress;

    function setUp() public override {
        super.setUp();

        // initialize LRTDepositPool
        lrtDepositPool.initialize(address(lrtConfig));

        rETHAddress = address(rETH);

        // add manager role within LRTConfig
        vm.startPrank(admin);
        lrtConfig.grantRole(LRTConstants.MANAGER, manager);
        vm.stopPrank();
    }


    function test_OracleCanModifyAssetMinted() external {
        
        vm.prank(alice);
        rETH.approve(address(lrtDepositPool), 2 ether);
        vm.prank(bob);
        rETH.approve(address(lrtDepositPool), 2 ether); 

        uint256 aliceDepositTime = block.timestamp;
        vm.prank(alice);
        lrtDepositPool.depositAsset(rETHAddress, 2 ether);

        mockOracle.setAssetPrice(1e17);

        uint256 bobDepositTime = block.timestamp;
        vm.prank(bob);
        lrtDepositPool.depositAsset(rETHAddress, 2 ether);

        uint256 aliceBalanceAfter = rseth.balanceOf(address(alice));
        uint256 bobBalanceAfter = rseth.balanceOf(address(bob));
        
        console.log(aliceBalanceAfter);
        console.log(bobBalanceAfter);    

        console.log(aliceDepositTime);
        console.log(bobDepositTime); 

        assertEq(aliceDepositTime, bobDepositTime);
        assertGt(aliceBalanceAfter, bobBalanceAfter);

    }

}