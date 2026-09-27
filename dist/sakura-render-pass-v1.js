'use strict';
// Sakura-inspired rendering pass v1.
// Rendering only: combat state, camera, animation, hit detection, input and model geometry stay untouched.
(()=>{
  if(window.__pdSakuraRenderV1Loaded)return;
  window.__pdSakuraRenderV1Loaded=true;
  const API=window.ParryVisual;
  if(!API?.VisualScene)return;

  const BaseScene=API.VisualScene;

  function patchMaterial(mat){
    if(!mat||mat.userData?.pdSakuraRenderV1)return;
    if(!(mat.isMeshStandardMaterial||mat.isMeshPhysicalMaterial))return;
    mat.userData=mat.userData||{};
    mat.userData.pdSakuraRenderV1=true;

    const previous=mat.onBeforeCompile;
    const previousKey=mat.customProgramCacheKey?.bind(mat);
    const metal=Number.isFinite(mat.metalness)?mat.metalness:0;
    const rough=Number.isFinite(mat.roughness)?mat.roughness:.6;
    const bandMix=metal>.45?.085:rough>.82?.145:.115;
    const shadowMix=metal>.45?.14:rough>.82?.24:.19;

    mat.onBeforeCompile=function(shader,renderer){
      previous?.call(this,shader,renderer);
      const hook='#include <opaque_fragment>';
      if(!shader.fragmentShader.includes(hook))return;
      const grading=`
        // PARRY DOLL Sakura pass: retain PBR highlights but simplify the mid-tone
        // response and hue-shift shadows instead of merely crushing them darker.
        float pdLum=max(dot(outgoingLight,vec3(0.2126,0.7152,0.0722)),0.0001);
        float pdBand=floor(pdLum*5.0+0.5)/5.0;
        float pdBandLum=mix(pdLum,pdBand,${bandMix.toFixed(3)});
        outgoingLight*=pdBandLum/pdLum;
        float pdShadow=1.0-smoothstep(0.16,0.70,pdLum);
        vec3 pdCool=outgoingLight*vec3(0.80,0.87,1.07)+vec3(0.010,0.014,0.030);
        outgoingLight=mix(outgoingLight,pdCool,pdShadow*${shadowMix.toFixed(3)});
        float pdLight=smoothstep(0.72,1.35,pdLum);
        outgoingLight=mix(outgoingLight,outgoingLight*vec3(1.035,1.012,0.988),pdLight*0.12);
      `;
      shader.fragmentShader=shader.fragmentShader.replace(hook,grading+'\n'+hook);
    };
    mat.customProgramCacheKey=()=>((previousKey?previousKey():'')+'|pd-sakura-render-v1');
    mat.needsUpdate=true;
  }

  class SakuraVisualScene extends BaseScene{
    constructor(canvas){
      super(canvas);
      // Keep highlights cinematic while restoring readable coloured shadows.
      this.renderer.toneMappingExposure=1.13;
      if(this.scene.environmentIntensity!==undefined)this.scene.environmentIntensity=.76;
      this.scene.background?.set?.('#b9d5e6');
      if(this.scene.fog){
        this.scene.fog.color?.set?.('#c2d9e6');
        if('density' in this.scene.fog)this.scene.fog.density=.0082;
      }

      // Two-light anime logic: warm key, cool opposite-side separation,
      // violet ground bounce instead of neutral/dark ambient shadow.
      const hemis=this.scene.children.filter(o=>o?.isHemisphereLight);
      for(const hemi of hemis){
        hemi.color?.set?.('#c9e6ff');
        hemi.groundColor?.set?.('#6c6880');
        hemi.intensity=1.66;
      }
      if(this.key){
        this.key.color?.set?.('#ffe8cb');
        this.key.intensity=3.72;
      }
      const dirs=this.scene.children.filter(o=>o?.isDirectionalLight&&o!==this.key);
      if(dirs[0]){
        dirs[0].color?.set?.('#8fc7f0');
        dirs[0].intensity=2.18;
      }

      // Cheap final resolve for the WebGL layer only; HUD/telegraphs keep their
      // semantic colours and touch readability.
      canvas.style.filter='saturate(1.055) contrast(1.035) brightness(1.012)';
      this._pdSweepMaterials();
    }

    _pdSweepMaterials(){
      this.scene.traverse?.(obj=>{
        if(!obj?.isMesh)return;
        const mats=Array.isArray(obj.material)?obj.material:[obj.material];
        mats.forEach(patchMaterial);
      });
    }

    render(state){
      const result=super.render(state);
      // Actors and the optional Blender heroine arrive lazily. Sweep frequently
      // during warm-up, then only occasionally so this has negligible frame cost.
      const n=this.frameCount||0;
      if((n<360&&n%20===1)||n%180===1)this._pdSweepMaterials();
      return result;
    }
  }

  API.VisualScene=SakuraVisualScene;
})();
