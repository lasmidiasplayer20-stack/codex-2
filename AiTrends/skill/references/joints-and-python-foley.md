# Articulações, ações e efeitos em Python — feedback do episódio 05

O usuário aceitou a voz (“a voz ficou ok”) e relatou articulações toscas. Pediu registrar o uso de efeitos sonoros em Python e melhorar o próximo episódio a partir dos movimentos, takes e câmera da referência, mantendo nossos personagens. O trecho exato das falhas ainda não foi indicado; não inventar diagnóstico do filme inteiro.

## Movimento antes do render longo

Não considerar o rig aprovado porque usa IK. Conferir visualmente em movimento: marcha e parada; mudança de direção; agachar/levantar; alcance frontal/lateral; pegar, apoiar e entregar objeto. Limitar flexão e extensão; usar polos anatômicos de cotovelo/joelho estáveis e diferentes quando a ação exigir. Evitar singularidades de braço quase esticado, mãos atravessando tronco, ombros deslocados e joelhos invertendo lado. Preferir pose clara e alcance viável a alvo impossível que o solver apenas encurta.

Pés em apoio devem ficar aproximadamente fixos no mundo; deslocamento do quadril/torso acompanha a passada. Reduzir cruzamento de pernas e deslize. Transições de repouso, marcha e gesto precisam de interpolação, sem saltos ao mudar booleanos. Cotovelos devem descrever arcos plausíveis; evitar encolher o braço para alcançar pontos atrás do tronco. Apoio no chão e sentar exigem geometria compatível.

Gerar piloto nativo de 10–20 s com ações reais do novo roteiro, conferir quadros consecutivos e pelo menos dois ângulos. Corrigir antes de expandir/renderizar completo. Não repetir o mesmo pacote de cinco câmeras em todas as sequências: cada take deve ter motivo e ação correspondente.

## Referência e direção

Analisar trechos consecutivos da referência, registrar tempo, enquadramento, deslocamento da câmera, movimento do personagem, objeto manipulado e consequência. Adaptar gramática visual e ritmo com nossos personagens e cenas autorais; não importar frames/personagens/trilha nem transcrever toda a fala do canal. Filmagem mais dinâmica inclui ações que avançam no espaço, reações, preparação/contato/resultado, diagramas que explicam processos e mudanças de escala.

## Foley e ambiente são obrigatórios, em Python

Criar `scripts/sound.py` (ou equivalente), `audio/sfx.mp3` e `audio/sfx-events.json` no projeto. Sintetizar sons próprios por Python/NumPy/SciPy ou utilitários locais do kit. Não chamar APIs pagas. Música, SFX e voz devem ter stems separados e mix final reproduzível.

Usar sons apropriados ao material e movimento: passos conforme apoio, toque de ferramenta, fricção/folha/corda, madeira, água/vento, mecanismo e acento discreto de câmera quando motivado. Variar textura e duração, não só frequência de um seno. Não colocar whoosh em todo corte ou loop de passos sem contato real.

Alinhar o instante do contato à mesma função/timeline usada pela animação; converter para amostra no script de áudio. Ganho/pan/duração/evento ficam no manifesto. Conferir presença na mix durante ação e silêncio da voz; reduzir camadas que competem com fala. Não confundir stem existente com efeito audível no vídeo final. Medições de pico e LUFS são verificações técnicas, não avaliação completa de naturalidade.

## Voz aceita

Conservar Puck / gemini-2.5-flash-preview-tts / generateContent e direção explícita em português, tratamento leve e mix discreta do episódio 05. O usuário já avaliou e aceitou a voz; não exigir nova aprovação das mesmas configurações. Uma mudança de voz/modelo/estilo deve passar por amostra curta antes de comprometer a narração inteira. Para 8min30s, começar perto de 1.150–1.230 palavras e ajustar com a duração real, sem acelerar artificialmente.
