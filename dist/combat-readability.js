'use strict';
// Combat readability pass: preserve impact while keeping silhouettes and reaction direction visible.
const readabilityStyle=document.createElement('style');
readabilityStyle.textContent=`
#toast.readability-parry{top:12%;left:auto;right:max(28px,env(safe-area-inset-right));width:auto;text-align:right;font-size:clamp(13px,2vw,18px);letter-spacing:2px;color:#ffe0a4}
#toast.readability-finisher{top:auto;bottom:29%;left:58%;right:auto;width:auto;padding:5px 9px;border:1px solid #f0c47a88;background:#15181bb8;font-size:clamp(13px,2vw,18px);letter-spacing:3px;color:#ffe2a3;border-radius:3px}
#toast.readability-normal{top:16%;left:0;right:0;width:100%;text-align:center}
#cue{top:25%;font-size:clamp(13px,2.2vw,17px);letter-spacing:2.5px}
@media(max-height:500px){#toast.readability-parry{top:10%}#toast.readability-finisher{bottom:27%}#cue{top:24%}}
`;
document.head.appendChild(readabilityStyle);

const readabilityAnnounce=announce;
announce=function(t,d){
 const el=$('toast');
 el.classList.remove('readability-parry','readability-finisher','readability-normal');
 if(t==='PERFECT PARRY'||t==='PARRY'||t==='弾 き 返 し')el.classList.add('readability-parry');
 else if(t==='斬 れ')el.classList.add('readability-finisher');
 else el.classList.add('readability-normal');
 return readabilityAnnounce(t,d);
};

// Suppress the whole-body white flash when a precise hit-location reaction is active.
// Replace it with a short glow on the actual struck node so the pose remains readable.
const readabilityDrawDoll=drawDoll;
drawDoll=function(d){
 const inv=d.invuln,localized=d.hitRegionT>0&&d.hp>0;
 if(localized)d.invuln=0;
 readabilityDrawDoll(d);
 d.invuln=inv;
 if(localized&&typeof hitNodeForRegion==='function'){
  const n=hitNodeForRegion(d,d.hitRegion,d.hitRegionSide);
  if(n){
   const pulse=Math.sin(clamp(d.hitRegionT/(d.hitRegionMax||.3),0,1)*Math.PI),base=d.player?'#bffcf0':'#ffd39a';
   orb(n.p,Math.max(n.r*1.55,.18*d.spec.scale),base);
   const q=add(n.p,V(0,.06*d.spec.scale,0));
   orb(q,Math.max(n.r*.72,.09*d.spec.scale),'#fff5d6');
  }
 }
};

// At contact range, move the camera laterally instead of only pulling back.
// The parallax separates the two silhouettes during hits and finishers.
const readabilitySetCamera=setCamera;
setCamera=function(){
 readabilitySetCamera();
 if(!player||!boss||mode!=='play'||!basis)return;
 const distance=Math.hypot(boss.pos.x-player.pos.x,boss.pos.z-player.pos.z);
 const active=player.attack>0||boss.strike>0||boss.broken>0||player.counter>0;
 let contact=clamp((3.25-distance)/1.55,0,1)*(active?1:.45);
 if(boss.spec.scale>1.8)contact*=.72;
 if(contact<=.01)return;
 const side=(level%2?-.82:1),shift=(W<H?.34:1.15)*contact*side;
 camera=add(camera,mul(basis.right,shift));
 const mid=add(mul(player.pos,.44),mul(boss.pos,.56)),focus=V(mid.x,1.28+Math.max(0,boss.spec.scale-1.3)*.48,mid.z);
 target=add(mul(target,1-contact*.34),mul(focus,contact*.34));
 const f=norm(sub(target,camera)),r=norm(V(-f.z,0,f.x)),up=V(r.y*f.z-r.z*f.y,r.z*f.x-r.x*f.z,r.x*f.y-r.y*f.x);basis={f,right:r,up};
};

