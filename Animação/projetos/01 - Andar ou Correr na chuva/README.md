# 01 - Andar ou Correr na chuva

**Exportação completa em andamento:** o código e o áudio já cobrem os oito minutos revisados. O MP4 completo no Git será substituído após terminar a renderização e a validação; enquanto isso, ele ainda é a versão anterior.

[Prévia aprovada de 1 minuto em 1080p](../../videos/01%20-%20Andar%20ou%20Correr%20na%20chuva%20-%20Preview%201min.mp4)

A produção usa o renderizador procedural **Three.js/Canvas dos primeiros vídeos**, com o cenário e os personagens próprios de casaco amarelo e verde. Os personagens um pouco mais alongados têm braços e pernas de comprimentos fixos, apoio dos pés ligado à distância percorrida e gestos com preparação e retorno. O experimento Blender está arquivado.

A abertura aprovada foi preservada. O restante inclui as comparações em duas pistas, as regiões do corpo expostas à chuva, recipientes com água subindo, vento, guarda-chuva, poça, passagem da toalha entre os personagens e a chegada ao abrigo. Os gestos de explicação têm início e fim; as gotas que escorrem da roupa caem para o chão. As câmeras alternam contexto, ação, detalhe e reação.

Os contornos, os personagens, os cenários e os pequenos traços dos casacos são geometria calculada por código. A narração Puck tratada foi mantida; não foi necessário gerar outra voz. Chuva, vento, passos e respingos são sintetizados em Python. O primeiro minuto da mixagem preserva o áudio aprovado.

## Executar e conferir

Requisitos: Node 22+, Python 3 com NumPy, Chromium e FFmpeg/FFprobe com libx264.

```sh
npm ci
npm run serve
npm test
npm run test:full
```

Abra o servidor local na porta 4175. `CHROMIUM_PATH` permite escolher outro executável Chromium; o padrão é `/usr/bin/chromium`.

Os testes conferem os personagens efetivamente posados: comprimentos dos membros, apoio dos pés, deslocamento, contato das mãos, enquadramentos finitos e erros do player. `qa/runtime-full-r4.json` registra a amostragem dos capítulos. `qa/approved-pilot-r4.json` compara quadros da abertura com a prévia aprovada. Isso complementa a conferência visual; não constitui uma avaliação humana de áudio.

## Recriar o som

```sh
node scripts/motion.mjs
python scripts/sound.py
python scripts/mix-approved-prefix.py --approved "../../videos/01 - Andar ou Correr na chuva - Preview 1min.mp4"
```

A narração já está em `audio/narracao.mp3`. A última etapa preserva os primeiros 60 segundos aprovados, atualiza `audio/mix.mp3` e verifica duração e amostras saturadas. `--wav-output /tmp/chuva-audio.wav` permite guardar a mixagem PCM para a exportação.

## Exportar o filme completo

```sh
python scripts/render-full.py --work /tmp/chuva-render --output /tmp/chuva-8min.mp4
```

A exportação calcula os quadros a **1920 × 1080, 24 fps**, em partes retomáveis. Depois monta os 480 segundos com a mixagem, verifica os 11.520 quadros e decodifica o arquivo inteiro. Se necessário para o limite de arquivo do GitHub, o encoder ajusta a compressão em duas passagens, mantendo a resolução nativa.

Os intermediários ficam na pasta `--work`. Para usar a mixagem PCM, passe `--audio /tmp/chuva-audio.wav`. `render-all.py` e `assemble_validate.py` são entradas de compatibilidade para esse mesmo fluxo.

Para renderizar somente a prévia ou um trecho sem áudio:

```sh
python scripts/render-preview.py --output /tmp/chuva-preview.mp4
node scripts/render.mjs --start 280 --duration 5 --output /tmp/vento.mp4
```

## Organização

- `film.js`: geometria, materiais, personagens, chuva, gráficos e saída Canvas.
- `opening.js`: trajetos e câmeras da abertura aprovada.
- `performance.js`: gestos, escolha entre caminhada e corrida e interações do restante do filme.
- `kinematics.js`: IK de dois segmentos e interpolação dos gestos em arco.
- `story.js`, `direction.js`, `timing.json`: capítulos, ações e direção.
- `scripts/`: síntese de som, servidor, renderização e validação.
- `qa/`: relatórios e quadros identificados por revisão.
- `vendor/three.min.js`: Three.js r128, licença MIT.

Toda a imagem nasce de código. Não há imagens prontas, modelos importados, vídeos de fundo ou efeitos sonoros de biblioteca. A voz é sintetizada pelo Gemini. As conferências de áudio são automatizadas, sem alegação de escuta humana.
