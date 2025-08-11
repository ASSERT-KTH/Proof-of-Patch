import { expect } from "chai";
import { ethers } from "hardhat";
import type { ERC20, LLMOracleCoordinator, LLMOracleRegistry } from "../typechain-types";
import type { HardhatEthersSigner } from "@nomicfoundation/hardhat-ethers/signers";
import { parseEther } from "ethers";
import { deployLLMFixture, deployTokenFixture } from "./fixtures/deploy";
import { registerOracles, safeRequest, safeRespond, safeValidate } from "./helpers";
import { TaskStatus } from "./types/enums";
import { transferTokens } from "./helpers";

/**
 * Test for underflow in score range calculation vulnerability
 */
describe("LLMOracleCoordinator", function () {
  let dria: HardhatEthersSigner;
  let requester: HardhatEthersSigner;
  let generators: HardhatEthersSigner[];
  let validators: HardhatEthersSigner[];

  let coordinator: LLMOracleCoordinator;
  let registry: LLMOracleRegistry;
  let token: ERC20;

  let coordinatorAddress: string;
  let registryAddress: string;

  let taskId = 0n; // this will be updated throughout the test

  /// mock LLM input & output
  const input = "0x" + Buffer.from("What is 2 + 2?").toString("hex");
  const output = "0x" + Buffer.from("2 + 2 equals 4.").toString("hex");
  const models = "0x" + Buffer.from("gpt-4o-mini").toString("hex");
  const metadata = "0x"; // empty metadata
  const difficulty = 2;
  const SUPPLY = parseEther("1000");

  const STAKES = {
    generatorStakeAmount: parseEther("0.01"),
    validatorStakeAmount: parseEther("0.01"),
  };

  const FEES = {
    platformFee: parseEther("0.001"),
    generationFee: parseEther("0.002"),
    validationFee: parseEther("0.0003"),
  };

  this.beforeAll(async function () {
    // assign roles, full = oracle that can do both generation & validation
    const [deployer, dum, req1, gen1, gen2, gen3, gen4, gen5, val1, val2, val3, val4, val5] = await ethers.getSigners();
    dria = deployer;
    requester = req1;
    generators = [gen1, gen2, gen3, gen4, gen5];
    validators = [val1, val2, val3, val4, val5];

    token = await deployTokenFixture(deployer, SUPPLY);

    ({ registry, coordinator } = await deployLLMFixture(dria, token, STAKES, FEES));

    const requesterFunds = parseEther("1");
    await transferTokens(token, [
      [requester.address, requesterFunds],

      // each oracle should have at least the stake amount
      ...generators.map<[string, bigint]>((oracle) => [oracle.address, STAKES.generatorStakeAmount]),
      ...validators.map<[string, bigint]>((oracle) => [oracle.address, STAKES.validatorStakeAmount]),
    ]);

    registryAddress = await registry.getAddress();
    coordinatorAddress = await coordinator.getAddress();
  });

  it("should register oracles", async function () {
    await registerOracles(token, registry, generators, validators, STAKES);
  });

  describe("underflow in score range calculation", function () {
    const [numGenerations, numValidations] = [1, 5];
    const scores = [
        parseEther("0"), 
        parseEther("0.000000000000000001"),  
        parseEther("0"),
        parseEther("0.000000000000000001"),
        parseEther("0.000000000000000002")
    ];
    let generatorAllowancesBefore: bigint[];
    let validatorAllowancesBefore: bigint[];

    this.beforeAll(async () => {
        taskId++;

        generatorAllowancesBefore = await Promise.all(
            generators.map((g) => token.allowance(coordinatorAddress, g.address))
        );
        validatorAllowancesBefore = await Promise.all(
            validators.map((v) => token.allowance(coordinatorAddress, v.address))
        );
    });

    it("should make a request", async function () {
        await safeRequest(coordinator, token, requester, taskId, input, models, {
            difficulty,
            numGenerations,
            numValidations,
        });
    });

    it("should respond to each generation", async function () {
      const availableGenerators = generators.length;
      const generationsToRespond = Math.min(numGenerations, availableGenerators);
  
      expect(availableGenerators).to.be.at.least(generationsToRespond);
  
      for (let i = 0; i < generationsToRespond; i++) {
          await safeRespond(coordinator, generators[i], output, metadata, taskId, BigInt(i));
      }
    });

    // UNDERFLOW TEST
    it("it should underflow calculating score ranges for inner mean", async function () {
      const requestBefore = await coordinator.requests(taskId);
      console.log(`Request status before validation: ${requestBefore.status}`);
  
      for (let i = 0; i < numValidations; i++) {
          console.log(`Validating with validator at index ${i} with address: ${validators[i].address}`);
          console.log(`Score being used: ${scores[i].toString()}, Task ID: ${taskId}`);

          try {
              if (i < numValidations - 1) {
                  
                  await safeValidate(coordinator, validators[i], [scores[i]], metadata, taskId, BigInt(i));
                  console.log(`Validation succeeded for validator at index ${i}`);
              } else {
                // For the last validator, expect a revert without a specific error
                await safeValidate(coordinator, validators[i], [scores[i]], metadata, taskId, BigInt(i));
                console.log(`Validation succeeded for validator at index ${i}`); // This should not run if it reverts
            }
          } catch (error:any) {
              if (i < numValidations - 1) {
                  console.error(`Validation failed for validator at index ${i} with error: ${error.message}`);
              } else {
                if (error instanceof Error) {
                  console.error(`Validation failed for validator at index ${i}: ${error.message}`);
              } else {
                  console.error(`Validation failed for validator at index ${i}: ${JSON.stringify(error)}`);
              }
            }
          }
      }
  
      // Confirm the tasks status
      const finalRequest = await coordinator.requests(taskId);
      console.log(`Request status after all validations: ${finalRequest.status}`);
  
      // Confirm the status is still 'PendingValidation'
      expect(finalRequest.status).to.equal(TaskStatus.PendingValidation);
    }); 
  });
});