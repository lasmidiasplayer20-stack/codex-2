# Teste de direção — chuva, Blender e Grease Pencil

Cena original de 60 segundos, criada por Python no Blender 4.3.2. Personagens, cenário, chuva e câmeras são geometria procedural. Não usa imagens, modelos importados, mocap ou plugins pagos.

Abra **01 - Chuva - Grease Pencil.blend** no Blender 4.3 ou posterior. A timeline vai de 1 a 1440, a 24 fps. Os marcadores selecionam 12 câmeras. A narração dos primeiros 60 segundos do episódio está no Sequencer; os sons são empacotados no arquivo. Para ouvir no editor, ative a reprodução de áudio. O modo de visualização de material pode demorar a compilar na primeira abertura.

O objeto **Grease Pencil • contorno desenhado** contém Line Art, limitado à coleção de geometria, seguido por Noise de baixa intensidade. O traço acompanha as malhas e o ponto de vista. É um acabamento de ilustração sobre volumes 3D; não é animação desenhada quadro a quadro. Chuva e poças ficam fora do contorno para preservar a leitura.

Os personagens usam um rig de objetos articulados, com segmentos e juntas calculados e keyframes explícitos. Não dependem de handlers Python para reproduzir a animação. Os passos relacionam distância percorrida e fase do ciclo; os braços descansam quando os personagens param. Este é um teste de linguagem e movimento, não a versão final dos oito minutos.

## Recriar

```bash
python efeitos.py
blender -b -t 4 --python criar_cena.py
```

A conferência visual é feita por quadros em `prancha.jpg`, renderizados em Workbench para avaliar o traço e os enquadramentos. O `.blend` preserva Eevee e a configuração 1080p; não inclui um MP4 completo renderizado deste teste.

O script salva o `.blend` nesta pasta e renders de conferência em `verificacao/`. Para escolher outro destino desses renders, defina `RAIN_RENDER_DIR`. A configuração salva da cena é 1920 × 1080, 24 fps, Eevee. Os quadros de conferência usam 50% para avaliação rápida.

`efeitos.py` usa Python e NumPy para sintetizar chuva e passos. `narracao-60s.wav` é um recorte da narração Gemini Puck já tratada do episódio. Não há chaves de API no projeto.
