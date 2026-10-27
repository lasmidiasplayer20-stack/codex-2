# Áudio, estabilidade temporal e controle de créditos

## Feedback obrigatório — episódio 04

O usuário reprovou o áudio de **04 — Quanto Tempo Resta**: “o áudio ficou péssimo”. Também relatou que “uma parte da animação ficou muito cintilante”. Pediu melhorar o próximo vídeo, registrar isso na skill e evitar repetir tentativas que consomem créditos. Vai fornecer outra referência. Não regenerar o episódio 04 nem chamar APIs por causa deste registro.

O áudio do episódio 04 **não é uma referência de qualidade aprovada**, embora use Puck e tenha passado por medições de volume. A decodificação completa dos arquivos prova integridade técnica; não prova naturalidade da voz, boa mixagem ou ausência de cintilação. Não repetir a cadeia anterior automaticamente.

O usuário ainda não especificou se a reprovação do áudio se refere principalmente à voz, prosódia, tratamento, trilha, efeitos ou à combinação deles. A localização e a causa exatas da cintilação também não foram confirmadas. Registrar como problemas reais relatados; manter o diagnóstico em aberto até analisar amostras em movimento e áudio. Não inventar uma causa ou afirmar que foi corrigida.

## Próxima produção: amostra antes de gastar com o lote

1. Ler a nova referência e fechar um trecho curto do roteiro antes de gerar a voz. Usar áudio existente/cache sempre que servir à avaliação, sem nova chamada à API.
2. Gerar **uma única amostra de 20–30 segundos** com a voz candidata. Puck continua sendo a preferência histórica, mas sua combinação de modelo/estilo/tratamento precisa de nova avaliação. Não trocar modelo automaticamente por limite de cota e presumir que a qualidade permaneceu igual.
3. Preparar três arquivos a partir dessa mesma geração: voz original, voz com tratamento leve e mix com trilha/efeitos. A comparação de tratamento e mix é local; não custa outra geração. Incluir fala normal, uma passagem expressiva e uma pausa natural.
4. Entregar a amostra curta ao usuário e **aguardar sua avaliação do áudio antes de gerar a narração completa**. Esta etapa implementa o pedido de evitar desperdício de créditos. Enquanto isso, trabalhar em roteiro, cenários e cenas que independam dessa aprovação. Não pedir confirmação de configurações já autorizadas.
5. Após aprovação, gerar apenas os trechos ainda necessários. Conferir cada trecho antes do próximo lote: palavras omitidas/repetidas, pronúncia, ritmo, timbre, pausas, ruídos, distorção e transições. Se houver falha, preservar os trechos bons e corrigir somente o trecho afetado. Se não houver meio de avaliar a fala, explicitar o limite e manter a aprovação pendente; não usar métricas como substituto da escuta.

## Voz e mix

- Priorizar uma narração natural, expressiva e inteligível. Não acelerar a leitura para encaixar um roteiro longo sem revisar o ritmo do texto primeiro.
- Preservar respirações e pausas de sentido. Evitar corte agressivo de silêncio, ganho oscilando, compressão excessiva, voz metálica e artefatos de mudança de velocidade. São itens a conferir, não causas confirmadas do episódio 04.
- Comparar o áudio tratado com o original; manter tratamento somente quando houver melhoria audível. Normalização e ausência de saturação, isoladamente, não aprovam a qualidade.
- Conferir voz sozinha e mix final. Música e Foley devem apoiar a fala; reduzir ou retirar camadas que causem ruído, repetição cansativa ou som artificial inadequado à cena. Usar ducking suave quando necessário e testar as entradas/saídas dos efeitos.
- Registrar quem avaliou e qual arquivo foi aprovado. Uma transcrição automática ajuda a verificar palavras, mas não avalia bem timbre, emoção ou qualidade da mixagem. Não declarar escuta ou aprovação que não ocorreu.

## Estabilidade temporal da animação

