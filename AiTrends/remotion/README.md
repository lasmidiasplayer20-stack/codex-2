# Estúdio Remotion do Então

Remotion **4.0.539**, React 19, TypeScript, Three.js e Chromium local. Renderiza quadros definidos por código em MP4; o Studio oferece uma timeline no navegador. Não é uma ferramenta que resolve automaticamente roteiro, atuação ou articulações. Este pacote adiciona Remotion ao estúdio existente sem substituir os projetos aiTrends.

## Composições

- `Original3DDemo`: 5 s, 1080×1920/24 fps. Usa **o mesmo rig arredondado original** do projeto 38, com `@remotion/three`, câmera em movimento, iluminação e expressão. Não usa Minecraft. É um teste visual sem narração.
- `EntaoDemo`: 10 s, 1080×1920/24 fps. Demonstração 2D em SVG de parallax, movimento e cartelas. Não define um novo estilo para os episódios. Sem áudio.
- `EpisodeMontage`: montagem de um MP4 aiTrends com a mixagem local e CTAs opcionais em `Sequence`. Duração calculada pelos props, sem fala duplicada: vídeo-base sempre mudo, mixagem em um único `Audio`. Não gera voz nem faz chamadas à API.

## Uso

```bash
cd AiTrends/remotion
npm ci
npm run typecheck
npm run compositions
npm run studio
npm run demo
npx --no-install remotion render src/index.ts Original3DDemo exports/remotion-3d-demo.mp4 --browser-executable=/usr/bin/chromium --gl=swangle --concurrency=1
npm run episode -- --project ../projetos/38-janela-pachinko --from 23 --seconds 3
```

O Studio roda apenas como ferramenta local; não foi publicado na internet. Os comandos usam `/usr/bin/chromium`, instalado neste ambiente. Em outra máquina ajustar esse argumento. Lock npm incluído. `node_modules/`, caches e mídias temporárias ficam fora do Git.

O adaptador de montagem confere dimensão/duração com ffprobe, copia mídias para `public/work/` ignorado, empacota React e exporta com `@remotion/renderer`. Por padrão usa o MP4 final do projeto e o stem `audio/mix.mp3` já publicado. Como o MP4 final já contém os CTAs, não os duplica. `--video` permite trocar pela fonte silenciosa, caso em que os CTAs precisam ser definidos separadamente na composição com assets **já transparentes**. Não aplicar chroma key verde ao filme inteiro. O adaptador inicial valida projetos verticais 1080p/24 fps; outro formato exige Composition apropriada.

Para animações novas, usar `useCurrentFrame()` como fonte de tempo e `useVideoConfig()` para fps/dimensões. Nada de `setTimeout`, CSS com tempo real ou aleatoriedade sem semente. O rig 3D é importado de `../projetos/38-janela-pachinko/scenes/rig.js`, precisa estar no checkout. A integração atual não converte automaticamente todas as cenas aiTrends em componentes React; a montagem pode reutilizar o render 3D existente, e novas cenas podem ser escritas diretamente em Remotion/Three.

Não há API de geração ou hospedagem paga neste pacote. A licença do Remotion prevê uso gratuito individual/organizações elegíveis e licença de empresa para outras situações; termos completos: https://github.com/remotion-dev/remotion/blob/main/LICENSE.md . As dependências mantêm suas próprias licenças; o elenco/procedurais do projeto são nossos. O render principal do episódio 38 continua sendo aiTrends/Three.js, não deve ser atribuído a Remotion.

Ver `qa/validation.json` para testes realmente executados e `exports/` para os previews. Nenhuma demo silenciosa deve ser anunciada como episódio narrado final.

Neste Chromium, o teste WebGL com `--gl=swiftshader` falhou na criação do contexto; `--gl=swangle` funcionou. Usar a opção validada ao reproduzir o demo 3D.
