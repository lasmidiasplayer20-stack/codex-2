# 15 — E se você pudesse enxergar a inércia?

História original do Então,90s, vertical nativo1080×1920/24fps,24takes. Nico e Lia com nossos personagens, carro em corte e pista fechada colorida. Silhueta transparente explicitamente identificada como recurso explicativo; os ocupantes reais permanecem de cinto.

## Conteúdo e fontes

Lei da inércia conferida no texto oficial OpenStax, lido via git no repositório do editor. Veja `story/references.json` para commit/arquivo e limites de acesso à NHTSA. Não há números de velocidade, força, lesão ou percentuais inventados. O desenho é ilustração cinemática, não simulação de colisão ou projeto de segurança certificado.

A inércia não é uma força adicional para a frente. O cinto aplica força ao corpo para desacelerá-lo. Ombro/peito e quadril são destacados; nenhum uso incorreto é encenado como solução. Retrator/catraca é esquema ilustrativo, com aviso de que projetos variam. Fixação da mochila é conceitual; siga o manual do veículo na vida real.

## Produção

Three.js via aiTrends adaptado, carro/cenário/rostos/contornos por código, Nico entra, afivela, freia com Lia, visualiza a silhueta e compara mochila solta/fixada. Câmera externa em acompanhamento, interior, ombro/quadril, roda, mecanismo e tomada superior da carga. Deslocamento do carro é contínuo entre cortes; giro das rodas deriva da distância. Braços por IK, mãos da motorista no plano do volante e mão do Nico no fecho.

Puck / gemini-2.5-flash-preview-tts / generateContent, uma única chamada, fonte próxima85s. Mesma direção aceita; pausas curtas, sem acelerar ou mudar tom. Curva lenta medida especificamente nesta geração, EQ suave e ganho final estático; sem compressor extra/AGC rápido. Ver `audio/consistency-check.json`. Fonte bruta/credenciais fora do Git. Métricas de nível não provam identidade perfeita de timbre ou naturalidade.

Efeitos/música Python: passo, clique do cinto, rodagem baixa, frenagem suave, tecido/mochila, travamento ilustrativo e cliques discretos dos CTAs.

**Pedido novo: dois CTAs diferentes do vídeo do usuário.** Variantes5 e6, em vez da antiga variante1. Excertos57–64s e71,5–78,5s do original, em `assets/cta-a.mp4` e `cta-b.mp4`. Sobrepostos aos15–22s e81–88s,900px/x90/y1440; chroma key/despill apenas nos assets, áudio original omitido. Proveniência em `assets/cta-provenance.json`.

Capa9:16 e arquivo único `YOUTUBE` com título/descrição/tags em `../../youtube/15 - E se você pudesse enxergar a inércia/`.

## Reproduzir

Na raiz do repo, `python3 AiTrends/studio.py doctor`; use `setup` se necessário. Dependências e licenças do kit aiTrends permanecem como no pacote fornecido pelo usuário.

```bash
node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/15-enxergar-a-inercia" --scale 1 --workers 2 --format jpeg --out /tmp/inercia/full-silent.mp4
AiTrends/.venv/bin/python AiTrends/projetos/15-enxergar-a-inercia/scripts/finish.py --work /tmp/inercia
```

Guarde o log em `/tmp/inercia/full-render.log`. O finalizador lê a fonte congelada e `audio/mix.wav`; se o WAV privado não estiver disponível, decodifique o MP3 publicado, aceitando recodificação adicional. Não regenere a voz para corrigir cenas ou mix.

## Verificação

Pilotos nativos, integração geométrica de96quadros, mãos/fecho, movimento da silhueta, cinto afivelado antes de o carro andar, bagagem presa e parada da catraca. Conferência final de90s/2160quadros, decodificação integral, áudio, CTAs e imagens reais do MP4 em `qa/`. Sem escuta humana integral ou transcrição independente; alinhamento aproximado por palavras/pausas.

Estado: MP4 final exportado e validado —90,000s/2160quadros,1080×1920/24fps, decodificação integral aprovada; áudio-18.7LUFS/-4.4dBTP. Prévia60s/1440quadros e pacote YouTube incluídos. Dois novos CTAs conferidos no arquivo exportado.
