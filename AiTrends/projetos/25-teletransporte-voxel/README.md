# 25 — Quem saiu da cabine?

Short original de 25 segundos, 600 quadros a 24 fps, vertical 1080×1920 nativo. Primeiro episódio do canal Então com nossos personagens adaptados ao estilo voxel inspirado em Minecraft. Animação Three.js/aiTrends inteiramente por código, sem Blender ou imagens importadas nas cenas. Cabeças, membros, expressões, cidades, cabines e mapa construídos proceduralmente. A capa é uma ilustração gerada separadamente.

Abertura: “Um segundo até Tóquio. Mas quem sai do outro lado?” Onze takes, transmissão em mapa e pergunta final sobre continuidade da identidade. Ficção; a máquina não representa uma tecnologia real nem explica teletransporte quântico.

## Áudio

Mesma Puck / gemini-2.5-flash-preview-tts / generateContent, direção aceita. Uma geração, cache privado, sem alterar velocidade ou tom. EQ leve e correção lenta calculada para esta fonte; sem compressão adicional. Foley Python obrigatório: passos, leitura elétrica, dados em trânsito, reconstrução e botão, stems e eventos publicados em audio/. Não regenerar voz para corrigir imagens ou mix. Métricas não substituem audição humana integral, que não é alegada.

Um CTA em vídeo fornecido pelo usuário, variante 6, entre 18 e 25 s, largura 900 px centralizada em x90/y1440, chroma key e despill somente no asset, sem áudio original. Um CTA em vez de dois para preservar tempo narrativo neste short de 25 s.

## Reprodução

Da raiz do repositório: `python3 AiTrends/studio.py doctor`; setup só se faltarem dependências. Para áudio, `AiTrends/.venv/bin/python AiTrends/projetos/25-teletransporte-voxel/scripts/audio.py --work /CAMINHO/PRIVADO`, com voice/block-01.wav já em cache. As chaves nunca são publicadas.

Render: `node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/25-teletransporte-voxel" --scale 1 --workers 2 --format jpeg --preset fast --crf 20 --out /CAMINHO/PRIVADO/full-silent.mp4`, salvando o log como full-render.log no mesmo diretório. Finalização: `AiTrends/.venv/bin/python AiTrends/projetos/25-teletransporte-voxel/scripts/finish.py --work /CAMINHO/PRIVADO`. Mix WAV local é necessário; MP3s dos stems são publicados. Licenças e atribuições do kit original permanecem válidas.

Entrega em exports/ e QA em qa/. Prévia de 10 s; filme completo de 25 s. Capa e arquivo único YOUTUBE em ../../youtube/25 - Quem saiu da cabine/. Publicação no GitHub, sem upload ao YouTube.

## Validação final

MP4: 25,000 s / 600 quadros / 24 fps / 1080×1920 nativo, com áudio; decodificação integral sem erros. Prévia: 10 s / 240 quadros, mesma resolução. Áudio final medido: −19,0 LUFS / pico verdadeiro −3,7 dBFS. Maior silêncio detectado na mix: 0,93 s. Uma geração de voz preservada, sem acelerar. Auditoria numérica em 44 instantes: zero erros de execução ou matrizes não finitas; não é uma validação física completa. Revisão visual dos quadros extraídos do MP4 final cobre os onze takes, entrada, leitura, percurso, reconstrução, expressões e CTA. Não se alega escuta humana integral nem transcrição independente.
