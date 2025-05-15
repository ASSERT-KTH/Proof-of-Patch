import { HardhatEthersSigner } from '@nomicfoundation/hardhat-ethers/signers';
import { expect } from 'chai';
import { ethers } from 'hardhat';
import {
  DevFund,
  NukeFund,
  TraitForgeNft,
  Airdrop,
  EntropyGenerator,
  EntityForging,
  EntityTrading,
} from '../typechain-types';
import generateMerkleTree from '../scripts/genMerkleTreeLib';
import { fastForward } from '../utils/evm';

describe('NukeFund', function () {
  let owner: HardhatEthersSigner,
    user1: HardhatEthersSigner,
    nukeFund: NukeFund,
    nft: TraitForgeNft,
    devFund: DevFund,
    airdrop: Airdrop,
    entityForging: EntityForging,
    merkleInfo: any,
    entityTrading: EntityTrading;
  beforeEach(async function () {
    [owner, user1] = await ethers.getSigners();

    const TraitForgeNft = await ethers.getContractFactory('TraitForgeNft');
    nft = (await TraitForgeNft.deploy()) as TraitForgeNft;
    await nft.waitForDeployment();

    devFund = await ethers.deployContract('DevFund');
    await devFund.waitForDeployment();

    await devFund.addDev(owner.address, 1);

    airdrop = await ethers.deployContract('Airdrop');
    await airdrop.waitForDeployment();

    await nft.setAirdropContract(await airdrop.getAddress());
    await airdrop.transferOwnership(await nft.getAddress());

    const NukeFund = await ethers.getContractFactory('NukeFund');

    nukeFund = (await NukeFund.deploy(
      await nft.getAddress(),
      await airdrop.getAddress(),
      await devFund.getAddress(),
      owner.address
    )) as NukeFund;
    await nukeFund.waitForDeployment();

    await nft.setNukeFundContract(await nukeFund.getAddress());

    // Deploy EntityForging contract
    const EntropyGenerator = await ethers.getContractFactory(
      'EntropyGenerator'
    );
    const entropyGenerator = (await EntropyGenerator.deploy(
      await nft.getAddress()
    )) as EntropyGenerator;

    await entropyGenerator.writeEntropyBatch1();

    await nft.setEntropyGenerator(await entropyGenerator.getAddress());

    // Deploy EntityForging contract
    const EntityForging = await ethers.getContractFactory('EntityForging');
    entityForging = (await EntityForging.deploy(
      await nft.getAddress()
    )) as EntityForging;
    await nft.setEntityForgingContract(await entityForging.getAddress());

    merkleInfo = generateMerkleTree([owner.address, user1.address]);

    await nft.setRootHash(merkleInfo.rootHash);

    entityTrading = await ethers.deployContract('EntityTrading', [
      await nft.getAddress(),
    ]);

    await entityTrading.setNukeFundAddress(await nukeFund.getAddress());

    await nft.connect(owner).mintToken(merkleInfo.whitelist[0].proof, {
      value: ethers.parseEther('1'),
    });
    // Set minimumDaysHeld to 0 for testing purpose
    await nukeFund.setMinimumDaysHeld(0);
  });
  
  it('should revert to nuke a token', async function () {
    const tokenId = 1;

    // Mint a token
    await nft.connect(owner).mintToken(merkleInfo.whitelist[0].proof, {
    value: ethers.parseEther('1'),
    });

    // Send some funds to the contract
    await user1.sendTransaction({
    to: await nukeFund.getAddress(),
    value: ethers.parseEther('1'),
    });

    const prevNukeFundBal = await nukeFund.getFundBalance();
    // Ensure the token can be nuked
    expect(await nukeFund.canTokenBeNuked(tokenId)).to.be.true;

    const prevUserEthBalance = await ethers.provider.getBalance(
    await owner.getAddress()
    );
    // await nft.connect(owner).approve(await nukeFund.getAddress(), tokenId);
    await nft.connect(owner).approve(user1, tokenId);
    await nft.connect(owner).setApprovalForAll(await nukeFund.getAddress(), true);

    const finalNukeFactor = await nukeFund.calculateNukeFactor(tokenId);
    const fund = await nukeFund.getFundBalance();

    // await expect(nukeFund.connect(owner).nuke(tokenId))
    await expect(nukeFund.connect(user1).nuke(tokenId)).to.be.revertedWith("Contract must be approved to transfer the NFT.");
});
});
