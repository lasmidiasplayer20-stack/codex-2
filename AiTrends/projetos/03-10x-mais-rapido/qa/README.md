# Verificação da entrega

O resultado definitivo está em `export-validation.json`: dimensões, duração, quantidade de quadros, SHA-256 do MP4 e das fontes. `ffprobe-final.json` e `ffprobe-preview.json` registram os streams. O exportador só conclui após decodificar integralmente os dois arquivos com FFmpeg `-xerror`.

Imagem: 1920×1080 nativo, 24 fps, 12.240 quadros em 510 s. Prévia: 1.440 quadros em 60 s. O limite de arquivo do GitHub exige compressão H.264 em duas passagens; não houve ampliação de um render menor. A folha `filme-completo.jpg` e as imagens dos CTAs são extraídas do próprio MP4 final.

Direção/rig: revisão dos 160 planos em folhas do player e amostras nativas de movimento. Joelhos com dobra consistente, cotovelos no mesmo lado de dobra anatômica, braços em oposição, marcha ligada à distância real. Câmeras incluem acompanhamento, detalhe, órbita e vista superior. Xícara, bandeja e bola usam posições mundiais das extremidades.

A inspeção final encontrou o encosto atravessando a roupa nas três sequências sentadas. A raiz do personagem foi deslocada 0,30 m para a frente do encosto: `z=2.8` no parque, `z=1.3` no terraço. Somente essas sequências foram renderizadas novamente, totalizando 1.070 quadros nativos. O exportador substitui os intervalos por número de quadro, preserva o áudio e faz nova codificação/decodificação integral. `native_replacements` no relatório identifica os limites. `apoio-banco.jpg` e `cta-final.jpg` mostram o resultado no filme entregue.

Áudio: entrada TTS conferida contra o roteiro/cache em oito trechos; métricas de pausas e volume em `audio/quality.json`. Mix medido em aproximadamente −16,22 LUFS e −4,68 dBTP, faixa de loudness 1,60 LU. Não houve amostras saturadas no áudio tratado. Puck em todos os trechos; dois modelos Gemini por esgotamento de cota no final, documentados no manifesto.

Limite de revisão de conteúdo falado: a transcrição independente ficou indisponível (Gemini HTTP 503/429; download do modelo Whisper HTTP 403, inclusive após nova tentativa de rede). Não se afirma escuta humana ou verificação ASR integral. O texto enviado ao TTS contém apenas a narração, sem notas de cena ou instruções técnicas. Os tempos internos de sequência/legendas são aproximados por texto e energia, não por alinhamento exato de palavras.

Para reproduzir tudo, renderize novamente o projeto completo com o código atual e use o exportador sem `--patches`. Os patches foram uma economia de render na revisão, não uma dependência ausente do projeto.
