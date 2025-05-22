// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {OFT} from "@layerzerolabs/oft-evm/contracts/OFT.sol";

contract Titn is OFT {
    // Bridged token holder may have transfer restricted
    mapping(address => bool) public isBridgedTokenHolder;
    bool private isBridgedTokensTransferLocked;
    address public transferAllowedContract;
    address private lzEndpoint;

    error BridgedTokensTransferLocked();

    constructor(
        string memory _name,
        string memory _symbol,
        address _lzEndpoint,
        address _delegate,
        uint256 initialMintAmount
    ) OFT(_name, _symbol, _lzEndpoint, _delegate) Ownable(_delegate) {
        _mint(msg.sender, initialMintAmount);
        lzEndpoint = _lzEndpoint;
        isBridgedTokensTransferLocked = true;
    }

    //////////////////////////////
    //  External owner setters  //
    //////////////////////////////

    event TransferAllowedContractUpdated(address indexed transferAllowedContract);
    function setTransferAllowedContract(address _transferAllowedContract) external onlyOwner {
        transferAllowedContract = _transferAllowedContract;
        emit TransferAllowedContractUpdated(_transferAllowedContract);
    }

    function getTransferAllowedContract() external view returns (address) {
        return transferAllowedContract;
    }

    event BridgedTokenTransferLockUpdated(bool isLocked);
    function setBridgedTokenTransferLocked(bool _isLocked) external onlyOwner {
        isBridgedTokensTransferLocked = _isLocked;
        emit BridgedTokenTransferLockUpdated(_isLocked);
    }

    function getBridgedTokenTransferLocked() external view returns (bool) {
        return isBridgedTokensTransferLocked;
    }

    //////////////////////////////
    //         Overrides        //
    //////////////////////////////

    function transfer(address to, uint256 amount) public override returns (bool) {
        _validateTransfer(msg.sender, to);
        return super.transfer(to, amount);
    }

    function transferFrom(address from, address to, uint256 amount) public override returns (bool) {
        _validateTransfer(from, to);
        return super.transferFrom(from, to, amount);
    }

    /**
     * @dev Validates transfer restrictions.
     * @param from The sender's address.
     * @param to The recipient's address.
     */
    function _validateTransfer(address from, address to) internal view {
        // Arbitrum chain ID
        uint256 arbitrumChainId = 42161;

        // Check if the transfer is restricted
        if (
            from != owner() && // Exclude owner from restrictions
            from != transferAllowedContract && // Allow transfers to the transferAllowedContract
            to != transferAllowedContract && // Allow transfers to the transferAllowedContract
            isBridgedTokensTransferLocked && // Check if bridged transfers are locked
            // Restrict bridged token holders OR apply Arbitrum-specific restriction
            (isBridgedTokenHolder[from] || block.chainid == arbitrumChainId) &&
            to != lzEndpoint // Allow transfers to LayerZero endpoint
        ) {
            revert BridgedTokensTransferLocked();
        }
    }

    /**
     * @dev Credits tokens to the specified address.
     * @param _to The address to credit the tokens to.
     * @param _amountLD The amount of tokens to credit in local decimals.
     * @dev _srcEid The source chain ID.
     * @return amountReceivedLD The amount of tokens ACTUALLY received in local decimals.
     */
    function _credit(
        address _to,
        uint256 _amountLD,
        uint32 /*_srcEid*/
    ) internal virtual override returns (uint256 amountReceivedLD) {
        if (_to == address(0x0)) _to = address(0xdead); // _mint(...) does not support address(0x0)
        // Default OFT mints on dst.
        _mint(_to, _amountLD);

        // Addresses that bridged tokens have some transfer restrictions
        if (!isBridgedTokenHolder[_to]) {
            isBridgedTokenHolder[_to] = true;
        }

        // In the case of NON-default OFT, the _amountLD MIGHT not be == amountReceivedLD.
        return _amountLD;
    }
}