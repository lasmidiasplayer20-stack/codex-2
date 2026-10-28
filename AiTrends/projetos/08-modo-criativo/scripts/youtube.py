"""One YOUTUBE metadata file as requested; no uploads or API calls."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];Y=P.parents[1]/'youtube'/'08 - E se você tivesse Modo Criativo na vida real'
def main():
 b=json.loads((P/'story/beats.json').read_text());chapters=[(0,'Um menu no mundo real'),(3,'O primeiro voo'),(5,'Poder não é permissão'),(7,'Uma ponte de verdade?'),(11,'Ouro sem limite'),(14,'Pedidos que não acabam'),(15,'Quem fica lá embaixo?'),(18,'Invencível não significa responsável'),(21,'Uma ilha perfeita e vazia'),(24,'Voltar para construir juntos'),(26,'Pensar antes de criar'),(29,'Escolher os próprios limites')]
 def tc(t):t=int(t);return f'{t//60:02}:{t%60:02}'
 content='''TÍTULO
E se você tivesse Modo Criativo na vida real?

DESCRIÇÃO
Um menu aparece no ar. Você pode criar objetos, voar entre prédios e mudar a cidade com um gesto. Mas o que acontece quando sua liberdade começa a ocupar o espaço das outras pessoas?

Nico e Lia exploram uma hipótese em que construir deixou de ser difícil — e escolher ficou muito mais importante. De uma cadeira simples a uma ilha suspensa, uma história original do Então sobre criatividade, consequências e os limites que a gente decide respeitar.

CAPÍTULOS
'''+''.join(tc(b[i]['start'])+' — '+name+'\n'for i,name in chapters)+'''
Qual seria sua primeira criação? E qual regra você colocaria para esse poder? Conta nos comentários e inscreva-se no Então para explorar a próxima hipótese.

Ficção especulativa. Os poderes e construções pertencem à fantasia da história; não são instruções de engenharia ou previsão científica. Personagens e história próprios, animação e efeitos por código, narração sintética.

#Então #ModoCriativo #ESe

TAGS
Então, modo criativo, modo criativo na vida real, e se, poder criar tudo, criatividade, poderes, voar, histórias animadas, ficção especulativa, consequências, imaginação, Nico e Lia, animação brasileira, inventário infinito, liberdade
'''
 Y.mkdir(exist_ok=True,parents=True);(Y/'YOUTUBE').write_text(content);print('YOUTUBE_UPDATED')
if __name__=='__main__':main()
