# 14 — E se você deixasse a geladeira aberta?

História original do Então com Nico e Lia,90segundos, vertical nativo1080×1920/24fps. Cozinha colorida,27takes, ações com porta/ventilador/termômetro e circuito de refrigeração por dentro. Adaptação do tema sugerido pelo usuário; nenhum vídeo de referência foi assistido ou copiado nesta produção.

## Animação e áudio

Three.js no aiTrends adaptado, geometria/contornos/rostos por código, câmera geral e detalhe, órbita do circuito, IK de dois segmentos. A mão do Nico acompanha a maçaneta durante a abertura/fechamento; a fase da passada recua ao puxar a porta. Ventilador deslocado por Nico/Lia com contato da mão; cabeça direciona o vento ao personagem. Biela do compressor calculada como mecanismo manivela-cursor de comprimento fixo0,30m na escala ilustrativa.

Puck / gemini-2.5-flash-preview-tts / generateContent, uma única geração com a direção já aceita. Fonte aproximada83,45s; sem acelerar ou mudar tom. Medimos a subida gradual desta geração, sem copiar a curva do13: diferença entre medianas RMS de janelas ativas3,20dB antes e0,60dB depois de compensação lenta pré-calculada. EQ leve, ganho final estático e folga; sem compressor adicional ou AGC rápido. Fonte bruta e credenciais fora do Git.

Foley/música sintetizados em Python: passos, vedação da porta, fluxo discreto, compressor baixo, clique/vento do ventilador e CTA. Stems MP3 reutilizáveis. CTA em vídeo do usuário,900px emx90/y1440,15–22s e81–88s, chroma key/despill só no asset. Áudio original do CTA omitido.

Capa própria9:16 e título/descrição/tags num único `YOUTUBE` em `../../youtube/14 - E se você deixasse a geladeira aberta/`. A capa ilustrada é separada das cenas por código.

## Reproduzir

Use `python3 AiTrends/studio.py doctor` na raiz do repositório; `studio.py setup` se as dependências estiverem ausentes. Mantêm-se as licenças do motor/kit fornecido pelo usuário; esta pasta não amplia direitos do pacote original.

```bash
node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/14-geladeira-porta-aberta" --scale 1 --workers 2 --format jpeg --out /tmp/geladeira/full-silent.mp4
AiTrends/.venv/bin/python AiTrends/projetos/14-geladeira-porta-aberta/scripts/finish.py --work /tmp/geladeira
```

Guarde a saída do render em `/tmp/geladeira/full-render.log`. O finalizador verifica fonte congelada, monta áudio/CTA e confere o MP4. Ele usa `audio/mix.wav`; se o WAV privado estiver ausente, decodifique o MP3 publicado localmente, aceitando uma recodificação adicional. `scripts/audio.py` reproduz o tratamento/Foley com a fonte Puck privada. Não execute `generate_voice.py` para uma revisão visual ou de mix: preserve a voz existente.

## Revisão e limites

Física simplificada baseada em balanço de energia; não é procedimento de instalação/reparo. Circuito sem escala, partículas/cores ilustrativas. Geladeira comum dissipa calor no mesmo ambiente; layouts/ciclos variam. Consulte `story/editorial-check.json`.

Pilotos nativos e quadros de movimento, auditoria numérica de contatos, MP4 final/decodificação/níveis em `qa/`. Alinhamento por estimativas de palavras e pausas da forma de onda; sem transcrição independente ou escuta humana integral. Métricas não equivalem a aprovação editorial.

Estado: MP4 final exportado e validado —90,000s/2160quadros,1080×1920/24fps, decodificação integral aprovada; áudio-18.9LUFS/-4.6dBTP. Prévia60s e pacote YouTube incluídos. Correções locais de marcha/termômetro em `qa/door-gait-fix.json` e `qa/thermometer-fix.json`, sem regenerar a voz.
