# 28 — NÃO APERTA DE NOVO! — revisão 2

Short de 15 segundos, 360 quadros, 24 fps e 1080×1920 nativo. Animação por código aiTrends/Three.js, visual Minecraft clássico com skin própria. Título sem nome do personagem.

## Correções solicitadas

A primeira versão foi reprovada por corpo rígido na descida e repetição de fala. Agora tronco, ombros e quadris têm poses independentes: braços equilibram o corpo, pernas alternam, cabeça acompanha a ação, pousos têm preparação e reação. Membros continuam inteiriços, conforme o modelo clássico. A câmera acompanha a descida e retorna suavemente ao enquadramento inicial. O trajeto de volta passa pela frente do pedestal; as poses do empurrão foram ajustadas para afastar o corpo do pistão. Não é simulação física completa.

A fala foi substituída por uma única frase: “Não aperta esse botão!”. Uma nova geração de substituição com a mesma Puck / gemini-2.5-flash-preview-tts, preservada em cache. Transcrição automática independente por gemini-3-flash-preview confirmou uma ocorrência e nenhuma repetição no áudio bruto; ver qa/narration-check.json. O modelo de análise não altera a voz TTS. A fonte tem 1,691 s, colocada uma vez em 0,25 s, sem mudança de velocidade/tom nem compressão extra. Não se afirma audição humana integral.

Foley sintetizado em Python: botão, pistões, slime, água e passos, incluindo contatos durante a descida. Mix discreta e música periódica; bordas da mix PCM coincidentes não garantem igualdade bit a bit após AAC. CTA fornecido pelo usuário, variante 6, somente em 4,5–11,5 s, ausente na emenda.

## Loop e revisão

Fase periódica quadro módulo 359 aplicada a movimentos e câmera. A igualdade visual é verificada novamente nos quadros extremos decodificados do MP4 final em qa/loop-boundary.json. O finalizador protege o último quadro com cópia do primeiro e IDRs com QP idêntico. H.264 High 4:2:0 de 8 bits em faixa completa, identificado pelo FFprobe como yuvj420p. Prévia de emenda de quatro segundos em exports/preview-emenda-4s.mp4.

Auditoria de 61 instantes e amplitudes medidas nos transformadores reais do rig em qa/body-motion.json. Métricas não substituem avaliação estética. Quadros do filme completo e da emenda em qa/. Capa e arquivo único YOUTUBE em ../../youtube/28 - Nao aperta de novo/.

## Reproduzir

Da raiz: python3 AiTrends/studio.py doctor. Render: node AiTrends/skill/scripts/render.mjs --project CAMINHO_ABSOLUTO_DO_PROJETO --scale 1 --workers 2 --format jpeg --preset fast --crf 20 --out DIRETORIO_PRIVADO/full-silent.mp4, com log full-render.log. Finalizar: AiTrends/.venv/bin/python CAMINHO_DO_PROJETO/scripts/finish.py --work DIRETORIO_PRIVADO, com mix.wav local. Para áudio, scripts/audio.py reutiliza voice/block-01.wav privado. Não regenerar voz para corrigir imagem. Chaves e fontes privadas não são publicadas. Skins/texturas originais por código; não é captura de gameplay. Sem upload ao YouTube.

## Entrega validada da revisão 2

MP4 final: 15 s / 360 quadros / 1080×1920, decodificação integral aprovada. Comparação RGB dos extremos: zero pixels diferentes. Áudio: -20.8 LUFS, pico verdadeiro -7.7 dBFS. Quadros exportados revisados em filme-completo.jpg e emenda.jpg. SHA-256: `7ca3ce884dadbd8f992a029f0a1bc0f009d58d9760d075d62fef811f85b62ecb`.
