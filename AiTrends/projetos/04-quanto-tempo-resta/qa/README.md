# Evidências de produção

`production-checks.json` registra roteiro de 1.426 palavras, 32 sequências, 160 planos contíguos e a conferência dos oito textos TTS contra o cache. O arquivo de leitura normaliza espaços no final das linhas; não houve alteração de palavras. `audio/voice-manifest.json` registra Puck e o mesmo modelo Gemini nos oito trechos.

Revisão visual: todas as sete folhas do player foram abertas, incluindo planos gerais, inserts, contraplanos, vista superior, personagens sentados e contato com carrinho/estante. Amostras de movimento em resolução nativa: 0–8 s e 320–324 s. Ajustes anteriores ao render completo: paredes para contraplanos, rosto focal visível, recuo entre banco e mesa, mãos em três dimensões, transferência gradual de props e visores que evitam cabeças.

O áudio tratado mediu aproximadamente 2,90 dB de diferença entre os percentis 90 e 10 do nível por segundo, nenhuma pausa de baixa energia acima de 0,8 s e zero amostras saturadas. O mix mediu −16,23 LUFS, −4,73 dBTP e faixa de loudness 1,70 LU. Música e efeitos foram sintetizados por NumPy, sem amostras comerciais.

Limite de revisão: não houve transcrição ASR independente integral nem escuta humana. Os serviços de transcrição e downloads de modelos haviam ficado indisponíveis nesta sessão; a conferência desta produção usa texto/cache e métricas do sinal. Não apresentamos essas verificações como prova de cada palavra pronunciada. A temporização interna das frases usa texto e mínimos próximos de energia, sem alinhamento exato por palavra.

A entrega final só é marcada como concluída depois de `export-validation.json`: resolução 1920×1080 nativa, 24 fps, 12.240 quadros em 510 s, prévia de 1.440 quadros em 60 s e decodificação completa dos dois MP4s com FFmpeg `-xerror`. O SHA-256 do filme e das fontes está no relatório. Compressão para caber no GitHub preserva as dimensões; não é ampliação de um render menor.

`filme-completo.jpg`, os três CTAs e os stills de banco/estante são extraídos do próprio MP4 final pelo exportador. Confira o relatório para o estado efetivamente concluído desta revisão.
