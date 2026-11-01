# Enoque — fluxo visual inspirado no tutorial

**Método preparado; clipes de vídeo ainda não gerados.** A proposta é manter integralmente a Algenib aprovada, gerar tomadas visuais no Flow e fazer a montagem final por código. Não foram acionados créditos de vídeo.

## Arquivos

- [Análise do tutorial](ANALISE-TUTORIAL.md): etapas, recursos observados e limites do que foi demonstrado.
- [Storyboard do primeiro minuto](STORYBOARD-01.md): oito tomadas, ações e movimentos de câmera.
- [Plano e prompts do piloto](piloto-01.json): IDs, caminhos, durações e descrição constante dos personagens.
- [Instrução para o Tool Builder do Flow](FLOW-PROMPT.txt): especificação original de uma ferramenta que gere somente o visual.
- [Índice das 25 partes](capitulos-25.json): referências aos WAVs e ao texto definitivo, sem regravar voz.
- [Montador local](assemble.py): Python + FFmpeg, sem chamadas a APIs.
- [Teste técnico do montador](qa-assembly-test.json): 2 s com duas imagens sólidas sintéticas e a narração existente; não é um piloto visual gerado pelo Flow.

## Produção proposta

1. Conferir acesso ao Google Flow e ao menu de ferramentas na conta. A sessão autenticada não está disponível neste ambiente; a chave Gemini não substitui esse login.
2. Usar a especificação para construir a ferramenta, ou inserir os prompts nas ferramentas de geração realmente disponíveis. Essa etapa Flow ainda não foi testada na conta.
3. Produzir somente os oito clipes do piloto, mantendo personagens e figurino. Os nomes esperados são `clips/001.mp4` até `008.mp4`.
4. Refinar os cortes ouvindo a narração: os slots atuais de 7,5 s são planejamento inicial, não alinhamento comprovado de palavras. Ajustar pontos de entrada e durações sem alterar os 60 s totais. Se necessário, gerar continuação ou uma segunda tomada; não congelar nem repetir o movimento para completar tempo.
5. Montar e revisar o minuto em movimento. Checar articulações, progresso dos passos, consistência de rosto/roupa, estabilidade da luz e relação entre fala e imagem.
6. Aplicar o método às demais partes. Uma média de 7,5 s indica cerca de 200 tomadas para 25 minutos; a contagem final depende da narrativa. Os 25 planos completos de cenas ainda não foram escritos.
7. Na finalização do vídeo, acrescentar Foley procedural Python e, se usado, ambiente musical discreto em faixa separada, preservando a voz já tratada. O montador atual trabalha apenas com os clipes e a narração; essa camada de som fica para a etapa de vídeo.

## Executar a montagem

A partir desta pasta:

```bash
python3 assemble.py --plan piloto-01.json --check
python3 assemble.py --plan piloto-01.json --allow-draft-preview --work /tmp/enoch-pilot-build --out piloto-01.mp4
```

`--check` lista clipes faltantes e confere durações sem gerar conteúdo. `--allow-draft-preview` identifica o resultado como piloto com temporização provisória. Após conferir os cortes de verdade, marcar `timing_status` como `ready` no plano e montar sem essa opção. Essa revisão técnica não exige reaprovar a voz já autorizada.

O programa exige vídeo de origem suficiente para cada tomada. Ignora seu áudio, normaliza formato, corta em quadros inteiros e monta em 1920×1080 a 24 fps com a narração externa. Não altera pitch ou velocidade e não cria voz. Saída 1080p não transforma material de origem 720p em detalhe nativo 1080p; preferir baixar os clipes na resolução final quando disponível.

O teste local validou concatenação, 48 quadros/2 s, presença da narração, resolução e decodificação integral. Não prova qualidade do Flow, fidelidade de personagens nem sincronismo visual do roteiro de Enoque, que dependem dos clipes reais.
