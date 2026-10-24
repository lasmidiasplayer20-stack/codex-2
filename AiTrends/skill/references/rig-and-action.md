# Contato, continuidade e câmera — implementação do episódio 03

Exemplo de código: `AiTrends/projetos/03-10x-mais-rapido/scenes/`.

`rig.js` mantém comprimentos de membros e resolve duas articulações. Verifique o lado de dobra dos joelhos no deslocamento: pose que parece plausível em um still pode dobrar para trás no ciclo. Distância percorrida controla fase, tempo em apoio controla amplitude, e altura do tênis desconta a sola. Mudança de câmera não reinicia a marcha.

`film.js` usa tempo global do beat. Props anexados consultam a posição mundial real da mão/pé depois de atualizar o rig. Mesmo primeiro quadro de um corte deve reconstruir todo o estado. A bola para no pé, a bandeja segue a palma e a xícara preserva a posição entre cortes.

Sentar: quadril na altura do assento; pés apoiados; orientar tronco para o lado aberto do banco. Não deixar o encosto atravessar a cintura. A câmera de rosto consulta a cabeça mundial, incluindo a altura reduzida ao sentar. Câmeras de detalhe podem cortar a cabeça, mas não devem ser confundidas com close de rosto.

`world.js` reutiliza cenários entre cortes para evitar centenas de contextos WebGL. Geometria e texturas de rosto são cacheadas. A renderização direta evita o composer caro em CPU, preservando perspectiva e resolução nativa. Sombras de contato são elipses geométricas; transparência discreta. A versão rápida não utiliza sombras dinâmicas ou MSAA por software.

Provar primeiro: folha de todos os planos, amostra de movimento nativa e inspeção de mãos, pés, banco e obstáculos em primeiro plano. Depois congelar fonte e temporização, renderizar completo, inspecionar imagens extraídas do MP4 e decodificar o arquivo inteiro.
