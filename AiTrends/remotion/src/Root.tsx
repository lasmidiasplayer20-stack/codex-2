import React from 'react';
import {Composition} from 'remotion';
import {Original3DDemo} from './three-demo';
import {EntaoDemo} from './demo';
import {EpisodeMontage, type EpisodeProps} from './montage';
const defaults: EpisodeProps={video:'',audio:'',durationSeconds:10,ctas:[],title:''};
export const Root: React.FC=()=> <>
  <Composition id="Original3DDemo" component={Original3DDemo} width={1080} height={1920} fps={24} durationInFrames={120}/>
  <Composition id="EntaoDemo" component={EntaoDemo} width={1080} height={1920} fps={24} durationInFrames={240}/>
  <Composition id="EpisodeMontage" component={EpisodeMontage} width={1080} height={1920} fps={24} durationInFrames={240} defaultProps={defaults} calculateMetadata={({props})=>({durationInFrames:Math.round(props.durationSeconds*24)})}/>
</>;
