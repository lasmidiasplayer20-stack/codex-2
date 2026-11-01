import React from 'react';
import {Composition} from 'remotion';
import {Original3DDemo} from './three-demo';
import {FactShort} from './FactShort';
import {EntaoDemo} from './demo';
import {EpisodeMontage, type EpisodeProps} from './montage';
const defaults: EpisodeProps={video:'',audio:'',durationSeconds:10,ctas:[],title:''};
export const Root: React.FC=()=> <>
  <Composition id="FactShort" component={FactShort} width={1080} height={1920} fps={24} durationInFrames={1080} defaultProps={{theme:39,durationSeconds:45,shots:Array.from({length:6},(_,i)=>({id:`s${i}`,start:i*7.5,end:(i+1)*7.5,params:{act:i,view:0,label:"TÉRREO ABERTO",sub:"Demonstração do cenário"}}))}} calculateMetadata={({props})=>({durationInFrames:Math.round(props.durationSeconds*24)})}/>
  <Composition id="Original3DDemo" component={Original3DDemo} width={1080} height={1920} fps={24} durationInFrames={120}/>
  <Composition id="EntaoDemo" component={EntaoDemo} width={1080} height={1920} fps={24} durationInFrames={240}/>
  <Composition id="EpisodeMontage" component={EpisodeMontage} width={1080} height={1920} fps={24} durationInFrames={240} defaultProps={defaults} calculateMetadata={({props})=>({durationInFrames:Math.round(props.durationSeconds*24)})}/>
</>;
