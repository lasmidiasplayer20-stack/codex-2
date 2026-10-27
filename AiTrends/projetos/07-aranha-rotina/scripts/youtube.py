"""Single user-requested YOUTUBE file; updates chapters from current timeline, offline."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];Y=P.parents[1]/'youtube'/'07 - E se uma aranha aprendesse sua rotina'
def main():
 b=json.loads((P/'story/beats.json').read_text());chapters=[(0,'Ela desapareceu'),(5,'A regra impossível'),(6,'Padrão ou coincidência?'),(9,'No tamanho da aranha'),(11,'Repetir também ensina'),(13,'O copo e o cartão'),(15,'Ela voltou?'),(17,'O que a câmera não mostra'),(22,'Um caminho diferente'),(25,'O fio no interruptor'),(27,'A luz se apaga'),(30,'A última pista')]
 def tc(t):t=int(t);return f'{t//60:02}:{t%60:02}'
 content='''TÍTULO
E se uma aranha aprendesse sua rotina?

DESCRIÇÃO
Você vê uma aranha no quarto. Vai buscar um copo. Quando volta, ela sumiu. Só que, nesta história, a visitante parece saber para onde você vai antes de você chegar.

Nico e Lia tentam separar coincidência, medo e pistas reais numa noite em que cada hábito pode entregar o próximo movimento. Até encontrarem um fio junto ao interruptor.

Uma ficção original de suspense do Então. A capacidade de aprender e antecipar rotinas humanas apresentada aqui é uma regra fantástica da história; as cenas não descrevem o comportamento de uma espécie real de aranha.

CAPÍTULOS
'''+''.join(tc(b[i]['start'])+' — '+title+'\n' for i,title in chapters)+'''
Qual rotina entregaria você primeiro? Conta nos comentários e inscreva-se no Então para a próxima hipótese.

Personagens, história e animação próprios. Narração sintética. Sem imagens de animais reais ou violência gráfica.

#Então #ESe #Suspense

TAGS
Então, e se, aranha, aranha no quarto, e se uma aranha aprendesse sua rotina, histórias animadas, suspense animado, ficção, mistério, rotina, medo, Nico e Lia, animação brasileira, suspense, hipóteses
'''
 Y.mkdir(exist_ok=True,parents=True);(Y/'YOUTUBE').write_text(content);print('YOUTUBE_SINGLE_FILE_UPDATED')
if __name__=='__main__':main()
