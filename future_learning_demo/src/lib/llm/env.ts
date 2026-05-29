export type LlmEnv = {
  apiKey: string;
  baseUrl: string;
  model: string;
};

export function getLlmEnv(): LlmEnv | null {
  const apiKey = process.env.OPENAI_API_KEY?.trim();
  if (!apiKey) return null;
  const baseUrl = (
    process.env.OPENAI_BASE_URL ?? "https://api.openai.com/v1"
  ).replace(/\/$/, "");
  const model = process.env.AGENT_MODEL?.trim() || "gpt-4o-mini";
  return { apiKey, baseUrl, model };
}
