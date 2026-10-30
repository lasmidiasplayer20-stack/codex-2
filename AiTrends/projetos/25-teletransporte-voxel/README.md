# 25 — Quem saiu da cabine?

Short original de 25 segundos, 600 quadros a 24 fps, vertical 1080×1920 nativo. Primeiro episódio do canal Então com modelo clássico de Minecraft e skins próprias. Animação Three.js/aiTrends inteiramente por código, sem Blender; skins e texturas PNG próprias geradas por código. Cabeças, membros, expressões, cidades, cabines e mapa construídos proceduralmente. A capa é uma ilustração gerada separadamente.

Abertura: “Um segundo até Tóquio. Mas quem sai do outro lado?” Onze takes, transmissão em mapa e pergunta final sobre continuidade da identidade. Ficção; a máquina não representa uma tecnologia real nem explica teletransporte quântico.

## Áudio

Mesma Puck / gemini-2.5-flash-preview-tts / generateContent, direção aceita. Uma geração, cache privado, sem alterar velocidade ou tom. EQ leve e correção lenta calculada para esta fonte; sem compressão adicional. Foley Python obrigatório: passos, leitura elétrica, dados em trânsito, reconstrução e botão, stems e eventos publicados em audio/. Não regenerar voz para corrigir imagens ou mix. Métricas não substituem audição humana integral, que não é alegada.

Um CTA em vídeo fornecido pelo usuário, variante 6, entre 18 e 25 s, largura 900 px centralizada em x90/y1440, chroma key e despill somente no asset, sem áudio original. Um CTA em vez de dois para preservar tempo narrativo neste short de 25 s.

## Reprodução

Da raiz do repositório: `python3 AiTrends/studio.py doctor`; setup só se faltarem dependências. Para áudio, `AiTrends/.venv/bin/python AiTrends/projetos/25-teletransporte-voxel/scripts/audio.py --work /CAMINHO/PRIVADO`, com voice/block-01.wav já em cache. As chaves nunca são publicadas.

Render: `node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/25-teletransporte-voxel" --scale 1 --workers 2 --format jpeg --preset fast --crf 20 --out /CAMINHO/PRIVADO/full-silent.mp4`, salvando o log como full-render.log no mesmo diretório. Finalização: `AiTrends/.venv/bin/python AiTrends/projetos/25-teletransporte-voxel/scripts/finish.py --work /CAMINHO/PRIVADO`. Mix WAV local é necessário; MP3s dos stems são publicados. Licenças e atribuições do kit original permanecem válidas.

Entrega em exports/ e QA em qa/. Prévia de 10 s; filme completo de 25 s. Capa e arquivo único YOUTUBE em ../../youtube/25 - Quem saiu da cabine/. Publicação no GitHub, sem upload ao YouTube.

## Refação visual solicitada pelo usuário

A versão anterior foi reprovada por parecer voxel genérico. Esta revisão troca o personagem por um modelo de proporções clássicas Minecraft: cabeça 8×8×8, tronco 8×12×4, braços e pernas 4×12×4, membros retos e inteiriços. Não há cotovelos, joelhos segmentados, mãos arredondadas ou sapatos modelados separadamente. Skins próprias 64×64 no padrão Java clássico de braços com 4 pixels, disponíveis em assets/skins/; Nico verde-água e Lia lavanda. Rostos em pixels, filtro nearest, sem suavização das texturas.

Vila e chão construídos com blocos de 1 unidade, grama/terra, troncos/tábuas, pedra e vidro; texturas originais 16×16 em assets/textures/. Materiais e personagens não são assets oficiais extraídos do jogo. É uma animação renderizada por código, não captura de gameplay.

As narrações, músicas e efeitos publicados permanecem idênticos byte a byte; não houve chamada de TTS nesta refação. A conferência dos hashes está em qa/minecraft-remake.json. Duração, roteiro, cortes e CTA foram preservados. As versões anteriores continuam recuperáveis no histórico do Git.

Gerar novamente as skins e texturas próprias: `AiTrends/.venv/bin/python AiTrends/projetos/25-teletransporte-voxel/scripts/build_minecraft_assets.py`. A semente é fixa.

## Validação desta refação

MP4 novo: 25,000 s / 600 quadros / 24 fps / 1080×1920 nativo, áudio presente, decodificação integral aprovada. Prévia de 10 s / 240 quadros, mesma resolução. Quadros do MP4 final revisados cobrindo todos os takes, ações e CTA; auditoria numérica em 44 instantes sem erros de execução ou matrizes não finitas.

Áudio final: -19,0 LUFS, pico verdadeiro -3,7 dBFS. O fluxo AAC é idêntico ao do MP4 anterior; hashes dos stems MP3 também idênticos. Zero chamadas TTS nesta refação. Não é alegada audição humana integral ou ASR independente.

SHA-256 do MP4: `6741bc0e51c174abf0f4cafeacefc406ca6be75471bfd379e7d6d932871fb693`.
