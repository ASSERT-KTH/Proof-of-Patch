//File:src/UTB.sol

contract UTB is Owned {

    ...

    function receiveFromBridge(
        SwapInstructions memory postBridge,
        address target,
        address paymentOperator,
        bytes memory payload,
        address payable refund
    ) public { // missing retrieveAndCollect modifier
        _swapAndExecute(postBridge, target, paymentOperator, payload, refund);
    }

    ...

    // if a feeCollector has been set, then this modifier validates the fee struct against the signer:

    modifier retrieveAndCollectFees(
        FeeStructure calldata fees,
        bytes memory packedInfo,
        bytes calldata signature
    ) {
        if (address(feeCollector) != address(0)) {
            uint value = 0;
            if (fees.feeToken != address(0)) {
                IERC20(fees.feeToken).transferFrom(
                    msg.sender,
                    address(this),
                    fees.feeAmount
                );
                IERC20(fees.feeToken).approve(
                    address(feeCollector),
                    fees.feeAmount
                );
            } else {
                value = fees.feeAmount;
            }
            feeCollector.collectFees{value: value}(fees, packedInfo, signature);
        }
        _;
    }

    ...
    
    // swapAndExecute/bridgeAndExecute functions both validate fees/instructions signatures via retrieveAndCollectFees modifier

    function swapAndExecute(
        SwapAndExecuteInstructions calldata instructions,
        FeeStructure calldata fees,
        bytes calldata signature
    )
        public
        payable
        retrieveAndCollectFees(fees, abi.encode(instructions, fees), signature)
    {
        _swapAndExecute(
            instructions.swapInstructions,
            instructions.target,
            instructions.paymentOperator,
            instructions.payload,
            instructions.refund
        );
    }

    function bridgeAndExecute(
        BridgeInstructions calldata instructions,
        FeeStructure calldata fees,
        bytes calldata signature
    )
        public
        payable
        retrieveAndCollectFees(fees, abi.encode(instructions, fees), signature)
        returns (bytes memory)
    {
        (
            uint256 amt2Bridge,
            BridgeInstructions memory updatedInstructions
        ) = swapAndModifyPostBridge(instructions);
        return callBridge(amt2Bridge, fees.bridgeFee, updatedInstructions);
    }

    ...

    // _swapAndExecute directly bypasses any signature/fee checks before the swap/payload is executed.

    function _swapAndExecute(
        SwapInstructions memory swapInstructions,
        address target,
        address paymentOperator,
        bytes memory payload,
        address payable refund
    ) private {
        (address tokenOut, uint256 amountOut) = performSwap(swapInstructions);
        if (tokenOut == address(0)) {
            executor.execute{value: amountOut}(
                target,
                paymentOperator,
                payload,
                tokenOut,
                amountOut,
                refund
            );
        } else {
            IERC20(tokenOut).approve(address(executor), amountOut);
            executor.execute(
                target,
                paymentOperator,
                payload,
                tokenOut,
                amountOut,
                refund
            );
        }
    }

}