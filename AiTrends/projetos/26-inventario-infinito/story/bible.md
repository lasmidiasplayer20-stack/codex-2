# Bíblia — Inventário infinito

História original de humor: Nico guarda carro, bicicleta, sofá e casa. Quando chove, o inventário desorganizado devolve os objetos errados. Sem abertura ou título “E se”. Abertura direta: “Nico colocou um carro no bolso. O problema foi tirar depois.”

Estilo voxel inspirado em Minecraft, mantendo identidade própria: Nico com cabeça cúbica preta, olhos e boca marfim, jaqueta verde-água, pernas pretas, sapatos creme. Geometria, ícones, inventário e expressões feitos por código, sem skins/texturas de Minecraft. Capa ilustrada gerada separadamente.

Jardim/praça colorido, casas coral/lavanda/amarelas, árvores cúbicas, flores, pavimento em blocos. Objetos encolhem e convergem para a mão recolhida junto ao bolso. A casa deixa uma base vazia. Sofá e bicicleta saem em planos distintos. Chuva com posição y = 4.5 - ((tempo * 3.2 + fase) % 4.5): movimento para baixo, sem inversão. Conferir quadros consecutivos e piloto em movimento. Partículas pequenas sem flash ou estrobo.

Inventário imaginário com contador 216 e ícones desenhados em canvas, não uma interface ou funcionalidade real do jogo. Capacidade infinita é uma regra fictícia. A presença de muitos ícones parecidos torna difícil localizar a própria casa; não afirmar um fenômeno científico.

## Revisão Minecraft clássico

Usar `scenes/rig.js` com modelo 8/12/12 e skins 64×64, sem reaplicar o rig anterior de braços articulados. Membros retos giram nos ombros/quadris; os objetos seguem o ponto real na extremidade do braço. A vila está em `scenes/minecraft-world.js`, com blocos de tamanho consistente e texturas próprias 16×16, nearest. Não voltar ao voxel genérico reprovado.
