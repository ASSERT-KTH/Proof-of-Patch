
//File:src/UTBExecutor.sol:

contract UTBExecutor is Owned {
   
    ...

    function execute(
        address target,
        address paymentOperator,
        bytes memory payload,
        address token,
        uint amount,
        address payable refund
    ) public payable onlyOwner {
        return
            execute(target, paymentOperator, payload, token, amount, refund, 0);
    }

    ...

    function execute(
        address target,
        address paymentOperator,
        bytes memory payload,
        address token,
        uint amount,
        address payable refund,
        uint extraNative
    ) public onlyOwner {
        bool success;
        if (token == address(0)) {
            (success, ) = target.call{value: amount}(payload);
            if (!success) {
                (refund.call{value: amount}(""));
            }
            return;
        }

        uint initBalance = IERC20(token).balanceOf(address(this));

        IERC20(token).transferFrom(msg.sender, address(this), amount);
        IERC20(token).approve(paymentOperator, amount);

        if (extraNative > 0) {
            (success, ) = target.call{value: extraNative}(payload);
            if (!success) {
                (refund.call{value: extraNative}(""));
            }
        } else {
            (success, ) = target.call(payload);
        }

        uint remainingBalance = IERC20(token).balanceOf(address(this)) -
            initBalance;

        if (remainingBalance == 0) {
            return;
        }

        IERC20(token).transfer(refund, remainingBalance);
    }
}