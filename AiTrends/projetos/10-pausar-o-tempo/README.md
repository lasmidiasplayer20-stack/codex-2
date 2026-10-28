# 10 — E se você pudesse pausar o tempo?

Short original do Então, **60segundos exatos, vertical1080×1920,24fps,1440quadros nativos**. Exportação concluída e validada tecnicamente; evidências em qa/export-validation.json.

- [MP4 completo](exports/10%20-%20E%20se%20voc%C3%AA%20pudesse%20pausar%20o%20tempo.mp4) — o próprio short serve de prévia de um minuto.
- [Capa vertical e arquivo único YOUTUBE](../../youtube/10%20-%20E%20se%20voc%C3%AA%20pudesse%20pausar%20o%20tempo/).
- [Roteiro](ROTEIRO.md); cenas JavaScript/Three.js no aiTrends e rig Nico/Lia próprios. Sem Blender ou imagens nas cenas.

20planos: relógio, bola/copo suspensos, câmera entre gotas, caminhada/desvio, tentativa de pegar água, resgate e retorno cômico. A pausa de10segundos narrativos é ampliada cinematograficamente e identificada na tela. É fantasia com licença para respirar/enxergar e guiar uma pessoa; objetos permanecem presos ao instante. Não é uma previsão física real.

Puck/modelo aceitos, uma geração54,571s, sem acelerar ou mudar o tom. Mix com EQ suave, ganho estático, música espaçada e Foley Python: relógio, passos, tecido, água e retorno do ambiente. Uma revisão local de volume não exige novas chamadas. Não houve escuta humana integral nem ASR independente; as limitações constam em qa/.

## Reprodução

Dependências: AiTrends/studio.py doctor.

1. Reutilizar MP3s prontos em audio/ sem chamar a API. `scripts/generate_voice.py --work PASTA_PRIVADA/voice` somente se gerar for necessário/autorizado; chave exclusivamente via ambiente.
2. Cache bruto→tratamento: AiTrends/.venv/bin/python scripts/audio.py --work PASTA_PRIVADA. `scripts/align_plan.py` altera o plano: só executar antes de congelar a fonte e renderizar.
3. Render nativo: node AiTrends/skill/scripts/render.mjs --project CAMINHO_ABSOLUTO --scale 1 --workers 2 --format jpeg --out PASTA_PRIVADA/full-silent.mp4; salvar log em full-render.log.
4. `scripts/finish.py --work PASTA_PRIVADA` monta áudio e valida60s/1440quadros/1080×1920, decode completo, picos e hash da fonte. Exige mix.wav do tratamento; para apenas montar com o áudio já pronto, decodificar mix.mp3 em WAV sem novas gerações.

WAVs intermediários e build ficam fora do Git. Capa original gerada separadamente, vertical9:16, padrão neon. Não enviada ao YouTube.
