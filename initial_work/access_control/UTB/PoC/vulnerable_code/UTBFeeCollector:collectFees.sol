//File:src/UTBFeeCollector.sol

    function collectFees(
        FeeStructure calldata fees,
        bytes memory packedInfo,
        bytes memory signature
    ) public payable onlyUtb {
        bytes32 constructedHash = keccak256(
            abi.encodePacked(BANNER, keccak256(packedInfo))
        );
        (bytes32 r, bytes32 s, uint8 v) = splitSignature(signature);
        address recovered = ecrecover(constructedHash, v, r, s);
        require(recovered == signer, "Wrong signature");
        if (fees.feeToken != address(0)) {
            IERC20(fees.feeToken).transferFrom(
                utb,
                address(this),
                fees.feeAmount
            );
        }
    }