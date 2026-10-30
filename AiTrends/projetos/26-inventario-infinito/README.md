# 26 — Cabe tudo, menos ordem

Short original de 25 s, 600 quadros a 24 fps, vertical 1080×1920 nativo. Continuação autorizada no estilo voxel do episódio 25, com nossos personagens e sem abertura “E se”. Animação aiTrends/Three.js inteiramente por código, onze takes, sem Blender ou imagens importadas nas cenas. Capa ilustrada separada do filme.

Nico guarda objetos enormes no inventário. Quando chove, não consegue encontrar a própria casa entre os itens e tira o sofá e a bicicleta. Geometria, personagem, objetos, cenário, partículas, chuva e ícones produzidos por código. Não são usados personagens, skins ou texturas de Minecraft.

## Voz e som

Mesma Puck / gemini-2.5-flash-preview-tts / generateContent e direção aceita. Uma geração de 24,210958 s preservada em cache privado, sem acelerar nem mudar tom. Pequenos espaços adicionados somente em silêncios existentes para fechar 25 s. EQ leve, ganho medido por fonte, sem compressão extra. Foley Python e stems: inventário/objetos, chuva contínua, sofá, bicicleta e interação com menu. Métricas não comprovam naturalidade e não é alegada audição humana integral.

Um CTA em vídeo, variante 6 fornecida pelo usuário, em 18–25 s, largura 900 px, x90/y1440, chroma key e despill somente no asset, áudio original omitido. Dois CTAs consumiriam tempo excessivo neste short; mantém o formato do episódio 25.

## Reprodução

Da raiz: `python3 AiTrends/studio.py doctor`, setup só se faltar dependência. Áudio com voz em cache privado: `AiTrends/.venv/bin/python AiTrends/projetos/26-inventario-infinito/scripts/audio.py --work /CAMINHO/PRIVADO` (voice/block-01.wav). Não regenerar fala para corrigir cena/mix. Chaves e WAV bruto não são publicados.

Render: `node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/26-inventario-infinito" --scale 1 --workers 2 --format jpeg --preset fast --crf 20 --out /CAMINHO/PRIVADO/full-silent.mp4`, guardando log em full-render.log no mesmo diretório. Finalização: `AiTrends/.venv/bin/python AiTrends/projetos/26-inventario-infinito/scripts/finish.py --work /CAMINHO/PRIVADO`, com mix.wav local disponível. Stems MP3 publicados. Licenças do kit original preservadas.

Entrega em exports/, prévia de 10 s e QA em qa/. Pacote em ../../youtube/26 - Cade minha casa/ com capa vertical e arquivo único YOUTUBE. Publicação no GitHub, sem upload ao YouTube.

## Validação final

MP4 final: 25,000 s, 600 quadros, 24 fps, 1080×1920 nativo, áudio presente e decodificação integral sem erros. Prévia: 10 s / 240 quadros na mesma resolução. Áudio medido no MP4: −19,2 LUFS, pico verdadeiro −4,1 dBFS; maior silêncio detectado na mix 0,73 s. Revisão visual dos quadros extraídos do arquivo final cobre os onze takes, objetos encolhendo, plano da casa vazia, chuva, inventário, sofá/bicicleta e CTA. Piloto nativo da casa/chuva revisado antes do render completo. Auditoria numérica em 44 instantes: zero erros de execução ou matrizes não finitas; não equivale a validação física completa. Não é alegada audição humana integral nem transcrição independente.
