// Wrapper padrão para todos os agentes do mining da Journal

import { Agent, routeAgentRequest } from "agents";

type MiningResult = {
  app: string;
  bundle_id: string;
  Record<string, any>;
};

export abstract class JournalMiningAgent extends Agent {
  abstract startMining(): Promise<void>;

  @callable()
  async start() {
    await this.runFiber("mining", async (ctx) => {
      await this.startMining();
    });
  }
}

export default {
  fetch: (req, env) => routeAgentRequest(req, env) ?? new Response("Not found", { status: 404 })
};