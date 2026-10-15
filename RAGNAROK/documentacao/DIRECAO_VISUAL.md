# Direção visual — primeira versão

## Linguagem

Gravura nórdica pintada: silhuetas angulares, contorno forte, três massas de luz e sombra, acabamento de pincel seco e textura de papel. A proposta preserva a identificação de Kratos e muda a apresentação visual em relação às imagens do jogo. As artes iniciais foram criadas antes do acesso ao vídeo; depois, quadros foram extraídos apenas para análise local, sem reutilização nas artes do projeto.

A referência acessada posteriormente usa corpos caricatos, olhos grandes e animação 2D com movimento seletivo. Para levar a direção atual à animação, simplificar o excesso de pequenos detalhes de couro, ornamentos e textura. Manter a identidade da arte principal, mas produzir uma versão limpa em camadas e testar um plano de atuação antes de expandir o elenco. Ver `ANALISE_VIDEO.md` para a comparação.

| Uso | Cor de referência |
| --- | --- |
| Neve, papel, pele clara | `#D8D0BF` |
| Couro, ferro, contorno | `#292827` |
| Neblina, gelo em sombra | `#526F75` |
| Tatuagem, tecido | `#873B32` |
| Bronze envelhecido | `#9B7951` |
| Energia de gelo | `#8AD4E4` |

Essas cores orientam futuras imagens; não são uma medição exata de todos os pixels das pranchas.

## Kratos

- Cabeça raspada, pele cinzenta clara, barba escura com fios grisalhos.
- Armadura e pelo no **ombro direito anatômico** deste design. Na vista frontal aparecem à esquerda da imagem.
- Tatuagem vermelha no lado oposto ao conjunto principal de armadura, mantendo a referência visual da arte principal.
- Saia de couro em camadas, tecido vermelho escuro, botas pesadas, ferragens de bronze.
- Movimento com peso: preparação visível, ação curta e recuperação mais longa; evitar flutuação ou saltos sem transferência de peso.
- Expressões prioritárias: contenção, raiva, luto e decisão. A expressão neutra é a referência para repouso.

## Hierarquia das referências

1. `kratos_conceito.png`: referência principal de identidade, roupa e acabamento.
2. `kratos_model_sheet.png`: estudo de rotação e expressão.
3. `kratos_poses.png`: propostas de silhueta e atuação.
4. Pranchas de armas e storyboard: exploração secundária.

Antes de recorte ou rig, fazer uma passagem de limpeza: padronizar tatuagem, proporções, fivelas, geometria da lâmina, mãos e continuidade dos lados entre vistas. Os desenhos gerados são estudos; não possuem a precisão de um turnaround redesenhado para produção.

## Câmera e cenário

Silhueta do personagem deve se destacar da neve. Reservar uma faixa de chão legível para os pés. Evitar partículas sobre os olhos durante diálogos. A direção inicial de percurso no teste é da esquerda para a direita; o último plano acompanha a saída em profundidade.

O cenário entregue é uma pintura única achatada. Separação real em primeiro plano, meio e fundo ainda precisa ser produzida para parallax.

## Efeitos e som

Gelo: antecipação discreta, expansão curta, impacto pontual e dissipação. Chamas das lâminas usam âmbar para diferenciar o elemento. Vento contínuo em nível baixo; golpes devem abrir espaço na mixagem para a fala.

Os MP3 estão separados por função. `machado_gelo.mp3` é uma amostra de golpe para cenas de ação futuras; não corresponde ao gesto calmo de segurar a arma no storyboard de abertura.
