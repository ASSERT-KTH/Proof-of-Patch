/// @inheritdoc IVirtualAccount
    function payableCall(PayableCall[] calldata calls) public payable returns (bytes[] memory returnData) {
        uint256 valAccumulator;
        uint256 length = calls.length;
        returnData = new bytes[](length);
        PayableCall calldata _call;
        for (uint256 i = 0; i < length;) {
            _call = calls[i];
            uint256 val = _call.value;
            // Humanity will be a Type V Kardashev Civilization before this overflows - andreas
            // ~ 10^25 Wei in existence << ~ 10^76 size uint fits in a uint256
            unchecked {
                valAccumulator += val;
            }

            bool success;

            if (isContract(_call.target)) (success, returnData[i]) = _call.target.call{value: val}(_call.callData);

            if (!success) revert CallFailed();

            unchecked {
                ++i;
            }
        }

        // Finally, make sure the msg.value = SUM(call[0...i].value)
        if (msg.value != valAccumulator) revert CallFailed();
    }