# 27 — Um bloco por dia

Pedido: criar o tema sugerido com 45 segundos. Short original em português, 1080×1920 nativo, 24 fps / 1080 quadros, dezoito takes. Modelo clássico Minecraft e skin própria do Nico, preservando a correção visual pedida nos episódios 25 e 26. Abertura direta, sem “E se”.

Nico gasta o único bloco do dia e descobre diamantes atrás da pedra. Quando a cota volta, precisa escolher entre o minério e liberar a saída. A cota é uma regra fictícia do episódio, explicitada no vídeo; não descreve uma mecânica do Minecraft padrão. É uma animação por código, não gameplay gravado.

## Construção visual

Three.js via aiTrends local, sem Blender. Cenário, personagem, picareta, minério/cascalho, câmera, HUD, partículas e movimentos por código. Skins próprias 64×64 e texturas originais 16×16, nearest. Nenhum asset oficial do jogo ou frame de referência incorporado. Capa ilustrada gerada separadamente, coerente com o modelo clássico. Licenças originais do kit preservadas.

Cota sincronizada com as duas quebras e o amanhecer; diamante sempre intacto. Um único protagonista evita contornar a regra com um ajudante. Corte lateral/superior de cenário para explicar posições, macro da descoberta, acompanhamento na fuga. Pilotos nativos da mineração e da fuga revisados antes da exportação completa. Não alegar simulação física integral com base apenas em poses amostradas.

## Voz, Foley e CTA

Puck / gemini-2.5-flash-preview-tts / generateContent, mesma direção aceita, uma geração em cache de 39,210958 s. Sem acelerar nem mudar tom. Pequenas inserções somente em pausas detectadas; EQ leve, sem compressão extra. Subida gradual medida de 2,47 dB foi reduzida por correção lenta limitada a 1,5 dB por janela, não AGC rápido. Fonte e tratamento registrados em audio/quality.json e audio/voice-review.json. Métricas não substituem audição humana integral; ela e ASR independente não são alegados.

Foley sintetizado em Python e publicado em stem separado: picareta/pedra, fragmentos, bloqueio da cota, passos, cascalho e fuga. Eventos em audio/sfx-events.json; plano em story/foley.json. Contatos das quebras e sons de queda alinhados às frações da animação, passos à distância da marcha. Trilha discreta. Dois CTAs em vídeo distintos fornecidos pelo usuário (variantes 5 e 6), em 15–22 e 37–44 s; largura 820 px, x130/y1480, áudio original omitido, key/despill somente nos assets.

## Reproduzir

Da raiz: `python3 AiTrends/studio.py doctor`; setup somente se faltar dependência. Recriar skins/texturas-base com `AiTrends/.venv/bin/python AiTrends/projetos/27-um-bloco-por-dia/scripts/build_minecraft_assets.py` e minério/cascalho com `AiTrends/.venv/bin/python AiTrends/projetos/27-um-bloco-por-dia/scripts/build_episode_assets.py`. Sementes fixas.

Áudio com voz em cache privado: `AiTrends/.venv/bin/python AiTrends/projetos/27-um-bloco-por-dia/scripts/audio.py --work /CAMINHO/PRIVADO` (voice/block-01.wav). Não regenerar voz para ajustar cenas ou mix. Chaves e fonte bruta não publicadas; stems MP3 disponíveis.

Render: `node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/27-um-bloco-por-dia" --scale 1 --workers 2 --format jpeg --preset fast --crf 20 --out /CAMINHO/PRIVADO/full-silent.mp4`, guardando log full-render.log no mesmo diretório. Finalizar com `AiTrends/.venv/bin/python AiTrends/projetos/27-um-bloco-por-dia/scripts/finish.py --work /CAMINHO/PRIVADO`, com mix.wav local. Congelamento da fonte inclui módulos, skins e texturas PNG.

Entrega em exports/; prévia 15 s e QA em qa/. Capa e arquivo único YOUTUBE em ../../youtube/27 - Um bloco por dia/. Publicação no GitHub, sem upload ao YouTube.

## Validação da entrega

MP4 final: 45,000 s / 1080 quadros / 24 fps / 1080×1920 nativo, com áudio; decodificação integral aprovada. Prévia: 15 s / 360 quadros, mesma resolução e decodificação sem erros. Quadros extraídos do MP4 final revisados cobrindo os dezoito takes, descobrimento do minério, tentativas, amanhecer, bloqueio/abertura da passagem, fuga e ambos os CTAs. Auditoria numérica em 72 instantes: zero erros de execução, matrizes não finitas ou desvios na ancoragem auditada; não é simulação física integral.

Áudio final: −20,0 LUFS, pico verdadeiro −3,1 dBFS. Maior silêncio detectado na mix: 1,26 s, sem trechos acima de 2 s. Uma geração de voz, sem mudar velocidade ou tom. Métricas de sinal e quadros amostrados não substituem audição humana integral; ela e ASR independente não são alegados.

SHA-256 do MP4: `87dc6ec5849dd4276b44ceae33666681c52f4a73dfec9e46810aa8c8e26842fb`.
