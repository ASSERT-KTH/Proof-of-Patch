//src/libraries/logic/IsolateLogic.sol
  function executeIsolateLiquidate(InputTypes.ExecuteIsolateLiquidateParams memory params) internal {
  ...
    if (params.supplyAsCollateral) {
        //@audit due to no check on msg.sender, anyone calls isolateLiquidate will get the collateral nft
 |>     VaultLogic.erc721TransferIsolateSupplyOnLiquidate(nftAssetData, params.msgSender, params.nftTokenIds);
    } else {
      VaultLogic.erc721DecreaseIsolateSupplyOnLiquidate(nftAssetData, params.nftTokenIds);

 |>     VaultLogic.erc721TransferOutLiquidity(nftAssetData, params.msgSender, params.nftTokenIds);
    }
  ...