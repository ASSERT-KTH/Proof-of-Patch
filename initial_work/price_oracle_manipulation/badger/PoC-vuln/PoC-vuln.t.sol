// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.17;

import "forge-std/Test.sol";
import {IPriceFeed} from "../contracts/Interfaces/IPriceFeed.sol";
import {PriceFeed} from "../contracts/PriceFeed.sol";
import {PriceFeedTester} from "../contracts/TestContracts/PriceFeedTester.sol";
import {MockTellor} from "../contracts/TestContracts/MockTellor.sol";
import {MockAggregator} from "../contracts/TestContracts/MockAggregator.sol";
import {eBTCBaseFixture} from "./BaseFixture.sol";
import {TellorCaller} from "../contracts/Dependencies/TellorCaller.sol";
import {AggregatorV3Interface} from "../contracts/Dependencies/AggregatorV3Interface.sol";

contract AuditPriceFeedTest is eBTCBaseFixture {
    address constant STETH_ETH_CL_FEED = 0x86392dC19c0b719886221c78AB11eb8Cf5c52812;

    PriceFeedTester internal priceFeedTester;
    MockAggregator internal _mockChainLinkEthBTC;
    MockAggregator internal _mockChainLinkStEthETH;
    uint80 internal latestRoundId = 321;
    int256 internal initEthBTCPrice = 7428000;
    int256 internal initStEthETHPrice = 9999e14;
    uint256 internal initStEthBTCPrice = 7428e13;
    address internal authUser;

    function setUp() public override {
        eBTCBaseFixture.setUp();
        eBTCBaseFixture.connectCoreContracts();
        eBTCBaseFixture.connectLQTYContractsToCore();

        // Set current and prev price
        _mockChainLinkEthBTC = new MockAggregator();
        _initMockChainLinkFeed(_mockChainLinkEthBTC, latestRoundId, initEthBTCPrice, 8);
        _mockChainLinkStEthETH = new MockAggregator();
        _initMockChainLinkFeed(_mockChainLinkStEthETH, latestRoundId, initStEthETHPrice, 18);

        priceFeedTester = new PriceFeedTester(
            address(0), // fallback oracle not set
            address(authority),
            address(_mockChainLinkStEthETH),
            address(_mockChainLinkEthBTC)
        );
        priceFeedTester.setStatus(IPriceFeed.Status.usingChainlinkFallbackUntrusted);

        // Grant permission on price feed
        authUser = _utils.getNextUserAddress();
        vm.startPrank(defaultGovernance);
        authority.setUserRole(authUser, 4, true);
        authority.setRoleCapability(4, address(priceFeedTester), SET_FALLBACK_CALLER_SIG, true);
        vm.stopPrank();
    }

    function _initMockChainLinkFeed(
        MockAggregator _mockFeed,
        uint80 _latestRoundId,
        int256 _price,
        uint8 _decimal
    ) internal {
        _mockFeed.setLatestRoundId(_latestRoundId);
        _mockFeed.setPrevRoundId(_latestRoundId - 1);
        _mockFeed.setPrice(_price);
        _mockFeed.setPrevPrice(_price);
        _mockFeed.setDecimals(_decimal);
        _mockFeed.setUpdateTime(block.timestamp);
    }

    function testPriceChangeOver50PerCent() public {
        uint256 lastGoodPrice = priceFeedTester.lastGoodPrice();

        // Price change over 50%
        int256 newEthBTCPrice = (initEthBTCPrice * 2) + 1;
        _mockChainLinkEthBTC.setPrice(newEthBTCPrice);

        // Get price
        uint256 newPrice = priceFeedTester.fetchPrice();
        IPriceFeed.Status status = priceFeedTester.status();
        assertEq(newPrice, lastGoodPrice); // last good price is used
        assertEq(uint256(status), 2); // bothOraclesUntrusted
        
        // Get price again in the same block (no changes in ChainLink price)
        newPrice = priceFeedTester.fetchPrice();
        status = priceFeedTester.status();
        assertGt(newPrice, lastGoodPrice * 2); // current ChainLink price is used
        assertEq(uint256(status), 4); // usingChainlinkFallbackUntrusted
    }
}