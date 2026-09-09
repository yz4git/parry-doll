import * as THREE from 'three';
// Preserve clothing materials. This pass owns only the skin and hair surface response.
export function heroineMaterials(shared){
 const base=new URL('.',document.currentScript?.src||location.href),texture=new THREE.TextureLoader().load(new URL('assets/hair-fibers.png',base).href);texture.wrapS=texture.wrapT=THREE.ClampToEdgeWrapping;texture.anisotropy=4;
 const mats={...shared,leather:shared.cloth,skin:new THREE.MeshPhysicalMaterial({vertexColors:true,roughness:.5,metalness:0,clearcoat:.06}),hair:new THREE.MeshPhysicalMaterial({vertexColors:true,roughness:.56,metalness:.01,clearcoat:.07}),hairCard:new THREE.MeshStandardMaterial({color:'#ffffff',vertexColors:true,roughness:.56,metalness:.01,alphaMap:texture,alphaTest:.34,side:THREE.DoubleSide,depthWrite:true})};
 return{mats,dispose(){mats.skin.dispose();mats.hair.dispose();mats.hairCard.dispose();texture.dispose()}};
}
