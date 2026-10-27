"""Write user's single YOUTUBE file; no remote calls."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];Y=P.parents[1]/'youtube'/'06 - Duas Pessoas Podem Recomeçar a Humanidade'
def main():
 beats=json.loads((P/'story/beats.json').read_text());chapters=[(0,'Uma cidade e duas pessoas'),(2,'A conta que parece resolver tudo'),(5,'As caixas da herança genética'),(8,'O que significa 25% neste exemplo'),(10,'Parentesco e riscos'),(13,'O peso do acaso'),(16,'Água, trabalho e cuidado'),(19,'E se existisse material preservado?'),(20,'Não há número mágico'),(23,'Procurando outras pessoas'),(26,'Uma comunidade muda o problema'),(29,'A resposta para a hipótese')]
 def tc(t):t=int(t);return f'{t//60:02}:{t%60:02}'
 text='''TÍTULO
Duas pessoas conseguiriam recomeçar a humanidade?

DESCRIÇÃO
A cidade está vazia. Só restaram Nico e Lia. Será que uma família crescendo resolveria tudo — ou existe um problema escondido na genética?

Uma história original do Então sobre diversidade genética, herança, sobrevivência e a diferença entre aumentar uma população e construir uma comunidade viável.

CAPÍTULOS
'''+''.join(tc(beats[i]['start'])+' — '+name+'\n'for i,name in chapters)+'''
Qual habilidade você procuraria primeiro numa comunidade começando do zero? Deixe sua resposta nos comentários e inscreva-se no Então para explorar a próxima hipótese.

Ficção explicativa. Os diagramas usam modelos simplificados, não previsões sobre famílias reais. O exemplo de 25% se refere especificamente a dois portadores da mesma condição autossômica recessiva no modelo apresentado. Risco não significa destino, e não existe aqui uma recomendação de reprodução ou aconselhamento médico.

Animação e efeitos sonoros criados por código; personagens e roteiro próprios; narração sintética Puck.

#Então #Genética #ESe

TAGS
Então, duas pessoas, recomeçar a humanidade, humanidade, genética, diversidade genética, gargalo populacional, deriva genética, herança genética, população, sobrevivência, ciência, histórias animadas, e se
'''
 Y.mkdir(parents=True,exist_ok=True);(Y/'YOUTUBE').write_text(text)
 print('YOUTUBE_SINGLE_FILE_UPDATED')
if __name__=='__main__':main()
