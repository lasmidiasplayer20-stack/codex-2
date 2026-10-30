# 24 - Eu sou o original

Pedido do usuário: um dos três novos episódios, cada um com 65 segundos, cenas por código e pasta própria. Vertical 1080 × 1920 nativo, 24 fps/1560 quadros, 24 takes. Projeto aiTrends/Three.js, elenco próprio Nico/verde-água,Lia/lavanda e amigos. Ficção/experimento imaginário, sem afirmar que o poder é ciência real.

Nico cria uma cópia para dividir trabalho e descanso. A disputa pelo posto de original só muda quando os dois passam a colaborar. Ficção com regras imaginárias, não uma explicação sobre clonagem real.

## Voz, efeitos e CTA

Mesma Puck/gemini-2.5-flash-preview-tts/generateContent e direção aceita. Uma geração bem-sucedida em cache privado, fonte 50.491 s. Sem acelerar ou mudar tom. Pausas adicionadas somente em silêncios detectados; tratamento suave 55 Hz/10500 Hz,8% de redução ampla de médios, ganho estático e correção lenta somente se diferença de janelas exceder 2,5 dB. Nova fonte medida: 2.71 dBantes/0.41 dBdepois; não reutilizar curva de outro vídeo. Métricas não comprovam naturalidade; não alegamos escuta humana integral nem ASR independente.

Foley sintetizado em Python, stems separados e eventos em audio/sfx-events.json; cenas/eventos específicos em story/foley.json. Dois CTAs diferentes fornecidos pelo usuário, variantes 5/6,15–22 s e 56–63 s,900 px centralizados(x 90/y 1440), chroma key/despill somente nos assets. Áudio original dos CTAs omitido.

## Reprodução e entrega

`python 3 AiTrends/studio.py doctor`; setup só se faltar dependência. Render: `node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/24-dividir-em-dois" --scale 1 --workers 2 --format jpeg --out /tmp/episodio/full-silent.mp 4`, guardando log em /tmp/episodio/full-render.log. Finalizar com `AiTrends/.venv/bin/python AiTrends/projetos/24-dividir-em-dois/scripts/finish.py --work /tmp/episodio`. Fonte congelada em qa/frozen-source.json; mix.wav privado necessário, ou decodificar mix.mp 3 publicado com recodificação adicional. Não regenerar voz para ajustes de cena/mix. Licenças do kit preservadas. Capa ilustrada separada das cenas por código.

MP 4/prévia e validações reais em exports/ e qa/. Pacote YouTube em ../../youtube/24 - Eu sou o original/, capa 9:16 e único arquivoYOUTUBE. Não é upload ao YouTube.

## Validação da entrega

MP4 final: 65,000 s, 1560 quadros, 24 fps, 1080×1920 nativo; decodificação integral aprovada. Prévia: 60 s, mesma resolução. Áudio final: −19,2 LUFS, pico verdadeiro −4,7 dBFS. Maior silêncio detectado na mix: 1,49 s. Revisão visual dos quadros do MP4 final cobrindo todos os takes, transporte/encaixe da tábua, aperto de mãos, fusão e ambos os CTAs. Auditoria numérica: 96 amostras, zero erros de execução, transformações não finitas ou desvios nos contatos auditados. Métricas de sinal e quadros amostrados não substituem audição humana integral; alinhamento da fala é aproximado, sem ASR independente.
