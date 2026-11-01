import React from 'react';
import {AbsoluteFill, Audio, OffthreadVideo, Sequence, staticFile, useVideoConfig} from 'remotion';
export type EpisodeProps={video:string;audio:string;durationSeconds:number;title:string;ctas:{src:string;start:number;duration:number;width?:number;top?:number}[]};
export const EpisodeMontage: React.FC<EpisodeProps>=({video,audio,ctas,title})=>{
 const {fps}=useVideoConfig();
 return <AbsoluteFill style={{backgroundColor:'#12213b'}}>
  {video?<OffthreadVideo src={staticFile(video)} muted style={{width:'100%',height:'100%',objectFit:'contain'}}/>:<AbsoluteFill style={{alignItems:'center',justifyContent:'center',color:'#fff',fontSize:56,padding:80,textAlign:'center'}}>Carregue um projeto aiTrends com npm run episode -- --project CAMINHO</AbsoluteFill>}
  {audio&&<Audio src={staticFile(audio)}/>}
  {ctas.map((cta,i)=><Sequence key={i} from={Math.round(cta.start*fps)} durationInFrames={Math.round(cta.duration*fps)}>
    <AbsoluteFill style={{alignItems:'center',justifyContent:'flex-start',paddingTop:cta.top??1550}}><OffthreadVideo src={staticFile(cta.src)} muted style={{width:cta.width??720}}/></AbsoluteFill>
  </Sequence>)}
  {title&&<div style={{position:'absolute',top:80,width:'100%',textAlign:'center',font:'bold 50px sans-serif',color:'white',textShadow:'0 4px 6px #000'}}>{title}</div>}
 </AbsoluteFill>;
};
