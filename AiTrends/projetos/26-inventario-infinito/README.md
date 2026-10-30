# 26 — Cabe tudo, menos ordem

Short original de 25 s, 600 quadros a 24 fps, vertical 1080×1920 nativo. Modelo clássico de Minecraft com skins próprias, seguindo a correção visual solicitada para os episódios 25 e 26, com nossos personagens e sem abertura “E se”. Animação aiTrends/Three.js inteiramente por código, onze takes, sem Blender; skins e texturas PNG próprias geradas por código. Capa ilustrada separada do filme.

Nico guarda objetos enormes no inventário. Quando chove, não consegue encontrar a própria casa entre os itens e tira o sofá e a bicicleta. Geometria, personagem, objetos, cenário, partículas, chuva e ícones produzidos por código. Não são usados personagens, skins ou texturas de Minecraft.

## Voz e som

Mesma Puck / gemini-2.5-flash-preview-tts / generateContent e direção aceita. Uma geração de 24,210958 s preservada em cache privado, sem acelerar nem mudar tom. Pequenos espaços adicionados somente em silêncios existentes para fechar 25 s. EQ leve, ganho medido por fonte, sem compressão extra. Foley Python e stems: inventário/objetos, chuva contínua, sofá, bicicleta e interação com menu. Métricas não comprovam naturalidade e não é alegada audição humana integral.

Um CTA em vídeo, variante 6 fornecida pelo usuário, em 18–25 s, largura 900 px, x90/y1440, chroma key e despill somente no asset, áudio original omitido. Dois CTAs consumiriam tempo excessivo neste short; mantém o formato do episódio 25.

## Reprodução

Da raiz: `python3 AiTrends/studio.py doctor`, setup só se faltar dependência. Áudio com voz em cache privado: `AiTrends/.venv/bin/python AiTrends/projetos/26-inventario-infinito/scripts/audio.py --work /CAMINHO/PRIVADO` (voice/block-01.wav). Não regenerar fala para corrigir cena/mix. Chaves e WAV bruto não são publicados.

Render: `node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/26-inventario-infinito" --scale 1 --workers 2 --format jpeg --preset fast --crf 20 --out /CAMINHO/PRIVADO/full-silent.mp4`, guardando log em full-render.log no mesmo diretório. Finalização: `AiTrends/.venv/bin/python AiTrends/projetos/26-inventario-infinito/scripts/finish.py --work /CAMINHO/PRIVADO`, com mix.wav local disponível. Stems MP3 publicados. Licenças do kit original preservadas.

Entrega em exports/, prévia de 10 s e QA em qa/. Pacote em ../../youtube/26 - Cade minha casa/ com capa vertical e arquivo único YOUTUBE. Publicação no GitHub, sem upload ao YouTube.

## Refação visual solicitada pelo usuário

A versão anterior foi reprovada por parecer voxel genérico. Esta revisão troca o personagem por um modelo de proporções clássicas Minecraft: cabeça 8×8×8, tronco 8×12×4, braços e pernas 4×12×4, membros retos e inteiriços. Não há cotovelos, joelhos segmentados, mãos arredondadas ou sapatos modelados separadamente. Skins próprias 64×64 no padrão Java clássico de braços com 4 pixels, disponíveis em assets/skins/; Nico verde-água e Lia lavanda. Rostos em pixels, filtro nearest, sem suavização das texturas.

Vila e chão construídos com blocos de 1 unidade, grama/terra, troncos/tábuas, pedra e vidro; texturas originais 16×16 em assets/textures/. A casa guardada no inventário também foi refeita com blocos texturizados. Materiais e personagens não são assets oficiais extraídos do jogo. É uma animação renderizada por código, não captura de gameplay.

As narrações, músicas e efeitos publicados permanecem idênticos byte a byte; não houve chamada de TTS nesta refação. A conferência dos hashes está em qa/minecraft-remake.json. Duração, roteiro, cortes e CTA foram preservados. As versões anteriores continuam recuperáveis no histórico do Git.

Gerar novamente as skins e texturas próprias: `AiTrends/.venv/bin/python AiTrends/projetos/26-inventario-infinito/scripts/build_minecraft_assets.py`. A semente é fixa.

## Validação desta refação

MP4 novo: 25,000 s / 600 quadros / 24 fps / 1080×1920 nativo, áudio presente, decodificação integral aprovada. Prévia de 10 s / 240 quadros, mesma resolução. Quadros do MP4 final revisados cobrindo todos os takes, ações e CTA; auditoria numérica em 44 instantes sem erros de execução ou matrizes não finitas.

Áudio final: -19,2 LUFS, pico verdadeiro -4,1 dBFS. O fluxo AAC é idêntico ao do MP4 anterior; hashes dos stems MP3 também idênticos. Zero chamadas TTS nesta refação. Não é alegada audição humana integral ou ASR independente.

SHA-256 do MP4: `bc86776eea12321969c513b5f0e1486c5b1ea8e24d6a7d994468e3bb04c99336`.
