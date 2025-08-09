
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import {ERC20} from "solmate/tokens/ERC20.sol";
import {UTB, SwapInstructions, SwapAndExecuteInstructions, FeeStructure} from "../src/UTB.sol";
import {UTBExecutor} from "../src/UTBExecutor.sol";
import {UniSwapper} from "../src/swappers/UniSwapper.sol";
import {SwapParams} from "../src/swappers/SwapParams.sol";
import {XChainExactOutFixture} from "./helpers/XChainExactOutFixture.sol";
import {UTBCommonAssertions} from "../test/helpers/UTBCommonAssertions.sol";
import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import {IDcntEth} from "lib/decent-bridge/src/interfaces/IDcntEth.sol";
import {IDecentBridgeExecutor} from "lib/decent-bridge/src/interfaces/IDecentBridgeExecutor.sol";
import {IDecentEthRouter} from "lib/decent-bridge/src/interfaces/IDecentEthRouter.sol";
import {DcntEth} from "lib/decent-bridge/src/DcntEth.sol";
import {DecentBridgeExecutor} from "lib/decent-bridge/src/DecentBridgeExecutor.sol";
import {DecentEthRouter} from "lib/decent-bridge/src/DecentEthRouter.sol";
import {IUTB} from "../src/interfaces/IUTB.sol";
import {IUTBExecutor} from "../src/interfaces/IUTBExecutor.sol";
import {IUTBFeeCollector} from "../src/interfaces/IUTBFeeCollector.sol";
import {LzChainSetup} from "lib/forge-toolkit/src/LzChainSetup.sol";
import {console2} from "forge-std/Test.sol";
import {VmSafe} from "forge-std/Vm.sol";

