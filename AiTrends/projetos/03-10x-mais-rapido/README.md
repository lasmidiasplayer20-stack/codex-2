# 03 — E se você fosse 10× mais rápido?

**Estado desta revisão:** fontes, áudio tratado e pacote YouTube prontos; MP4 completo em renderização. Links de export/QA serão preenchidos após a validação.

Episódio original do canal **Então**, feito por código com o aiTrends/Three.js: Nico (menta) e Lia (violeta) exploram velocidade, percepção, curvas, frenagem e convivência. Projeto horizontal, 8min30, 24 fps, render nativo 1920×1080.

- [Roteiro](ROTEIRO.md), [bíblia visual](story/bible.md) e [referência/hipóteses](REFERENCIA.md).
- [Vídeo completo](exports/03%20-%2010x%20Mais%20Rápido.mp4) e [preview de um minuto](exports/03%20-%2010x%20Mais%20Rápido%20-%20Preview%201min.mp4).
- [Pacote YouTube](../../youtube/03%20-%2010x%20Mais%20Rápido/).
- [Skill reutilizável e comandos](../../skill/SKILL.md). Leia também `AiTrends/README-CODEX.md` e a skill original adaptada.

A voz Puck usa a chave somente do ambiente. Arquivos `audio/narracao.mp3`, `trilha.mp3` e `mix.mp3` permitem render offline sem chamar a API novamente. O áudio não contém instruções técnicas. A duração foi ajustada por tratamento moderado; os limites internos das sequências são aproximados por texto/energia, não alinhamento por palavra.

Reprodução da imagem, da raiz do repositório:

```bash
python3 AiTrends/studio.py doctor
node AiTrends/skill/scripts/render.mjs --project /workspace/codex-2/AiTrends/projetos/03-10x-mais-rapido --scale 1 --workers 2 --format jpeg --preset fast --crf 20 --out /tmp/full-silent.mp4
```

Para remontar áudio a partir do WAV tratado local: `AiTrends/.venv/bin/python AiTrends/skill/scripts/sound.py --project /CAMINHO/ABSOLUTO/PROJETO`. WAVs/intermediários não são versionados; para remontar sem API, decodifique o MP3 tratado existente. Antes de exportar use `skill/scripts/export.py`, com log de render bem-sucedido. Não repita `scripts/build_story.py` depois de temporizar a voz: ele recria os tempos iniciais.

Consulte `qa/export-validation.json` para dimensões, quadros, duração, SHA e cobertura real de validação. A folha `qa/filme-completo.jpg` é extraída do próprio MP4 entregue.

Neste episódio, os trechos 1–7 usam `gemini-3.1-flash-tts-preview`; após a cota diária esgotar, o trecho 8 usa `gemini-2.5-flash-preview-tts`, ambos com Puck. O tratamento comum reduz diferenças de volume; isso não garante identidade acústica perfeita entre modelos. Não houve habilitação de cobrança. A transcrição independente ficou indisponível (serviço remoto e download do Whisper); o relatório registra essa limitação, sem alegar conferência integral da fala.
