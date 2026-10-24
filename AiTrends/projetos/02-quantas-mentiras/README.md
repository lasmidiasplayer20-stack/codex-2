# 02 — Quantas mentiras / Então

Animação própria em português, feita com o **aiTrends adaptado deste repositório**. Duração-alvo 8min20s, horizontal, 1920×1080 a 24 fps. Roteiro novo inspirado na premissa enviada pelo usuário; o conflito principal e a narração foram reescritos. Nenhum frame da referência é usado no filme.

## Arquivos

- `ROTEIRO.md`: narração e capítulos; `input/narracao.txt`: somente o texto falado.
- `story/bible.md`, `story/beats.json`, `story/shots.json`: direção e 128 planos.
- `scenes/`: elenco, cenários, poses, objetos, cenas 2D/2,5D, estabelecimentos 3D e CTAs por código.
- `audio/`: narração Puck tratada, mix e evidências de qualidade (quando concluídos).
- `timeline/legendas-provisorias.srt`: legendas de leitura estimadas por frase, não timestamps exatos de palavras.
- `exports/`: MP4 completo e prévia, após validação.
- Capa, título, descrição e tags: `../../../Animação/youtube/02 - Quantas mentiras/`.

## Reproduzir a animação sem chamar APIs

Na raiz do repositório:

```bash
python3 AiTrends/studio.py doctor
python3 AiTrends/studio.py aitrends --project "$PWD/AiTrends/projetos/02-quantas-mentiras" --sheet --scale 0.3
node AiTrends/projetos/02-quantas-mentiras/scripts/render-fast.mjs --project "$PWD/AiTrends/projetos/02-quantas-mentiras" --scale 1 --workers 2 --format jpeg --ff-grade --crf 20 --preset fast --out /tmp/mentiras-silencioso.mp4
```

O adaptador deriva do renderizador incluído no aiTrends: mesmo player, registro de cenas, rig, fontes, estilos e biblioteca Three.js. Captura o canvas final diretamente e usa Canvas 2D em software para evitar rasterização 2D em SwiftShader. A opção `--ff-grade` desloca o LUT da paleta midnight para FFmpeg e omite o grão para acelerar e reduzir compressão; não aumenta a resolução de uma imagem menor. Como a correção passa após a vinheta, há uma pequena diferença de ordem de composição em relação ao renderizador original. As cenas 3D continuam renderizadas em 1920×1080, com bloom desativado e sombras de 1024 para CPU.

Não execute `scripts/build_story.py` depois de alinhar a voz sem intenção de refazer a temporização: ele restaura a montagem textual inicial. O script `treat_voice.py` usa limites reais dos oito trechos e aproxima os limites dos parágrafos com energia de áudio e proporção do texto. Não é alinhamento por reconhecimento de cada palavra.

## Voz e som

O áudio existente pode ser reutilizado sem chamadas de API. Regeneração é uma ação separada: `generate_voice.py` exige `GEMINI_API_KEY` no ambiente e diretório privado em `--work`; usa a voz Puck. Nunca cole a chave no projeto. A autorização do usuário foi dada nesta conversa para usar a chave do ambiente; o projeto não configura cobrança nem contrata serviço. Modelos e quotas precisam estar disponíveis na conta. O verificador opcional `audit_voice.py` também faz chamadas ao Gemini e não integra a reprodução local comum.

Música e efeitos: `scripts/sound.py --seconds 500 --output /tmp/trilha.mp3`, usando o Python de `AiTrends/.venv`. O arquivo gerado não contém fala. A montagem final precisa combinar narração e trilha; vídeo silencioso não é o produto narrado. Os scripts verificam saídas e os exports finais são inspecionados com FFprobe e decodificação completa do FFmpeg.

## Origem e direitos dos recursos

Cenários, props, CTAs, composição e história deste projeto são código/texto novos. Motor e rig são do pacote aiTrends fornecido pelo usuário, com suas condições originais preservadas; esta pasta não concede novos direitos sobre o kit. As fontes Fredoka, Nunito e Playfair Display vêm das dependências `@fontsource` do kit, sob suas licenças OFL; preserve os avisos de licença ao redistribuir as fontes. Nenhum ícone, foto, vídeo de estoque ou modelo 3D externo foi incorporado. Não foi usado After Effects ou Blender.
