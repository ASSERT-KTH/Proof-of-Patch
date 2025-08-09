File: contracts\WooPPV2.sol
513:     function _swapBaseToBase(
...
520:     ) private nonReentrant whenNotPaused returns (uint256 base2Amount) {
521:         require(baseToken1 != address(0) && baseToken1 != quoteToken, "WooPPV2: !baseToken1");
522:         require(baseToken2 != address(0) && baseToken2 != quoteToken, "WooPPV2: !baseToken2");
...
527:         IWooracleV2.State memory state1 = IWooracleV2(wooracle).state(baseToken1);
528:         IWooracleV2.State memory state2 = IWooracleV2(wooracle).state(baseToken2);
...
539:             uint256 newBase1Price;
540:             (quoteAmount, newBase1Price) = _calcQuoteAmountSellBase(baseToken1, base1Amount, state1);
541:             IWooracleV2(wooracle).postPrice(baseToken1, uint128(newBase1Price));
...
554:             uint256 newBase2Price;
555:             (base2Amount, newBase2Price) = _calcBaseAmountSellQuote(baseToken2, quoteAmount, state2);
556:             IWooracleV2(wooracle).postPrice(baseToken2, uint128(newBase2Price));
...
578:     }
