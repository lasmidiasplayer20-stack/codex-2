# 28 — NÃO APERTA DE NOVO!

Short original de 15,000 s / 360 quadros / 24 fps / 1080×1920 nativo. Título sem nome de personagem, conforme pedido. Ação contínua em Minecraft clássico, skin própria do Nico; botão dispara uma sequência de pistões, slime e água que devolve o personagem à posição inicial.

## Loop comprovado

O primeiro e o último quadro do MP4 final foram decodificados em RGB e comparados integralmente: **zero pixels diferentes**, diferença máxima por canal **0**. PNGs em qa/primeiro-quadro.png e qa/ultimo-quadro.png; resultado em qa/loop-boundary.json. O teste dos PNGs nativos da cena, antes da codificação, também registrou igualdade em qa/source-loop-boundary.json.

A cena usa quadro módulo 359: com 360 quadros totais, o estado do quadro 359 é o mesmo do quadro 0. Todos os movimentos, expressões e mecanismos usam essa fase, com câmera e iluminação fixas. O finalizador ainda copia o quadro inicial para a posição final para proteger a igualdade contra variações da compressão intermediária. Encode H.264 compatível em yuv420p, QP constante e IDRs nas duas extremidades com mesmo QP, sem AQ/psy/mbtree/B-frames ou fade. O teste é no MP4 de entrega, não apenas no projeto.

A prévia exports/preview-emenda-4s.mp4 mostra os últimos dois segundos seguidos dos primeiros dois, sem pausa inserida. O filme principal continua tendo exatamente 15 segundos.

## Áudio e CTA

Mesma Puck / gemini-2.5-flash-preview-tts / generateContent e direção aceita. Uma geração em cache. Foram encurtados somente silêncios detectados; palavras preservadas, sem mudar velocidade ou tom. EQ suave e ganho estático, sem compressão extra. Voz curta: “Era só não apertar. Agora aguenta.” Os mecanismos e a trilha acompanham a ação restante; não há locução contínua nos 15 s.

Foley sintetizado em Python, stems publicados: botão, pistões, impulso, slime, água, saída e passos. Música com número inteiro de ciclos e primeiro/último sample PCM coincidentes; eventos terminam antes da emenda. AAC é o codec de distribuição, não se afirma igualdade bit a bit do PCM após essa compressão. Não é alegada audição humana integral nem ASR independente.

Um CTA em vídeo variante 6 fornecida pelo usuário, em 4,5–11,5 s, 650 px em x215/y1640, áudio original omitido, key/despill apenas no asset. Está ausente tanto no primeiro quanto no último quadro. Marca Então constante. Capa e arquivo único YOUTUBE em ../../youtube/28 - Nao aperta de novo/.

## Reproduzir

Animação aiTrends/Three.js por código, sem Blender ou imagens geradas nas cenas. Skins/texturas próprias geradas em Python, filtro nearest; licenças do kit preservadas. Capa ilustrada gerada separadamente. Não é captura de gameplay ou mecanismo testado no Minecraft.

Da raiz: `python3 AiTrends/studio.py doctor`; setup só se faltar dependência. Voz em cache privado: `AiTrends/.venv/bin/python AiTrends/projetos/28-botao-errado-loop/scripts/audio.py --work /CAMINHO/PRIVADO`, com voice/block-01.wav. Não regenerar voz para corrigir imagens, emenda ou mix. Chaves e fonte bruta não são publicadas; stems MP3 disponíveis.

Render: `node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/28-botao-errado-loop" --scale 1 --workers 2 --format jpeg --preset fast --crf 20 --out /CAMINHO/PRIVADO/full-silent.mp4`, guardando log full-render.log no mesmo diretório. Finalizar com `AiTrends/.venv/bin/python AiTrends/projetos/28-botao-errado-loop/scripts/finish.py --work /CAMINHO/PRIVADO`, com mix.wav local. Fonte congelada inclui módulos, skins e texturas. Entrega e QA em exports/ e qa/; sem upload ao YouTube.

## Validação da entrega

15,000 s, 360 quadros a 24 fps, 1080×1920 nativo; áudio presente e decodificação integral sem erros. Primeiro e último quadro decodificados do MP4: diferença máxima 0 e zero pixels diferentes. Quadros finais revisados em todas as fases e na emenda; auditoria numérica em 61 instantes sem erros de execução ou matrizes não finitas. Não é uma simulação física completa.

H.264 High, 4:2:0 de 8 bits em faixa completa (FFprobe identifica como yuvj420p). Áudio final medido: −19,5 LUFS, pico verdadeiro −4,2 dBFS. Prévia da emenda: 4 s / 96 quadros / 1080×1920, decodificação aprovada. Os samples inicial e final da mix PCM são coincidentes; métricas não substituem audição humana integral.

SHA-256 do MP4: `e060de870795d758289e4d65ac5f15e7a01b83930fea773d02777d085f2af16e`.
