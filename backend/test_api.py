import asyncio
from adapters.factory import AdapterFactory
from adapters.base import GenerationRequest


async def main():
    req = GenerationRequest(
        prompt="Diga apenas: 'API funcionando!'",
        model="openai/gpt-4.1-mini",
        system_prompt="Você é um assistente de teste.",
        max_tokens=50,
        temperature=0.1,
    )

    adapter = AdapterFactory.get(req.model)
    result = await adapter.generate(req)

    print(f"✅ Modelo:   {result.model}")
    print(f"✅ Resposta: {result.content}")
    print(
        f"✅ Tokens:   {result.prompt_tokens} in / {result.output_tokens} out")
    print(f"✅ Latência: {result.latency_ms}ms")

asyncio.run(main())
