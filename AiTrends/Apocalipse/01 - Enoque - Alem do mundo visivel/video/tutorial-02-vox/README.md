# Tutorial 2 — colagem documental animada

**Especificação atual do usuário:** 25 partes × 60 s, cada uma com 15 cenas de 4 s: 375 cenas no total. Imagens e animações no Flow, com Nano Banana 2 e Omni. Conta paga informada; acesso ao Flow não está conectado ao chat. [Primeiro lote de 15 cenas](partes/01%20-%20O%20medo%20no%20berco/README.md).

Referência solicitada pelo usuário: `tutorial_2.mp4`, ID Drive `1xD6sLbYfCYDhT7RQoHQJzhzUX00F5I_e`. Duração 640,569 s (10min41s), 1280×720. Inspeção de 48 quadros distribuídos pelo vídeo, oito quadros adicionais em resolução original e análise automática da fala integral em quatro trechos. Não houve escuta humana integral, teste ao vivo na conta Flow ou validação dos custos anunciados. O vídeo e a transcrição de terceiros permanecem fora do Git.

## O estilo observado

Colagem editorial/documental: papel envelhecido claro, mapas, imagens recortadas em preto e branco/meio-tom, bordas rasgadas, sobreposição de documentos, sombras de papel, alfinetes, fita, linhas e pontos vermelhos, detalhes em amarelo-mostarda e tipografia informativa. O movimento monta gradualmente a composição: os elementos chegam, se encaixam e formam a imagem final.

Essa referência difere da proposta anterior de personagens ilustrados em cenários pintados, guardada em `../tutorial-flow/`. A imagem de Lameque gerada no chat também pertence àquela outra estética; não deve ser tratada como amostra da colagem deste tutorial.

## Etapas demonstradas

| Tempo aproximado | Conteúdo observado |
|---|---|
| 00:00–03:20 | ChatGPT cria roteiro, divide em beats, escreve prompts de imagens, prompt de animação e ideias de thumbnail. |
| 03:40–04:55 | Comandos de direção visual e envio de prompts em lote ao agente do Flow. |
| 04:56 | O painel afirma ter criado dez imagens com **Nano Banana 2**, em 16:9. Isso identifica o modelo mostrado no tutorial, sem comprovar disponibilidade em toda conta. |
| 05:00–05:40 | Animação das imagens em lotes; em 05:36 o painel mostra **Omni Flash**. A fala automática reconhece o nome como “On Flash”; o quadro resolve a grafia. O autor pede clipes de até seis segundos. |
| 05:10–05:30 | ElevenLabs para gerar voz; esta etapa não é necessária em Enoque. |
| 05:50–06:25 | Alternativa no Qwen: a interface exibe **Qwen3.8-Max**, anexo de imagem e opção **Criar Vídeo**. A animação aparece como resultado. Isso foi observado no tutorial, não testado nesta sessão. |
| 06:40–08:40 | CapCut: narração como base, corte das partes estáticas dos clipes e ajuste de cada imagem à frase efetivamente narrada. |
| 08:50–10:05 | Resultado: colagem documental animada, música discreta e montagem segundo a fala. |
| Final | Exportação escolhida pelo autor em 2K. Nosso alvo já solicitado continua 1080p. |

## Detalhe importante da animação

O texto visível no Qwen define a imagem fornecida como **quadro final**, para o qual a animação converge. O movimento deve preservar a composição, com os recortes entrando como peças de papel. Isso é mais específico do que aplicar apenas zoom à imagem inteira. Não é necessário inventar personagens andando para reproduzir esse tipo de cena.

A descrição completa dos comandos do autor não é legível em todos os trechos; não foi recuperado um pacote original de prompts. Os prompts anexos são reconstruções nossas do método observado.

## Adaptação a Enoque

1. Conservar os 25 WAVs Algenib aprovados. Não trocar para ElevenLabs, gerar outra voz ou aplicar novamente redução de ruído/realce e aumento de volume sobre o áudio já tratado.
2. Dividir a fala em beats visuais. Cada beat informa o trecho narrado, ideia visual, elementos da colagem e a referência textual/histórica que sustenta a informação.
3. Gerar no Nano Banana 2 as composições finais, com aparência consistente. Para o primeiro minuto: berço e família em gravura, ficha de Primeiro Enoque, genealogia, manuscrito e panorama simbólico das visões. Não fabricar manuscritos supostamente autênticos ou citações antigas legíveis.
4. Animar a montagem dos recortes, preservando a composição final. O tutorial usa Flow/Omni Flash e apresenta Qwen como alternativa. Acesso autenticado a esses geradores não está conectado neste ambiente.
5. Juntar os clipes à narração existente, cortando entradas estáticas e ajustando a duração real de cada beat. Isso pode ser feito em Python/Remotion/FFmpeg aqui, em lugar da edição manual do CapCut. Foley Python e trilha discreta entram em camadas separadas.
6. Validar um trecho curto em movimento antes de ampliar o projeto. A aprovação da voz permanece válida; ela não aprova automaticamente a nova estética visual.

A estimativa inicial para clipes de seis segundos era de aproximadamente 250 clipes. A escolha posterior do usuário é quatro segundos por cena: agora são 375 cenas. Cortes mais curtos, continuações e reaproveitamento editorial mudam essa conta. O orçamento anterior de 200 tomadas de 7,5 s não deve ser aplicado diretamente a clipes limitados a seis segundos.

## Situação

Análise e proposta de adaptação registradas. Não foram geradas imagens ou animações nesta etapa, não foi instalado um agente na conta Flow e nenhum crédito de vídeo foi acionado. O autor chama uma alternativa de gratuita; disponibilidade, duração e limites atuais não foram verificados. O montador local existente continua útil, mas o storyboard anterior precisa ser substituído por beats de colagem e durações reais.

- [Prompt original de imagem para teste](PROMPT-IMAGEM.txt)
- [Prompt original de animação para teste](PROMPT-ANIMACAO.txt)
