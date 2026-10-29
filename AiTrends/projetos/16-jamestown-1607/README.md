# 16 — Um dia em Jamestown,1607

**Pedido final do usuário: cerca de50segundos, vertical1080p, trabalhar a voz após reprovação do último áudio e sugerir continuação nas entrelinhas.** A proposta inicial de8min foi substituída antes da geração. Projeto50s/1200quadros/24fps,14takes; uma única Puck em cache, cerca43,45s de fonte. O próprio short serve como prévia, sem duplicata60s.

Nico é personagem fictício. Jornada imaginada em junho de1607, com flashforward final identificado para22dejunho, quando Newport parte para a Inglaterra. Madeira/forte, Companhia da Virgínia, território Powhatan, água e suprimentos. Não mistura o inverno da fome1609–1610 com1607, não encena romance de Pocahontas, não apresenta pensamentos/diálogos inventados de pessoas históricas como documentos.

## Pesquisa e direção

NPS A Short History of Jamestown, First Residents e contextoPowhatan de Pocahontas: Her Life and Legend, lidos diretamente. OpenStax oficial lido via git. Fontes, fatos e interpretações em `story/fact-check.json`. A página arqueológica HistoricJamestowne ficou bloqueada; não alegamos consulta. Layout/escala, embarcações, roupas individuais, casas e aldeia são representações estilizadas, não levantamentos arqueológicos. Fortetriangular como fato; dimensões/desenho exatos não afirmados. Não mostra todos os navios partindo juntos.

Nico conserva nossa identidade visual em gibão com botões, calções, meias, calçado castanho e barrete simples; sem zíper/tênis/hoodie moderno. Outros colonos visíveis são figuras masculinas esquemáticas. TerritórioPowhatan apresentado como habitado e socialmente organizado, com aldeias e cultivo; sem estereótipos de povos de outras regiões.

CenasThree.js por código/aiTrends adaptado: carregamento de tábua, vista aérea do forte, mesa/pergaminho simbólico, aldeia esquemática, balde, martelo, parede e tampa articulada do barril acompanhada pela mão. Luz muda gradualmente para o entardecer, sem estrobo. Figurinos/mapas identificados como reconstituição livre. Final em aberto com mantimentos e partida do navio, sem dizer parte2 ou continua.

## Áudio e CTA

Puck / gemini-2.5-flash-preview-tts / generateContent, mesma direção aceita. Feedback negativo do15 registrado; sua naturalidade não é considerada aprovada. Tratamento mais leve55Hz/10500Hz e redução ampla de médios8%, ganho estático e folga. Fonte deste16 apresentou variação0,83dB entre janelas ativas, sem curva de ganho adicional. Sem compressor, aceleração ou mudança de tom. A fonte bruta é privada/cache; não regenerar para ajustes de cena/mix. Nenhuma afirmação de que medidas de volume resolvem toda percepção sintética; limites em `audio/voice-review.json`.

FoleyPython: passos de couro/terra, madeira/ferramenta, balde/água, barril, rio/vento e cliques discretos. CTA em vídeo com duas variantes novas5/6 já selecionadas,15–22s e42–49s,900px/x90/y1440, chroma key/despill só nos assets; áudio original omitido. Capa9:16 e único arquivoYOUTUBE no pacote do episódio.

## Reproduzir e revisar

Use `python3 AiTrends/studio.py doctor` e `setup` se necessário. Da raiz do repo:

```bash
node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/16-jamestown-1607" --scale 1 --workers 2 --format jpeg --out /tmp/jamestown/full-silent.mp4
AiTrends/.venv/bin/python AiTrends/projetos/16-jamestown-1607/scripts/finish.py --work /tmp/jamestown
```

Guarde o log em `/tmp/jamestown/full-render.log`. O finalizador verifica a fonte congelada e usa `audio/mix.wav`; se o WAV privado estiver ausente, decodifique o MP3 publicado, aceitando recodificação adicional. Mantêm-se licenças/dependências do kit fornecido pelo usuário. Capa ilustrada separada das cenas por código; não se apresenta como fotografia histórica.

Piloto nativo15s e integração de56quadros/contatos de props. Decodificação, duração, níveis e imagens reais do MP4 final em `qa/`. Sem escuta humana integral ou ASR independente; alinhamento aproximado por roteiro/pausas. Estado: MP4 final exportado e validado —50,000s/1200quadros,1080×1920/24fps, decodificação integral aprovada; áudio-20.0LUFS/-3.0dBTP. O próprio short serve como prévia. Pacote YouTube e fontes incluídos.
