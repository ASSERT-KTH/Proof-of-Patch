// SPDX-License-Identifier: GPL-3.0-or-later

pragma solidity ^0.8.24;

import "forge-std/Test.sol";

import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import {
    LiquidityManagement,
    PoolRoleAccounts,
    RemoveLiquidityKind,
    AfterSwapParams,
    SwapKind,
    AddLiquidityKind
} from "@balancer-labs/v3-interfaces/contracts/vault/VaultTypes.sol";
import { IVaultExtension } from "@balancer-labs/v3-interfaces/contracts/vault/IVaultExtension.sol";
import { IVaultAdmin } from "@balancer-labs/v3-interfaces/contracts/vault/IVaultAdmin.sol";
import { IVaultMock } from "@balancer-labs/v3-interfaces/contracts/test/IVaultMock.sol";
import { IVault } from "@balancer-labs/v3-interfaces/contracts/vault/IVault.sol";
import { IHooks } from "@balancer-labs/v3-interfaces/contracts/vault/IHooks.sol";
import "forge-std/console2.sol";
import {IVaultExplorer} from "@balancer-labs/v3-interfaces/contracts/vault/IVaultExplorer.sol";

import { CastingHelpers } from "@balancer-labs/v3-solidity-utils/contracts/helpers/CastingHelpers.sol";
import { BasicAuthorizerMock } from "@balancer-labs/v3-vault/contracts/test/BasicAuthorizerMock.sol";
import { ArrayHelpers } from "@balancer-labs/v3-solidity-utils/contracts/test/ArrayHelpers.sol";
import { FixedPoint } from "@balancer-labs/v3-solidity-utils/contracts/math/FixedPoint.sol";
import { BaseTest } from "@balancer-labs/v3-solidity-utils/test/foundry/utils/BaseTest.sol";
import { BaseVaultTest } from "@balancer-labs/v3-vault/test/foundry/utils/BaseVaultTest.sol";

import { BatchRouterMock } from "@balancer-labs/v3-vault/contracts/test/BatchRouterMock.sol";
import { PoolFactoryMock } from "@balancer-labs/v3-vault/contracts/test/PoolFactoryMock.sol";
import { BalancerPoolToken } from "@balancer-labs/v3-vault/contracts/BalancerPoolToken.sol";
import { RouterMock } from "@balancer-labs/v3-vault/contracts/test/RouterMock.sol";
import { PoolMock } from "@balancer-labs/v3-vault/contracts/test/PoolMock.sol";

import { MockUpdateWeightRunner } from "pool-quantamm/contracts/mock/MockUpdateWeightRunner.sol";

import { Ownable } from "@openzeppelin/contracts/access/Ownable.sol";

import { UpliftOnlyExample } from "../../contracts/hooks-quantamm/UpliftOnlyExample.sol";
import { LPNFT } from "../../contracts/hooks-quantamm/LPNFT.sol";

