# Contato, continuidade e câmera — implementação do episódio 03

Exemplo de código: `AiTrends/projetos/03-10x-mais-rapido/scenes/`.

`rig.js` mantém comprimentos de membros e resolve duas articulações. Verifique o lado de dobra dos joelhos no deslocamento: pose que parece plausível em um still pode dobrar para trás no ciclo. Distância percorrida controla fase, tempo em apoio controla amplitude, e altura do tênis desconta a sola. Mudança de câmera não reinicia a marcha.

`film.js` usa tempo global do beat. Props anexados consultam a posição mundial real da mão/pé depois de atualizar o rig. Mesmo primeiro quadro de um corte deve reconstruir todo o estado. A bola para no pé, a bandeja segue a palma e a xícara preserva a posição entre cortes.

Sentar: quadril na altura do assento; pés apoiados; orientar tronco para o lado aberto do banco. Não deixar o encosto atravessar a cintura. A câmera de rosto consulta a cabeça mundial, incluindo a altura reduzida ao sentar. Câmeras de detalhe podem cortar a cabeça, mas não devem ser confundidas com close de rosto.

`world.js` reutiliza cenários entre cortes para evitar centenas de contextos WebGL. Geometria e texturas de rosto são cacheadas. A renderização direta evita o composer caro em CPU, preservando perspectiva e resolução nativa. Sombras de contato são elipses geométricas; transparência discreta. A versão rápida não utiliza sombras dinâmicas ou MSAA por software.

Provar primeiro: folha de todos os planos, amostra de movimento nativa e inspeção de mãos, pés, banco e obstáculos em primeiro plano. Depois congelar fonte e temporização, renderizar completo, inspecionar imagens extraídas do MP4 e decodificar o arquivo inteiro.

Revisão final do episódio 03: igualar a altura do quadril e do assento não basta. O centro do personagem deve estar à frente do encosto por pelo menos o raio do tronco mais metade da espessura da madeira. Aqui o encosto fica em `z=1`/`2.5` e a raiz sentada em `z=1.3`/`2.8`. Esse recuo evita madeira atravessando roupa em planos próximos.

O exportador aceita `--patches manifest.json` para substituir somente intervalos nativos re-renderizados. Cada entrada contém `action`, `start_frame`, `end_frame` (exclusivo), `path`; o log `patch-AÇÃO.log` precisa conter sucesso. Use limites `ceil(tempo*fps)`, render em `frame/fps`, valide a quantidade de quadros. O exportador recorta por número de quadro, concatena e comprime em duas passagens sem ampliar resolução. Depois valide o filme inteiro novamente. Não altere outras cenas do código e apresente o patch como se elas também tivessem sido renderizadas.
