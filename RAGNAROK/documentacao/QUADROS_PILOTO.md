# Quadros separados — Kratos assume guarda

## Entrega

Quatro imagens PNG novas, numeradas, **1672×941**, com o mesmo enquadramento e ambiente de inverno. Elas mostram uma progressão de poses da mesma ação, sem usar quadros do vídeo de referência.

- Pasta: `../imagens/animacoes/cena_001_kratos_guarda/quadros/`.
- Manifesto: `../imagens/animacoes/cena_001_kratos_guarda/manifesto.json`.
- Prévia: `../videos/testes/kratos_guarda_animatic_4s.mp4`.
- Compositor: `../scripts/montar_animatic_guarda.py`.

## Ordem e duração do animatic

| Arquivo | Pose | Tempo na prévia | Quadros de reprodução a 24 fps |
| --- | --- | --- | --- |
| `kratos_guarda_0001.png` | Repouso; machado baixo. | 00:00–00:01 | 24 |
| `kratos_guarda_0002.png` | Percebe algo à direita; antecipa a reação. | 00:01–00:01,75 | 18 |
| `kratos_guarda_0003.png` | Leva o machado à frente do corpo; empunhadura com duas mãos. | 00:01,75–00:02,50 | 18 |
| `kratos_guarda_0004.png` | Guarda firme; gelo acende na lâmina. | 00:02,50–00:04 | 36 |

A prévia tem 96 quadros de reprodução, mas apenas **quatro desenhos distintos**. Os mesmos desenhos são mantidos pelos tempos da tabela. Não foi aplicada interpolação automática, morphing, animação de membros ou sincronização labial.

## Áudio

- `vento_midgard.mp3`: ambiente baixo durante a prévia.
- `gelo_despertar.mp3`: novo efeito ElevenLabs, entrando em 00:02,50.
- Sem voz: o personagem permanece de boca fechada.

O compositor ajusta volumes, limita picos, corta o áudio na duração do teste e exporta H.264/AAC em 1280×720, 24 fps. O tamanho original dos PNGs é preservado; a adaptação de formato ocorre apenas no vídeo.

## Como montar e continuar

Os PNGs podem ser importados em um editor de vídeo ou ferramenta de animação como poses-chave. Cada um contém personagem e fundo juntos, sem camadas ou transparência.

Para uma animação contínua:

1. Estabilizar o desenho: revisar o cabo/lâmina do machado, mãos, tatuagem, dobras e pequenas variações entre poses.
2. Separar personagem e fundo ou redesenhar os elementos em camadas.
3. Definir arcos do machado, transferência de peso e tempos de antecipação/guarda.
4. Criar poses de passagem e intermediários, ou preparar um rig e corrigir rotações com desenhos de apoio.
5. Adicionar respiração, tecido e efeitos separados; revisar a atuação antes de ampliar para outras cenas.

Manter uma câmera semelhante ajuda a continuidade, mas uma geração por imagem não garante alinhamento perfeito de todos os detalhes. Estas quatro poses são um teste concreto de produção e montagem, não a animação final do longa.

Para reexportar sem gerar imagens nem consumir créditos da ElevenLabs:

```bash
python3 RAGNAROK/scripts/montar_animatic_guarda.py --saida /tmp/kratos_guarda.mp4
```
