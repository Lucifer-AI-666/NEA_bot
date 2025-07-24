#!/bin/bash
echo "Avvio Jarbot - NeaBot @SilayaBot"
source config.env

# Controlla se Ollama è attivo
if curl -s http://localhost:11434 > /dev/null; then
    echo "Ollama attivo, uso LLaMA"
    python3 core_jarbot.py --model llama3
else
    echo "Ollama non disponibile, passo a OpenAI"
    python3 core_jarbot.py --model gpt
fi
