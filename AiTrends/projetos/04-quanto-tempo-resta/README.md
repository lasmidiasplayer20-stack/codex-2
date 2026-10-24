# 04 — Quanto Tempo Resta / Então

**Entrega concluída:** vídeo de 8min30 e prévia de 1 minuto em 1080p nativo. Ambos passaram pela decodificação integral. [Evidências de QA](qa/README.md).

Nico enxerga contadores sobre as pessoas. Uma contagem de oito minutos sobre Dona Sol transforma uma noite de leitura na biblioteca em um mistério. História original de ficção, 8min30, horizontal, 1920×1080 nativo, 24 fps.

- [Roteiro](ROTEIRO.md), [bíblia de produção](story/bible.md) e [análise da referência](REFERENCIA.md).
- [Vídeo completo](exports/04%20-%20Quanto%20Tempo%20Resta.mp4) e [preview de 1 minuto](exports/04%20-%20Quanto%20Tempo%20Resta%20-%20Preview%201min.mp4).
- [Capa, título, descrição e tags](../../youtube/04%20-%20Quanto%20Tempo%20Resta/).
- [Skill reutilizável](../../skill/SKILL.md).

Personagens, cenários, câmera, rostos, contadores e efeitos do filme são gerados por JavaScript/Three.js e Canvas no aiTrends. O rig mantém comprimentos fixos e resolve braços em 3D. As ações usam tempo global por sequência e os props consultam as palmas mundiais. Os cenários incluem piso, livros, móveis e paredes para os contraplanos; nenhuma imagem de fundo ou frame de terceiros foi importado para o filme.

Voz autorizada: Gemini Puck em português brasileiro, oito trechos do mesmo modelo `gemini-2.5-flash-preview-tts`. Tratamento local reduz pausas, nivela volume e ajusta moderadamente a duração preservando o tom. O roteiro enviado à API contém apenas fala, sem instruções técnicas. Os MP3s tratados em `audio/` permitem reaproveitamento offline. Música/Foley originais: `scripts/sound.py`, NumPy e FFmpeg.

Reprodução, da raiz do repositório:

```bash
python3 AiTrends/studio.py doctor
node AiTrends/skill/scripts/render.mjs --project /workspace/codex-2/AiTrends/projetos/04-quanto-tempo-resta --scale 1 --workers 2 --format jpeg --preset fast --crf 23 --out /tmp/full-silent-1080.mp4
```

Guarde o log como `WORK/full-render.log`; use `AiTrends/skill/scripts/export.py --project PROJETO --silent /tmp/full-silent-1080.mp4 --work WORK` para montar com `audio/mix.mp3`, exportar preview e validar o arquivo inteiro. Para recriar `narracao.wav` sem API, decodifique `audio/narracao.mp3`. Só execute `scripts/build_story.py` para refazer o storyboard inicial: ele substitui a temporização já tratada.

`qa/export-validation.json` registra dimensões, duração, quadros, SHA e a checagem do arquivo completo; a folha final vem do próprio MP4 entregue. Limite da revisão de fala: foi conferido texto/cache e sinal, sem ASR independente integral nem escuta humana. A temporização interna das frases usa proporção de texto e mínimos próximos de energia, não alinhamento exato por palavra.
