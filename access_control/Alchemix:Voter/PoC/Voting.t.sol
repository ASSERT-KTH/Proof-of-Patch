// SPDX-License-Identifier: GPL-3
pragma solidity ^0.8.15;

import "./BaseTest.sol";

contract VotingTest is BaseTest {
    function setUp() public {
        setupContracts(block.timestamp);
    }

    function testPocAccrueFluxMultipleTimes() public {
        uint256 tokenId = createVeAlcx(admin, TOKEN_1, MAXTIME, true);
        address[] memory pools = new address[](1);
        pools[0] = alETHPool;
        uint256[] memory weights = new uint256[](1);
        weights[0] = 5000;

        hevm.startPrank(admin);
        voter.vote(tokenId, pools, weights, 0);
        voter.poke(tokenId); // 1st time
        console.log("unclaimed flux balance",flux.getUnclaimedFlux(tokenId));
        voter.poke(tokenId); // 2nd time
        uint256 unclaimedFlux_1 = flux.getUnclaimedFlux(tokenId);
        voter.poke(tokenId); // 3rd time
        uint256 unclaimedFlux_2 = flux.getUnclaimedFlux(tokenId);
        console.log("increased flux balance",flux.getUnclaimedFlux(tokenId));
        assertGt(unclaimedFlux_2,unclaimedFlux_1);
    }

}
