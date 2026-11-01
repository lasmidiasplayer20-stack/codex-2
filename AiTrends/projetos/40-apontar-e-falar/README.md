# 40 — Por que ele aponta e fala sozinho?

**Exportado e validado:** 45,000 s / 1.080 quadros / 1080×1920. A publicação depende de esta revisão estar no GitHub.

[MP4 completo](exports/40%20-%20apontar-e-falar.mp4) · [Prévia de 12 s](exports/preview-12s.mp4) · [QA visual](qa/filme-completo.jpg)

Mix final: -17.6 LUFS, pico verdadeiro -4.9 dBTP; decodificação integral aprovada.

45 segundos exatos / 1.080 quadros / 24 fps / 1080×1920 nativo. Remotion + Three.js, elenco arredondado original, sem Minecraft. História e cenários próprios.

Roteiro em input/narracao.txt; plano em story/shots.json; fontes e limites em research/FATOS-E-LIMITES.md. Voz Puck/modelo aceitos, uma geração em cache, EQ leve, sem acelerar nem mudar o tom. Foley Python com stems e eventos. Dois CTAs em vídeo fornecidos pelo usuário, variantes 5/6, aos 15–22 e 37–44 s.

Pacote YouTube em ../../youtube/40 - Por que ele aponta e fala sozinho/, capa própria e arquivo único YOUTUBE. Sem publicação no YouTube.

Render: `node AiTrends/remotion/scripts/render-fact.mjs --project PROJETO_ABSOLUTO --workers 2 --out PRIVADO/full-silent.mp4`, guardar log em PRIVADO/full-render.log. Áudio: script do projeto ou `AiTrends/.venv/bin/python AiTrends/skill/scripts/facts45_audio.py --project PROJETO --work PRIVADO`. Renderizador usa snapshots locais scenes/world.js e scenes/rig.js; não depende de frames de terceiros. O módulo React compartilhado seleciona o snapshot pelo número do tema.

A voz original fica em cache privado. Para revisar só imagem/capa a partir do Git, decodificar audio/mix.mp3 para WAV local e reutilizar. Não chamar TTS para alterar câmeras ou efeitos. ASR e métricas não equivalem a escuta humana integral. Licenças do kit e fonte Anton preservadas.
