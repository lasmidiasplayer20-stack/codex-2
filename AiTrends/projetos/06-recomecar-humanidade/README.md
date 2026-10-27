# 06 — Duas pessoas podem recomeçar a humanidade?

**Pré-produção e prévia inicial prontas; voz restante aguardando cota.** História original em português, alvo inicial de 8min30s, horizontal 1920×1080/24 fps, 1.203 palavras, 32 sequências e 164 planos. A duração final acompanhará a leitura natural, sem acelerar a Puck.

[Prévia inicial de 1 minuto](exports/06%20-%20Previa%20inicial%201min.mp4) · [Roteiro](ROTEIRO.md) · [Capa e YOUTUBE](../../youtube/06%20-%20Duas%20Pessoas%20Podem%20Recome%C3%A7ar%20a%20Humanidade/)

<!-- CURRENT_STATUS_START -->
## Estado atual

Dois blocos Puck estão gerados e guardados em cache; faltam seis. A API confirmou limite diário gratuito de **10 chamadas desse modelo** e indicou nova tentativa após aproximadamente 07h UTC / 04h de Brasília. O usuário escolheu **“Aguardar a mesma voz/modelo”**. Não trocar timbre/modelo, não habilitar cobrança e não repetir chamadas antes da liberação. Perfil aceito após o episódio 05, registrado em `audio/voice-profile.json`.

A prévia inicial usa os trechos existentes, tratados levemente e com pausas prolongadas encurtadas. Só os primeiros oito beats têm áudio e tempos baseados em geração real; o restante da temporização é provisório. O arquivo completo ainda não foi exportado.

A rotina `scripts/resume_after_quota.py` permite aguardar a liberação no ambiente ativo, verificar que a fonte não mudou, gerar somente os blocos faltantes, tratar/mixar localmente, renderizar e validar os MP4s e publicar no GitHub. Para diante de nova cota/erro ou alteração da fonte; não entra em loop de geração. Estado da execução em diretório privado de trabalho, sem chaves no Git. Não representa um agendador externo durável se o ambiente for encerrado.
<!-- CURRENT_STATUS_END -->

## Direção e articulações

Elenco próprio: Nico verde-menta e Lia violeta; personagens de apoio coral/ocre. Cenários por código: rua/café, escola/quadro, diagramas, jardim, depósito, clínica e passarela. A referência foi analisada em quadros distribuídos e tiras consecutivas; ritmo/tipos de take foram adaptados a cenas originais, sem importar seus personagens/frames/fala/trilha.

O rig foi revisado para cotovelos com polo para baixo/fora, alcance limitado, braços neutros menos dobrados e transições de marcha/gesto. Comprimentos fixos conferidos em 360 casos numéricos; isso não prova naturalidade sozinho. Pilotos nativos e quadros consecutivos conferem as poses. O usuário ainda não aprovou as novas articulações. A passarela tem altura de apoio dos pés específica para plataforma/tábua. Caixas possuem tampas articuladas, cartas/rádio seguem as mãos e câmera/ações usam tempo global do beat.

Antialiasing ligado, iluminação estável, sem grão e sem modulação contínua de opacidade. O detalhe do semáforo e o enquadramento do quadro foram corrigidos durante revisão.

## Efeitos sonoros em Python

`scripts/sound.py` gera stems separados: `audio/sfx.mp3`, `audio/trilha.mp3` e mix. `audio/sfx-events.json` registra instantes, materiais, ganhos e ações. Passos derivam da distância/fase da marcha; há contatos de madeira, rádio, papel, água, ferramentas e acentos discretos de CTA. Os eventos posteriores ao beat 8 permanecem provisórios até a voz completa; o pipeline os recalcula sem chamar APIs. A mix parcial está em `audio/mix-inicial-parcial.mp3`, sem confundi-la com narração completa.

## Reproduzir / retomar

Da raiz do repositório, `python3 AiTrends/studio.py doctor`. Usar `node AiTrends/skill/scripts/render.mjs --project CAMINHO_ABSOLUTO --from 0 --to 6 --scale 1 --workers 1 --format jpeg --out /tmp/teste.mp4`. O render é silencioso; montar com a mix existente.

Ao retomar voz, usar `scripts/generate_voice.py --work DIRETÓRIO_PRIVADO` com cache dos dois blocos. Credencial somente em `GEMINI_API_KEY`. `treat_natural.py` exige oito blocos completos. Não reexecutar `build_story.py`: ele recria o rascunho de tempos. A rotina de retomada para se a fonte congelada mudou; não deve sobrescrever edições de outro chat.

## Ciência e limites

Roteiro autoral explica gargalo, deriva, parentesco e um modelo recessivo condicional, sem apresentar uma população mínima universal ou estatísticas não verificadas do vídeo de referência. O quadrado de herança corresponde ao modelo Aa × Aa; não é previsão geral de saúde. Tentativas de fontes externas MedlinePlus/NHGRI retornaram 403; não se afirma pesquisa online concluída. Validação matemática do modelo é separada de aconselhamento médico.

## Licenças e arte

Geometria, rig, textos e sons próprios; o motor e fontes aiTrends mantêm as licenças do kit. Capa nova gerada com ferramenta de imagem seguindo o padrão neon aprovado do Então; o vídeo permanece produzido por código. Metadados reunidos no arquivo `YOUTUBE`, como solicitado. Nenhum upload para o YouTube.