contract UpliftOnlyExampleTest is BaseVaultTest {
    using CastingHelpers for address[];
    using ArrayHelpers for *;
    using FixedPoint for uint256;

    uint256 internal daiIdx;
    uint256 internal usdcIdx;

    address internal owner;
    address internal addr1;
    address internal addr2;

    // Maximum exit fee of 10%
    uint64 private constant _MIN_SWAP_FEE_PERCENTAGE = 0.001e16; // 0.001%
    uint64 private constant _MAX_SWAP_FEE_PERCENTAGE = 10e16; // 10%
    uint64 private constant _MAX_UPLIFT_WITHDRAWAL_FEE = 20e16; // 20%

    uint256 internal constant DEFAULT_AMP_FACTOR = 200;

    MockUpdateWeightRunner internal updateWeightRunner;

    UpliftOnlyExample internal upliftOnlyRouter;

    // Overrides `setUp` to include a deployment for UpliftOnlyExample.
    function setUp() public virtual override {
        BaseTest.setUp();
        (address ownerLocal, address addr1Local, address addr2Local) = (vm.addr(1), vm.addr(2), vm.addr(3));
        owner = ownerLocal;
        addr1 = addr1Local;
        addr2 = addr2Local;

        vault = deployVaultMock();
        vm.label(address(vault), "vault");
        vaultExtension = IVaultExtension(vault.getVaultExtension());
        vm.label(address(vaultExtension), "vaultExtension");
        vaultAdmin = IVaultAdmin(vault.getVaultAdmin());
        vm.label(address(vaultAdmin), "vaultAdmin");
        authorizer = BasicAuthorizerMock(address(vault.getAuthorizer()));
        vm.label(address(authorizer), "authorizer");
        factoryMock = PoolFactoryMock(address(vault.getPoolFactoryMock()));
        vm.label(address(factoryMock), "factory");
        router = deployRouterMock(IVault(address(vault)), weth, permit2);
        vm.label(address(router), "router");
        batchRouter = deployBatchRouterMock(IVault(address(vault)), weth, permit2);
        vm.label(address(batchRouter), "batch router");
        feeController = vault.getProtocolFeeController();
        vm.label(address(feeController), "fee controller");

        vm.startPrank(address(vaultAdmin));
        updateWeightRunner = new MockUpdateWeightRunner(address(vaultAdmin), address(addr2), true);
        vm.label(address(updateWeightRunner), "updateWeightRunner");
        updateWeightRunner.setQuantAMMSwapFeeTake(0);

        vm.stopPrank();

        vm.startPrank(owner);
        upliftOnlyRouter = new UpliftOnlyExample(
            IVault(address(vault)),
            weth,
            permit2,
            200,
            5,
            address(updateWeightRunner),
            "Uplift LiquidityPosition v1",
            "Uplift LiquidityPosition v1",
            "Uplift LiquidityPosition v1"
        );
        vm.stopPrank();
        vm.label(address(upliftOnlyRouter), "upliftOnlyRouter");

        // Here the Router is also the hook.
        poolHooksContract = address(upliftOnlyRouter);
        (pool, ) = createPool();

        // Approve vault allowances.
        for (uint256 i = 0; i < users.length; ++i) {
            address user = users[i];
            vm.startPrank(user);
            approveForSender();
            vm.stopPrank();
        }
        if (pool != address(0)) {
            approveForPool(IERC20(pool));
        }
        // Add initial liquidity.
        initPool();

        (daiIdx, usdcIdx) = getSortedIndexes(address(dai), address(usdc));
    }

    // PoC test function
    function testRemoveLiquiditySmallPositivePriceChangeWrongFee() public {
        // Add liquidity
        uint256[] memory maxAmountsIn = [dai.balanceOf(bob), usdc.balanceOf(bob)].toMemoryArray();
        vm.prank(bob);
        upliftOnlyRouter.addLiquidityProportional(pool, maxAmountsIn, bptAmount, false, bytes(""));
        vm.stopPrank();

        // Set prices to be 3/2 of the initial prices (int256(i) * 1e18)
        // (refer to the test function `testRemoveLiquidityDoublePositivePriceChange`, #L551)
        int256[] memory prices = new int256[](100);
        int256 priceMultiplier = 3e18 / 2;
        for (uint256 i = 0; i < tokens.length; ++i) {
            prices[i] = int256(i) * priceMultiplier;
        }
        updateWeightRunner.setMockPrices(pool, prices);

        // upliftOnlyRouter default fee rates
        console2.log("upliftOnlyRouter.upliftFeeBps: ", upliftOnlyRouter.upliftFeeBps());
        console2.log("upliftOnlyRouter.minWithdrawalFeeBps: ", upliftOnlyRouter.minWithdrawalFeeBps());

        // lpTokenDepositValueChange should only consider prices change ratio, since pool balances remain the same
        // (priceMultiplier - 1e18) times 1e18 before division to avoid rounding to zero
        // (refer to the function `getPoolLPTokenValue` of the contract `UpliftOnlyExample`, #L672)
        // (refer to the logics of test function `testRemoveLiquidityDoublePositivePriceChange`)
        int256 lpTokenDepositValueChange = (priceMultiplier - 1e18) * 1e18 / 1e18;
        console2.log("lpTokenDepositValueChange: ", lpTokenDepositValueChange);
        assertTrue(lpTokenDepositValueChange > 0, "lpTokenDepositValueChange should be positive");

        // Calculate expected feePerLP and feePercentageBps
        // (refer to the function `onAfterRemoveLiquidity` of the contract `UpliftOnlyExample`, #L480-484)
        // (refer to the function `onAfterRemoveLiquidity` of the contract `UpliftOnlyExample`, #L495, #L514)
        uint256 feePerLPExpected = uint256(lpTokenDepositValueChange) * uint256(upliftOnlyRouter.upliftFeeBps()) / 10000;
        uint256 feePercentageExpectedBps = (bptAmount * feePerLPExpected) / bptAmount * 10000 / 1e18;
        console2.log("feePercentageExpectedBps: ", feePercentageExpectedBps);

        // Record pool states before remove liquidity
        uint256 bptTotalSupplyBeforeRemoveLiquidity = IVaultExplorer(address(vault)).totalSupply(pool);
        uint256[] memory poolBalancesBeforeRemoveLiquidity =
            IVaultExplorer(address(vault)).getPoolData(pool).balancesLiveScaled18;

        // Remove liquidity
        uint256[] memory minAmountsOut = [uint256(0), uint256(0)].toMemoryArray();
        uint256[] memory amountsOut = new uint256[](100);
        vm.startPrank(bob);
        amountsOut = upliftOnlyRouter.removeLiquidityProportional(bptAmount, minAmountsOut, false, pool);
        vm.stopPrank();

        // Calculate raw amountsOut in proportional manner when remove liquidity
        // (refer to the function `computeProportionalAmountsOut` of the contract `BasePoolMath`, #L106)
        uint256[] memory amountsOutRaw = new uint256[](100);
        for (uint256 i = 0; i < 2; ++i) {
            amountsOutRaw[i] = poolBalancesBeforeRemoveLiquidity[i] * bptAmount / bptTotalSupplyBeforeRemoveLiquidity;
        }

        // Calculate fee amounts and percentages
        uint256[] memory feeAmounts = new uint256[](100);
        uint256[] memory feePercentagesActualBps = new uint256[](100);
        for (uint256 i = 0; i < 2; ++i) {
            feeAmounts[i] = amountsOutRaw[i] - amountsOut[i];
            feePercentagesActualBps[i] = feeAmounts[i] * 10000 / amountsOutRaw[i];
            console2.log("feeAmounts[", i, "]: ", feeAmounts[i]);
            console2.log("feePercentagesActualBps[", i, "]: ", feePercentagesActualBps[i]);
        }

        // Check if the fee percentages are matched with the designed rates
        for (uint256 i = 0; i < 2; ++i) {
            assertTrue(
                feePercentagesActualBps[i] != feePercentageExpectedBps,
                "fee percentage is not based on the uplift fee rate due to the integer division rounding vulnerability"
            );
            assertTrue(
                feePercentagesActualBps[i] == upliftOnlyRouter.minWithdrawalFeeBps(),
                "fee percentage is the minimum fee rate due to the integer division rounding vulnerability"
            );
        }
    }

    // Overrides approval to include upliftOnlyRouter.
    function approveForSender() internal override {
        for (uint256 i = 0; i < tokens.length; ++i) {
            tokens[i].approve(address(permit2), type(uint256).max);
            permit2.approve(address(tokens[i]), address(router), type(uint160).max, type(uint48).max);
            permit2.approve(address(tokens[i]), address(batchRouter), type(uint160).max, type(uint48).max);
            permit2.approve(address(tokens[i]), address(upliftOnlyRouter), type(uint160).max, type(uint48).max);
        }
    }

    // Overrides approval to include upliftOnlyRouter.
    function approveForPool(IERC20 bpt) internal override {
        for (uint256 i = 0; i < users.length; ++i) {
            vm.startPrank(users[i]);

            bpt.approve(address(router), type(uint256).max);
            bpt.approve(address(batchRouter), type(uint256).max);
            bpt.approve(address(upliftOnlyRouter), type(uint256).max);

            IERC20(bpt).approve(address(permit2), type(uint256).max);
            permit2.approve(address(bpt), address(router), type(uint160).max, type(uint48).max);
            permit2.approve(address(bpt), address(batchRouter), type(uint160).max, type(uint48).max);
            permit2.approve(address(bpt), address(upliftOnlyRouter), type(uint160).max, type(uint48).max);

            vm.stopPrank();
        }
    }

    // Overrides pool creation to set liquidityManagement (disables unbalanced liquidity).
    function _createPool(
        address[] memory tokens,
        string memory label
    ) internal override returns (address newPool, bytes memory poolArgs) {
        string memory name = "Uplift Pool";
        string memory symbol = "Uplift Pool";

        newPool = address(deployPoolMock(IVault(address(vault)), name, symbol));
        vm.label(newPool, label);
        int256[] memory prices = new int256[](tokens.length);
        for (uint256 i = 0; i < tokens.length; ++i) {
            prices[i] = int256(i) * 1e18;
        }
        updateWeightRunner.setMockPrices(address(newPool), prices);

        PoolRoleAccounts memory roleAccounts;
        roleAccounts.poolCreator = lp;

        LiquidityManagement memory liquidityManagement;
        liquidityManagement.disableUnbalancedLiquidity = true;
        liquidityManagement.enableDonation = true;

        factoryMock.registerPool(
            newPool,
            vault.buildTokenConfig(tokens.asIERC20()),
            roleAccounts,
            poolHooksContract,
            liquidityManagement
        );

        poolArgs = abi.encode(vault, name, symbol);
    }
}
