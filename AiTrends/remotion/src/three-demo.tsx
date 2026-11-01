import React, {useMemo} from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
// Reuse the original rounded cast, not a Minecraft avatar or downloaded model.
// @ts-expect-error Existing aiTrends JavaScript rig has no TypeScript declarations.
import {actor} from '../../projetos/38-janela-pachinko/scenes/rig.js';
const CameraMotion: React.FC<{time:number}>=({time})=>{const {camera}=useThree();camera.position.set(2.7+Math.sin(time*.6)*.35,2.4,5.4);camera.lookAt(0,1.1,0);return null;};
const Cast: React.FC<{time:number}>=({time})=>{
 const cast=useMemo(()=>actor({THREE},'nico'),[]);
 cast.update({time,x:Math.sin(time*.6)*.15,z:0,y:0,yaw:-Math.PI/2+.12*Math.sin(time),headYaw:.15*Math.sin(time*.7),moving:false,expr:'smile',gesture:'point',gestureWeight:.38+.08*Math.sin(time*2)});
 return <primitive object={cast.root}/>;
};
export const Original3DDemo: React.FC=()=>{
 const frame=useCurrentFrame(),{width,height,fps}=useVideoConfig(),time=frame/fps;
 return <AbsoluteFill style={{background:'#172949'}}>
  <ThreeCanvas width={width} height={height} camera={{position:[2.7,2.4,5.4],fov:43}} gl={{antialias:true}}>
   <color attach="background" args={['#182747']}/><hemisphereLight args={['#d9f6ff','#603f67',2]}/><directionalLight position={[3,6,5]} intensity={2}/><pointLight position={[-2,2,-1]} color="#e568d9" intensity={8}/>
   <CameraMotion time={time}/><Cast time={time}/>
   <mesh position={[0,-.12,0]}><boxGeometry args={[15,.24,15]}/><meshLambertMaterial color="#557c91"/></mesh>
   {[-3,-1.7,1.7,3].map((x,i)=><group key={i} position={[x,0,-2]}><mesh position={[0,1.2,0]}><boxGeometry args={[1.1,2.4,1]}/><meshLambertMaterial color={['#dc93b7','#80c3cd','#b79ad4','#dbb27b'][i]}/></mesh><mesh position={[0,1.7,.51]}><boxGeometry args={[.55,.6,.025]}/><meshBasicMaterial color="#ffe7a2"/></mesh></group>)}
  </ThreeCanvas>
  <div style={{position:'absolute',top:150,width:'100%',font:'900 76px sans-serif',textAlign:'center',color:'#fff1ba',textShadow:'0 5px 4px #10213b'}}>NOSSO PERSONAGEM 3D</div>
  <div style={{position:'absolute',bottom:150,width:'100%',font:'bold 38px sans-serif',textAlign:'center',color:'#fff7df'}}>Remotion + Three.js • teste do motor</div>
 </AbsoluteFill>;
};
