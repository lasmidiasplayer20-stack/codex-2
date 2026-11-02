# Parte 01 — O medo no berço

Plano ajustado à escolha do usuário: **15 cenas × 4 s = 60 s**, 1920×1080, 24 fps. Imagens: Nano Banana 2 no Flow. Animação: Omni disponível no Flow. Narração: primeira Algenib aprovada, reaproveitada sem geração de voz.

- `LOTE-IMAGENS-01-10.txt` e `LOTE-IMAGENS-11-15.txt`: prompts de imagens em dois lotes.
- `ANIMAR-15-CENAS.txt`: orientação e movimentos por cena.
- `plano-01.json`: grade, prompts e referências aos arquivos.
- `clips/001.mp4` a `015.mp4`: destinos esperados; 001 recebido, 002–015 ainda faltantes.

A composição dos recortes converge para a imagem final. Solicitar quatro segundos ao gerador quando disponíveis; se ele exportar mais, escolher na edição uma janela de quatro segundos que preserve o movimento e a leitura final, sem acelerar ou congelar. O modelo não foi testado na conta e sua duração nativa não está confirmada.

O plano temporal segue a escolha de quatro segundos por cena. A relação de cada imagem com a frase naquele instante ainda precisa de conferência com reprodução e clipes reais. É possível reordenar ou revisar a arte para acertar o sentido, mantendo a grade e a narração.

A conta paga foi informada pelo usuário. Não há ferramenta conectada à conta Flow neste chat; imagens e animações não foram geradas. Os prompts podem ser usados pelo agente do Flow. O montador local pode receber os clipes baixados e montar o minuto.

Da raiz do repositório, conferir o plano com o `assemble.py` de `video/tutorial-flow/`, usando `--plan` para este `plano-01.json` e `--check`. O modo de prévia aceita `--allow-draft-preview`; a finalização exige revisar a associação fala/imagem e marcar a temporização como pronta.

## Primeiro clipe recebido

O usuário disponibilizou `enoque-01.mp4` no Drive. Original preservado em `originais/001-flow-original.mp4`. A versão `clips/001.mp4` tem exatamente quatro segundos, 96 quadros, 1080p/24 fps, sem áudio. Foi removido o quadro inicial isolado que mostrava a composição pronta antes de ela desaparecer e ser reconstruída. Uma pausa editorial de três quadros foi acrescentada na composição final já formada; não houve aceleração nem repetição de movimento. A narração permanece intacta para a montagem do minuto completo. Ver `QA-001.json`. Os outros 14 clipes ainda faltam.

O quadro final `imagens/001-referencia-final.png` está disponível como referência visual para os próximos lotes. Os prompts seguintes foram ajustados para adultos e objetos simbólicos e para túnicas/mantos/sandálias em lugar de roupas modernas. A imagem anterior com bebê sofreu bloqueio do Google. Os lotes marcam a cena 001 como concluída para evitar nova geração desnecessária.

## Execução por comando mestre

Usar preferencialmente o [comando mestre e o guia](../../automation/COMO-USAR.md), que incluem referências fixas dos personagens e excluem a cena 001 já concluída. Os lotes de texto anteriores continuam como alternativa de consulta, mas o comando mestre é a versão consolidada com regras de continuidade.
