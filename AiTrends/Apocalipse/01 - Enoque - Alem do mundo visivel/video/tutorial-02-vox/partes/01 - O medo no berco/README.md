# Parte 01 — O medo no berço

Plano ajustado à escolha do usuário: **15 cenas × 4 s = 60 s**, 1920×1080, 24 fps. Imagens: Nano Banana 2 no Flow. Animação: Omni disponível no Flow. Narração: primeira Algenib aprovada, reaproveitada sem geração de voz.

- `LOTE-IMAGENS-01-10.txt` e `LOTE-IMAGENS-11-15.txt`: prompts de imagens em dois lotes.
- `ANIMAR-15-CENAS.txt`: orientação e movimentos por cena.
- `plano-01.json`: grade, prompts e referências aos arquivos.
- `clips/001.mp4` a `015.mp4`: destinos esperados, ainda sem clipes reais.

A composição dos recortes converge para a imagem final. Solicitar quatro segundos ao gerador quando disponíveis; se ele exportar mais, escolher na edição uma janela de quatro segundos que preserve o movimento e a leitura final, sem acelerar ou congelar. O modelo não foi testado na conta e sua duração nativa não está confirmada.

O plano temporal segue a escolha de quatro segundos por cena. A relação de cada imagem com a frase naquele instante ainda precisa de conferência com reprodução e clipes reais. É possível reordenar ou revisar a arte para acertar o sentido, mantendo a grade e a narração.

A conta paga foi informada pelo usuário. Não há ferramenta conectada à conta Flow neste chat; imagens e animações não foram geradas. Os prompts podem ser usados pelo agente do Flow. O montador local pode receber os clipes baixados e montar o minuto.

Da raiz do repositório, conferir o plano com o `assemble.py` de `video/tutorial-flow/`, usando `--plan` para este `plano-01.json` e `--check`. O modo de prévia aceita `--allow-draft-preview`; a finalização exige revisar a associação fala/imagem e marcar a temporização como pronta.
