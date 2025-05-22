// SPDX-License-Identifier: ISC
pragma solidity >=0.8.25;

import {Governor} from "@openzeppelin/contracts/governance/Governor.sol";
import {GovernorCountingSimple} from "@openzeppelin/contracts/governance/extensions/GovernorCountingSimple.sol";
import {GovernorVotes} from "@openzeppelin/contracts/governance/extensions/GovernorVotes.sol";
import {GovernorVotesQuorumFraction} from "@openzeppelin/contracts/governance/extensions/GovernorVotesQuorumFraction.sol";
import {IVotes} from "@openzeppelin/contracts/governance/utils/IVotes.sol";
import {Time} from "@openzeppelin/contracts/utils/types/Time.sol";
import {Agent} from "./Agent.sol";

//////////////////////////////////////////////////////////////////////////////
//                                                                          //
//  888   e88 88e         e Y8b                                d8           //
//  888  d888 888b       d8b Y8b     e88 888  ,e e,  888 8e   d88    dP"Y   //
//  888 C8888 8888D     d888b Y8b   d888 888 d88 88b 888 88b d88888 C88b    //
//  888  Y888 888P     d888888888b  Y888 888 888   , 888 888  888    Y88D   //
//  888   "88 88"     d8888888b Y8b  "88 888  "YeeP" 888 888  888   d,dP    //
//            b                       ,  88P                                //
//            8b,                    "8",P"                                 //
//////////////////////////////////////////////////////////////////////////////

/**
 * @title TokenGovernor
 * @dev TokenGovernor contract
 */
contract TokenGovernor is Governor, GovernorCountingSimple, GovernorVotes, GovernorVotesQuorumFraction {
    // The voting delay in seconds
    //uint32 public votingDelayInSeconds = 1 days; // 1 day in seconds

    // The voting period in seconds
    //uint32 public votingPeriodInSeconds = 7 days; // 1 week in seconds

    // The proposal threshold percentage
    //uint32 public proposalThresholdPercentage = 100; // 1% of supply

    // Settings for testing
    uint32 public votingDelayInSeconds = 2 minutes; // 2 minutes in seconds
    uint32 public votingPeriodInSeconds = 5 minutes; // 5 minutes in seconds
    uint32 public proposalThresholdPercentage = 1; // 0.01%

    // The agent
    Agent public agent;

    /// @dev Constructor
    /// @param _name  The name of the governor
    /// @param _token The token
    constructor(
        string memory _name,
        IVotes _token,
        Agent _agent
    )
        Governor(_name)
        GovernorVotes(_token)
        GovernorVotesQuorumFraction(4) // quorum is 25% (1/4th) of supply
    {
        agent = _agent;
    }

    /// @dev Vote delay
    /// @return The vote delay in seconds
    function votingDelay() public view override returns (uint256) {
        return votingDelayInSeconds;
    }

    /// @dev Voting period
    /// @return The voting period in seconds
    function votingPeriod() public view override returns (uint256) {
        return votingPeriodInSeconds;
    }

    /// @dev Proposal threshold
    /// @return The proposal threshold in votes
    function proposalThreshold() public view override returns (uint256) {
        if (agent.stage() == 0) return type(uint256).max;
        else return (token().getPastTotalSupply(Time.timestamp() - 1) * proposalThresholdPercentage) / 10_000;
    }

    /// @dev Set proposal threshold percentage
    /// @param _proposalThresholdPercentage percentage of supply 10_000 base
    function setProposalThresholdPercentage(uint32 _proposalThresholdPercentage) public {
        if (msg.sender != address(this)) revert NotGovernor();
        if (proposalThresholdPercentage > 1000) revert InvalidThreshold(); // Max 10%
        proposalThresholdPercentage = _proposalThresholdPercentage;
        emit ProposalThresholdSet(_proposalThresholdPercentage);
    }

    /// @dev Set voting period
    /// @param _votingPeriodInSeconds The voting period in seconds
    function setVotingPeriod(uint32 _votingPeriodInSeconds) public {
        if (msg.sender != address(this)) revert NotGovernor();
        if (_votingPeriodInSeconds > 30 days) revert InvalidPeriod(); // Max 30 days
        if (_votingPeriodInSeconds < 3 days) revert InvalidPeriod(); // Min 3 days
        votingPeriodInSeconds = _votingPeriodInSeconds;
        emit VotingPeriodSet(_votingPeriodInSeconds);
    }

    /// @dev Set voting delay
    /// @param _votingDelayInSeconds The voting delay in seconds
    function setVotingDelay(uint32 _votingDelayInSeconds) public {
        if (msg.sender != address(this)) revert NotGovernor();
        if (_votingDelayInSeconds > 7 days) revert InvalidDelay(); // Max 7 days
        if (_votingDelayInSeconds < 12 hours) revert InvalidDelay(); // Min 12 hours
        votingDelayInSeconds = _votingDelayInSeconds;
        emit VotingDelaySet(_votingDelayInSeconds);
    }

    // The functions below are overrides required by Solidity.

    /// @dev Get the state of the proposal
    /// @param proposalId The proposal ID
    /// @return The state of the proposal
    /// @dev Proposal ID: uint256(keccak256(abi.encode(targets, values, calldatas, descriptionHash)))
    function state(uint256 proposalId) public view override(Governor) returns (ProposalState) {
        return super.state(proposalId);
    }

    /// @dev Gets whether the proposal is need to be queued
    /// @notice Will Always return false
    function proposalNeedsQueuing(uint256 proposalId) public view virtual override(Governor) returns (bool) {
        return super.proposalNeedsQueuing(proposalId);
    }

    /// @dev execute the proposal
    /// @param proposalId      The proposal ID
    /// @param targets         The targets
    /// @param values          The values
    /// @param calldatas       The calldatas
    /// @param descriptionHash The description hash
    function _executeOperations(
        uint256 proposalId,
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override(Governor) {
        super._executeOperations(proposalId, targets, values, calldatas, descriptionHash);
    }

    /// @dev Cancel the proposal
    /// @param targets         The targets
    /// @param values          The values
    /// @param calldatas       The calldatas
    /// @param descriptionHash The description hash
    function _cancel(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override(Governor) returns (uint256) {
        return super._cancel(targets, values, calldatas, descriptionHash);
    }

    /// @dev Get the executor
    /// @return The executor
    function _executor() internal view override(Governor) returns (address) {
        return super._executor();
    }

    // Events
    /// @dev Event for setting the proposal threshold
    /// @param _proposalThresholdPercentage The proposal threshold percentage in 1e4
    event ProposalThresholdSet(uint32 _proposalThresholdPercentage);

    /// @dev Event for setting the voting period
    /// @param _votingPeriodInSeconds The voting period in seconds
    event VotingPeriodSet(uint32 _votingPeriodInSeconds);

    /// @dev Event for setting the voting delay
    /// @param _votingDelayInSeconds The voting delay in seconds
    event VotingDelaySet(uint32 _votingDelayInSeconds);

    // Errors
    error NotGovernor();
    error InvalidThreshold();
    error InvalidPeriod();
    error InvalidDelay();
}