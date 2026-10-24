"""Roteiro autoral e montagem preliminar. Recalibrar cortes com a voz real."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent.parent
# location, dramatic action, counter state, narration. New story, inspired by user's premise.
BEATS=[
('home','door',9314,'Você pergunta: está tudo bem? Ela sorri e responde que sim. Acima da cabeça dela, um número vermelho aumenta. Nove mil, trezentas e quatorze mentiras. Você acabou de descobrir uma mentira. Mas ainda não descobriu a verdade. E essa diferença vai custar muito mais do que imagina.'),
('street','reveal',9317,'Imagine enxergar o total de mentiras que cada pessoa já contou. Nenhum aplicativo. Nenhum interrogatório. Só um contador, flutuando sobre a cabeça. Você pensaria em políticos, golpistas, criminosos. Caio pensou primeiro na própria casa. Só que, para entender aquela noite, precisamos voltar uma semana.'),
('court','arrival',0,'Caio era juiz. Organizado, respeitado, conhecido por não deixar passar uma contradição. Naquela manhã, atravessou o tribunal ouvindo um elogio que adorava: o senhor sabe ler as pessoas. Sorriu como quem recebe uma confirmação. Nunca perguntou quantas vezes tinha lido alguém errado.'),
('street','reject',0,'Na saída, um homem sentado perto da escadaria pediu ajuda para comer. Chamava-se Rui. Olhos baixos, mãos inquietas, voz quase sumindo. Caio apertou a pasta contra o corpo e seguiu. Na cabeça dele, aqueles sinais já formavam uma história. Uma história que ninguém tinha contado.'),
('home','rest',0,'Em casa, Mara perguntou se ele estava cansado. Só um pouco. Era mentira. Ele estava esgotado. Mesmo assim, abriu o computador durante o jantar. Ela recolheu os pratos em silêncio. Às vezes, o primeiro problema de uma conversa não é o que alguém diz. É o que ninguém pergunta.'),
('home','blackout',9311,'Mais tarde, uma queda de energia apagou o apartamento. Por um instante, tudo ficou preto. Quando a luz voltou, Caio viu os olhos de Mara, a porta da cozinha e um número impossível sobre a cabeça dela. Nove mil, trezentas e onze. Piscou. O número continuava ali.'),
('home','test',9312,'Ele perguntou se ela tinha mexido no seu celular. Mara respondeu que não. O contador subiu. Caio mostrou o aparelho. Ela suspirou: estava tocando, eu desliguei o alarme. Uma mentira pequena. Uma resposta apressada. O primeiro teste funcionara. Ele mal conseguiu dormir.'),
('mirror','self',14003,'De manhã, o espelho trouxe uma surpresa menos agradável. Quatorze mil e três. O próprio número era maior que o dela. Caio procurou uma explicação confortável. Educação. Trabalho. Gentileza. Coisas sem importância. Em poucos segundos, tinha encontrado desculpas para si que não oferecera a mais ninguém.'),
('mirror','belief',14003,'Fez um segundo teste. Eu nunca julgo ninguém antes de ouvir os dois lados. O contador não mudou. Caio sorriu. Mas aquilo não provava que a frase era verdadeira. Naquele mundo imaginário, o contador só registrava o que a pessoa dizia sabendo que era falso. Convicção também pode estar errada.'),
('cafe','kindness',412,'Na cafeteria, a atendente disse que estava tudo ótimo. O número avançou. Antes que Caio comentasse, ela deixou cair uma colher. Tinha passado a noite com o filho doente. Não queria explicar a própria vida para cada cliente. Ele recebeu o café e, pela primeira vez, não soube o que fazer com a informação.'),
('street','crowd',22310,'Na rua, os números eram tantos que o mundo parecia uma vitrine de preços. Um vendedor sorridente. Uma criança escondendo um biscoito. Um homem dizendo ao telefone que já estava chegando, ainda sentado no banco. Caio via cada mudança. Começava a prestar menos atenção em quem carregava o número.'),
('court','witness',18440,'No tribunal, um segurança afirmou ter visto um rapaz esconder um telefone. A voz era firme. A postura, impecável. O contador aumentou. O rapaz tremia, mal conseguia levantar o rosto. Disse que não tinha pegado nada. Seu número permaneceu igual. Duas aparências. Nenhuma delas bastava.'),
('court','questions',18441,'Caio não apontou para uma testa invisível. Pediu que descrevessem a posição da câmera, o horário, a distância. A história do segurança começou a mudar. Uma gravação esquecida mostrou outro cliente recolhendo o aparelho. O que resolveu a situação não foi a acusação mágica. Foram perguntas que outras pessoas também podiam verificar.'),
('court','release',2906,'O rapaz saiu aliviado. Caio ficou olhando a cadeira vazia. Uma semana antes, talvez tivesse confundido medo com culpa. Agora possuía uma vantagem impossível. Isso não tornava suas decisões infalíveis. Tornava ainda mais importante não pular etapas. Ele anotou duas palavras no caderno: conferir primeiro.'),
('home','distance',9313,'Naquela noite, Mara recebeu uma ligação e foi para a varanda. Voltou dizendo que era coisa do trabalho. Mais uma mentira. Caio sentiu o peito apertar. Trabalho de quem? Com quem? O contador mostrava uma resposta falsa. Sua imaginação ofereceu imediatamente uma explicação completa. Não havia prova daquela explicação.'),
('home','phone',9313,'O celular dela ficou sobre a mesa. Caio estendeu a mão. Parou antes de tocar. A tela acendeu com uma mensagem curta: amanhã, no mesmo horário. Ele não leu mais nada. Mesmo assim, passou a noite montando uma cena inteira a partir de seis palavras. Cada detalhe inventado parecia uma descoberta.'),
('office','friend',6042,'No dia seguinte, perguntou ao colega André se tinha visto Mara. Ele respondeu que não. O número subiu. André mudou de assunto e ofereceu um café. Caio recusou. De repente, uma xícara parecia uma distração planejada. Quando a suspeita domina, até um gesto simples pode virar evidência na nossa cabeça.'),
('street','follow',9314,'À tarde, Caio viu Mara entrar em um carro. André estava ao volante. Atravessou a rua e seguiu os dois à distância. Já não olhava para os semáforos, para as pessoas ou para o caminho. Só para as duas cabeças à frente. O poder de enxergar mais estava fazendo seu mundo ficar menor.'),
('hospital','reveal',9314,'O carro parou diante de um hospital. Mara desceu carregando uma sacola. André abriu o porta-malas e tirou uma manta. Caio permaneceu do outro lado da rua. A história que tinha inventado perdeu a primeira peça. Depois outra. Um prédio podia mudar o sentido de tudo sem alterar nenhum contador.'),
('hospital','mother',6810,'Pela janela, viu sua mãe numa cadeira, esperando um exame. Mara ajeitou a manta sobre os joelhos dela. André entregou documentos na recepção. Sua mãe sorriu para os dois. Aquela era a reunião secreta. Não uma explicação para todas as mentiras do mundo. A explicação daquela, naquele dia.'),
('hospital','talk',6811,'Caio entrou. Por que ninguém me contou? A mãe baixou os olhos. Eu pedi. Queria entender os exames antes de te preocupar. Mara respirou fundo. Eu devia ter conversado com você. O contador ficou parado. As palavras verdadeiras não tornaram aquela conversa fácil. Só permitiram que ela finalmente começasse.'),
('hospital','listen',9314,'Ele tinha razão em perceber que escondiam alguma coisa. Estava errado sobre o que era. As duas coisas cabiam na mesma história. Mara também podia ter agido de outro jeito. Entender um motivo não apaga uma escolha. Mas escolher como responder exige mais do que flagrar alguém numa mentira.'),
('office','promise',6043,'Mais tarde, André tentou aliviar o clima. Eu sabia que você ia entender. O número avançou. Ele percebeu o silêncio de Caio e se corrigiu: na verdade, eu estava com medo da sua reação. Caio quase riu. A frase mais desconfortável daquela semana foi também a que devolveu alguma confiança entre os dois.'),
('street','zero',0,'Na saída do hospital, Caio reencontrou Rui, o homem da escadaria. Agora reparou no que não tinha visto antes. Zero. Nenhuma mentira registrada. A primeira reação foi desconfiar do contador. Parecia mais fácil imaginar um defeito no universo do que admitir que tinha julgado aquele homem sem ouvir sua história.'),
('street','ask',0,'Desta vez, ele parou. Perguntou o nome. Perguntou se já tinha comido. Rui respondeu que sim, de manhã, mas aceitava um lanche para mais tarde. O zero não mudou. Caio lembrou do pedido anterior. Não havia descoberto uma fraude. Só tinha ido embora antes de descobrir qualquer coisa.'),
('bench','share',0,'Compraram dois sanduíches. Rui abriu o seu, separou metade e ofereceu. Caio explicou que já tinha um. Guarda para depois, então. O contador continuava em zero. Aquilo não fazia de Rui um santo nem uma prova sobre todas as pessoas. Fazia dele alguém que merecia ser tratado como alguém.'),
('mirror','admit',14003,'Em casa, Caio encontrou Mara na cozinha. Eu achei que tinha entendido tudo, disse. Eu não tinha prova. Completei as lacunas. Olhou o reflexo no vidro. Pela primeira vez naquele dia, não procurou uma absolvição no próprio número. Pediu desculpas sem colocar uma explicação defensiva no final.'),
('home','agreement',9314,'Eles combinaram conversar sobre a mãe dele, os exames e o medo dos dois. Sem interrogatório. Sem prometer uma vida sem nenhuma mentira. Caio também contou que quase mexera no celular. Mara afastou o prato e ouviu. O poder não consertou a relação. O trabalho continuava sendo deles.'),
('court','lesson',18441,'Na manhã seguinte, alguém entrou nervoso na sala de audiência. Caio percebeu as mãos tremendo e abriu espaço para uma pausa. Outra pessoa falou com segurança. Ele pediu detalhes do mesmo jeito. Seu dom continuava ali. O que tinha mudado era a pressa de transformar impressão em sentença.'),
('diagram','rules',0,'Esse contador pertence à ficção. Na vida real, não temos números flutuantes nem um gesto que entregue toda mentira. E a história funciona justamente por isso: ela exagera uma habilidade para revelar um hábito comum. A gente vê um sinal, completa as lacunas e chama o resultado de certeza.'),
('bench','ending',0,'Talvez você quisesse esse poder para nunca mais ser enganado. Caio também queria. No fim, descobriu outro medo: passar a vida inteira julgando corretamente uma frase e compreendendo errado uma pessoa. Saber que alguém mentiu pode abrir uma pergunta. Não deveria encerrar todas as outras.'),
('street','question',0,'Agora imagine o contador aparecendo sobre a sua própria cabeça. Você gostaria que as pessoas vissem apenas aquele total? Ou pediria que conhecessem a história antes de decidir quem você é? Se pudesse enxergar as mentiras de todo mundo, qual seria a primeira pergunta que faria? Conte nos comentários. Se essa pergunta ficou na sua cabeça, inscreva-se no Então e ative o sino. Aqui, uma hipótese abre espaço para outra.')
]

TRIMS={
 'Você pensaria em políticos, golpistas, criminosos. ':'',
 'Organizado, respeitado, conhecido por não deixar passar uma contradição. ':'Conhecido por não deixar passar uma contradição. ',
 'Sorriu como quem recebe uma confirmação. ':'',
 'Uma história que ninguém tinha contado.':'Ninguém tinha contado aquela história.',
 'Mesmo assim, abriu o computador durante o jantar. ':'Abriu o computador durante o jantar. ',
 'Por um instante, tudo ficou preto. ':'',
 'Piscou. O número continuava ali.':'O número continuava ali.',
 'Uma mentira pequena. Uma resposta apressada. ':'',
 'Ele mal conseguiu dormir.':'',
 'Educação. Trabalho. Gentileza. Coisas sem importância. ':'Gentileza. Coisas sem importância. ',
 'Naquele mundo imaginário, o contador só registrava':'O contador só registrava',
 'Ele recebeu o café e, pela primeira vez, não soube o que fazer com a informação.':'Ele não soube o que fazer com a informação.',
 'Um vendedor sorridente. Uma criança escondendo um biscoito. ':'Uma criança escondendo um biscoito. ',
 'Duas aparências. Nenhuma delas bastava.':'Nenhuma aparência bastava.',
 'Pediu que descrevessem a posição da câmera, o horário, a distância.':'Perguntou pela câmera, pelo horário, pela distância.',
 'Agora possuía uma vantagem impossível. Isso não tornava suas decisões infalíveis. ':'A vantagem impossível não tornava suas decisões infalíveis. ',
 'Caio sentiu o peito apertar. Trabalho de quem? Com quem? ':'Caio sentiu o peito apertar. ',
 'Ele não leu mais nada. Mesmo assim, ':'',
 'De repente, uma xícara parecia uma distração planejada. ':'A xícara parecia uma distração. ',
 'Já não olhava para os semáforos, para as pessoas ou para o caminho.':'Já não olhava para as pessoas ou para o caminho.',
 'Depois outra. ':'',
 'Não uma explicação para todas as mentiras do mundo. A explicação daquela, naquele dia.':'Era a explicação daquela mentira.',
 'O contador ficou parado. As palavras verdadeiras não tornaram aquela conversa fácil.':'O contador parou. A verdade não tornou a conversa fácil.',
 'As duas coisas cabiam na mesma história. ':'',
 'Mara também podia ter agido de outro jeito. ':'',
 'A frase mais desconfortável daquela semana foi também a que devolveu alguma confiança entre os dois.':'A frase desconfortável devolveu alguma confiança entre os dois.',
 'Parecia mais fácil imaginar um defeito no universo do que admitir que tinha julgado aquele homem sem ouvir sua história.':'Parecia mais fácil imaginar um defeito no universo do que admitir o próprio preconceito.',
 'O zero não mudou. ':'',
 'Caio lembrou do pedido anterior. ':'',
 'Caio explicou que já tinha um. ':'',
 'O contador continuava em zero. ':'',
 'Pela primeira vez naquele dia, não procurou uma absolvição no próprio número.':'Não procurou absolvição no próprio número.',
 'Sem prometer uma vida sem nenhuma mentira. ':'',
 'Seu dom continuava ali. ':'',
 'E a história funciona justamente por isso: ela exagera uma habilidade para revelar um hábito comum.':'A história exagera uma habilidade para revelar um hábito comum.',
 'Caio também queria. ':'',
 'Ou pediria que conhecessem a história antes de decidir quem você é?':'Ou pediria que conhecessem a história antes de julgar?',
}
BEATS=[(loc,action,count,__import__('functools').reduce(lambda text,pair:text.replace(*pair),TRIMS.items(),text).strip()) for loc,action,count,text in BEATS]

def main():
 duration=500.0
 weights=[len(re.findall(r'\S+',b[3]))+5 for b in BEATS];total=sum(weights)
 beats=[];shots=[];t=0
 for i,(loc,action,count,narration) in enumerate(BEATS):
  end=round(t+weights[i]/total*duration,3) if i<len(BEATS)-1 else duration
  # Four intentional framings per beat, no narration rewritten by the renderer.
  modes=['wide','two','insert','close']
  if action in ['questions','talk','listen','agreement']:modes=['two','ots','close','two']
  if action in ['belief','self','admit']:modes=['wide','insert','close','ots']
  if action in ['follow','arrival','reveal','ending']:modes=['wide','track','ots','close']
  beats.append(dict(id=i+1,start=t,end=end,set=loc,action=action,count=count,text=narration))
  for j,mode in enumerate(modes):
   a=round(t+(end-t)*j/4,3);b=round(t+(end-t)*(j+1)/4,3)
   shots.append(dict(id=f's{len(shots)+1:03}',start=a,end=b,line=narration,scene=f'{loc}: {action}; {mode}; atuação motivada, olhar e objetos em continuidade',set=loc,bars='none',**{'in':{'type':'dip' if j==0 and i in [2,5,11,18,23,26,29] else 'cut','dur':.25}},params=dict(beat=i,mode=mode,part=j),sfx=[],notes='Timing preliminar; alinhar com segmentos de voz real.'))
  t=end
 (ROOT/'story/beats.json').write_text(json.dumps(beats,ensure_ascii=False,indent=2))
 (ROOT/'story/shots.json').write_text(json.dumps(dict(title='E se você pudesse ver as mentiras?',duration=duration,shots=shots,music=[]),ensure_ascii=False,indent=2))
 (ROOT/'input/narracao.txt').write_text('\n\n'.join(b[3] for b in BEATS)+'\n')
 (ROOT/'ROTEIRO.md').write_text('# E se você pudesse ver as mentiras?\n\nRoteiro próprio inspirado na premissa fornecida. Duração-alvo: 8min20s. Timestamps abaixo são preliminares, não alinhamento de voz. Narração Puck ainda pendente.\n\n'+'\n\n'.join(f'## {int(b["start"])//60:02}:{int(b["start"])%60:02} — {b["action"]}\n\n{b["text"]}' for b in beats)+'\n')
 cfg=dict(title='02 - Quantas mentiras',aspect='16:9',resolution='1080p',fps=24,style='midnight',voiceover='audio/narracao.wav',script='input/narracao.txt',duration=duration,captions=False,bars='none',fadeIn=.25,fadeOut=.8,music=dict(enabled=False),sfx=dict(enabled=True),loudness=-16)
 (ROOT/'config.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2))
 print(len(BEATS),'sequências;',len(shots),'planos;',sum(w-5 for w in weights),'palavras;',duration,'segundos')

if __name__=='__main__':main()
