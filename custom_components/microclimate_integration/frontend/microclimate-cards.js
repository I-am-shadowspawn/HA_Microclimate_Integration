var me=[{temperature:0,color:"#f6c85f"},{temperature:20,color:"#f5a623"},{temperature:25,color:"#ef7d16"},{temperature:30,color:"#d94b24"},{temperature:35,color:"#b52222"}];function Y(s){if(s!==void 0&&(!Array.isArray(s)||s.length===0||s.some(t=>!t||typeof t.temperature!="number"||!Number.isFinite(t.temperature)||t.temperature<0||t.temperature>100||typeof t.color!="string"||!/^#[0-9a-f]{6}$/i.test(t.color))||new Set(s.map(t=>t.temperature)).size!==s.length))throw new Error("Temperature colours require unique Celsius bounds from 0 to 100 and #RRGGBB colours.")}function ft(s,t=me){if(s===null||!Number.isFinite(s))return"#737373";let e=[...t].sort((i,r)=>i.temperature-r.temperature);return(e.filter(i=>s>=i.temperature).at(-1)??e[0]).color}function mt(s){let t=[1,3,5].map(i=>{let r=parseInt(s.slice(i,i+2),16)/255;return r<=.04045?r/12.92:((r+.055)/1.055)**2.4});return t[0]*.2126+t[1]*.7152+t[2]*.0722>.179?"#000000":"#ffffff"}function Re(s,t,e){let i=t==="\xB0C"?ft(s,e):"#327b80";return`--segment-color:${i};--segment-text:${mt(i)}`}function C(){let s=crypto.getRandomValues(new Uint8Array(16));s[6]=s[6]&15|64,s[8]=s[8]&63|128;let t=Array.from(s,e=>e.toString(16).padStart(2,"0")).join("");return`${t.slice(0,8)}-${t.slice(8,12)}-${t.slice(12,16)}-${t.slice(16,20)}-${t.slice(20)}`}function O(s,t=100){return typeof s=="number"&&Number.isFinite(s)&&s>=0&&s<=t}function G(s){return O(s,86399)&&Number.isInteger(s)}function Q(s,t){return s==="Multi"?t>=2&&t<=8:s==="Day Night"?t===2:s==="Seasonal"?t===8:!1}function ge(s){if(typeof s!="string"||s.length!==5||!/^[0-9]{2}\/[0-9]{2}$/.test(s))return null;let[t,e]=s.split("/").map(Number),i=new Date(Date.UTC(2001,e-1,t));return i.getUTCMonth()!==e-1||i.getUTCDate()!==t?null:Math.floor((i.getTime()-Date.UTC(2001,0,1))/864e5)}var Ue=s=>s.seconds===0&&s.target_native===0,_=s=>s===null?"":`${Math.floor(s/3600).toString().padStart(2,"0")}:${Math.floor(s/60%60).toString().padStart(2,"0")}:${(s%60).toString().padStart(2,"0")}`;function Oe(s){if(!/^\d{2}:\d{2}(:\d{2})?$/.test(s))return null;let[t,e,i=0]=s.split(":").map(Number);return t<24&&e<60&&i<60?t*3600+e*60+i:null}var b=(s,t,e)=>t==="\xB0C"&&e?s*9/5+32:s,ee=(s,t,e)=>t==="\xB0C"&&e?(s-32)*5/9:s;function j(s){let t=String(s.fields.find(n=>n.key===`${s.channel}_timing_type`)?.value??""),e=[],i=t==="Day Night"?2:["Multi","Seasonal"].includes(t)?8:0;for(let n=1;n<=i;n++)e.push({draft_id:C(),source_slot:n,seconds:s.fields.find(o=>o.key===`${s.channel}_period_${n}_time`)?.value??null,target_native:s.fields.find(o=>o.key===`${s.channel}_period_${n}_setpoint`)?.value??null});if(t==="Multi")for(;e.length&&Ue(e.at(-1));)e.pop();let r={base:s,values:Object.fromEntries(s.fields.filter(n=>!n.index&&(!n.shared||!s.channel)).map(n=>[n.key,n.value])),points:e,mode:t,repair:!1};return r.repair=t==="Multi"&&w(r)!==null,r}function w(s){if(!["Multi","Day Night","Seasonal"].includes(s.mode))return null;if(!Q(s.mode,s.points.length))return s.mode==="Multi"?"Multi needs 2\u20138 points.":`${s.mode} needs ${s.mode==="Day Night"?2:8} points.`;if(s.points.some(t=>!G(t.seconds)||!O(t.target_native)))return"Complete every time and target (0\u2013100).";if(s.mode==="Multi"){if(s.points.some(Ue))return"Midnight with target zero is reserved for unused slots.";if(s.points.some((t,e)=>e>0&&t.seconds<=s.points[e-1].seconds))return"Multi starts must be distinct and chronological."}else if(s.points.some((t,e)=>e%2===0&&t.seconds===s.points[e+1]?.seconds))return"Day and Night must have distinct starts.";return null}function gt(s){let t=[];for(let e of s){if(e==="00/00")continue;if(typeof e!="string"||!/^\d{2}\/\d{2}$/.test(e))return"Use DD/MM for every season date.";let i=ge(e);if(i===null)return"Use valid calendar dates; 29/02 is not supported.";t.push(i)}return new Set(t).size!==t.length?"Season starts must be distinct.":t.length>1&&t.reduce((e,i,r)=>e+(t[(r+1)%t.length]-i+365)%365,0)!==365?"Seasons must follow one annual cycle (one year wrap is allowed).":null}function P(s){return Object.fromEntries(Object.entries(s.values).filter(([t,e])=>e!==s.base.fields.find(i=>i.key===t)?.value))}function Z(s){let t=j(s.base);return JSON.stringify(s.points.map(e=>[e.seconds,e.target_native]))!==JSON.stringify(t.points.map(e=>[e.seconds,e.target_native]))}function Ne(s){let t=P(s);if(Object.keys(t).filter(r=>s.base.fields.find(n=>n.key===r)?.kind==="enum").length)return{kind:"mode",fields:t};let i={kind:s.base.channel?"channel":"season_dates",fields:t};return Z(s)&&(i.schedule={mode:s.mode,points:s.points}),i}var N=s=>Object.keys(P(s)).length>0||Z(s);function ve(s){let t=P(s),e=Object.keys(t);if(e.filter(r=>s.base.fields.find(n=>n.key===r)?.kind==="enum").length&&(e.length>1||Z(s)))return"Save one mode change separately from other edits.";for(let r of e){let n=s.base.fields.find(l=>l.key===r),o=t[r];if(!n.writable)return`${n.label} is not editable.`;if(["number","setpoint","ramp"].includes(n.kind)&&(!O(o,n.maximum)||o<n.minimum||n.kind==="ramp"&&!Number.isInteger(o)))return`${n.label}: enter ${n.minimum}\u2013${n.maximum}${n.kind==="ramp"?" whole minutes":""}.`;if(n.kind==="date"&&ge(o)===null)return"Use a valid DD/MM date; unset dates cannot be written.";if(n.kind==="enum"&&(typeof o!="string"||!n.options.includes(o)))return"Choose a supported mode."}if(!s.base.channel&&e.length){let r=s.base.fields.filter(n=>n.kind==="date").map(n=>t[n.key]??(n.validity==="unset"?"00/00":n.value));return gt(r)}return Z(s)?w(s):null}function Ie(s){if(!s.length||s.some(i=>i.seconds===null||i.target_native===null))return[];let t=[...s].sort((i,r)=>i.seconds-r.seconds);if(new Set(t.map(i=>i.seconds)).size!==t.length)return[];let e=t.map((i,r)=>({point:i,start:i.seconds,end:t[r+1]?.seconds??86400,carry:r===t.length-1&&t[0].seconds>0}));return t[0].seconds>0&&e.unshift({point:t.at(-1),start:0,end:t[0].seconds,carry:!0}),e}var He="microclimate.schedule.v1",Le=4096;function je(s){let t=s.base.fields.find(e=>e.key===`${s.base.channel}_period_1_setpoint`);if(t?.unit==="\xB0C")return"celsius";if(t?.unit==="%")return"percent";throw new Error("Schedule unit is unavailable.")}function Fe(s){if(!["Day Night","Multi","Seasonal"].includes(s.mode)||w(s))throw new Error("Complete the supported schedule before exporting.");return{format:He,mode:s.mode,unit:je(s),points:s.points.map(t=>({seconds:t.seconds,target_native:t.target_native}))}}function Be(s,t){if(!t||typeof t!="object"||Array.isArray(t))throw new Error("Invalid schedule preset.");let e=t;if(Object.keys(e).sort().join(",")!=="format,mode,points,unit"||e.format!==He)throw new Error("Unsupported schedule preset format.");if(e.mode!==s.mode||e.unit!==je(s))throw new Error("Preset mode and native units must match this channel.");if(!Array.isArray(e.points))throw new Error("Invalid schedule points.");if(!Q(s.mode,e.points.length))throw new Error("Incorrect number of schedule points.");let i=e.points.map(o=>{if(!o||typeof o!="object"||Object.keys(o).sort().join(",")!=="seconds,target_native"||!G(o.seconds)||!O(o.target_native))throw new Error("Invalid schedule point.");return{draft_id:C(),seconds:o.seconds,target_native:o.target_native}}),r={...s,points:i,repair:!1},n=w(r);if(n)throw new Error(n);return r}var te=globalThis,ie=te.ShadowRoot&&(te.ShadyCSS===void 0||te.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,be=Symbol(),ze=new WeakMap,F=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==be)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(ie&&t===void 0){let i=e!==void 0&&e.length===1;i&&(t=ze.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&ze.set(e,t))}return t}toString(){return this.cssText}},qe=s=>new F(typeof s=="string"?s:s+"",void 0,be),B=(s,...t)=>{let e=s.length===1?s[0]:t.reduce((i,r,n)=>i+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+s[n+1],s[0]);return new F(e,s,be)},Ve=(s,t)=>{if(ie)s.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let i=document.createElement("style"),r=te.litNonce;r!==void 0&&i.setAttribute("nonce",r),i.textContent=e.cssText,s.appendChild(i)}},$e=ie?s=>s:s=>s instanceof CSSStyleSheet?(t=>{let e="";for(let i of t.cssRules)e+=i.cssText;return qe(e)})(s):s;var{is:vt,defineProperty:bt,getOwnPropertyDescriptor:$t,getOwnPropertyNames:yt,getOwnPropertySymbols:_t,getPrototypeOf:wt}=Object,se=globalThis,We=se.trustedTypes,xt=We?We.emptyScript:"",Et=se.reactiveElementPolyfillSupport,z=(s,t)=>s,ye={toAttribute(s,t){switch(t){case Boolean:s=s?xt:null;break;case Object:case Array:s=s==null?s:JSON.stringify(s)}return s},fromAttribute(s,t){let e=s;switch(t){case Boolean:e=s!==null;break;case Number:e=s===null?null:Number(s);break;case Object:case Array:try{e=JSON.parse(s)}catch{e=null}}return e}},Xe=(s,t)=>!vt(s,t),Je={attribute:!0,type:String,converter:ye,reflect:!1,useDefault:!1,hasChanged:Xe};Symbol.metadata??=Symbol("metadata"),se.litPropertyMetadata??=new WeakMap;var x=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=Je){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let i=Symbol(),r=this.getPropertyDescriptor(t,i,e);r!==void 0&&bt(this.prototype,t,r)}}static getPropertyDescriptor(t,e,i){let{get:r,set:n}=$t(this.prototype,t)??{get(){return this[e]},set(o){this[e]=o}};return{get:r,set(o){let l=r?.call(this);n?.call(this,o),this.requestUpdate(t,l,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??Je}static _$Ei(){if(this.hasOwnProperty(z("elementProperties")))return;let t=wt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(z("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(z("properties"))){let e=this.properties,i=[...yt(e),..._t(e)];for(let r of i)this.createProperty(r,e[r])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[i,r]of e)this.elementProperties.set(i,r)}this._$Eh=new Map;for(let[e,i]of this.elementProperties){let r=this._$Eu(e,i);r!==void 0&&this._$Eh.set(r,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let i=new Set(t.flat(1/0).reverse());for(let r of i)e.unshift($e(r))}else t!==void 0&&e.push($e(t));return e}static _$Eu(t,e){let i=e.attribute;return i===!1?void 0:typeof i=="string"?i:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Ve(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){let i=this.constructor.elementProperties.get(t),r=this.constructor._$Eu(t,i);if(r!==void 0&&i.reflect===!0){let n=(i.converter?.toAttribute!==void 0?i.converter:ye).toAttribute(e,i.type);this._$Em=t,n==null?this.removeAttribute(r):this.setAttribute(r,n),this._$Em=null}}_$AK(t,e){let i=this.constructor,r=i._$Eh.get(t);if(r!==void 0&&this._$Em!==r){let n=i.getPropertyOptions(r),o=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:ye;this._$Em=r;let l=o.fromAttribute(e,n.type);this[r]=l??this._$Ej?.get(r)??l,this._$Em=null}}requestUpdate(t,e,i,r=!1,n){if(t!==void 0){let o=this.constructor;if(r===!1&&(n=this[t]),i??=o.getPropertyOptions(t),!((i.hasChanged??Xe)(n,e)||i.useDefault&&i.reflect&&n===this._$Ej?.get(t)&&!this.hasAttribute(o._$Eu(t,i))))return;this.C(t,e,i)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:r,wrapped:n},o){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,o??e??this[t]),n!==!0||o!==void 0)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),r===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,n]of this._$Ep)this[r]=n;this._$Ep=void 0}let i=this.constructor.elementProperties;if(i.size>0)for(let[r,n]of i){let{wrapped:o}=n,l=this[r];o!==!0||this._$AL.has(r)||l===void 0||this.C(r,void 0,n,l)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(i=>i.hostUpdate?.()),this.update(e)):this._$EM()}catch(i){throw t=!1,this._$EM(),i}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};x.elementStyles=[],x.shadowRootOptions={mode:"open"},x[z("elementProperties")]=new Map,x[z("finalized")]=new Map,Et?.({ReactiveElement:x}),(se.reactiveElementVersions??=[]).push("2.1.2");var we=globalThis,Ke=s=>s,re=we.trustedTypes,Ye=re?re.createPolicy("lit-html",{createHTML:s=>s}):void 0,xe="$lit$",E=`lit$${Math.random().toFixed(9).slice(2)}$`,Ee="?"+E,St=`<${Ee}>`,D=document,V=()=>D.createComment(""),W=s=>s===null||typeof s!="object"&&typeof s!="function",Se=Array.isArray,it=s=>Se(s)||typeof s?.[Symbol.iterator]=="function",_e=`[ 	
\f\r]`,q=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Ge=/-->/g,Qe=/>/g,T=RegExp(`>|${_e}(?:([^\\s"'>=/]+)(${_e}*=${_e}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),Ze=/'/g,et=/"/g,st=/^(?:script|style|textarea|title)$/i,Ae=s=>(t,...e)=>({_$litType$:s,strings:t,values:e}),c=Ae(1),qt=Ae(2),Vt=Ae(3),v=Symbol.for("lit-noChange"),h=Symbol.for("lit-nothing"),tt=new WeakMap,M=D.createTreeWalker(D,129);function rt(s,t){if(!Se(s)||!s.hasOwnProperty("raw"))throw Error("invalid template strings array");return Ye!==void 0?Ye.createHTML(t):t}var nt=(s,t)=>{let e=s.length-1,i=[],r,n=t===2?"<svg>":t===3?"<math>":"",o=q;for(let l=0;l<e;l++){let a=s[l],u,m,d=-1,p=0;for(;p<a.length&&(o.lastIndex=p,m=o.exec(a),m!==null);)p=o.lastIndex,o===q?m[1]==="!--"?o=Ge:m[1]!==void 0?o=Qe:m[2]!==void 0?(st.test(m[2])&&(r=RegExp("</"+m[2],"g")),o=T):m[3]!==void 0&&(o=T):o===T?m[0]===">"?(o=r??q,d=-1):m[1]===void 0?d=-2:(d=o.lastIndex-m[2].length,u=m[1],o=m[3]===void 0?T:m[3]==='"'?et:Ze):o===et||o===Ze?o=T:o===Ge||o===Qe?o=q:(o=T,r=void 0);let f=o===T&&s[l+1].startsWith("/>")?" ":"";n+=o===q?a+St:d>=0?(i.push(u),a.slice(0,d)+xe+a.slice(d)+E+f):a+E+(d===-2?l:f)}return[rt(s,n+(s[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),i]},J=class s{constructor({strings:t,_$litType$:e},i){let r;this.parts=[];let n=0,o=0,l=t.length-1,a=this.parts,[u,m]=nt(t,e);if(this.el=s.createElement(u,i),M.currentNode=this.el.content,e===2||e===3){let d=this.el.content.firstChild;d.replaceWith(...d.childNodes)}for(;(r=M.nextNode())!==null&&a.length<l;){if(r.nodeType===1){if(r.hasAttributes())for(let d of r.getAttributeNames())if(d.endsWith(xe)){let p=m[o++],f=r.getAttribute(d).split(E),g=/([.?@])?(.*)/.exec(p);a.push({type:1,index:n,name:g[2],strings:f,ctor:g[1]==="."?oe:g[1]==="?"?ae:g[1]==="@"?le:U}),r.removeAttribute(d)}else d.startsWith(E)&&(a.push({type:6,index:n}),r.removeAttribute(d));if(st.test(r.tagName)){let d=r.textContent.split(E),p=d.length-1;if(p>0){r.textContent=re?re.emptyScript:"";for(let f=0;f<p;f++)r.append(d[f],V()),M.nextNode(),a.push({type:2,index:++n});r.append(d[p],V())}}}else if(r.nodeType===8)if(r.data===Ee)a.push({type:2,index:n});else{let d=-1;for(;(d=r.data.indexOf(E,d+1))!==-1;)a.push({type:7,index:n}),d+=E.length-1}n++}}static createElement(t,e){let i=D.createElement("template");return i.innerHTML=t,i}};function R(s,t,e=s,i){if(t===v)return t;let r=i!==void 0?e._$Co?.[i]:e._$Cl,n=W(t)?void 0:t._$litDirective$;return r?.constructor!==n&&(r?._$AO?.(!1),n===void 0?r=void 0:(r=new n(s),r._$AT(s,e,i)),i!==void 0?(e._$Co??=[])[i]=r:e._$Cl=r),r!==void 0&&(t=R(s,r._$AS(s,t.values),r,i)),t}var ne=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:i}=this._$AD,r=(t?.creationScope??D).importNode(e,!0);M.currentNode=r;let n=M.nextNode(),o=0,l=0,a=i[0];for(;a!==void 0;){if(o===a.index){let u;a.type===2?u=new I(n,n.nextSibling,this,t):a.type===1?u=new a.ctor(n,a.name,a.strings,this,t):a.type===6&&(u=new de(n,this,t)),this._$AV.push(u),a=i[++l]}o!==a?.index&&(n=M.nextNode(),o++)}return M.currentNode=D,r}p(t){let e=0;for(let i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},I=class s{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,r){this.type=2,this._$AH=h,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=R(this,t,e),W(t)?t===h||t==null||t===""?(this._$AH!==h&&this._$AR(),this._$AH=h):t!==this._$AH&&t!==v&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):it(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==h&&W(this._$AH)?this._$AA.nextSibling.data=t:this.T(D.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:i}=t,r=typeof i=="number"?this._$AC(t):(i.el===void 0&&(i.el=J.createElement(rt(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===r)this._$AH.p(e);else{let n=new ne(r,this),o=n.u(this.options);n.p(e),this.T(o),this._$AH=n}}_$AC(t){let e=tt.get(t.strings);return e===void 0&&tt.set(t.strings,e=new J(t)),e}k(t){Se(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,i,r=0;for(let n of t)r===e.length?e.push(i=new s(this.O(V()),this.O(V()),this,this.options)):i=e[r],i._$AI(n),r++;r<e.length&&(this._$AR(i&&i._$AB.nextSibling,r),e.length=r)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let i=Ke(t).nextSibling;Ke(t).remove(),t=i}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},U=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,r,n){this.type=1,this._$AH=h,this._$AN=void 0,this.element=t,this.name=e,this._$AM=r,this.options=n,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=h}_$AI(t,e=this,i,r){let n=this.strings,o=!1;if(n===void 0)t=R(this,t,e,0),o=!W(t)||t!==this._$AH&&t!==v,o&&(this._$AH=t);else{let l=t,a,u;for(t=n[0],a=0;a<n.length-1;a++)u=R(this,l[i+a],e,a),u===v&&(u=this._$AH[a]),o||=!W(u)||u!==this._$AH[a],u===h?t=h:t!==h&&(t+=(u??"")+n[a+1]),this._$AH[a]=u}o&&!r&&this.j(t)}j(t){t===h?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},oe=class extends U{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===h?void 0:t}},ae=class extends U{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==h)}},le=class extends U{constructor(t,e,i,r,n){super(t,e,i,r,n),this.type=5}_$AI(t,e=this){if((t=R(this,t,e,0)??h)===v)return;let i=this._$AH,r=t===h&&i!==h||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,n=t!==h&&(i===h||r);r&&this.element.removeEventListener(this.name,this,i),n&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},de=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){R(this,t)}},ot={M:xe,P:E,A:Ee,C:1,L:nt,R:ne,D:it,V:R,I,H:U,N:ae,U:le,B:oe,F:de},At=we.litHtmlPolyfillSupport;At?.(J,I),(we.litHtmlVersions??=[]).push("3.3.3");var at=(s,t,e)=>{let i=e?.renderBefore??t,r=i._$litPart$;if(r===void 0){let n=e?.renderBefore??null;i._$litPart$=r=new I(t.insertBefore(V(),n),n,void 0,e??{})}return r._$AI(s),r};var ke=globalThis,$=class extends x{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=at(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return v}};$._$litElement$=!0,$.finalized=!0,ke.litElementHydrateSupport?.({LitElement:$});var kt=ke.litElementPolyfillSupport;kt?.({LitElement:$});(ke.litElementVersions??=[]).push("4.2.2");var S={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},ce=s=>(...t)=>({_$litDirective$:s,values:t}),H=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};var{I:Ct}=ot,lt=s=>s;var ct=s=>s.strings===void 0,dt=()=>document.createComment(""),L=(s,t,e)=>{let i=s._$AA.parentNode,r=t===void 0?s._$AB:t._$AA;if(e===void 0){let n=i.insertBefore(dt(),r),o=i.insertBefore(dt(),r);e=new Ct(n,o,s,s.options)}else{let n=e._$AB.nextSibling,o=e._$AM,l=o!==s;if(l){let a;e._$AQ?.(s),e._$AM=s,e._$AP!==void 0&&(a=s._$AU)!==o._$AU&&e._$AP(a)}if(n!==r||l){let a=e._$AA;for(;a!==n;){let u=lt(a).nextSibling;lt(i).insertBefore(a,r),a=u}}}return e},A=(s,t,e=s)=>(s._$AI(t,e),s),Pt={},he=(s,t=Pt)=>s._$AH=t,ht=s=>s._$AH,ue=s=>{s._$AR(),s._$AA.remove()};var ut=(s,t,e)=>{let i=new Map;for(let r=t;r<=e;r++)i.set(s[r],r);return i},Ce=ce(class extends H{constructor(s){if(super(s),s.type!==S.CHILD)throw Error("repeat() can only be used in text expressions")}dt(s,t,e){let i;e===void 0?e=t:t!==void 0&&(i=t);let r=[],n=[],o=0;for(let l of s)r[o]=i?i(l,o):o,n[o]=e(l,o),o++;return{values:n,keys:r}}render(s,t,e){return this.dt(s,t,e).values}update(s,[t,e,i]){let r=ht(s),{values:n,keys:o}=this.dt(t,e,i);if(!Array.isArray(r))return this.ut=o,n;let l=this.ut??=[],a=[],u,m,d=0,p=r.length-1,f=0,g=n.length-1;for(;d<=p&&f<=g;)if(r[d]===null)d++;else if(r[p]===null)p--;else if(l[d]===o[f])a[f]=A(r[d],n[f]),d++,f++;else if(l[p]===o[g])a[g]=A(r[p],n[g]),p--,g--;else if(l[d]===o[g])a[g]=A(r[d],n[g]),L(s,a[g+1],r[d]),d++,g--;else if(l[p]===o[f])a[f]=A(r[p],n[f]),L(s,r[d],r[p]),p--,f++;else if(u===void 0&&(u=ut(o,f,g),m=ut(l,d,p)),u.has(l[d]))if(u.has(l[p])){let y=m.get(o[f]),fe=y!==void 0?r[y]:null;if(fe===null){let De=L(s,r[d]);A(De,n[f]),a[f]=De}else a[f]=A(fe,n[f]),L(s,r[d],fe),r[y]=null;f++}else ue(r[p]),p--;else ue(r[d]),d++;for(;f<=g;){let y=L(s,a[g+1]);A(y,n[f]),a[f++]=y}for(;d<=p;){let y=r[d++];y!==null&&ue(y)}return this.ut=o,he(s,a),v}});var X=ce(class extends H{constructor(s){if(super(s),s.type!==S.PROPERTY&&s.type!==S.ATTRIBUTE&&s.type!==S.BOOLEAN_ATTRIBUTE)throw Error("The `live` directive is not allowed on child or event bindings");if(!ct(s))throw Error("`live` bindings can only contain a single expression")}render(s){return s}update(s,[t]){if(t===v||t===h)return t;let e=s.element,i=s.name;if(s.type===S.PROPERTY){if(t===e[i])return v}else if(s.type===S.BOOLEAN_ATTRIBUTE){if(!!t===e.hasAttribute(i))return v}else if(s.type===S.ATTRIBUTE&&e.getAttribute(i)===t+"")return v;return he(s),t}});var k="microclimate_integration/card/",pt=s=>!s||["succeeded","failed","partial","uncertain","stopped"].includes(s.status);var K=class extends ${constructor(){super(...arguments);this.error="";this.notice="";this.selected="";this.saving=!1;this.submissionUnknown=!1;this.navigateAfterSave=!1;this.epoch=0;this.subscribed="";this.unload=e=>{this.draft&&N(this.draft)&&(e.preventDefault(),e.returnValue="")};this.reconnect=()=>{this.release(),this.subscribe()}}static{this.properties={view:{state:!0},draft:{state:!0},job:{state:!0},error:{state:!0},selected:{state:!0},saving:{state:!0},notice:{state:!0},submissionUnknown:{state:!0},pendingConfig:{state:!0},_config:{state:!0},_hass:{state:!0}}}static{this.styles=B`
    :host {
      display: block;
      color: var(--primary-text-color, #20252c);
      font-family: var(--paper-font-body1_-_font-family, system-ui);
      font-size: 14px;
    }
    * {
      box-sizing: border-box;
    }
    ha-card {
      display: block;
      background: var(--ha-card-background, var(--card-background-color, #fff));
      border: 1px solid var(--divider-color, #d9dfe5);
      border-radius: var(--ha-card-border-radius, 16px);
      padding: 20px;
      overflow: hidden;
    }
    header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }
    h2 {
      font-size: 21px;
      font-weight: 600;
      line-height: 1.3;
      margin: 0 0 5px;
      overflow-wrap: anywhere;
    }
    h3 {
      font-size: 14px;
      margin: 20px 0 10px;
    }
    .muted {
      color: var(--secondary-text-color, #68737e);
      font-size: 12px;
      line-height: 1.6;
    }
    button,
    input,
    select {
      font: inherit;
      color: inherit;
    }
    button {
      min-height: 44px;
      border: 1px solid var(--divider-color, #bac7d2);
      border-radius: 9px;
      background: transparent;
      padding: 8px 13px;
      cursor: pointer;
    }
    button.primary {
      background: var(--primary-color, #007fa3);
      border-color: transparent;
      color: var(--text-primary-color, #fff);
    }
    button:disabled {
      opacity: 0.45;
      cursor: default;
    }
    button:focus-visible,
    input:focus-visible,
    select:focus-visible {
      outline: 3px solid var(--primary-color, #007fa3);
      outline-offset: 2px;
    }
    .badges,
    .actions,
    .observations {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .badges {
      margin: 16px 0;
    }
    .badge {
      background: var(--secondary-background-color, #eff3f6);
      padding: 6px 9px;
      border-radius: 6px;
      font-size: 12px;
    }
    .observations {
      margin: 16px 0;
    }
    .observation {
      flex: 1;
      min-width: 90px;
      padding: 10px;
      background: var(--secondary-background-color, #eff3f6);
      border-radius: 8px;
    }
    .observation strong {
      display: block;
      font-size: 18px;
    }
    .row {
      margin: 16px 0 24px;
    }
    .row-title {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
      font-weight: 600;
    }
    .row-title small {
      font-weight: 400;
    }
    .timeline {
      height: 72px;
      position: relative;
      border-radius: 8px;
      background: var(--secondary-background-color, #edf1f5);
      margin: 22px 0 6px;
    }
    .segment {
      position: absolute;
      top: 0;
      bottom: 0;
      border-right: 1px solid #ffffff80;
      background: var(--segment-color);
      color: var(--segment-text);
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      white-space: nowrap;
      font-size: 12px;
    }
    .segment.carry {
      background:
        repeating-linear-gradient(
          135deg,
          #ffffff28 0px,
          #ffffff28 5px,
          transparent 5px,
          transparent 10px
        ),
        var(--segment-color);
    }
    .segment:first-child {
      border-radius: 8px 0 0 8px;
    }
    .segment:last-of-type {
      border-radius: 0 8px 8px 0;
    }
    .handle {
      position: absolute;
      top: -14px;
      bottom: -5px;
      width: 24px;
      min-height: 40px;
      padding: 0;
      transform: translateX(-50%);
      border: 0;
      background: transparent;
      touch-action: pan-y;
      z-index: 2;
    }
    .handle::before {
      content: "";
      display: block;
      width: 3px;
      background: var(--primary-text-color, #20252c);
      height: 80%;
      margin: auto;
    }
    .handle::after {
      content: "◆";
      position: absolute;
      top: 0;
      left: 3px;
      color: var(--primary-color, #007fa3);
      font-size: 22px;
    }
    .handle[aria-pressed="true"]::before {
      background: var(--primary-color, #007fa3);
      width: 5px;
    }
    .axis {
      display: flex;
      justify-content: space-between;
      color: var(--secondary-text-color, #68737e);
      font-size: 11px;
    }
    .point-list {
      display: grid;
      gap: 8px;
      margin: 12px 0;
    }
    .point {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      align-items: center;
      gap: 8px;
    }
    .point.selected {
      border-left: 3px solid var(--primary-color, #007fa3);
      padding-left: 6px;
    }
    .point button {
      text-align: left;
    }
    .point span {
      font-variant-numeric: tabular-nums;
    }
    .form {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .field {
      display: grid;
      gap: 5px;
      min-width: 0;
    }
    input,
    select {
      width: 100%;
      min-width: 0;
      min-height: 42px;
      border: 1px solid var(--divider-color, #bac7d2);
      background: var(--card-background-color, #fff);
      border-radius: 7px;
      padding: 8px;
    }
    input[type="range"] {
      padding: 0;
      accent-color: var(--primary-color, #007fa3);
    }
    .alert {
      margin: 12px 0;
      padding: 10px 12px;
      border-radius: 8px;
      background: var(--secondary-background-color, #eff3f6);
      line-height: 1.5;
      overflow-wrap: anywhere;
    }
    .error {
      border-left: 3px solid var(--error-color, #c84436);
    }
    .actions {
      justify-content: flex-end;
      margin-top: 18px;
    }
    .settings {
      margin-top: 20px;
      border-top: 1px solid var(--divider-color, #d9dfe5);
      padding-top: 14px;
    }
    summary {
      cursor: pointer;
      min-height: 36px;
      font-weight: 600;
    }
    .review {
      font-size: 12px;
      line-height: 1.7;
      max-height: 160px;
      overflow: auto;
    }
    progress {
      width: 100%;
      accent-color: var(--primary-color, #007fa3);
    }
    .status {
      font-size: 12px;
    }
    .empty {
      padding: 22px;
      text-align: center;
    }
    .slider {
      margin: 14px 0;
    }
    .sr {
      position: absolute;
      clip: rect(0, 0, 0, 0);
      width: 1px;
      height: 1px;
      overflow: hidden;
    }
    @media (max-width: 360px) {
      ha-card {
        padding: 12px;
      }
      .form {
        grid-template-columns: 1fr;
      }
      .point {
        grid-template-columns: 1fr 1fr;
      }
      .point button {
        grid-column: 1/-1;
      }
      .row-title {
        flex-wrap: wrap;
      }
      .segment {
        font-size: 10px;
      }
    }
  `}set hass(e){let i=this._hass?.connection!==e.connection;i&&(this._hass?.connection.removeEventListener?.("ready",this.reconnect),this.release()),this._hass=e,i&&e.connection.addEventListener?.("ready",this.reconnect),this.subscribe()}get hass(){return this._hass}setConfig(e){if(Y(e.temperature_colors),!e.device_id||typeof e.device_id!="string")throw new Error("Select a Microclimate device.");if(this._config?.device_id!==e.device_id){if(this.draft&&N(this.draft)){this.pendingConfig=e;return}this.release(),this.view=void 0,this.job=void 0}this._config={...e},this.subscribe()}connectedCallback(){super.connectedCallback(),window.addEventListener("beforeunload",this.unload),this._hass?.connection.addEventListener?.("ready",this.reconnect),this.subscribe()}disconnectedCallback(){super.disconnectedCallback(),window.removeEventListener("beforeunload",this.unload),this._hass?.connection.removeEventListener?.("ready",this.reconnect),this.release()}release(){this.epoch++,this.unsubscribe?.(),this.unsubJob?.(),this.unsubscribe=void 0,this.unsubJob=void 0,this.subscribed=""}async subscribe(){if(!this.isConnected||!this._hass||!this._config||this.subscribed)return;let e=this.epoch;this.subscribed=this._config.device_id;try{let i=await this._hass.connection.subscribeMessage(r=>{if(e===this.epoch){if(r.error){this.error=r.error,this.view=void 0;return}this.view=r,this.error=""}},{type:k+"subscribe",device_id:this._config.device_id});if(e!==this.epoch){i();return}this.unsubscribe=i,this.job?await this.watchJob(this.job.operation_id):this.submissionUnknown&&await this.recoverRequest()}catch{e===this.epoch&&(this.subscribed="",this.error="Unable to load this device. Check the integration version, device and permissions.")}}async watchJob(e){this.unsubJob?.();let i=this.epoch,r=await this.hass.connection.subscribeMessage(n=>{if(i===this.epoch){if(n.error){this.error="Save status unavailable. Refresh and review before another Save.",this.saving=!1;return}if(!(this.job?.operation_id===n.operation_id&&n.sequence<this.job.sequence)&&(this.job=n,pt(n)))if(this.saving=!1,n.status==="succeeded"){if(this.draft=void 0,this.submissionUnknown=!1,this.requestId=void 0,this.notice="Changes confirmed by API readback.",this.navigateAfterSave&&this.pendingConfig){let o=this.pendingConfig;this.pendingConfig=void 0,this.navigateAfterSave=!1,this.setConfig(o)}}else this.notice="Some changes may already be applied. Refresh and review before saving again."}},{type:k+"operation",operation_id:e});i!==this.epoch?r():this.unsubJob=r}static getConfigElement(){return document.createElement("microclimate-card-editor")}static getStubConfig(){return{device_id:""}}getCardSize(){return this.view?.kind==="controller"?5:this.mode==="Seasonal"?15:8}getGridOptions(){return{columns:12,min_columns:6}}get fahrenheit(){return this._hass?.config?.unit_system.temperature==="\xB0F"}get mode(){return this.draft?.mode??String(this.view?.fields.find(e=>e.key===`${this.view?.channel}_timing_type`)?.value??"")}get working(){if(this.draft)return this.draft;if(this.view)return this.observedDraft?.base!==this.view&&(this.observedDraft=j(this.view)),this.observedDraft}get conflict(){return!!this.draft&&!!this.view&&(this.draft.base.revision!==this.view.revision||this.draft.base.runtime_generation!==this.view.runtime_generation)}get canEdit(){return!!this.view&&this.view.schema_version===1&&this.view.online&&!this.view.busy&&this.view.writes_enabled&&!this._config?.read_only&&this.view.fields.some(e=>e.writable)}unit(e){return e?.unit==="\xB0C"&&this.fahrenheit?"\xB0F":e?.unit??""}format(e,i){return e===null?"Unknown":`${Number(b(e,i?.unit??null,this.fahrenheit).toFixed(3))} ${this.unit(i)}`}fieldFor(e,i="setpoint"){return this.view?.fields.find(r=>r.key===`${this.view?.channel}_period_${e}_${i}`)}get allScheduleWritable(){let e=this.mode==="Day Night"?2:8;return Array.from({length:e},(i,r)=>["time","setpoint"].every(n=>this.fieldFor(r+1,n)?.writable)).every(Boolean)}edit(){this.canEdit&&(this.draft=j(this.view),this.job=void 0,this.notice="",this.selected=this.draft.points[0]?.draft_id??"")}navigate(e){if(e==="stay"){this.pendingConfig=void 0;return}if(e==="save"){this.navigateAfterSave=!0,this.save();return}let i=this.pendingConfig;this.pendingConfig=void 0,this.draft=void 0,i&&this.setConfig(i)}cancel(){this.draft=void 0,this.notice="Draft discarded; no changes sent.",this.error=""}updatePoint(e,i,r=!0){if(!this.draft||this.saving||!this.allScheduleWritable)return;let n=this.draft.points.map(o=>o.draft_id===e?{...o,...i}:o);r&&this.mode==="Multi"&&!this.draft.repair&&n.sort((o,l)=>(o.seconds??1/0)-(l.seconds??1/0)),this.draft={...this.draft,points:n}}add(){if(!this.draft||this.draft.points.length>=8||!this.allScheduleWritable)return;let e=new Set(this.draft.points.map(n=>n.seconds)),i=43200;for(;e.has(i)&&i<86399;)i++;if(e.has(i))for(i=1;e.has(i);)i++;let r={draft_id:C(),seconds:i,target_native:20};this.draft={...this.draft,points:[...this.draft.points,r].sort((n,o)=>(n.seconds??1/0)-(o.seconds??1/0))},this.selected=r.draft_id}removePoint(e){!this.draft||this.draft.points.length<=2||!this.allScheduleWritable||(this.draft={...this.draft,points:this.draft.points.filter(i=>i.draft_id!==e)},this.selected=this.draft.points[0]?.draft_id??"")}repair(){this.draft&&(this.draft={...this.draft,repair:!1,points:this.draft.points.filter(e=>!(e.seconds===0&&e.target_native===0)).sort((e,i)=>(e.seconds??1/0)-(i.seconds??1/0))},this.notice="Review the rebuilt list before Save. Unknown values require correction.")}downloadPreset(){if(!(!this.working||!this.view?.channel))try{let e=JSON.stringify(Fe(this.working),null,2),i=URL.createObjectURL(new Blob([e],{type:"application/json"})),r=document.createElement("a");r.href=i,r.download=`microclimate-${this.mode.toLowerCase().replaceAll(" ","-")}-schedule.json`,r.click(),setTimeout(()=>URL.revokeObjectURL(i),0),this.notice="Schedule preset downloaded in native Celsius/% units; no controller identity included."}catch(e){this.error=e.message}}async loadPreset(e){let i=e.target,r=i.files?.[0];if(i.value="",!(!r||!this.draft||this.saving||!this.canEdit||!this.allScheduleWritable))try{if(r.size>Le)throw new Error("Preset file is too large.");let n=JSON.parse(await r.text());this.draft=Be(this.draft,n),this.selected=this.draft.points[0]?.draft_id??"",this.notice="Preset loaded into a local draft. Review changes, then Save or Cancel.",this.error=""}catch(n){this.error=n instanceof SyntaxError?"Invalid preset JSON.":n.message}}setField(e,i){if(!this.draft||this.saving)return;let r=i.target,n=r.value;["number","ramp","setpoint"].includes(e.kind)&&(n=r.value===""?null:ee(Number(r.value),e.unit,this.fahrenheit)),this.draft={...this.draft,values:{...this.draft.values,[e.key]:n}}}async save(){if(!(!this.draft||!N(this.draft)||ve(this.draft)||this.conflict||this.saving||this.submissionUnknown||!this.canEdit)){this.saving=!0,this.error="",this.requestId=C();try{let e=await this.hass.callWS({type:k+"save",schema_version:1,device_id:this._config.device_id,runtime_generation:this.draft.base.runtime_generation,base_revision:this.draft.base.revision,request_id:this.requestId,patch:Ne(this.draft)});this.job={operation_id:e.operation_id,sequence:-1,status:"pending",phase:"Preflight",confirmed:0,total:0,fields:[],reason:null},await this.watchJob(e.operation_id)}catch(e){this.saving=!1;let i=e;this.submissionUnknown=!i.code,this.error=i.message??"Save acknowledgement was lost. Check request status before any further Save.",this.submissionUnknown&&await this.recoverRequest()}}}async recoverRequest(){if(this.requestId)try{let e=await this.hass.callWS({type:k+"request",device_id:this._config.device_id,request_id:this.requestId});e?(this.submissionUnknown=!1,this.saving=!0,await this.watchJob(e.operation_id)):this.error="No retained Save record found. Verify controller settings before discarding this draft; it will not be resubmitted automatically."}catch{this.error="Cannot determine Save status. Reconnect and check again; no update has been retried."}}async stop(){if(this.job)try{await this.hass.callWS({type:k+"stop",operation_id:this.job.operation_id}),this.notice="Stopping after the current request; applied changes remain."}catch{this.error="Could not stop. Check the current operation status."}}rebase(){if(!this.draft||!this.view)return;let e=this.draft,i=j(this.view),r=P(e);if(i.mode!==e.mode||i.base.runtime_generation!==e.base.runtime_generation){this.error="Mode or connection changed. Discard this draft and edit fresh settings.";return}this.draft={...e,base:this.view,values:{...i.values,...r}},this.job=void 0,this.notice="Draft retained against fresh observations. Review every difference before a new Save."}pointerDown(e,i){if(!this.draft||this.saving||!this.allScheduleWritable)return;let r=e.currentTarget;this.selected=i.draft_id,this.drag={id:i.draft_id,x:e.clientX,pointer:e.pointerId,start:i.seconds??0,el:r,moved:!1},r.setPointerCapture(e.pointerId)}pointerMove(e){let i=this.drag;if(!i||i.pointer!==e.pointerId||Math.abs(e.clientX-i.x)<5&&!i.moved)return;i.moved=!0,e.preventDefault();let r=i.el.parentElement.getBoundingClientRect(),n=Math.min(86399,Math.max(0,Math.round((e.clientX-r.left)/r.width*86400/300)*300));this.updatePoint(i.id,{seconds:n})}pointerUp(){this.drag=void 0}key(e,i){!this.draft||this.saving||(e.key==="ArrowLeft"||e.key==="ArrowRight"?(e.preventDefault(),this.updatePoint(i.draft_id,{seconds:Math.max(0,Math.min(86399,(i.seconds??0)+(e.key==="ArrowRight"?1:-1)*(e.shiftKey?300:60)))})):e.key==="Delete"&&this.mode==="Multi"&&(e.preventDefault(),this.removePoint(i.draft_id)))}row(e,i,r){let n=this.mode==="Multi"&&this.working&&w(this.working)?[]:Ie(e),o=this.fieldFor(1),l=e.find(a=>a.draft_id===this.selected)??e[0];return c`<section class="row">
      <div class="row-title">
        <span>${i}</span>${r!==void 0?c`<small>Starts ${r??"Unknown"}</small>`:h}
      </div>
      <div
        class="timeline"
        aria-label=${`${i} configured 24-hour timeline`}
      >
        ${n.map(a=>c`<div
              class="segment ${a.carry?"carry":""}"
              style=${`left:${a.start/864}%;width:${(a.end-a.start)/864}%;${Re(a.point.target_native,o?.unit,this._config?.temperature_colors)}`}
              title=${`${a.carry?"Configured carry-over \xB7 ":""}${_(a.start)}\u2013${_(a.end===86400?0:a.end)} \xB7 ${this.format(a.point.target_native,o)}`}
            >
              <span
                >${a.end-a.start>3600?this.format(a.point.target_native,o):""}</span
              >
            </div>`)}
        ${n.length===0?c`<div class="empty muted">
              Unknown or incomplete boundaries
            </div>`:h}
        ${Ce(e,a=>a.draft_id,a=>a.seconds===null?h:c`<button
                  class="handle"
                  style=${`left:${a.seconds/864}%`}
                  aria-label=${`${i} ${_(a.seconds)} boundary`}
                  aria-pressed=${l?.draft_id===a.draft_id}
                  title=${_(a.seconds)}
                  @click=${()=>this.selected=a.draft_id}
                  @pointerdown=${u=>this.pointerDown(u,a)}
                  @pointermove=${this.pointerMove}
                  @pointerup=${this.pointerUp}
                  @pointercancel=${this.pointerUp}
                  @keydown=${u=>this.key(u,a)}
                ></button>`)}
      </div>
      <div class="axis">
        <span>00</span><span>04</span><span>08</span><span>12</span
        ><span>16</span><span>20</span><span>24</span>
      </div>
      ${this.draft&&l?c`<label class="field slider">
            ${this.mode==="Multi"?`Point ${e.indexOf(l)+1}`:e.indexOf(l)%2===0?"Day":"Night"}
            target · ${_(l.seconds)} ·
            ${this.format(l.target_native,this.fieldFor(1))}<input
              aria-label=${`${i} selected target slider`}
              type="range"
              min=${b(0,this.fieldFor(1)?.unit??null,this.fahrenheit)}
              max=${b(100,this.fieldFor(1)?.unit??null,this.fahrenheit)}
              step="0.5"
              .value=${String(b(l.target_native??0,this.fieldFor(1)?.unit??null,this.fahrenheit))}
              ?disabled=${this.saving||!this.allScheduleWritable}
              @input=${a=>this.updatePoint(l.draft_id,{target_native:ee(Number(a.target.value),this.fieldFor(1)?.unit??null,this.fahrenheit)})}
          /></label>`:h}
      <details class="slot-table">
        <summary>${i} slot table</summary>
        <div class="point-list">
          ${Ce(e,a=>a.draft_id,(a,u)=>{let m=this.mode==="Multi"?`Point ${this.working.points.indexOf(a)+1}`:u%2===0?"Day":"Night";return c`<div
                class="point ${this.selected===a.draft_id?"selected":""}"
              >
                <button @click=${()=>this.selected=a.draft_id}>
                  ${m}</button
                >${this.draft?c`<input
                        aria-label=${`${i} ${m} start`}
                        type="time"
                        step="1"
                        .value=${X(_(a.seconds))}
                        ?disabled=${this.saving||!this.allScheduleWritable}
                        @input=${d=>this.updatePoint(a.draft_id,{seconds:Oe(d.target.value)},!1)}
                        @change=${()=>this.updatePoint(a.draft_id,{})}
                      /><input
                        aria-label=${`${i} ${m} target ${this.unit(o)}`}
                        type="number"
                        min=${b(0,o?.unit??null,this.fahrenheit)}
                        max=${b(100,o?.unit??null,this.fahrenheit)}
                        step="any"
                        .value=${X(a.target_native===null?"":String(b(a.target_native,o?.unit??null,this.fahrenheit)))}
                        ?disabled=${this.saving||!this.allScheduleWritable}
                        @input=${d=>{let p=d.target.value;this.updatePoint(a.draft_id,{target_native:p===""?null:ee(Number(p),o?.unit??null,this.fahrenheit)})}}
                      />`:c`<span>${_(a.seconds)||"Unknown"}</span
                      ><span>${this.format(a.target_native,o)}</span>`}
              </div>`})}
        </div>
      </details>
    </section>`}reviewChanges(){if(!this.draft)return[];let e=this.draft,i=Object.entries(P(e)).map(([r,n])=>{let o=e.base.fields.find(a=>a.key===r),l=a=>typeof a=="number"?this.format(a,o):a??"Unknown";return`${o.label}: ${l(o.value)} \u2192 ${l(n)}`});if(["Multi","Day Night","Seasonal"].includes(e.mode)){let r=e.mode==="Day Night"?2:8;for(let n=1;n<=r;n++){let o=e.points[n-1];for(let l of["time","setpoint"]){let a=e.base.fields.find(d=>d.key===`${e.base.channel}_period_${n}_${l}`);if(!a)continue;let u=o?l==="time"?o.seconds:o.target_native:0;if(u===a.value)continue;let m=d=>l==="time"?_(d)||"Unknown":this.format(d,a);i.push(`${a.label}: ${m(a.value)} \u2192 ${m(u)}${o?"":" (clear tail)"}`)}}}return i}setting(e){let i=this.draft&&Object.hasOwn(this.draft.values,e.key)?this.draft.values[e.key]:e.value,r=!!this.draft&&N(this.draft),n=this.saving||!e.writable||e.kind==="enum"&&r&&!Object.hasOwn(P(this.draft),e.key);return c`<label class="field"
      ><span>${e.label}${this.unit(e)?` (${this.unit(e)})`:""}</span>${this.draft?e.kind==="enum"?c`<select
              aria-label=${e.label}
              .value=${X(String(i??""))}
              ?disabled=${n}
              @change=${o=>this.setField(e,o)}
            >
              <option value="" disabled>Unknown</option>
              ${e.options.map(o=>c`<option value=${o} ?selected=${o===i}>
                    ${o}
                  </option>`)}
            </select>`:c`<input
              aria-label=${e.label}
              type=${e.kind==="date"?"text":"number"}
              placeholder=${e.kind==="date"?"DD/MM":""}
              maxlength=${e.kind==="date"?5:h}
              min=${b(e.minimum,e.unit,this.fahrenheit)}
              max=${b(e.maximum,e.unit,this.fahrenheit)}
              step=${e.step}
              .value=${X(i===null?"":String(typeof i=="number"?b(i,e.unit,this.fahrenheit):i))}
              ?disabled=${n}
              @input=${o=>this.setField(e,o)}
            />`:c`<strong
            >${typeof i=="number"?this.format(i,e):i??"Unknown"}</strong
          >`}${e.writable?h:c`<small class="muted">${e.reason}</small>`}</label
    >`}render(){let e=this.view,i=this.working,r=this.draft?ve(this.draft):null,n=i?.points??[],o=n.find(a=>a.draft_id===this.selected),l=this.localName==="microclimate-controller-card"?"controller":"channel";return e&&e.kind!==l?c`<ha-card
        >Select a ${l} device for this card.</ha-card
      >`:c`<ha-card
      ><header>
        <div>
          <h2>${this._config?.title??e?.name??"Microclimate"}</h2>
          <div class="muted">
            ${e?.model??"Connecting\u2026"}${this.draft?" \xB7 Draft preview":""}${e&&!e.online?" \xB7 Offline":""}
          </div>
        </div>
        ${!this.draft&&this.canEdit?c`<button class="primary" @click=${this.edit}>Edit</button>`:h}
      </header>
      ${this.pendingConfig?c`<section
            role="dialog"
            aria-label="Unsaved schedule changes"
            class="alert"
          >
            <p>Save or discard this draft before changing devices?</p>
            <div class="actions">
              <button @click=${()=>this.navigate("stay")}>Stay</button
              ><button
                ?disabled=${this.saving||this.submissionUnknown}
                @click=${()=>this.navigate("discard")}
              >
                Discard draft</button
              ><button
                ?disabled=${!!r||this.conflict||this.saving||!this.canEdit}
                @click=${()=>this.navigate("save")}
              >
                Save then switch
              </button>
            </div>
          </section>`:h}${this.error?c`<div role="alert" class="alert error">${this.error}</div>`:h}${e?.schema_version!==1&&e?c`<div class="alert error">
            Card/backend version mismatch. Update both before editing.
          </div>`:h}
      ${e&&i?c`${e.kind==="controller"?c`<h3>Season start dates</h3>
                <p class="muted">
                  Shared by every channel on this controller. Dates follow one
                  annual cycle; a December/January wrap is allowed.
                </p>
                <div class="form">
                  ${e.fields.filter(a=>a.kind==="date").map(a=>this.setting(a))}
                </div>`:c` <div class="badges">
                  ${e.fields.filter(a=>a.kind==="enum").map(a=>c`<span class="badge"
                          >${a.value??"Unknown"}</span
                        >`)}
                </div>
                ${this._config?.show_observations!==!1&&e.observations.length?c`<div class="observations">
                      ${e.observations.map(a=>c`<div class="observation">
                            <span class="muted">${a.name}</span
                            ><strong>${a.value} ${a.unit??""}</strong>
                          </div>`)}
                    </div>`:h}
                <h3>Configured schedule · controller local time</h3>
                ${this.mode==="Seasonal"?c`<p class="muted">
                        Dates shared by all channels. Edit dates in the
                        controller card.
                      </p>
                      ${[0,1,2,3].map(a=>this.row(n.slice(a*2,a*2+2),`Season ${a+1}`,e.fields.find(u=>u.key===`season_${a+1}_start_pin`)?.value??null))}`:["Multi","Day Night"].includes(this.mode)?this.row(n,this.mode==="Multi"?"Multi":"Day & Night"):c`<div class="alert">
                        ${this.mode==="Constant"?"Constant target writing is not mapped.":this.mode==="Periodic"?"Periodic interval/duration editing is not supported.":"Timing mode unknown."}
                      </div>`}
                ${this.draft&&this.mode==="Multi"?c`${i.repair?c`<div class="alert error">
                            Existing points need review. Opening this card makes
                            no changes.
                            <button @click=${this.repair}>
                              Review/rebuild point list
                            </button>
                          </div>`:h}
                      <div class="actions">
                        <button
                          ?disabled=${n.length>=8||this.saving||!this.allScheduleWritable}
                          @click=${this.add}
                        >
                          Add point</button
                        ><button
                          ?disabled=${n.length<=2||!o||this.saving||!this.allScheduleWritable}
                          @click=${()=>o&&this.removePoint(o.draft_id)}
                        >
                          Remove selected
                        </button>
                      </div>
                      <p class="muted">
                        2–8 consecutive points. Inserting/removing shifts later
                        points; unused tail slots are cleared.
                      </p>`:h}
                ${!this.draft&&i.repair?c`<div class="alert error">
                      ${w(i)} Edit to review/rebuild; observations are
                      unchanged.
                    </div>`:h}
                ${["Day Night","Multi","Seasonal"].includes(this.mode)?c`<div class="actions">
                      <button
                        ?disabled=${!!w(i)}
                        @click=${this.downloadPreset}
                      >Download preset</button>
                      ${this.draft?c`<button
                              ?disabled=${this.saving||!this.canEdit||!this.allScheduleWritable}
                              @click=${()=>this.renderRoot.querySelector("#preset-file")?.click()}
                            >Import preset</button>
                            <input
                              id="preset-file"
                              type="file"
                              accept=".json,application/json"
                              hidden
                              @change=${this.loadPreset}
                            />`:h}
                    </div>
                    <p class="muted">Presets contain schedule points only, in native Celsius or percent. Import stays local until Save. To copy between cards, download then import on a compatible channel.</p>`:h}
                <details class="settings" ?open=${!!this.draft}>
                  <summary>Channel settings</summary>
                  <p class="muted">
                    Save each mode change separately. Schedule modes share the
                    same stored time/target pairs.
                  </p>
                  <div class="form">
                    ${e.fields.filter(a=>!a.index&&!a.shared).map(a=>this.setting(a))}
                  </div>
                </details>`}`:h}
      ${this.submissionUnknown?c`<div class="alert error">
            Save result is unresolved.
            <button @click=${this.recoverRequest}>Check request status</button>
          </div>`:h}${this.notice?c`<div role="status" class="alert">${this.notice}</div>`:h}
      ${this.draft?c`${r?c`<div role="alert" class="alert error">${r}</div>`:h}${this.conflict&&!this.saving?c`<div class="alert error">
                  Settings changed since editing began.
                  <button @click=${this.rebase}>
                    Refresh and review draft
                  </button>
                </div>`:h}
            <p class="muted">
              Save sends changes sequentially. Intermediate settings may affect
              the controller; confirmed changes cannot be rolled back
              automatically.
            </p>
            <details class="review" open>
              <summary>
                ${this.reviewChanges().length} changed fields · review
              </summary>
              ${this.reviewChanges().map(a=>c`<div>${a}</div>`)}
            </details>
            <div class="actions">
              ${this.saving?c`<button @click=${this.stop}>
                    Stop remaining changes
                  </button>`:c`<button @click=${this.cancel}>Cancel</button
                    ><button
                      class="primary"
                      ?disabled=${!N(this.draft)||!!r||this.conflict||!this.canEdit||this.draft.repair||this.submissionUnknown}
                      @click=${this.save}
                    >
                      Save changes
                    </button>`}
            </div>`:h}
      ${this.job?c`<section aria-live="polite" class="alert">
            <strong
              >${this.job.status} · ${this.job.confirmed}/${this.job.total}
              confirmed</strong
            ><progress
              max=${Math.max(1,this.job.total)}
              value=${this.job.confirmed}
            ></progress
            >${this.job.reason?c`<p>${this.job.reason.replaceAll("_"," ")}</p>`:h}
            <details>
              <summary>Change results</summary>
              ${this.job.fields.map(a=>c`<div class="status">${a.label}: ${a.status}</div>`)}
            </details>
          </section>`:h}
    </ha-card>`}};var pe=class extends ${constructor(){super(...arguments);this.devices=[];this.error="";this.colorError=""}static{this.properties={config:{state:!0},devices:{state:!0},error:{state:!0},colorError:{state:!0}}}static{this.styles=B`
    label {
      display: block;
      margin: 12px 0;
    }
    input,
    select {
      display: block;
      width: 100%;
      box-sizing: border-box;
      min-height: 44px;
      margin: 6px 0;
      font: inherit;
    }
    input[type="checkbox"] {
      width: auto;
      display: inline;
      min-height: 0;
    }
  `}set hass(e){if(this._hass===e)return;let i=!this._hass;this._hass=e,i&&e.callWS({type:k+"list"}).then(r=>this.devices=r).catch(()=>this.error="Unable to list authorized Microclimate devices.")}setConfig(e){this.config={...e}}change(e,i){this.config={...this.config,[e]:i},this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:this.config},bubbles:!0,composed:!0}))}colors(){return this.config?.temperature_colors??me}changeColor(e,i,r){let n=this.colors().map((o,l)=>l===e?{...o,[i]:i==="temperature"?r.trim()?Number(r):NaN:r}:{...o});try{Y(n),this.colorError="",this.change("temperature_colors",n)}catch(o){this.colorError=o.message}}render(){let e=this.config?.type.includes("controller")?"controller":"channel";return c`<p>
        ${this.error||"Select a registered Microclimate device. Entity renames do not change this binding."}
      </p>
      <label
        >Device<select
          aria-label="Device"
          .value=${this.config?.device_id??""}
          @change=${i=>this.change("device_id",i.target.value)}
        >
          <option value="">Select device</option>
          ${this.devices.filter(i=>i.kind===e).map(i=>c`<option
                  value=${i.device_id}
                  ?selected=${i.device_id===this.config?.device_id}
                >
                  ${i.name}
                </option>`)}
        </select></label
      ><label
        >Title<input
          .value=${this.config?.title??""}
          @input=${i=>this.change("title",i.target.value)} /></label
      ><label
        ><input
          type="checkbox"
          .checked=${!!this.config?.read_only}
          @change=${i=>this.change("read_only",i.target.checked)}
        />Always read only</label
      >${e==="channel"?c`<details>
            <summary>Temperature colours</summary>
            <p>
              Inclusive lower bounds in °C, also when HA displays °F. Below the
              lowest bound uses its colour. Percentage targets use teal.
            </p>
            ${this.colorError?c`<p role="alert">${this.colorError}</p>`:h}
            ${this.colors().map((i,r)=>c`<fieldset>
                  <legend>Colour ${r+1}</legend>
                  <label
                    >Lower temperature (°C)<input
                      type="number"
                      min="0"
                      max="100"
                      step="any"
                      aria-label=${`Colour ${r+1} lower temperature \xB0C`}
                      .value=${String(i.temperature)}
                      @change=${n=>this.changeColor(r,"temperature",n.target.value)}
                  /></label>
                  <label
                    >Colour<input
                      type="color"
                      aria-label=${`Colour ${r+1} value`}
                      .value=${i.color}
                      @input=${n=>this.changeColor(r,"color",n.target.value)}
                  /></label>
                  <button
                    ?disabled=${this.colors().length===1}
                    @click=${()=>{this.colorError="",this.change("temperature_colors",this.colors().filter((n,o)=>o!==r))}}
                  >
                    Remove colour ${r+1}
                  </button>
                </fieldset>`)}
            <button
              ?disabled=${this.colors().length>=101}
              @click=${()=>{let i=new Set(this.colors().map(n=>n.temperature)),r=0;for(;i.has(r);)r++;this.change("temperature_colors",[...this.colors(),{temperature:r,color:"#b52222"}])}}
            >
              Add temperature colour
            </button>
            <button
              @click=${()=>{this.colorError="",this.change("temperature_colors",void 0)}}
            >
              Reset temperature colours
            </button>
          </details>`:h}`}};var Pe=class extends K{},Te=class extends K{};customElements.define("microclimate-channel-card",Pe);customElements.define("microclimate-controller-card",Te);customElements.define("microclimate-card-editor",pe);var Me=window;Me.customCards=Me.customCards??[];Me.customCards.push({type:"microclimate-channel-card",name:"Microclimate channel",description:"Daily, Multi and seasonal schedule with explicit Save/Cancel."},{type:"microclimate-controller-card",name:"Microclimate controller",description:"Shared season start dates."});
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
lit-html/lit-html.js:
lit-element/lit-element.js:
lit-html/directive.js:
lit-html/directives/repeat.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directive-helpers.js:
lit-html/directives/live.js:
  (**
   * @license
   * Copyright 2020 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