contract UTBReceiveFromBridge is XChainExactOutFixture {

    UTB src_utb;
    UTB dst_utb;
    UniSwapper src_swapper;
    UniSwapper dst_swapper;
    DecentEthRouter src_DecentEthRouter;
    DecentEthRouter dst_DecentEthRouter;
    IDcntEth src_IDcntEth;
    address src_weth; 
    address src_usdc; 
    address dst_weth;
    address dst_usdc;
    uint256 slippage = 1;
    uint256 FEE_AMOUNT = 0.01 ether;
    CalledPOC ap;

    function setUp() public {
        src = arbitrum;
        dst = polygon;
        preSlippage = 2;
        postSlippage = 3;
        initialEthBalance = 1 ether;
        initialUsdcBalance = 10e6;
        MINT_GAS = 9e5;
        setRuntime(ENV_FORGE_TEST);
        loadAllChainInfo();
        setupUsdcInfo();
        setupWethHelperInfo();
        loadAllUniRouterInfo();
        setSkipFile(true);
        vm.label(alice, "alice");
        vm.label(bob, "bob");
        src_weth = getWeth(src);
        src_usdc = getUsdc(src);
        dst_weth = getWeth(dst);
        dst_usdc = getUsdc(dst);
        feeAmount = FEE_AMOUNT;
        _setupXChainUTBInfra();
        _srcChainSetup();
        // start all activities in src chain by default
        switchTo(src);
        ap = new CalledPOC();
    }

    function _setupXChainUTBInfra() internal {
        (src_utb,,src_swapper,src_DecentEthRouter,,) = deployUTBAndItsComponents(src);
        (dst_utb,,dst_swapper,dst_DecentEthRouter,,) = deployUTBAndItsComponents(dst);
        wireUpXChainUTB(src, dst);
    }

    function _srcChainSetup() internal {
        dealTo(src, alice, initialEthBalance);
        mintUsdcTo(src, alice, initialUsdcBalance);
        mintWethTo(src, alice, initialEthBalance);
        cat = deployTheCat(src);
        catUsdcPrice = cat.price();
        catEthPrice = cat.ethPrice();
    }

    function _setupAndGetInstructionsFeesSignature() internal returns(
        SwapAndExecuteInstructions memory,
        FeeStructure memory,
        bytes memory){
        (SwapParams memory swapParams, uint expected) = getSwapParamsExactOut(
            src,
            src_weth,
            src_usdc,
            catUsdcPrice,
            slippage
        );
        address payable refund = payable(alice);
        SwapInstructions memory swapInstructions = SwapInstructions({
            swapperId: src_swapper.getId(),
            swapPayload: abi.encode(swapParams, address(src_utb), refund)
        });
        startImpersonating(alice);
        ERC20(src_weth).approve(address(src_utb), swapParams.amountIn);
        SwapAndExecuteInstructions
            memory instructions = SwapAndExecuteInstructions({
                swapInstructions: swapInstructions,
                target: address(cat),
                paymentOperator: address(cat),
                refund: refund,
                payload: abi.encodeCall(cat.mintWithUsdc, (bob))
            });

        (   bytes memory signature,
            FeeStructure memory fees
        ) = getFeesAndSignature(instructions);
        stopImpersonating();
        return (instructions, fees, signature);
    }

    /*
    Testing correct UTB fee collection/signature validation during normal swap. 
    Adapted from UTBExactOutRoutesTest:testSwapWethToUsdcAndMintAnNft
    */
    function testUTBReceiveFromBridge_SwapWethToUsdcAndMintAnNFTWithFees() public {
        (SwapAndExecuteInstructions memory _instructions,
        FeeStructure memory _fees,
        bytes memory _signature) = _setupAndGetInstructionsFeesSignature();
        startImpersonating(alice);
        uint256 aliceETHBalanceBefore = address(alice).balance;
        src_utb.swapAndExecute{value: feeAmount}(_instructions, _fees, _signature);
        stopImpersonating();
        // confirm alice has spent feeAmount
        assertEq(address(alice).balance, aliceETHBalanceBefore - feeAmount);
        // confirm bob got the NFT
        assertEq(cat.balanceOf(bob), 1);
        assertEq(ERC20(src_usdc).balanceOf(address(cat)), cat.price());
        // checking fees
        address feeCollector = address(feeCollectorLookup[src]);
        if (feeToken == address(0)) {
            // expect src feeCollector balance to be the feeAmount
            assertEq(feeCollector.balance, feeAmount);
        } else {
            assertEq(ERC20(feeToken).balanceOf(feeCollector), feeAmount);
        }
    }

    /*
    Missing access control on UTB:receiveFromBridge allows UTB swaps to be executed while bypassing fee/swap instruction signature verification. 
    */
    function testUTBReceiveFromBridge_BypassFeesAndSignature() public {
        /* getting the SwapAndExecuteInstructions struct for 
        swapping WETH to USDC and minting bob a VeryCoolCat NFT.
        FeeStructure and signature are not necessary this time.
        */
        (SwapAndExecuteInstructions memory _instructions,,) = _setupAndGetInstructionsFeesSignature();
        // checking feeCollector to see if it has receievd any fees
        address feeCollector = address(feeCollectorLookup[src]);
        uint256 aliceETHBalanceBefore = address(alice).balance;
        uint256 feeCollectorETHBalanceBefore = address(feeCollector).balance;
         startImpersonating(alice);
        /* use UTB:receiveFromBridge to directly call UTB:_swapAndExecute,
         bypassing UTB:retrieveAndCollectFees modifier to send tx without fees or signature
         with arbitrary additional payload.*/
        src_utb.receiveFromBridge(
            _instructions.swapInstructions,
            _instructions.target,
            _instructions.paymentOperator,
            _instructions.payload,
            _instructions.refund);
        stopImpersonating();
        // confirm alice has not spent any ETH/fees
        assertEq(address(alice).balance, aliceETHBalanceBefore);
        // confirm bob got the NFT
        assertEq(cat.balanceOf(bob), 1);
        assertEq(ERC20(src_usdc).balanceOf(address(cat)), cat.price());
        if (feeToken == address(0)) {
            // expect src feeCollector ETH balance not to change. In this case, it is 0
            assertEq(feeCollector.balance, feeCollectorETHBalanceBefore); 
            assertEq(feeCollector.balance, 0); 
        } else {
            assertEq(ERC20(feeToken).balanceOf(feeCollector), 0);
        }
    }

    /* Showing arbitrary calldata being executed in SwapAndExecuteInstructions.payload 
    by using UTB:receiveFromBridge to send an unsigned swap for 0 amount with no fees*/
    function testUTBReceiveFromBridge_ArbitraryCalldata() public {
        // arg: SwapInstructions memory postBridge
        (SwapParams memory swapParams, uint expected) = getSwapParamsExactOut(
            src, // string memory chain
            src_weth, // address tokenIn/tokenOut can be the same.
            src_weth, // address tokenOut
            0, // uitn256 amountOut can be zero
            slippage // uint256 slippage
        );
        // arg: address payable refund
        address payable refund = payable(alice); 
        // get SwapInstructions for SwapAndExecuteInstructions
        SwapInstructions memory swapInstructions = SwapInstructions({
            swapperId: src_swapper.getId(),
            swapPayload: abi.encode(swapParams, address(src_utb), refund)
        });
        startImpersonating(alice);
        //get SwapAndExecuteInstructions
        SwapAndExecuteInstructions
        memory _instructions = SwapAndExecuteInstructions({
            swapInstructions: swapInstructions,
            target:address(ap), // will be sending funds to alice on DST
            paymentOperator: address(alice), // address UTBExecutor approves
            refund: payable(address(alice)),
            // make arbitrary call
            payload: abi.encodeCall(ap.called, ())
        });
        // start recording for events
        vm.recordLogs();
        /* use UTB:receiveFromBridge to directly call UTB:_swapAndExecute,
        bypassing UTB:retrieveAndCollectFees modifier to send tx without fees or signature
        with arbitrary additional payload.*/
        src_utb.receiveFromBridge(
            _instructions.swapInstructions,
            _instructions.target,
            _instructions.paymentOperator,
            _instructions.payload,
            _instructions.refund);
        stopImpersonating();
        // capture emitted events
        VmSafe.Log[] memory entries = vm.getRecordedLogs();
        for (uint i = 0; i < entries.length; i++) {
        if (entries[i].topics[0] == keccak256("Called(string)")) {
            // assert that the event data contains the POC contract's string.
            assertEq(abi.decode(entries[i].data, (string)), 
            "POC contract called");
            }   
        }
    }
}

// simple test contract to register an event if called() is called.
contract CalledPOC {

    event Called(string);

    constructor() payable {}
    function called() public payable {
        emit Called("POC contract called");
    }

    receive() external payable {}

    fallback() external payable {}
}
