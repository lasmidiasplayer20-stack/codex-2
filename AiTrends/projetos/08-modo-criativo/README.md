# 08 — E se você tivesse Modo Criativo na vida real? / Então

<!-- CURRENT_STATUS_START -->
**Completo: 8min29s, 1920×1080/24fps, abaixo de10min.** Puck em quatro blocos da mesma sessão/modelo, sem aceleração, Foley Python e prévia final de1min. Decodificação integral validada; não se declara escuta humana integral nem aprovação editorial.
<!-- CURRENT_STATUS_END -->

História original de Nico/Lia sobre criar objetos e aprender a compartilhar o espaço. Um menu, cadeira e copos; voo entre prédios; abrigo e ponte; jardim; ouro/comida; excesso de construção; desfazer; ilha suspensa; retorno e cooperação. Fantasia declarada, sem apresentar ponte ou poderes como instrução científica/engenharia real.

## Visual e movimento

169 planos/32 sequências. Personagens próprios: Nico menta, Lia violeta, Ari ocre e Sol coral, cabeças pretas com expressões, membros longos e IK. Cenários/props em geometria própria e contornos: praça, cidade, oficina, ilha/ponte, jardim e plataforma celeste. Árvores, janelas instanciadas, telhados, mesa, cadeiras, abrigos, construções por peças, maquete e objetos transportados. Nenhuma imagem da referência foi inserida no vídeo. Fontes e texturas de rosto são geradas no motor/canvas por código.

A referência de10min49s foi analisada em contato distribuído e seis trechos consecutivos. A adaptação usa tracking, voo, aproximação/recuo, órbitas, macro de mãos/objetos, plano baixo, vista superior e mudança de escala. Não é uma cópia quadro a quadro nem transcrição integral. Leia `input/reference-analysis.md` e `story/bible.md`.

Rig revisado: compensação de inclinação da cabeça em voo; braços dentro do alcance; nenhuma marcha no ar; pés apoiados nas margens e na ponte; redução gradual da sombra quando voa; contatos e transferência de peças ligados aos pontos reais das mãos. Câmera frontal deriva da orientação real da cabeça, inclusive no voo. MSAA ativo, luz estável, grão/bloom desligados, sem strobe.

## Áudio e limite

[Narração tratada](audio/narracao.mp3) · [Mix com Foley Python](audio/mix.mp3).

Puck/gemini-2.5-flash-preview-tts/generateContent, direção em português com perfil aceito nos episódios anteriores.1.221 palavras, quatro chamadas produtivas na mesma sessão/credencial; nenhuma troca de modelo ou repetição de trechos. Blocos de8sequências reduzem transições em relação ao07, mas não garantem timbre idêntico entre chamadas. Tratamento leve:65Hz, compressão1,6:1,−18LUFS; apenas vazios sustentados longos encurtados; sem aceleração ou mudança de tom. Tempo final509,083s; limite obrigatório600s também verificado nos scripts de render/export.

`audio/quality.json` registra blocos, picos, pausas e ausência de saturação. Essas medições não substituem uma escuta. Não se declara escuta humana integral ou ASR completo. O download do modelo local falhou no episódio anterior; não foi repetido para desperdiçar tempo ou apresentado como auditoria aprovada.

Foley reproduzível em `scripts/sound.py`, com87 eventos de materialização, montagem, passos, madeira, ferramenta, papel, vidro, inventário, ar do voo e CTAs. Stems `sfx.mp3`/`trilha.mp3`, manifesto com tempo/ganho/pan e mix separada. Harmonia discreta; sem whoosh a cada corte. Nenhuma cobrança de API foi ativada; áudio bruto e chaves ficam fora do Git. Não imprimir anexos de credenciais.

## Organização e reprodução

`ROTEIRO.md`/`input/narracao.txt` contêm a história em português, sem notas de produção no texto falado. `story/` organiza sequências e planos; temporização por blocos e proporção do texto é aproximada, não alinhamento exato por palavra. Não reexecutar o gerador de storyboard sobre a voz já temporizada.

`scenes/` contém mundo, rig, câmera e animação; `scripts/` contém voz com cache, tratamento, Foley, auditoria do player, YouTube e render/export. O renderizador é o aiTrends compartilhado, usando Chromium/Three.js/FFmpeg, sem Blender/AfterEffects. Dependências verificadas com `python3 AiTrends/studio.py doctor`. Leia `../../skill/SKILL.md` antes de reproduzir.

`render_and_deliver.py --work DIRETORIO_PRIVADO --expected-source SHA --publish` usa o áudio pronto e não chama TTS. Guarda o hash da fonte, faz auditoria, render nativo1080p/24fps, mux, decode completo, prévia de1min e publicação autorizada no Git. Exige ambiente ativo. Mudanças na fonte durante o render interrompem a exportação; não iniciar outro render do mesmo intervalo.

[Pacote YouTube](../../youtube/08%20-%20E%20se%20voc%C3%AA%20tivesse%20Modo%20Criativo%20na%20vida%20real/): capa neon1280×720 e arquivo único`YOUTUBE` com título, descrição/capítulos e tags. Nenhum upload ao YouTube. CTAs do Então por código perto45s, no meio e no encerramento.

Licenças do motor aiTrends e fontes do kit preservadas; não se ampliam direitos sobre o pacote fornecido. Geometria, elenco, roteiro e Foley próprios; capa gerada pela ferramenta de imagem conforme padrão aprovado. O anexo informa premissa aérea/gesto de poder, adaptados para nosso elenco e história.

## Revisão da mix — feedback do usuário

O usuário percebeu aspereza/volume projetado no final (“megafone”). Foi aplicada revisão local, sem nova geração: cortes suaves em1750/2800Hz, redução de agudos em4800Hz por bloco, filtro em10kHz e ganho estático mais baixo, com o último bloco discretamente mais baixo. Não foi acrescentada compressão. Picos da mixPCM em−4,49dBFS, sem amostras saturadas; isso é verificação técnica, não avaliação humana integral do timbre. Duração e amostras da timeline permanecem idênticas, sem refazer cenas.

`audio/remix-quality.json` detalha a revisão. `scripts/remix_voice.py --work DIRETORIO_PRIVADO` aplica essa etapa depois do tratamento/Foley, usando os blocos locais já existentes. Nenhuma API é chamada. Voz e mix anteriores foram preservadas na área privada para comparação.

## Exportação final

[Vídeo completo](exports/08%20-%20E%20se%20voc%C3%AA%20tivesse%20Modo%20Criativo%20na%20vida%20real.mp4) · [Prévia final de1min](exports/08%20-%20E%20se%20voc%C3%AA%20tivesse%20Modo%20Criativo%20na%20vida%20real%20-%20Preview%201min.mp4)

Validações, quadros, codecs, duração, hash e CTAs em `qa/export-validation.json`.
