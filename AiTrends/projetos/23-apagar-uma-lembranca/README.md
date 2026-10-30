# 23 - O que eu apaguei

Pedido do usuário: um dos três novos episódios, cada um com65segundos, cenas por código e pasta própria. Vertical1080×1920 nativo,24fps/1560quadros,29takes. Projeto aiTrends/Three.js, elenco próprio Nico/verde-água,Lia/lavanda e amigos. Ficção/experimento imaginário, sem afirmar que o poder é ciência real.

Nico apaga a vergonha de um tropeço com tinta e perde junto a lição daquele dia. No ateliê, repete o erro. A foto de Lia deixa claro o que aconteceu; reaprender exige limpar, reorganizar a passagem e terminar a pintura com cuidado. Ontem e hoje são identificados, e o aparelho não desfaz o mundo físico. A memória apagada é uma regra de ficção, não uma afirmação sobre funcionamento real do cérebro.

## Voz, efeitos e CTA

Mesma Puck/gemini-2.5-flash-preview-tts/generateContent e direção aceita. Uma geração bem-sucedida em cache privado, fonte51.851s. Sem acelerar ou mudar tom. Pausas adicionadas somente em silêncios detectados; tratamento suave55Hz/10500Hz,8%redução ampla de médios, ganho estático e correção lenta somente se diferença de janelas exceder2,5dB. Nova fonte medida: 1.23dBantes/1.23dBdepois; não reutilizar curva de outro vídeo. Métricas não comprovam naturalidade; não alegamos escuta humana integral nem ASR independente.

Foley sintetizado em Python, stems separados e eventos em audio/sfx-events.json; cenas/eventos específicos em story/foley.json. Dois CTAs diferentes fornecidos pelo usuário, variantes5/6,15–22s e56–63s,900px centralizados(x90/y1440), chroma key/despill somente nos assets. Áudio original dos CTAs omitido.

## Reprodução e entrega

`python3 AiTrends/studio.py doctor`; setup só se faltar dependência. Render: `node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/23-apagar-uma-lembranca" --scale 1 --workers 2 --format jpeg --out /tmp/episodio/full-silent.mp4`, guardando log em /tmp/episodio/full-render.log. Finalizar com `AiTrends/.venv/bin/python AiTrends/projetos/23-apagar-uma-lembranca/scripts/finish.py --work /tmp/episodio`. Fonte congelada em qa/frozen-source.json; mix.wav privado necessário, ou decodificar mix.mp3 publicado com recodificação adicional. Não regenerar voz para ajustes de cena/mix. Licenças do kit preservadas. Capa ilustrada separada das cenas por código.

MP4/prévia e validações reais em exports/ e qa/. Pacote YouTube em ../../youtube/23 - O que eu apaguei/, capa9:16 e único arquivoYOUTUBE. Não é upload ao YouTube.