- Renderizar uma amostra em movimento de 10–20 segundos antes do filme completo, na resolução e FPS finais. Incluir câmera em deslocamento, bordas finas, livros/piso repetidos, luz, transparências, partículas e visores. Folhas de imagens não detectam cintilação temporal.
- Usar iluminação e exposição estáveis. Evitar luz, opacidade, brilho e cor pulsando continuamente; preferir um destaque estável ou uma transição suave e motivada. Não usar strobe/glitch como recurso padrão.
- Conferir aliasing em linhas finas e detalhes subpixel, superfícies quase coplanares (z-fighting), transparências, mudanças bruscas de visibilidade, saltos de rótulos e movimentos de câmera. Reduzir detalhes finos, separar superfícies, estabilizar o layout e testar antialiasing conforme a causa observada. Não pressupor que um desses itens seja a causa sem comparar os quadros.
- A opção `fast3D` do renderizador compartilhado desativa MSAA em software para ganhar velocidade. Isso é uma escolha de desempenho, **não um selo de qualidade**. Comparar uma amostra com antialiasing habilitado antes de escolher; preservar a resolução nativa.
- No código do episódio 04 há modulação periódica da opacidade do contador durante `support`, transição de iluminação em `blackout`, partículas finas e mudanças condicionais de visibilidade. São pontos de inspeção para a queixa, não um diagnóstico confirmado. Não copiar esses efeitos automaticamente para o próximo episódio.
- Revisar o vídeo exportado em reprodução e, se necessário, quadros consecutivos das passagens suspeitas. Diferenças de luminância podem ajudar a localizar oscilações, mas cortes e movimentos normais também geram diferenças; não concluir somente por um número.

## Evitar gasto repetido

Guardar cache e manifesto da geração com texto, voz, modelo e configurações relevantes, sem credenciais. Manter áudio bruto e variantes em área privada e versionar apenas arquivos próprios necessários à reprodução. Mudanças de tratamento, volumes, música e SFX devem reaproveitar a voz já gerada. Não regenerar tudo para corrigir a mixagem.

Registrar amostra avaliada, decisão do usuário, trechos aprovados, falhas encontradas e revisões tentadas. Definir um limite de tentativas para cada amostra; se a primeira for reprovada, diagnosticar e discutir a alteração concreta antes de outra chamada. Nunca entrar em ciclos de regeneração ou habilitar cobrança para superar limites.


## Perfil aprovado no episódio 05

O usuário manteve a Puck e aprovou `projetos/05-imortal/audio/03-voz-com-mix.mp3` (caminho a partir de `AiTrends/`) com a resposta “Aprovada com mix discreta”. Modelo: `gemini-2.5-flash-preview-tts`, API `generateContent`. Enviar direção explícita de leitura em português dentro do prompt; o helper antigo omitira essa direção nesse caminho. Conservar volume uniforme, curiosidade calorosa e ritmo confortável, sem sussurrar/gritar ou dramatizar como trailer. Nenhuma troca automática de modelo nem regeneração do trecho aprovado.

A amostra usa tratamento leve (65 Hz, compressão 1,6:1, −18 LUFS), harmonia espaçada e Foley muito baixo. A versão completa só encurta vazios sustentados >1,2 s para cerca de 0,65 s e mantém pausas breves; não muda velocidade/tom. Aprovação da amostra não equivale a aprovação do filme completo. Registro: `AiTrends/projetos/05-imortal/qa/voice-sample.json`.

**Planejar duração antes de gerar:** o episódio 05 terminou com 1.391 palavras em 590,625 s (~141 palavras/min), apesar de um alvo inicial de 510 s. A amostra curta foi mais rápida do que os blocos longos. Nos próximos roteiros com este perfil, orçar aproximadamente 135–145 palavras/min (cerca de 1.150–1.230 palavras para 8min30s), verificar com a amostra e reservar pausas. Se a duração for rígida, encurtar o texto antes do lote. Não descobrir o desvio apenas depois de gastar com toda a narração nem corrigir acelerando a voz.


## Feedback posterior do episódio 05

O usuário avaliou a entrega: “a voz ficou ok”, mas algumas articulações ficaram toscas. Assim, a voz do episódio 05 está aceita; preservar seu perfil e cache. A etapa de reavaliar voz é necessária se mudar voz/modelo/estilo, sem pedir de novo aprovação da mesma configuração já aceita. O novo controle obrigatório de articulações e efeitos Python está em [joints-and-python-foley.md](joints-and-python-foley.md). Essa aceitação não aprova a animação inteira.