// Exaggerate the non-human silhouettes so their attacks read without relying on text/telegraphs.
Object.assign(REVIEW_PREP['二連噛み'],{xScale:.74,zScale:.84,crouch:.28,headZ:-.56,frontRetract:.40});
Object.assign(REVIEW_PREP['跳びかかり'],{xScale:.54,zScale:.56,crouch:.74,headZ:-.42,allLegPull:.52});
Object.assign(REVIEW_PREP['牙の直進突撃'],{xScale:.66,zScale:1.18,crouch:.42,headZ:.34,frontRetract:.62});
Object.assign(REVIEW_PREP['尾の回転薙ぎ'],{xScale:1.58,zScale:1.16,crouch:.08,twist:1.12});
Object.assign(REVIEW_PREP['双脚刺突'],{xScale:1.36,crouch:.08,headZ:-.30,frontRetract:1.02,frontLift:.28});
Object.assign(REVIEW_PREP['八脚回転'],{xScale:1.72,zScale:1.16,crouch:.08,twist:1.24});
Object.assign(REVIEW_PREP['天蓋落とし'],{xScale:.42,zScale:.48,crouch:.70,headZ:-.38,allLegPull:.58});
Object.assign(REVIEW_PREP['三連脚槍'],{xScale:1.48,zScale:.78,crouch:.15,frontRetract:.94,legWave:.44});

const readabilityEnemyPose=enemyPoseTarget;
enemyPoseTarget=function(d,n){
 let p=readabilityEnemyPose(d,n);
 if(d.spec.type==='human'||d.strike<=0)return p;
 p={...p};const move=enemyMove(d),a=clamp(d.strikeElapsed/(move.active||1),0,1),pulse=Math.sin(a*Math.PI),s=d.spec.scale;
 if(move.name==='跳びかかり'||move.name==='天蓋落とし'){
  if(n.name==='knee'||n.name==='foot'){p.x*=1-.26*pulse;p.z*=1-.22*pulse;}
  if(n.name==='head')p.z+=.32*s*pulse;
 }
 if(move.name==='三連脚槍'&&(n.name==='knee'||n.name==='foot')&&n.rest.z>0){p.z+=.72*s*pulse;p.x*=1.12;}
 if(move.name==='八脚回転'||move.name==='尾の回転薙ぎ'){p.x*=1+.18*pulse;}
 if(move.name==='牙の直進突撃'&&n.name==='head')p.z+=.46*s*pulse;
 return p;
};

// Use more of the directional reaction system instead of repeatedly driving the same axis.
const readabilityEnemyStrikeDirection=enemyStrikeDirection;
enemyStrikeDirection=function(move,index){
 const i=Math.max(0,(index||1)-1),dirs={
  '二連・袈裟返し':[V(-1,-.52,.28),V(1,.28,.20)],
  '踏み込み突き':[V(.10,.08,1)],
  '溜め・一刀落とし':[V(.08,-1,.18)],
  '横歩き・逆薙ぎ':[V(1,.08,.18)],
  '二連噛み':[V(-.70,.10,.62),V(.76,-.18,.54)],
  '跳びかかり':[V(.18,-.74,.76)],
  '牙の直進突撃':[V(-.16,.06,1)],
  '尾の回転薙ぎ':[V(-1,-.18,.16)],
  '双脚刺突':[V(.18,.30,.94)],
  '八脚回転':[V(1,-.12,.12)],
  '天蓋落とし':[V(-.16,-1,.34)],
  '三連脚槍':[V(-1,.26,.18),V(.12,.06,1),V(1,-.56,.14)],
  '鐘砕き・溜め落とし':[V(.08,-1,.20)],
  '大薙ぎ':[V(-1,.06,.18)],
  '震脚':[V(.10,-1,.04)],
  '巨腕の押し込み':[V(.24,.12,1)]
 };
 const local=dirs[move?.name]?.[i%dirs[move?.name]?.length];
 return local?norm(boss.local(local)):readabilityEnemyStrikeDirection(move,index);
};
