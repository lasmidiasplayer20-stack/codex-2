# 17 — Jamestown: o forte não basta — Parte2

Pedido:90segundos, takes e ângulos diferentes. Projeto novo aiTrends/Three.js por código,27takes,1080×1920 nativo,24fps/2160quadros. Nico e demais personagens estilizados próprios; sem Blender. Duas variantes diferentes do CTA fornecido,15–22s e81–88s,900px centralizados, chaveadas individualmente; áudio original omitido.

## História

Continuidade após22junho1607, verão de doença/escassez, seguida de salto explicitamente identificado para inverno1607–1608 e importância da ajuda indígena. Não confundir com1609–1610. Nico, colega e remador são fictícios; tigela, ajuda individual, rota e ação da canoa são cenas imaginadas, não eventos específicos documentados. Mapas sem escala e figurinos livres. Povos indígenas possuem comunidades, cultivos e decisões próprias. Fontes NPS e OpenStax efetivamente consultadas/reaproveitadas e limites em story/fact-check.json. Capa ilustrativa separada.

## Movimento e áudio

Nico realmente se desloca, carrega tigela, agacha e a entrega ao companheiro; mãos com alvos alcançáveis. Canoa avança entre tomadas; duas mãos no remo, lâmina fora do casco, remador sentado no assento. Cesto segue ambas as mãos até o chão.27takes alternam gerais, aéreos, órbita, acompanhamento, detalhes, reação e ângulo baixo. Pilotos nativos de entrega e canoa foram inspecionados em sequências de quadros;108amostras numéricas verificam contatos, visibilidade, cronologia e matrizes. Não são simulação biomecânica ou certificação histórica.

Mesma Puck/gemini-2.5-flash-preview-tts/generateContent e direção do16, uma chamada preservada em cache privado. Fonte71,851s,169palavras. Distribuição em90s por21pausas naturais ampliadas em0,7904s, sem mudar velocidade ou tom, sem cortar fala. Última fala termina por volta de88,7s. Tratamento leve55Hz/10500Hz, redução ampla de médios8%, sem compressor. Fonte apresentou subida gradual4,04dB: correção lenta previamente medida, limitada a3dB, reduziu diferença de janelas ativas para0,51dB. Isso não comprova naturalidade; sem alegar escuta humana integral ou transcrição independente.

Foley obrigatório sintetizado em Python: terra/passos, madeira, tigela, tecido, remo/água, cesto, rio/vento e cliques discretos de CTA. Música baixa, sem sons do CTA fornecido.

## Reprodução

`python3 AiTrends/studio.py doctor`; setup somente se necessário. Renderizar com `node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/17-jamestown-parte-2" --scale 1` e `--workers 2`; salvar full-silent.mp4/full-render.log em pasta privada. Finalizar com `AiTrends/.venv/bin/python AiTrends/projetos/17-jamestown-parte-2/scripts/finish.py --work PASTA_PRIVADA`. Verifica fonte congelada e exige mix.wav; se ausente, decodificar mix.mp3 publicado, aceitando recodificação adicional. Não regenerar voz para corrigir câmera/mix. Preservar licenças do kit.

QA e validação real de exportação em qa/. Pacote YouTube em `../../youtube/17 - Jamestown - Parte 2/`. Não há publicação no YouTube.

Estado final: MP4 exportado e validado,90,000s/2160quadros,1080×1920 nativo/24fps; decodificação integral aprovada. Prévia60s/1440quadros validada. Níveis finais em qa/final-audio-validation.json.
