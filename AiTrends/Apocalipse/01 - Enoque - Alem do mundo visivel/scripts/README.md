# Reprodução e retomada

A voz/modelo/direção ficam em `../audio/voice-profile.json`. A aprovação é da amostra original, revisão 1. Os caminhos de credenciais e cache são argumentos locais, nunca arquivos deste repositório.

```bash
python3 build_audio.py --credentials /caminho/privado/chaves.txt --work /caminho/privado/cache --from-part 1 --to-part 25 --assemble
```

Este comando chama Gemini somente para gerações ou transcrições sem cache. Não o executar apenas para mudar o volume. `finish_parts.py --work ...` refaz a montagem/mix a partir dos WAVs brutos sem API; `assemble_master.py --work ...` junta as partes já conferidas. Guardar o cache bruto e os manifestos associados: hashes diferentes de texto, voz ou direção bloqueiam sobrescrita silenciosa.

A montagem usa silêncio identificado por energia e não acelera nem altera pitch. Frases maiores que o minuto sem pausas suficientes exigem revisão editorial. O master é montado a partir dos WAVs PCM exatos, não concatenando MP3s com padding.

`check_speech.py` solicita transcrição independente, sem fornecer o roteiro esperado no prompt. Diferenças devem ser avaliadas: grafia de nomes, números e pequenas variantes de fala não justificam regeneração automática. As transcrições e medições são verificações técnicas, não uma escuta humana integral. O QA registra essa limitação.
