> **Experimento arquivado.** A produção principal continua no [renderizador procedural original](../../projetos/01%20-%20Andar%20ou%20Correr%20na%20chuva/).

# Chuva — direção, personagens alongados e traço por código

A revisão atual é **02 - Chuva - Atuacao e traco.blend**. Ela contém uma cena original de 60 segundos, 17 planos e os dois áudios empacotados. Abra no Blender 4.3 ou posterior; reproduza a timeline pela câmera. Não precisa executar scripts para reproduzir os keyframes salvos.

Os personagens foram redesenhados com pernas e tronco mais longos. Braços e pernas usam IK analítica de dois segmentos, com polos de dobra consistentes e comprimentos fixos. Os ciclos dependem da distância percorrida; há aceleração, frenagem, preparação da corrida, apoio dos pés, reação ao respingo e um cumprimento no abrigo. Os gestos seguem arcos de preparação, ação e recuperação.

O Grease Pencil fornece tanto os contornos Line Art quanto traços desenhados ponto a ponto: sobrancelhas, sorriso, costuras, hachuras, ondulações e arcos de respingo. Os traços do rosto acompanham a superfície e são ocultados nas vistas de costas. Tudo é geometria ou traço procedural. Não há imagens prontas, modelos importados, mocap, plugins pagos ou chaves de API.

As referências orientam a alternância entre ação, detalhe e reação, o acompanhamento lateral, a vista sobre o ombro e as comparações de trajeto. Os personagens são próprios. A base visual continua volumétrica em 3D.

A renderização usa Workbench com iluminação de estúdio, sombras, cavidade, antialiasing e Grease Pencil, em **1920 × 1080 / 24 fps**. A cena salva usa a mesma configuração da prévia. A narração é o primeiro minuto da versão tratada de Gemini Puck já existente; chuva, passos e respingo são sintetizados em Python. A conferência de áudio é automatizada, sem alegação de escuta humana.

## Recriar e renderizar a revisão 2

Requisitos: Blender 4.3+, Python com NumPy para os sons e FFmpeg para montar o MP4.

```bash
python efeitos_v2.py
blender -b --python-exit-code 1 --python criar_cena_v2.py
blender -b "02 - Chuva - Atuacao e traco.blend" --python-exit-code 1 --python verificar_v2.py
blender -b "02 - Chuva - Atuacao e traco.blend" --python-exit-code 1 --python renderizar_v2.py
python montar_previa_v2.py
```

`cena_base.py` constrói a rua e os abrigos. `criar_cena_v2.py` cria personagens, articulações, traços, atuação e câmeras; os keyframes são gravados no `.blend`, sem handlers de animação. `renderizar_v2.py` aceita `-- --start 1 --end 360 --out /caminho/dos/quadros` para renderizar intervalos. Os quadros intermediários ficam fora do Git.

`verificar_v2.py` confere o arquivo salvo: dimensões, áudio empacotado, comprimentos dos segmentos, apoio dos pés e contato das mãos. O relatório descreve o alcance amostrado dessas verificações; ele não substitui a avaliação visual da atuação.

---

## Primeiro experimento, preservado para comparação

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
