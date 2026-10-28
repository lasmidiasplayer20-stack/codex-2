# 09 — E se a gravidade sumisse no elevador?

Short original do Então: **60,000 segundos exatos, 1080×1920 vertical, 24fps, 1440quadros nativos**.

- [MP4 completo — também serve como prévia de um minuto](exports/09%20-%20E%20se%20a%20gravidade%20sumisse%20no%20elevador.mp4)
- [Capa e arquivo único YOUTUBE](../../youtube/09%20-%20E%20se%20a%20gravidade%20sumisse%20no%20elevador/)
- [Roteiro](ROTEIRO.md), cenas JavaScript/Three.js no aiTrends, rig Nico/Lia próprio; sem Blender ou imagens nas cenas.

Puck/modelo aceitos, uma geração bem-sucedida, sem acelerar. Mix discreta: filtros suaves, ganho estático, música e efeitos sintetizados em Python. A revisão técnica mede duração, picos e decode; não equivale a escuta humana integral.

19planos, cabine aberta em corte, cabos/contrapeso, flutuação, celular solto, pedalada sem apoio, impulso contra parede e alça compartilhada com IK. A hipótese de remoção seletiva do peso é ficção; distinguimos de queda livre. Referência visual documentada em input/reference-analysis.md; nenhuma voz/frame/modelo do canal original foi reutilizado.

## Reproduzir

Voz: exportar GEMINI_API_KEY em área privada e usar scripts/generate_voice.py --work PASTA_PRIVADA/voice (somente se precisar gerar; preservar cache). Para reutilizar os MP3 prontos, não chamar a API. Tratamento a partir do cache bruto: AiTrends/.venv/bin/python scripts/audio.py --work PASTA_PRIVADA. Render pela skill AiTrends/skill/scripts/render.mjs, configuração local9:16/1080p/24fps. O MP4 final tem QA em qa/export-validation.json e qa/final-audio-validation.json. A finalização lê mix.wav do tratamento; mantenha intermediários privados ou decodifique mix.mp3 para WAV antes de montar sem novas gerações.

Capa vertical9:16/1080×1920 original gerada separadamente no padrão neon e não utilizada como frame da animação. Não enviado ao YouTube.
