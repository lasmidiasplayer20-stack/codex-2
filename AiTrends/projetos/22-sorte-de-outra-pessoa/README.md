# 22 - Sorte de quem

Pedido do usuário: um dos três novos episódios, cada um com65segundos, cenas por código e pasta própria. Vertical1080×1920 nativo,24fps/1560quadros,26takes. Projeto aiTrends/Three.js, elenco próprio Nico/verde-água e Sol/laranja. Ficção/experimento imaginário, sem afirmar que o poder é ciência real.

Nico ganha sorte enquanto Sol perde: moeda, cesta, chaves, café e prêmio tornam a troca visível. Um fio dourado mostra a transferência de Sol para Nico. Quando o amigo precisa de ajuda, Nico larga o prêmio, devolve a moeda e escolhe continuar jogando sem roubar a sorte de ninguém. Regras e acontecimentos são ficção; ações, contato entre mãos, queda de objetos e retorno da bola são animação própria por código.

## Voz, efeitos e CTA

Mesma Puck/gemini-2.5-flash-preview-tts/generateContent e direção aceita. Uma geração bem-sucedida em cache privado, fonte52.491s. Sem acelerar ou mudar tom. Pausas adicionadas somente em silêncios detectados; tratamento suave55Hz/10500Hz,8%redução ampla de médios, ganho estático e correção lenta somente se diferença de janelas exceder2,5dB. Nova fonte medida: 2.72dBantes/0.17dBdepois; não reutilizar curva de outro vídeo. Métricas não comprovam naturalidade; não alegamos escuta humana integral nem ASR independente.

Foley sintetizado em Python, stems separados e eventos em audio/sfx-events.json; cenas/eventos específicos em story/foley.json. Dois CTAs diferentes fornecidos pelo usuário, variantes5/6,15–22s e56–63s,900px centralizados(x90/y1440), chroma key/despill somente nos assets. Áudio original dos CTAs omitido.

## Reprodução e entrega

`python3 AiTrends/studio.py doctor`; setup só se faltar dependência. Render: `node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/22-sorte-de-outra-pessoa" --scale 1 --workers 2 --format jpeg --out /tmp/episodio/full-silent.mp4`, guardando log em /tmp/episodio/full-render.log. Finalizar com `AiTrends/.venv/bin/python AiTrends/projetos/22-sorte-de-outra-pessoa/scripts/finish.py --work /tmp/episodio`. Fonte congelada em qa/frozen-source.json; mix.wav privado necessário, ou decodificar mix.mp3 publicado com recodificação adicional. Não regenerar voz para ajustes de cena/mix. Licenças do kit preservadas. Capa ilustrada separada das cenas por código.

MP4/prévia e validações reais em exports/ e qa/. Pacote YouTube em ../../youtube/22 - Sorte de quem/, capa9:16 e único arquivoYOUTUBE. Não é upload ao YouTube.

Estado final:65,000s/1560quadros,1080×1920/24fps nativo. Decodificação integral e prévia60s aprovadas; mix final-19.1LUFS/-5.6dBTP.26takes, contatos, objetos e doisCTAs conferidos em imagens reais do MP4. Sem alegação de escuta humana integral.
