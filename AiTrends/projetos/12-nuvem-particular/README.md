# 12 — E se uma nuvem seguisse só você?

Short original do Então: **60 segundos exatos, vertical1080×1920,24 fps,1440 quadros nativos**. Exportação concluída e validada; evidências em qa/export-validation.json.

- [MP4 completo — também é a prévia de um minuto](exports/12%20-%20E%20se%20uma%20nuvem%20seguisse%20s%C3%B3%20voc%C3%AA.mp4)
- [Capa vertical e arquivo único YOUTUBE](../../youtube/12%20-%20E%20se%20uma%20nuvem%20seguisse%20s%C3%B3%20voc%C3%AA/)
- [Roteiro](ROTEIRO.md), cenas/rig em scenes/, efeitos/montagem em scripts/.

## Ação e cenário

Rua colorida própria do Então, com fachadas, toldos, flores, árvores, bicicleta, nuvens e borboletas.20 planos: nuvem particular, corrida e mudança de direção, guarda-chuva com bloqueio de gotas, chuva lateral nos tênis, jardim murcho, irrigação, solo escurecendo, flores erguendo-se e arco-íris em miniatura. Nico/Lia e nuvem modelados por geometria/código, sem Blender ou imagens nas cenas. A premissa e a recuperação rápida das flores são fantasia explícita.

Chuva:72 instâncias de gotas finas, animação contínua, pequenos anéis no chão e poças ancoradas ao cenário. Guarda-chuva preso à palma após IK; varetas/dossel fecham juntos. Roupa molhada é geometria de cor aplicada ao personagem.

Puck/modelo aceitos, uma chamada de 51,291s, sem alterar velocidade/tom. EQ leve, ganho estático, harmonia espaçada e Foley Python: chuva discreta, tênis, tecido, pingos e sinos do CTA/arco-íris. Sem alegação de escuta humana integral ou ASR independente.

## CTA atualizado pelo pedido atual

Asset fornecido no Drive e selecionado no11: assets/cta-green.mp4,7s. **Agora maior e centralizado na largura: janela900 px, x90/y1440, em15–22 s e53–60 s.** Chroma key/despill apenas no CTA. O desenho fica na faixa inferior central; texto/rostos permanecem livres. Áudio original do asset não misturado; cliques/sino Python. Origem/recorte em assets/cta-provenance.json. Essa configuração substitui o tamanho650 px/posição esquerda do11 para este short.

## Reproduzir

Rodar python3 AiTrends/studio.py doctor; dependências locais do estúdio. Reutilizar audio/*.mp3 sem chamadas. Para geração autorizada: scripts/generate_voice.py --work PASTA_PRIVADA/voice, chave só via ambiente; preservar cache. Para tratar o cache e produzir WAV/MP3: AiTrends/.venv/bin/python scripts/audio.py --work PASTA_PRIVADA. scripts/align_plan.py altera os tempos e só deve rodar antes do congelamento/render.

Render nativo: node AiTrends/skill/scripts/render.mjs --project CAMINHO_ABSOLUTO --scale 1 --workers 2 --format jpeg --out PASTA_PRIVADA/full-silent.mp4; salvar log em full-render.log. Montagem/QA: scripts/finish.py --work PASTA_PRIVADA, com mix.wav e CTA. Exige fonte congelada; verifica60s/1440 quadros/1080×1920, decode completo, picos e equivalência de nível da mix. Para remontar sem API, decodificar mix.mp3 em WAV.

WAVs/build privados fora do Git. Capa vertical gerada separadamente; não entra como imagem na animação. Não publicado no YouTube.
