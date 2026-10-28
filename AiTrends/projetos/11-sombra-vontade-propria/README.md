# 11 — E se sua sombra tivesse vontade própria?

Short original do Então: **60segundos exatos, vertical1080×1920,24fps,1440quadros nativos**. Exportação concluída e validada; evidências em qa/export-validation.json.

- [MP4 completo — também serve como prévia de um minuto](exports/11%20-%20E%20se%20sua%20sombra%20tivesse%20vontade%20pr%C3%B3pria.mp4)
- [Capa vertical e arquivo único YOUTUBE](../../youtube/11%20-%20E%20se%20sua%20sombra%20tivesse%20vontade%20pr%C3%B3pria/)
- [Roteiro](ROTEIRO.md), cenas e rig em scenes/, Foley e montagem em scripts/.

## Cenário e ação

Rua original colorida com fachadas coral/turquesa/lilás/amarelo, toldos, flores, árvores, bancos, bicicleta, nuvens e borboletas discretas. Piso claro preserva a leitura da sombra.21planos com deslocamento independente, aceno/cruzar braços, tentativa de pisar, aviso, janela, salto e vaso de cerâmica cartoon. A sombra é geometria do nosso rig projetada no piso, sem imagem de silhueta ou Blender. Hipótese declaradamente fictícia.

Puck/modelo aceitos, uma geração51,571s, sem acelerar/mudar tom. Tratamento suave com EQ e ganho estático. Música e efeitos Python específicos: passos, tecido, batidas da sombra, cerâmica e cliques/sino discretos. Sem escuta humana integral nem ASR independente; limites em QA.

## CTA fornecido pelo usuário

Trecho4,7–11,7s da primeira animação do vídeo da pasta Drive, salvo em assets/cta-green.mp4. Chroma key e despill aplicados somente ao CTA, preservando a roupa mint dos personagens. Janela de650px; desenho principal ocupa cerca de metade da largura do short, posicionado na zona inferior, em43–50s e53–60s. Áudio original do asset não misturado; cliques/sino feitos em Python. Origem e recorte em assets/cta-provenance.json. O CTA é uma exceção explícita solicitada ao uso de assets externos; as demais cenas são procedurais.

## Reproduzir

Dependências: python3 AiTrends/studio.py doctor. Reutilizar audio/*.mp3 sem chamar API. Cache de voz bruto em pasta privada: scripts/generate_voice.py --work PASTA_PRIVADA/voice, chave só via ambiente, somente se nova geração for necessária/autorizada. Tratamento: AiTrends/.venv/bin/python scripts/audio.py --work PASTA_PRIVADA. Temporização aproximada: scripts/align_plan.py, somente antes de congelar/renderizar.

Render: node AiTrends/skill/scripts/render.mjs --project CAMINHO_ABSOLUTO --scale 1 --workers 2 --format jpeg --out PASTA_PRIVADA/full-silent.mp4; salvar log em full-render.log. Montagem: scripts/finish.py --work PASTA_PRIVADA, usando mix.wav privado e asset do CTA; exige fonte congelada e verifica resolução, duração,1440quadros, decode completo e picos. Pode-se decodificar mix.mp3 para WAV para remontar sem API.

WAVs/build privados fora do Git. Capa original vertical gerada separadamente; não é usada como frame. Não publicado no YouTube.
