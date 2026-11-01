# Reprodução e retomada

A voz/modelo/direção ficam em `../audio/voice-profile.json`. A aprovação é da amostra original, revisão 1. Os caminhos de credenciais e cache são argumentos locais, nunca arquivos deste repositório.

```bash
python3 build_audio.py --credentials /caminho/privado/chaves.txt --work /caminho/privado/cache --from-part 1 --to-part 25 --assemble
```

Este comando chama Gemini somente para gerações ou transcrições sem cache. Não o executar apenas para mudar o volume. `finish_parts.py --work ...` refaz a montagem/mix a partir dos WAVs brutos sem API; `assemble_master.py --work ...` junta as partes já conferidas. Guardar o cache bruto e os manifestos associados: hashes diferentes de texto, voz ou direção bloqueiam sobrescrita silenciosa.

A montagem usa silêncio identificado por energia e não acelera nem altera pitch. Frases maiores que o minuto sem pausas suficientes exigem revisão editorial. O master é montado a partir dos WAVs PCM exatos, não concatenando MP3s com padding.

`check_speech.py` solicita transcrição independente, sem fornecer o roteiro esperado no prompt. Diferenças devem ser avaliadas: grafia de nomes, números e pequenas variantes de fala não justificam regeneração automática. As transcrições e medições são verificações técnicas, não uma escuta humana integral. O QA registra essa limitação.

## Blocos usados nesta entrega

Para economizar chamadas à API, as partes 17–19 foram geradas como uma tomada contínua. As próximas podem usar pares. `generate_block.py` guarda a tomada; `align_block.py` estima tempos por frase; `split_block.py` só aceita cortes em regiões silenciosas. Conferir as palavras de cada arquivo depois de dividir: os tempos do modelo são aproximados. Nunca aplicar os mesmos tempos a uma geração nova.

A parte 19 recebeu uma breve transição original adicional para completar o minuto com fala e pausas naturais. `append_supplement.py` preserva a tomada anterior, ajusta o ganho fixo da transição e registra a composição. O texto final está no roteiro. A parte 10 teve uma frase de ligação removida; os cortes e o motivo estão em `roteiro/audio-edits.json`. Essas intervenções reaproveitam a voz existente.
