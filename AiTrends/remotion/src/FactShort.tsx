import React, {useMemo} from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {worlds} from './fact-scenes';
export type FactShot={id:string;start:number;end:number;params:{act:number;view:number;label:string;sub:string}};
export type FactProps={theme:number;shots:FactShot[];durationSeconds:number;cover?:boolean};
const Scene:React.FC<FactProps>=({theme,shots,cover})=>{const frame=useCurrentFrame(),{fps}=useVideoConfig(),{camera}=useThree();const world=worlds[theme];const scene=useMemo(()=>world.createFactScene(THREE,theme),[theme,world]);world.updateFactScene(scene,camera,frame/fps,shots,cover);return <primitive object={scene.root}/>;};
export const FactShort:React.FC<FactProps>=props=>{
 const frame=useCurrentFrame(),{fps,width,height}=useVideoConfig(),time=frame/fps,shot=props.shots.find(s=>time>=s.start&&time<s.end)||props.shots[props.shots.length-1];
 return <AbsoluteFill style={{background:'#9acfe0'}}>
  <ThreeCanvas width={width} height={height} camera={{position:[3,2.6,6.5],fov:43}} gl={{antialias:true}}><color attach="background" args={[props.cover?'#14213d':props.theme===41?'#45365e':props.theme===43?'#9dc9df':'#9acfe0']}/><Scene {...props}/></ThreeCanvas>
  {!props.cover&&shot&&<><div style={{position:'absolute',top:125,left:55,width:970,minHeight:130,padding:'20px 24px',borderRadius:22,boxSizing:'border-box',background:'#13253fee',textAlign:'center',fontFamily:'sans-serif',boxShadow:'0 4px 14px #14233a22'}}><div style={{fontSize:37,fontWeight:900,color:'#ffe49a',lineHeight:1.20}}>{shot.params.label}</div><div style={{fontSize:30,fontWeight:600,color:'#e3fff5',marginTop:12,lineHeight:1.25}}>{shot.params.sub}</div></div><div style={{position:'absolute',bottom:105,width:'100%',textAlign:'center',font:'700 23px sans-serif',color:'#fff8de',textShadow:'0 2px 4px #15243b'}}>ENTÃO • EXPLICAÇÃO ILUSTRADA</div></>}
 </AbsoluteFill>;
};
