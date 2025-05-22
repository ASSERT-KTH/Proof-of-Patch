import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/signers'
import { time } from '@nomicfoundation/hardhat-network-helpers'
import { expect } from 'chai'
import { Contract, ContractFactory } from 'ethers'
import { deployments, ethers } from 'hardhat'

import { Options } from '@layerzerolabs/lz-v2-utilities'

describe('MergeTgt tests', function () {
    // Constant representing a mock Endpoint ID for testing purposes
    const eidA = 1
    const eidB = 2
    // Other variables to be used in the test suite
    let Titn: ContractFactory
    let MergeTgt: ContractFactory
    let Tgt: ContractFactory
    let EndpointV2Mock: ContractFactory
    let ownerA: SignerWithAddress
    let ownerB: SignerWithAddress
    let endpointOwner: SignerWithAddress
    let user1: SignerWithAddress
    let user2: SignerWithAddress
    let user3: SignerWithAddress
    let baseTITN: Contract
    let arbTITN: Contract
    let mergeTgt: Contract
    let tgt: Contract
    let mockEndpointV2A: Contract
    let mockEndpointV2B: Contract
    // Before hook for setup that runs once before all tests in the block
    before(async function () {
        // Contract factory for our tested contract
        Titn = await ethers.getContractFactory('Titn')
        MergeTgt = await ethers.getContractFactory('MergeTgt')
        Tgt = await ethers.getContractFactory('Tgt')
        // Fetching the first three signers (accounts) from Hardhat's local Ethereum network
        const signers = await ethers.getSigners()
        ;[ownerA, ownerB, endpointOwner, user1, user2, user3] = signers
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

        // Defining the amount of tokens to send and constructing the parameters for the send operation
        const tokensToSend = ethers.utils.parseEther('173700000')
        // Defining extra message execution options for the send operation
        const options = Options.newOptions().addExecutorLzReceiveOption(200000, 0).toHex().toString()
        const sendParam = [
            eidB,
            ethers.utils.zeroPad(ownerB.address, 32),
            tokensToSend,
            tokensToSend,
            options,
            '0x',
            '0x',
        ]
        // Fetching the native fee for the token send operation
        const [nativeFee] = await baseTITN.quoteSend(sendParam, false)
        // Executing the send operation from TITN contract
        await baseTITN.send(sendParam, [nativeFee, 0], ownerA.address, { value: nativeFee })

        // Deply MockTGT contract
        tgt = await Tgt.deploy('Tgt', 'TGT', ownerB.address, ethers.utils.parseUnits('1000000000', 18))

        // Deploy MergeTgt contract
        mergeTgt = await MergeTgt.deploy(tgt.address, arbTITN.address, ownerB.address)

        // Arbitrum setup
        await arbTITN.connect(ownerB).setTransferAllowedContract(mergeTgt.address)
        await mergeTgt.connect(ownerB).setLaunchTime()
        await mergeTgt.connect(ownerB).setLockedStatus(1)

        // now the admin should deposit all ARB.TITN into the mergeTGT contract
        await arbTITN.connect(ownerB).approve(mergeTgt.address, ethers.utils.parseUnits('173700000', 18))
        await mergeTgt.connect(ownerB).deposit(arbTITN.address, ethers.utils.parseUnits('173700000', 18))

        // let's send some TGT to user1 and user2
        await tgt.connect(ownerB).transfer(user1.address, ethers.utils.parseUnits('1000', 18))
        await tgt.connect(ownerB).transfer(user2.address, ethers.utils.parseUnits('1000', 18))
        await tgt.connect(ownerB).transfer(user3.address, ethers.utils.parseUnits('1000', 18))
    })

    describe('General tests', function () {
        it('should let a user to deposit TGT into the merge contract', async function () {
            // transfer TGT to the merge contract
            await tgt.connect(user1).approve(mergeTgt.address, ethers.utils.parseUnits('100', 18))
            await tgt.connect(user1).transferAndCall(mergeTgt.address, ethers.utils.parseUnits('100', 18), '0x')
            // claim TITN
            const claimableAmount = await mergeTgt.claimableTitnPerUser(user1.address)
            expect(claimableAmount.toString()).to.be.equal('30000000000000000000')
            await mergeTgt.connect(user1).claimTitn(claimableAmount)
            const titnBalance = await arbTITN.balanceOf(user1.address)
            expect(titnBalance.toString()).to.be.equal('30000000000000000000')
        })
        it('should not let a user to transfer TITN tokens', async function () {
            // transfer TGT to the merge contract
            await tgt.connect(user1).approve(mergeTgt.address, ethers.utils.parseUnits('100', 18))
            await tgt.connect(user1).transferAndCall(mergeTgt.address, ethers.utils.parseUnits('100', 18), '0x')
            // claim TITN
            const claimableAmount = await mergeTgt.claimableTitnPerUser(user1.address)
            await mergeTgt.connect(user1).claimTitn(claimableAmount)
            // attempt to transfer TITN (spoiler alert: it should fail)
            try {
                await arbTITN.connect(user1).transfer(user2.address, ethers.utils.parseUnits('1', 18))
                expect.fail('Transaction should have reverted')
            } catch (error: any) {
                expect(error.message).to.include('BridgedTokensTransferLocked')
            }
        })
        it('should not let a user to transfer TITN tokens', async function () {
            // transfer TGT to the merge contract
            await tgt.connect(user1).approve(mergeTgt.address, ethers.utils.parseUnits('100', 18))
            await tgt.connect(user1).transferAndCall(mergeTgt.address, ethers.utils.parseUnits('100', 18), '0x')
            // claim TITN
            const claimableAmount = await mergeTgt.claimableTitnPerUser(user1.address)
            await mergeTgt.connect(user1).claimTitn(claimableAmount)
            // attempt to transfer TITN (spoiler alert: it should fail)
            try {
                await arbTITN.connect(user1).transfer(user2.address, ethers.utils.parseUnits('1', 18))
                expect.fail('Transaction should have reverted')
            } catch (error: any) {
                expect(error.message).to.include('BridgedTokensTransferLocked')
            }
        })
        it('should let a user to bridge TITN tokens to BASE', async function () {
            // transfer TGT to the merge contract
            await tgt.connect(user1).approve(mergeTgt.address, ethers.utils.parseUnits('100', 18))
            await tgt.connect(user1).transferAndCall(mergeTgt.address, ethers.utils.parseUnits('100', 18), '0x')
            // claim TITN
            const claimableAmount = await mergeTgt.claimableTitnPerUser(user1.address)
            await mergeTgt.connect(user1).claimTitn(claimableAmount)

            // Attempt to bridge ARB.TITN to BASE.TITN
            // Defining extra message execution options for the send operation
            const options = Options.newOptions().addExecutorLzReceiveOption(200000, 0).toHex().toString()
            const sendParam = [
                eidA,
                ethers.utils.zeroPad(user1.address, 32),
                claimableAmount.toString(),
                claimableAmount.toString(),
                options,
                '0x',
                '0x',
            ]

            // Fetching the native fee for the token send operation
            const [nativeFee] = await arbTITN.quoteSend(sendParam, false)
            // Executing the send operation from TITN contract
            await arbTITN.connect(user1).send(sendParam, [nativeFee, 0], user1.address, { value: nativeFee })
            const balanceBase = await baseTITN.balanceOf(user1.address)
            const balanceArb = await arbTITN.balanceOf(user1.address)
            // their ARB balance should be 0 and their BASE balance should have increased
            expect(balanceBase).to.be.eql(claimableAmount)
            expect(balanceArb).to.be.eql(ethers.utils.parseUnits('0', 18))

            // they should not be able to transfer the BASE TITN
            try {
                await baseTITN.connect(user1).transfer(user2.address, ethers.utils.parseUnits('1', 18))
                expect.fail('Transaction should have reverted')
            } catch (error: any) {
                expect(error.message).to.include('BridgedTokensTransferLocked')
            }

            // but it the admin enables trading they should be able to transfer
            await baseTITN.connect(ownerA).setBridgedTokenTransferLocked(false)
            await baseTITN.connect(user1).transfer(user2.address, ethers.utils.parseUnits('1', 18))
            expect(await baseTITN.balanceOf(user2.address)).to.be.eql(ethers.utils.parseUnits('1', 18))
        })
    })
    describe('Time-based tests', function () {
        it('should get lower quotes after 90 days have elapsed', async function () {
            const amountOfTgtToDeposit = ethers.utils.parseUnits('1000', 18)
            const quote = Number(ethers.utils.formatUnits(await mergeTgt.quoteTitn(amountOfTgtToDeposit), 18))
            expect(quote).to.be.eql(300)

            // Fast forward 89 days
            await time.increase(89 * 24 * 60 * 60)

            // before the 90 days have elapsed the quote should as high as day one
            const quote1 = Number(ethers.utils.formatUnits(await mergeTgt.quoteTitn(amountOfTgtToDeposit), 18))
            expect(quote1).to.be.eq(300)

            // Fast forward 2 days
            await time.increase(2 * 24 * 60 * 60)

            // after 90 days the quotes should be less than initially and get gradually lower as times goes by (until day 365)
            const quote2 = Number(ethers.utils.formatUnits(await mergeTgt.quoteTitn(amountOfTgtToDeposit), 18))
            expect(quote2).to.be.lt(quote1)

            // Fast forward 30 days
            await time.increase(30 * 24 * 60 * 60)
            const quote3 = Number(ethers.utils.formatUnits(await mergeTgt.quoteTitn(amountOfTgtToDeposit), 18))
            expect(quote3).to.be.lt(quote2)

            // Fast forward 250 days
            await time.increase(250 * 24 * 60 * 60)
            const quote4 = Number(ethers.utils.formatUnits(await mergeTgt.quoteTitn(amountOfTgtToDeposit), 18))
            expect(quote4).to.be.eq(0)
        })
        it('should allow withdrawal of remaining TITN after 1 year', async function () {
            // user1 transfers TGT to the merge contract
            await tgt.connect(user1).approve(mergeTgt.address, ethers.utils.parseUnits('100', 18))
            await tgt.connect(user1).transferAndCall(mergeTgt.address, ethers.utils.parseUnits('100', 18), '0x')

            // user2 transfers TGT to the merge contract
            await tgt.connect(user2).approve(mergeTgt.address, ethers.utils.parseUnits('100', 18))
            await tgt.connect(user2).transferAndCall(mergeTgt.address, ethers.utils.parseUnits('100', 18), '0x')

            // user3 transfers TGT to the merge contract
            await tgt.connect(user3).approve(mergeTgt.address, ethers.utils.parseUnits('100', 18))
            await tgt.connect(user3).transferAndCall(mergeTgt.address, ethers.utils.parseUnits('100', 18), '0x')

            // user1 claims their TITN
            const claimableAmount = await mergeTgt.claimableTitnPerUser(user1.address)
            await mergeTgt.connect(user1).claimTitn(claimableAmount)

            expect((await arbTITN.balanceOf(user1.address)).toString()).to.be.eql('30000000000000000000')

            // user2 and user3 will wait 1 year and then try to withdraw their claimable amount + 50% of the remaining (unclaimed TITN)
            // Fast forward 365 days
            await time.increase(365 * 24 * 60 * 60)

            const availableTitn = await arbTITN.balanceOf(mergeTgt.address)
            expect(availableTitn.toString()).to.be.eql('173699970000000000000000000')

            // user2 and user3 should be able to withdraw half of availableTitn each
            await mergeTgt.connect(user2).withdrawRemainingTitn()
            expect((await arbTITN.balanceOf(user2.address)).toString()).to.be.eql('86849985000000000000000000')

            await mergeTgt.connect(user3).withdrawRemainingTitn()
            expect((await arbTITN.balanceOf(user3.address)).toString()).to.be.eql('86849985000000000000000000')
        })
    })
})
