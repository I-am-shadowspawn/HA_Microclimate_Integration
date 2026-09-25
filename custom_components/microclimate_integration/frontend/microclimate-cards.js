var ut=[{temperature:0,color:"#f6c85f"},{temperature:20,color:"#f5a623"},{temperature:25,color:"#ef7d16"},{temperature:30,color:"#d94b24"},{temperature:35,color:"#b52222"}];function X(s){if(s!==void 0&&(!Array.isArray(s)||s.length===0||s.some(e=>!e||typeof e.temperature!="number"||!Number.isFinite(e.temperature)||e.temperature<0||e.temperature>100||typeof e.color!="string"||!/^#[0-9a-f]{6}$/i.test(e.color))||new Set(s.map(e=>e.temperature)).size!==s.length))throw new Error("Temperature colours require unique Celsius bounds from 0 to 100 and #RRGGBB colours.")}function ne(s,e=ut){if(s===null||!Number.isFinite(s))return"#737373";let t=[...e].sort((i,r)=>i.temperature-r.temperature);return(t.filter(i=>s>=i.temperature).at(-1)??t[0]).color}function oe(s){let e=[1,3,5].map(i=>{let r=parseInt(s.slice(i,i+2),16)/255;return r<=.04045?r/12.92:((r+.055)/1.055)**2.4});return e[0]*.2126+e[1]*.7152+e[2]*.0722>.179?"#000000":"#ffffff"}function Pt(s,e,t){let i=e==="\xB0C"?ne(s,t):"#327b80";return`--segment-color:${i};--segment-text:${oe(i)}`}function H(){let s=crypto.getRandomValues(new Uint8Array(16));s[6]=s[6]&15|64,s[8]=s[8]&63|128;let e=Array.from(s,t=>t.toString(16).padStart(2,"0")).join("");return`${e.slice(0,8)}-${e.slice(8,12)}-${e.slice(12,16)}-${e.slice(16,20)}-${e.slice(20)}`}var G=globalThis,Y=G.ShadowRoot&&(G.ShadyCSS===void 0||G.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,pt=Symbol(),Tt=new WeakMap,I=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==pt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(Y&&e===void 0){let i=t!==void 0&&t.length===1;i&&(e=Tt.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&Tt.set(t,e))}return e}toString(){return this.cssText}},Mt=s=>new I(typeof s=="string"?s:s+"",void 0,pt),L=(s,...e)=>{let t=s.length===1?s[0]:e.reduce((i,r,n)=>i+(a=>{if(a._$cssResult$===!0)return a.cssText;if(typeof a=="number")return a;throw Error("Value passed to 'css' function must be a 'css' function result: "+a+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+s[n+1],s[0]);return new I(t,s,pt)},Ut=(s,e)=>{if(Y)s.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let i=document.createElement("style"),r=G.litNonce;r!==void 0&&i.setAttribute("nonce",r),i.textContent=t.cssText,s.appendChild(i)}},ft=Y?s=>s:s=>s instanceof CSSStyleSheet?(e=>{let t="";for(let i of e.cssRules)t+=i.cssText;return Mt(t)})(s):s;var{is:ae,defineProperty:le,getOwnPropertyDescriptor:de,getOwnPropertyNames:ce,getOwnPropertySymbols:he,getPrototypeOf:ue}=Object,Q=globalThis,Dt=Q.trustedTypes,pe=Dt?Dt.emptyScript:"",fe=Q.reactiveElementPolyfillSupport,j=(s,e)=>s,mt={toAttribute(s,e){switch(e){case Boolean:s=s?pe:null;break;case Object:case Array:s=s==null?s:JSON.stringify(s)}return s},fromAttribute(s,e){let t=s;switch(e){case Boolean:t=s!==null;break;case Number:t=s===null?null:Number(s);break;case Object:case Array:try{t=JSON.parse(s)}catch{t=null}}return t}},Nt=(s,e)=>!ae(s,e),Rt={attribute:!0,type:String,converter:mt,reflect:!1,useDefault:!1,hasChanged:Nt};Symbol.metadata??=Symbol("metadata"),Q.litPropertyMetadata??=new WeakMap;var y=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=Rt){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let i=Symbol(),r=this.getPropertyDescriptor(e,i,t);r!==void 0&&le(this.prototype,e,r)}}static getPropertyDescriptor(e,t,i){let{get:r,set:n}=de(this.prototype,e)??{get(){return this[t]},set(a){this[t]=a}};return{get:r,set(a){let l=r?.call(this);n?.call(this,a),this.requestUpdate(e,l,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??Rt}static _$Ei(){if(this.hasOwnProperty(j("elementProperties")))return;let e=ue(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(j("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(j("properties"))){let t=this.properties,i=[...ce(t),...he(t)];for(let r of i)this.createProperty(r,t[r])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[i,r]of t)this.elementProperties.set(i,r)}this._$Eh=new Map;for(let[t,i]of this.elementProperties){let r=this._$Eu(t,i);r!==void 0&&this._$Eh.set(r,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let i=new Set(e.flat(1/0).reverse());for(let r of i)t.unshift(ft(r))}else e!==void 0&&t.push(ft(e));return t}static _$Eu(e,t){let i=t.attribute;return i===!1?void 0:typeof i=="string"?i:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Ut(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){let i=this.constructor.elementProperties.get(e),r=this.constructor._$Eu(e,i);if(r!==void 0&&i.reflect===!0){let n=(i.converter?.toAttribute!==void 0?i.converter:mt).toAttribute(t,i.type);this._$Em=e,n==null?this.removeAttribute(r):this.setAttribute(r,n),this._$Em=null}}_$AK(e,t){let i=this.constructor,r=i._$Eh.get(e);if(r!==void 0&&this._$Em!==r){let n=i.getPropertyOptions(r),a=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:mt;this._$Em=r;let l=a.fromAttribute(t,n.type);this[r]=l??this._$Ej?.get(r)??l,this._$Em=null}}requestUpdate(e,t,i,r=!1,n){if(e!==void 0){let a=this.constructor;if(r===!1&&(n=this[e]),i??=a.getPropertyOptions(e),!((i.hasChanged??Nt)(n,t)||i.useDefault&&i.reflect&&n===this._$Ej?.get(e)&&!this.hasAttribute(a._$Eu(e,i))))return;this.C(e,t,i)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:r,wrapped:n},a){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,a??t??this[e]),n!==!0||a!==void 0)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),r===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,n]of this._$Ep)this[r]=n;this._$Ep=void 0}let i=this.constructor.elementProperties;if(i.size>0)for(let[r,n]of i){let{wrapped:a}=n,l=this[r];a!==!0||this._$AL.has(r)||l===void 0||this.C(r,void 0,n,l)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(i=>i.hostUpdate?.()),this.update(t)):this._$EM()}catch(i){throw e=!1,this._$EM(),i}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};y.elementStyles=[],y.shadowRootOptions={mode:"open"},y[j("elementProperties")]=new Map,y[j("finalized")]=new Map,fe?.({ReactiveElement:y}),(Q.reactiveElementVersions??=[]).push("2.1.2");var vt=globalThis,Ot=s=>s,Z=vt.trustedTypes,Ht=Z?Z.createPolicy("lit-html",{createHTML:s=>s}):void 0,bt="$lit$",w=`lit$${Math.random().toFixed(9).slice(2)}$`,$t="?"+w,me=`<${$t}>`,P=document,z=()=>P.createComment(""),B=s=>s===null||typeof s!="object"&&typeof s!="function",_t=Array.isArray,Bt=s=>_t(s)||typeof s?.[Symbol.iterator]=="function",gt=`[ 	
\f\r]`,F=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,It=/-->/g,Lt=/>/g,k=RegExp(`>|${gt}(?:([^\\s"'>=/]+)(${gt}*=${gt}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),jt=/'/g,Ft=/"/g,qt=/^(?:script|style|textarea|title)$/i,yt=s=>(e,...t)=>({_$litType$:s,strings:e,values:t}),c=yt(1),ke=yt(2),Ce=yt(3),v=Symbol.for("lit-noChange"),h=Symbol.for("lit-nothing"),zt=new WeakMap,C=P.createTreeWalker(P,129);function Vt(s,e){if(!_t(s)||!s.hasOwnProperty("raw"))throw Error("invalid template strings array");return Ht!==void 0?Ht.createHTML(e):e}var Wt=(s,e)=>{let t=s.length-1,i=[],r,n=e===2?"<svg>":e===3?"<math>":"",a=F;for(let l=0;l<t;l++){let o=s[l],u,m,d=-1,p=0;for(;p<o.length&&(a.lastIndex=p,m=a.exec(o),m!==null);)p=a.lastIndex,a===F?m[1]==="!--"?a=It:m[1]!==void 0?a=Lt:m[2]!==void 0?(qt.test(m[2])&&(r=RegExp("</"+m[2],"g")),a=k):m[3]!==void 0&&(a=k):a===k?m[0]===">"?(a=r??F,d=-1):m[1]===void 0?d=-2:(d=a.lastIndex-m[2].length,u=m[1],a=m[3]===void 0?k:m[3]==='"'?Ft:jt):a===Ft||a===jt?a=k:a===It||a===Lt?a=F:(a=k,r=void 0);let f=a===k&&s[l+1].startsWith("/>")?" ":"";n+=a===F?o+me:d>=0?(i.push(u),o.slice(0,d)+bt+o.slice(d)+w+f):o+w+(d===-2?l:f)}return[Vt(s,n+(s[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),i]},q=class s{constructor({strings:e,_$litType$:t},i){let r;this.parts=[];let n=0,a=0,l=e.length-1,o=this.parts,[u,m]=Wt(e,t);if(this.el=s.createElement(u,i),C.currentNode=this.el.content,t===2||t===3){let d=this.el.content.firstChild;d.replaceWith(...d.childNodes)}for(;(r=C.nextNode())!==null&&o.length<l;){if(r.nodeType===1){if(r.hasAttributes())for(let d of r.getAttributeNames())if(d.endsWith(bt)){let p=m[a++],f=r.getAttribute(d).split(w),g=/([.?@])?(.*)/.exec(p);o.push({type:1,index:n,name:g[2],strings:f,ctor:g[1]==="."?et:g[1]==="?"?it:g[1]==="@"?st:M}),r.removeAttribute(d)}else d.startsWith(w)&&(o.push({type:6,index:n}),r.removeAttribute(d));if(qt.test(r.tagName)){let d=r.textContent.split(w),p=d.length-1;if(p>0){r.textContent=Z?Z.emptyScript:"";for(let f=0;f<p;f++)r.append(d[f],z()),C.nextNode(),o.push({type:2,index:++n});r.append(d[p],z())}}}else if(r.nodeType===8)if(r.data===$t)o.push({type:2,index:n});else{let d=-1;for(;(d=r.data.indexOf(w,d+1))!==-1;)o.push({type:7,index:n}),d+=w.length-1}n++}}static createElement(e,t){let i=P.createElement("template");return i.innerHTML=e,i}};function T(s,e,t=s,i){if(e===v)return e;let r=i!==void 0?t._$Co?.[i]:t._$Cl,n=B(e)?void 0:e._$litDirective$;return r?.constructor!==n&&(r?._$AO?.(!1),n===void 0?r=void 0:(r=new n(s),r._$AT(s,t,i)),i!==void 0?(t._$Co??=[])[i]=r:t._$Cl=r),r!==void 0&&(e=T(s,r._$AS(s,e.values),r,i)),e}var tt=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:i}=this._$AD,r=(e?.creationScope??P).importNode(t,!0);C.currentNode=r;let n=C.nextNode(),a=0,l=0,o=i[0];for(;o!==void 0;){if(a===o.index){let u;o.type===2?u=new D(n,n.nextSibling,this,e):o.type===1?u=new o.ctor(n,o.name,o.strings,this,e):o.type===6&&(u=new rt(n,this,e)),this._$AV.push(u),o=i[++l]}a!==o?.index&&(n=C.nextNode(),a++)}return C.currentNode=P,r}p(e){let t=0;for(let i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}},D=class s{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,r){this.type=2,this._$AH=h,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=T(this,e,t),B(e)?e===h||e==null||e===""?(this._$AH!==h&&this._$AR(),this._$AH=h):e!==this._$AH&&e!==v&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Bt(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==h&&B(this._$AH)?this._$AA.nextSibling.data=e:this.T(P.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:i}=e,r=typeof i=="number"?this._$AC(e):(i.el===void 0&&(i.el=q.createElement(Vt(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===r)this._$AH.p(t);else{let n=new tt(r,this),a=n.u(this.options);n.p(t),this.T(a),this._$AH=n}}_$AC(e){let t=zt.get(e.strings);return t===void 0&&zt.set(e.strings,t=new q(e)),t}k(e){_t(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,i,r=0;for(let n of e)r===t.length?t.push(i=new s(this.O(z()),this.O(z()),this,this.options)):i=t[r],i._$AI(n),r++;r<t.length&&(this._$AR(i&&i._$AB.nextSibling,r),t.length=r)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let i=Ot(e).nextSibling;Ot(e).remove(),e=i}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},M=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,r,n){this.type=1,this._$AH=h,this._$AN=void 0,this.element=e,this.name=t,this._$AM=r,this.options=n,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=h}_$AI(e,t=this,i,r){let n=this.strings,a=!1;if(n===void 0)e=T(this,e,t,0),a=!B(e)||e!==this._$AH&&e!==v,a&&(this._$AH=e);else{let l=e,o,u;for(e=n[0],o=0;o<n.length-1;o++)u=T(this,l[i+o],t,o),u===v&&(u=this._$AH[o]),a||=!B(u)||u!==this._$AH[o],u===h?e=h:e!==h&&(e+=(u??"")+n[o+1]),this._$AH[o]=u}a&&!r&&this.j(e)}j(e){e===h?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},et=class extends M{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===h?void 0:e}},it=class extends M{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==h)}},st=class extends M{constructor(e,t,i,r,n){super(e,t,i,r,n),this.type=5}_$AI(e,t=this){if((e=T(this,e,t,0)??h)===v)return;let i=this._$AH,r=e===h&&i!==h||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,n=e!==h&&(i===h||r);r&&this.element.removeEventListener(this.name,this,i),n&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},rt=class{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){T(this,e)}},Jt={M:bt,P:w,A:$t,C:1,L:Wt,R:tt,D:Bt,V:T,I:D,H:M,N:it,U:st,B:et,F:rt},ge=vt.litHtmlPolyfillSupport;ge?.(q,D),(vt.litHtmlVersions??=[]).push("3.3.3");var Kt=(s,e,t)=>{let i=t?.renderBefore??e,r=i._$litPart$;if(r===void 0){let n=t?.renderBefore??null;i._$litPart$=r=new D(e.insertBefore(z(),n),n,void 0,t??{})}return r._$AI(s),r};var wt=globalThis,$=class extends y{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Kt(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return v}};$._$litElement$=!0,$.finalized=!0,wt.litElementHydrateSupport?.({LitElement:$});var ve=wt.litElementPolyfillSupport;ve?.({LitElement:$});(wt.litElementVersions??=[]).push("4.2.2");var x={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},nt=s=>(...e)=>({_$litDirective$:s,values:e}),R=class{constructor(e){}get _$AU(){return this._$AM._$AU}_$AT(e,t,i){this._$Ct=e,this._$AM=t,this._$Ci=i}_$AS(e,t){return this.update(e,t)}update(e,t){return this.render(...t)}};var{I:be}=Jt,Xt=s=>s;var Yt=s=>s.strings===void 0,Gt=()=>document.createComment(""),N=(s,e,t)=>{let i=s._$AA.parentNode,r=e===void 0?s._$AB:e._$AA;if(t===void 0){let n=i.insertBefore(Gt(),r),a=i.insertBefore(Gt(),r);t=new be(n,a,s,s.options)}else{let n=t._$AB.nextSibling,a=t._$AM,l=a!==s;if(l){let o;t._$AQ?.(s),t._$AM=s,t._$AP!==void 0&&(o=s._$AU)!==a._$AU&&t._$AP(o)}if(n!==r||l){let o=t._$AA;for(;o!==n;){let u=Xt(o).nextSibling;Xt(i).insertBefore(o,r),o=u}}}return t},S=(s,e,t=s)=>(s._$AI(e,t),s),$e={},ot=(s,e=$e)=>s._$AH=e,Qt=s=>s._$AH,at=s=>{s._$AR(),s._$AA.remove()};var Zt=(s,e,t)=>{let i=new Map;for(let r=e;r<=t;r++)i.set(s[r],r);return i},xt=nt(class extends R{constructor(s){if(super(s),s.type!==x.CHILD)throw Error("repeat() can only be used in text expressions")}dt(s,e,t){let i;t===void 0?t=e:e!==void 0&&(i=e);let r=[],n=[],a=0;for(let l of s)r[a]=i?i(l,a):a,n[a]=t(l,a),a++;return{values:n,keys:r}}render(s,e,t){return this.dt(s,e,t).values}update(s,[e,t,i]){let r=Qt(s),{values:n,keys:a}=this.dt(e,t,i);if(!Array.isArray(r))return this.ut=a,n;let l=this.ut??=[],o=[],u,m,d=0,p=r.length-1,f=0,g=n.length-1;for(;d<=p&&f<=g;)if(r[d]===null)d++;else if(r[p]===null)p--;else if(l[d]===a[f])o[f]=S(r[d],n[f]),d++,f++;else if(l[p]===a[g])o[g]=S(r[p],n[g]),p--,g--;else if(l[d]===a[g])o[g]=S(r[d],n[g]),N(s,o[g+1],r[d]),d++,g--;else if(l[p]===a[f])o[f]=S(r[p],n[f]),N(s,r[d],r[p]),p--,f++;else if(u===void 0&&(u=Zt(a,f,g),m=Zt(l,d,p)),u.has(l[d]))if(u.has(l[p])){let _=m.get(a[f]),ht=_!==void 0?r[_]:null;if(ht===null){let Ct=N(s,r[d]);S(Ct,n[f]),o[f]=Ct}else o[f]=S(ht,n[f]),N(s,r[d],ht),r[_]=null;f++}else at(r[p]),p--;else at(r[d]),d++;for(;f<=g;){let _=N(s,o[g+1]);S(_,n[f]),o[f++]=_}for(;d<=p;){let _=r[d++];_!==null&&at(_)}return this.ut=a,ot(s,o),v}});var V=nt(class extends R{constructor(s){if(super(s),s.type!==x.PROPERTY&&s.type!==x.ATTRIBUTE&&s.type!==x.BOOLEAN_ATTRIBUTE)throw Error("The `live` directive is not allowed on child or event bindings");if(!Yt(s))throw Error("`live` bindings can only contain a single expression")}render(s){return s}update(s,[e]){if(e===v||e===h)return e;let t=s.element,i=s.name;if(s.type===x.PROPERTY){if(e===t[i])return v}else if(s.type===x.BOOLEAN_ATTRIBUTE){if(!!e===t.hasAttribute(i))return v}else if(s.type===x.ATTRIBUTE&&t.getAttribute(i)===e+"")return v;return ot(s),e}});var E="microclimate_integration/card/",te=s=>!s||["succeeded","failed","partial","uncertain","stopped"].includes(s.status);var ee=s=>s.seconds===0&&s.target_native===0,A=s=>s===null?"":`${Math.floor(s/3600).toString().padStart(2,"0")}:${Math.floor(s/60%60).toString().padStart(2,"0")}:${(s%60).toString().padStart(2,"0")}`;function ie(s){if(!/^\d{2}:\d{2}(:\d{2})?$/.test(s))return null;let[e,t,i=0]=s.split(":").map(Number);return e<24&&t<60&&i<60?e*3600+t*60+i:null}var b=(s,e,t)=>e==="\xB0C"&&t?s*9/5+32:s,dt=(s,e,t)=>e==="\xB0C"&&t?(s-32)*5/9:s;function W(s){let e=String(s.fields.find(n=>n.key===`${s.channel}_timing_type`)?.value??""),t=[],i=e==="Day Night"?2:["Multi","Seasonal"].includes(e)?8:0;for(let n=1;n<=i;n++)t.push({draft_id:H(),source_slot:n,seconds:s.fields.find(a=>a.key===`${s.channel}_period_${n}_time`)?.value??null,target_native:s.fields.find(a=>a.key===`${s.channel}_period_${n}_setpoint`)?.value??null});if(e==="Multi")for(;t.length&&ee(t.at(-1));)t.pop();let r={base:s,values:Object.fromEntries(s.fields.filter(n=>!n.index&&(!n.shared||!s.channel)).map(n=>[n.key,n.value])),points:t,mode:e,repair:!1};return r.repair=e==="Multi"&&J(r)!==null,r}function J(s){if(!["Multi","Day Night","Seasonal"].includes(s.mode))return null;if(s.mode==="Multi"&&(s.points.length<2||s.points.length>8))return"Multi needs 2\u20138 points.";if(s.points.some(e=>e.seconds===null||!Number.isInteger(e.seconds)||e.seconds<0||e.seconds>=86400||e.target_native===null||!Number.isFinite(e.target_native)||e.target_native<0||e.target_native>100))return"Complete every time and target (0\u2013100).";if(s.mode==="Multi"){if(s.points.some(ee))return"Midnight with target zero is reserved for unused slots.";if(s.points.some((e,t)=>t>0&&e.seconds<=s.points[t-1].seconds))return"Multi starts must be distinct and chronological."}else if(s.points.some((e,t)=>t%2===0&&e.seconds===s.points[t+1]?.seconds))return"Day and Night must have distinct starts.";return null}function _e(s){let e=[];for(let t of s){if(t==="00/00")continue;if(typeof t!="string"||!/^\d{2}\/\d{2}$/.test(t))return"Use DD/MM for every season date.";let[i,r]=t.split("/").map(Number),n=new Date(Date.UTC(2001,r-1,i));if(n.getUTCMonth()!==r-1||n.getUTCDate()!==i)return"Use valid calendar dates; 29/02 is not supported.";e.push(Math.floor((n.getTime()-Date.UTC(2001,0,1))/864e5))}return new Set(e).size!==e.length?"Season starts must be distinct.":e.length>1&&e.reduce((t,i,r)=>t+(e[(r+1)%e.length]-i+365)%365,0)!==365?"Seasons must follow one annual cycle (one year wrap is allowed).":null}function U(s){return Object.fromEntries(Object.entries(s.values).filter(([e,t])=>t!==s.base.fields.find(i=>i.key===e)?.value))}function lt(s){let e=W(s.base);return JSON.stringify(s.points.map(t=>[t.seconds,t.target_native]))!==JSON.stringify(e.points.map(t=>[t.seconds,t.target_native]))}function se(s){let e=U(s);if(Object.keys(e).filter(r=>s.base.fields.find(n=>n.key===r)?.kind==="enum").length)return{kind:"mode",fields:e};let i={kind:s.base.channel?"channel":"season_dates",fields:e};return lt(s)&&(i.schedule={mode:s.mode,points:s.points}),i}var O=s=>Object.keys(U(s)).length>0||lt(s);function At(s){let e=U(s),t=Object.keys(e);if(t.filter(r=>s.base.fields.find(n=>n.key===r)?.kind==="enum").length&&(t.length>1||lt(s)))return"Save one mode change separately from other edits.";for(let r of t){let n=s.base.fields.find(l=>l.key===r),a=e[r];if(!n.writable)return`${n.label} is not editable.`;if(["number","setpoint","ramp"].includes(n.kind)&&(typeof a!="number"||!Number.isFinite(a)||a<n.minimum||a>n.maximum||n.kind==="ramp"&&!Number.isInteger(a)))return`${n.label}: enter ${n.minimum}\u2013${n.maximum}${n.kind==="ramp"?" whole minutes":""}.`;if(n.kind==="enum"&&!n.options.includes(String(a)))return"Choose a supported mode."}if(!s.base.channel&&t.length){let r=s.base.fields.filter(n=>n.kind==="date").map(n=>e[n.key]??(n.validity==="unset"?"00/00":n.value));return _e(r)}return lt(s)?J(s):null}function re(s){if(!s.length||s.some(i=>i.seconds===null||i.target_native===null))return[];let e=[...s].sort((i,r)=>i.seconds-r.seconds);if(new Set(e.map(i=>i.seconds)).size!==e.length)return[];let t=e.map((i,r)=>({point:i,start:i.seconds,end:e[r+1]?.seconds??86400,carry:r===e.length-1&&e[0].seconds>0}));return e[0].seconds>0&&t.unshift({point:e.at(-1),start:0,end:e[0].seconds,carry:!0}),t}var K=class extends ${constructor(){super(...arguments);this.error="";this.notice="";this.selected="";this.saving=!1;this.submissionUnknown=!1;this.navigateAfterSave=!1;this.epoch=0;this.subscribed="";this.unload=t=>{this.draft&&O(this.draft)&&(t.preventDefault(),t.returnValue="")};this.reconnect=()=>{this.release(),this.subscribe()}}static{this.properties={view:{state:!0},draft:{state:!0},job:{state:!0},error:{state:!0},selected:{state:!0},saving:{state:!0},notice:{state:!0},submissionUnknown:{state:!0},pendingConfig:{state:!0},_config:{state:!0},_hass:{state:!0}}}static{this.styles=L`
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
  `}set hass(t){let i=this._hass?.connection!==t.connection;i&&(this._hass?.connection.removeEventListener?.("ready",this.reconnect),this.release()),this._hass=t,i&&t.connection.addEventListener?.("ready",this.reconnect),this.subscribe()}get hass(){return this._hass}setConfig(t){if(X(t.temperature_colors),!t.device_id||typeof t.device_id!="string")throw new Error("Select a Microclimate device.");if(this._config?.device_id!==t.device_id){if(this.draft&&O(this.draft)){this.pendingConfig=t;return}this.release(),this.view=void 0,this.job=void 0}this._config={...t},this.subscribe()}connectedCallback(){super.connectedCallback(),window.addEventListener("beforeunload",this.unload),this._hass?.connection.addEventListener?.("ready",this.reconnect),this.subscribe()}disconnectedCallback(){super.disconnectedCallback(),window.removeEventListener("beforeunload",this.unload),this._hass?.connection.removeEventListener?.("ready",this.reconnect),this.release()}release(){this.epoch++,this.unsubscribe?.(),this.unsubJob?.(),this.unsubscribe=void 0,this.unsubJob=void 0,this.subscribed=""}async subscribe(){if(!this.isConnected||!this._hass||!this._config||this.subscribed)return;let t=this.epoch;this.subscribed=this._config.device_id;try{let i=await this._hass.connection.subscribeMessage(r=>{if(t===this.epoch){if(r.error){this.error=r.error,this.view=void 0;return}this.view=r,this.error=""}},{type:E+"subscribe",device_id:this._config.device_id});if(t!==this.epoch){i();return}this.unsubscribe=i,this.job?await this.watchJob(this.job.operation_id):this.submissionUnknown&&await this.recoverRequest()}catch{t===this.epoch&&(this.subscribed="",this.error="Unable to load this device. Check the integration version, device and permissions.")}}async watchJob(t){this.unsubJob?.();let i=this.epoch,r=await this.hass.connection.subscribeMessage(n=>{if(i===this.epoch){if(n.error){this.error="Save status unavailable. Refresh and review before another Save.",this.saving=!1;return}if(!(this.job?.operation_id===n.operation_id&&n.sequence<this.job.sequence)&&(this.job=n,te(n)))if(this.saving=!1,n.status==="succeeded"){if(this.draft=void 0,this.submissionUnknown=!1,this.requestId=void 0,this.notice="Changes confirmed by API readback.",this.navigateAfterSave&&this.pendingConfig){let a=this.pendingConfig;this.pendingConfig=void 0,this.navigateAfterSave=!1,this.setConfig(a)}}else this.notice="Some changes may already be applied. Refresh and review before saving again."}},{type:E+"operation",operation_id:t});i!==this.epoch?r():this.unsubJob=r}static getConfigElement(){return document.createElement("microclimate-card-editor")}static getStubConfig(){return{device_id:""}}getCardSize(){return this.view?.kind==="controller"?5:this.mode==="Seasonal"?15:8}getGridOptions(){return{columns:12,min_columns:6}}get fahrenheit(){return this._hass?.config?.unit_system.temperature==="\xB0F"}get mode(){return this.draft?.mode??String(this.view?.fields.find(t=>t.key===`${this.view?.channel}_timing_type`)?.value??"")}get working(){if(this.draft)return this.draft;if(this.view)return this.observedDraft?.base!==this.view&&(this.observedDraft=W(this.view)),this.observedDraft}get conflict(){return!!this.draft&&!!this.view&&(this.draft.base.revision!==this.view.revision||this.draft.base.runtime_generation!==this.view.runtime_generation)}get canEdit(){return!!this.view&&this.view.schema_version===1&&this.view.online&&!this.view.busy&&this.view.writes_enabled&&!this._config?.read_only&&this.view.fields.some(t=>t.writable)}unit(t){return t?.unit==="\xB0C"&&this.fahrenheit?"\xB0F":t?.unit??""}format(t,i){return t===null?"Unknown":`${Number(b(t,i?.unit??null,this.fahrenheit).toFixed(3))} ${this.unit(i)}`}fieldFor(t,i="setpoint"){return this.view?.fields.find(r=>r.key===`${this.view?.channel}_period_${t}_${i}`)}get allScheduleWritable(){let t=this.mode==="Day Night"?2:8;return Array.from({length:t},(i,r)=>["time","setpoint"].every(n=>this.fieldFor(r+1,n)?.writable)).every(Boolean)}edit(){this.canEdit&&(this.draft=W(this.view),this.job=void 0,this.notice="",this.selected=this.draft.points[0]?.draft_id??"")}navigate(t){if(t==="stay"){this.pendingConfig=void 0;return}if(t==="save"){this.navigateAfterSave=!0,this.save();return}let i=this.pendingConfig;this.pendingConfig=void 0,this.draft=void 0,i&&this.setConfig(i)}cancel(){this.draft=void 0,this.notice="Draft discarded; no changes sent.",this.error=""}updatePoint(t,i,r=!0){if(!this.draft||this.saving||!this.allScheduleWritable)return;let n=this.draft.points.map(a=>a.draft_id===t?{...a,...i}:a);r&&this.mode==="Multi"&&!this.draft.repair&&n.sort((a,l)=>(a.seconds??1/0)-(l.seconds??1/0)),this.draft={...this.draft,points:n}}add(){if(!this.draft||this.draft.points.length>=8||!this.allScheduleWritable)return;let t=new Set(this.draft.points.map(n=>n.seconds)),i=43200;for(;t.has(i)&&i<86399;)i++;if(t.has(i))for(i=1;t.has(i);)i++;let r={draft_id:H(),seconds:i,target_native:20};this.draft={...this.draft,points:[...this.draft.points,r].sort((n,a)=>(n.seconds??1/0)-(a.seconds??1/0))},this.selected=r.draft_id}removePoint(t){!this.draft||this.draft.points.length<=2||!this.allScheduleWritable||(this.draft={...this.draft,points:this.draft.points.filter(i=>i.draft_id!==t)},this.selected=this.draft.points[0]?.draft_id??"")}repair(){this.draft&&(this.draft={...this.draft,repair:!1,points:this.draft.points.filter(t=>!(t.seconds===0&&t.target_native===0)).sort((t,i)=>(t.seconds??1/0)-(i.seconds??1/0))},this.notice="Review the rebuilt list before Save. Unknown values require correction.")}setField(t,i){if(!this.draft||this.saving)return;let r=i.target,n=r.value;["number","ramp","setpoint"].includes(t.kind)&&(n=r.value===""?null:dt(Number(r.value),t.unit,this.fahrenheit)),this.draft={...this.draft,values:{...this.draft.values,[t.key]:n}}}async save(){if(!(!this.draft||!O(this.draft)||At(this.draft)||this.conflict||this.saving||this.submissionUnknown||!this.canEdit)){this.saving=!0,this.error="",this.requestId=H();try{let t=await this.hass.callWS({type:E+"save",schema_version:1,device_id:this._config.device_id,runtime_generation:this.draft.base.runtime_generation,base_revision:this.draft.base.revision,request_id:this.requestId,patch:se(this.draft)});this.job={operation_id:t.operation_id,sequence:-1,status:"pending",phase:"Preflight",confirmed:0,total:0,fields:[],reason:null},await this.watchJob(t.operation_id)}catch(t){this.saving=!1;let i=t;this.submissionUnknown=!i.code,this.error=i.message??"Save acknowledgement was lost. Check request status before any further Save.",this.submissionUnknown&&await this.recoverRequest()}}}async recoverRequest(){if(this.requestId)try{let t=await this.hass.callWS({type:E+"request",device_id:this._config.device_id,request_id:this.requestId});t?(this.submissionUnknown=!1,this.saving=!0,await this.watchJob(t.operation_id)):this.error="No retained Save record found. Verify controller settings before discarding this draft; it will not be resubmitted automatically."}catch{this.error="Cannot determine Save status. Reconnect and check again; no update has been retried."}}async stop(){if(this.job)try{await this.hass.callWS({type:E+"stop",operation_id:this.job.operation_id}),this.notice="Stopping after the current request; applied changes remain."}catch{this.error="Could not stop. Check the current operation status."}}rebase(){if(!this.draft||!this.view)return;let t=this.draft,i=W(this.view),r=U(t);if(i.mode!==t.mode||i.base.runtime_generation!==t.base.runtime_generation){this.error="Mode or connection changed. Discard this draft and edit fresh settings.";return}this.draft={...t,base:this.view,values:{...i.values,...r}},this.job=void 0,this.notice="Draft retained against fresh observations. Review every difference before a new Save."}pointerDown(t,i){if(!this.draft||this.saving||!this.allScheduleWritable)return;let r=t.currentTarget;this.selected=i.draft_id,this.drag={id:i.draft_id,x:t.clientX,pointer:t.pointerId,start:i.seconds??0,el:r,moved:!1},r.setPointerCapture(t.pointerId)}pointerMove(t){let i=this.drag;if(!i||i.pointer!==t.pointerId||Math.abs(t.clientX-i.x)<5&&!i.moved)return;i.moved=!0,t.preventDefault();let r=i.el.parentElement.getBoundingClientRect(),n=Math.min(86399,Math.max(0,Math.round((t.clientX-r.left)/r.width*86400/300)*300));this.updatePoint(i.id,{seconds:n})}pointerUp(){this.drag=void 0}key(t,i){!this.draft||this.saving||(t.key==="ArrowLeft"||t.key==="ArrowRight"?(t.preventDefault(),this.updatePoint(i.draft_id,{seconds:Math.max(0,Math.min(86399,(i.seconds??0)+(t.key==="ArrowRight"?1:-1)*(t.shiftKey?300:60)))})):t.key==="Delete"&&this.mode==="Multi"&&(t.preventDefault(),this.removePoint(i.draft_id)))}row(t,i,r){let n=this.mode==="Multi"&&this.working&&J(this.working)?[]:re(t),a=this.fieldFor(1),l=t.find(o=>o.draft_id===this.selected)??t[0];return c`<section class="row">
      <div class="row-title">
        <span>${i}</span>${r!==void 0?c`<small>Starts ${r??"Unknown"}</small>`:h}
      </div>
      <div
        class="timeline"
        aria-label=${`${i} configured 24-hour timeline`}
      >
        ${n.map(o=>c`<div
              class="segment ${o.carry?"carry":""}"
              style=${`left:${o.start/864}%;width:${(o.end-o.start)/864}%;${Pt(o.point.target_native,a?.unit,this._config?.temperature_colors)}`}
              title=${`${o.carry?"Configured carry-over \xB7 ":""}${A(o.start)}\u2013${A(o.end===86400?0:o.end)} \xB7 ${this.format(o.point.target_native,a)}`}
            >
              <span
                >${o.end-o.start>3600?this.format(o.point.target_native,a):""}</span
              >
            </div>`)}
        ${n.length===0?c`<div class="empty muted">
              Unknown or incomplete boundaries
            </div>`:h}
        ${xt(t,o=>o.draft_id,o=>o.seconds===null?h:c`<button
                  class="handle"
                  style=${`left:${o.seconds/864}%`}
                  aria-label=${`${i} ${A(o.seconds)} boundary`}
                  aria-pressed=${l?.draft_id===o.draft_id}
                  title=${A(o.seconds)}
                  @click=${()=>this.selected=o.draft_id}
                  @pointerdown=${u=>this.pointerDown(u,o)}
                  @pointermove=${this.pointerMove}
                  @pointerup=${this.pointerUp}
                  @pointercancel=${this.pointerUp}
                  @keydown=${u=>this.key(u,o)}
                ></button>`)}
      </div>
      <div class="axis">
        <span>00</span><span>04</span><span>08</span><span>12</span
        ><span>16</span><span>20</span><span>24</span>
      </div>
      ${this.draft&&l?c`<label class="field slider">
            ${this.mode==="Multi"?`Point ${t.indexOf(l)+1}`:t.indexOf(l)%2===0?"Day":"Night"}
            target · ${A(l.seconds)} ·
            ${this.format(l.target_native,this.fieldFor(1))}<input
              aria-label=${`${i} selected target slider`}
              type="range"
              min=${b(0,this.fieldFor(1)?.unit??null,this.fahrenheit)}
              max=${b(100,this.fieldFor(1)?.unit??null,this.fahrenheit)}
              step="0.5"
              .value=${String(b(l.target_native??0,this.fieldFor(1)?.unit??null,this.fahrenheit))}
              ?disabled=${this.saving||!this.allScheduleWritable}
              @input=${o=>this.updatePoint(l.draft_id,{target_native:dt(Number(o.target.value),this.fieldFor(1)?.unit??null,this.fahrenheit)})}
          /></label>`:h}
      <details class="slot-table">
        <summary>${i} slot table</summary>
        <div class="point-list">
          ${xt(t,o=>o.draft_id,(o,u)=>{let m=this.mode==="Multi"?`Point ${this.working.points.indexOf(o)+1}`:u%2===0?"Day":"Night";return c`<div
                class="point ${this.selected===o.draft_id?"selected":""}"
              >
                <button @click=${()=>this.selected=o.draft_id}>
                  ${m}</button
                >${this.draft?c`<input
                        aria-label=${`${i} ${m} start`}
                        type="time"
                        step="1"
                        .value=${V(A(o.seconds))}
                        ?disabled=${this.saving||!this.allScheduleWritable}
                        @input=${d=>this.updatePoint(o.draft_id,{seconds:ie(d.target.value)},!1)}
                        @change=${()=>this.updatePoint(o.draft_id,{})}
                      /><input
                        aria-label=${`${i} ${m} target ${this.unit(a)}`}
                        type="number"
                        min=${b(0,a?.unit??null,this.fahrenheit)}
                        max=${b(100,a?.unit??null,this.fahrenheit)}
                        step="any"
                        .value=${V(o.target_native===null?"":String(b(o.target_native,a?.unit??null,this.fahrenheit)))}
                        ?disabled=${this.saving||!this.allScheduleWritable}
                        @input=${d=>{let p=d.target.value;this.updatePoint(o.draft_id,{target_native:p===""?null:dt(Number(p),a?.unit??null,this.fahrenheit)})}}
                      />`:c`<span>${A(o.seconds)||"Unknown"}</span
                      ><span>${this.format(o.target_native,a)}</span>`}
              </div>`})}
        </div>
      </details>
    </section>`}reviewChanges(){if(!this.draft)return[];let t=this.draft,i=Object.entries(U(t)).map(([r,n])=>{let a=t.base.fields.find(o=>o.key===r),l=o=>typeof o=="number"?this.format(o,a):o??"Unknown";return`${a.label}: ${l(a.value)} \u2192 ${l(n)}`});if(["Multi","Day Night","Seasonal"].includes(t.mode)){let r=t.mode==="Day Night"?2:8;for(let n=1;n<=r;n++){let a=t.points[n-1];for(let l of["time","setpoint"]){let o=t.base.fields.find(d=>d.key===`${t.base.channel}_period_${n}_${l}`);if(!o)continue;let u=a?l==="time"?a.seconds:a.target_native:0;if(u===o.value)continue;let m=d=>l==="time"?A(d)||"Unknown":this.format(d,o);i.push(`${o.label}: ${m(o.value)} \u2192 ${m(u)}${a?"":" (clear tail)"}`)}}}return i}setting(t){let i=this.draft&&Object.hasOwn(this.draft.values,t.key)?this.draft.values[t.key]:t.value,r=!!this.draft&&O(this.draft),n=this.saving||!t.writable||t.kind==="enum"&&r&&!Object.hasOwn(U(this.draft),t.key);return c`<label class="field"
      ><span>${t.label}${this.unit(t)?` (${this.unit(t)})`:""}</span>${this.draft?t.kind==="enum"?c`<select
              aria-label=${t.label}
              .value=${V(String(i??""))}
              ?disabled=${n}
              @change=${a=>this.setField(t,a)}
            >
              <option value="" disabled>Unknown</option>
              ${t.options.map(a=>c`<option value=${a} ?selected=${a===i}>
                    ${a}
                  </option>`)}
            </select>`:c`<input
              aria-label=${t.label}
              type=${t.kind==="date"?"text":"number"}
              placeholder=${t.kind==="date"?"DD/MM":""}
              maxlength=${t.kind==="date"?5:h}
              min=${b(t.minimum,t.unit,this.fahrenheit)}
              max=${b(t.maximum,t.unit,this.fahrenheit)}
              step=${t.step}
              .value=${V(i===null?"":String(typeof i=="number"?b(i,t.unit,this.fahrenheit):i))}
              ?disabled=${n}
              @input=${a=>this.setField(t,a)}
            />`:c`<strong
            >${typeof i=="number"?this.format(i,t):i??"Unknown"}</strong
          >`}${t.writable?h:c`<small class="muted">${t.reason}</small>`}</label
    >`}render(){let t=this.view,i=this.working,r=this.draft?At(this.draft):null,n=i?.points??[],a=n.find(o=>o.draft_id===this.selected),l=this.localName==="microclimate-controller-card"?"controller":"channel";return t&&t.kind!==l?c`<ha-card
        >Select a ${l} device for this card.</ha-card
      >`:c`<ha-card
      ><header>
        <div>
          <h2>${this._config?.title??t?.name??"Microclimate"}</h2>
          <div class="muted">
            ${t?.model??"Connecting\u2026"}${this.draft?" \xB7 Draft preview":""}${t&&!t.online?" \xB7 Offline":""}
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
          </section>`:h}${this.error?c`<div role="alert" class="alert error">${this.error}</div>`:h}${t?.schema_version!==1&&t?c`<div class="alert error">
            Card/backend version mismatch. Update both before editing.
          </div>`:h}
      ${t&&i?c`${t.kind==="controller"?c`<h3>Season start dates</h3>
                <p class="muted">
                  Shared by every channel on this controller. Dates follow one
                  annual cycle; a December/January wrap is allowed.
                </p>
                <div class="form">
                  ${t.fields.filter(o=>o.kind==="date").map(o=>this.setting(o))}
                </div>`:c` <div class="badges">
                  ${t.fields.filter(o=>o.kind==="enum").map(o=>c`<span class="badge"
                          >${o.value??"Unknown"}</span
                        >`)}
                </div>
                ${this._config?.show_observations!==!1&&t.observations.length?c`<div class="observations">
                      ${t.observations.map(o=>c`<div class="observation">
                            <span class="muted">${o.name}</span
                            ><strong>${o.value} ${o.unit??""}</strong>
                          </div>`)}
                    </div>`:h}
                <h3>Configured schedule · controller local time</h3>
                ${this.mode==="Seasonal"?c`<p class="muted">
                        Dates shared by all channels. Edit dates in the
                        controller card.
                      </p>
                      ${[0,1,2,3].map(o=>this.row(n.slice(o*2,o*2+2),`Season ${o+1}`,t.fields.find(u=>u.key===`season_${o+1}_start_pin`)?.value??null))}`:["Multi","Day Night"].includes(this.mode)?this.row(n,this.mode==="Multi"?"Multi":"Day & Night"):c`<div class="alert">
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
                          ?disabled=${n.length<=2||!a||this.saving||!this.allScheduleWritable}
                          @click=${()=>a&&this.removePoint(a.draft_id)}
                        >
                          Remove selected
                        </button>
                      </div>
                      <p class="muted">
                        2–8 consecutive points. Inserting/removing shifts later
                        points; unused tail slots are cleared.
                      </p>`:h}
                ${!this.draft&&i.repair?c`<div class="alert error">
                      ${J(i)} Edit to review/rebuild; observations are
                      unchanged.
                    </div>`:h}
                <details class="settings" ?open=${!!this.draft}>
                  <summary>Channel settings</summary>
                  <p class="muted">
                    Save each mode change separately. Schedule modes share the
                    same stored time/target pairs.
                  </p>
                  <div class="form">
                    ${t.fields.filter(o=>!o.index&&!o.shared).map(o=>this.setting(o))}
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
              ${this.reviewChanges().map(o=>c`<div>${o}</div>`)}
            </details>
            <div class="actions">
              ${this.saving?c`<button @click=${this.stop}>
                    Stop remaining changes
                  </button>`:c`<button @click=${this.cancel}>Cancel</button
                    ><button
                      class="primary"
                      ?disabled=${!O(this.draft)||!!r||this.conflict||!this.canEdit||this.draft.repair||this.submissionUnknown}
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
              ${this.job.fields.map(o=>c`<div class="status">${o.label}: ${o.status}</div>`)}
            </details>
          </section>`:h}
    </ha-card>`}};var ct=class extends ${constructor(){super(...arguments);this.devices=[];this.error="";this.colorError=""}static{this.properties={config:{state:!0},devices:{state:!0},error:{state:!0},colorError:{state:!0}}}static{this.styles=L`
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
  `}set hass(t){if(this._hass===t)return;let i=!this._hass;this._hass=t,i&&t.callWS({type:E+"list"}).then(r=>this.devices=r).catch(()=>this.error="Unable to list authorized Microclimate devices.")}setConfig(t){this.config={...t}}change(t,i){this.config={...this.config,[t]:i},this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:this.config},bubbles:!0,composed:!0}))}colors(){return this.config?.temperature_colors??ut}changeColor(t,i,r){let n=this.colors().map((a,l)=>l===t?{...a,[i]:i==="temperature"?r.trim()?Number(r):NaN:r}:{...a});try{X(n),this.colorError="",this.change("temperature_colors",n)}catch(a){this.colorError=a.message}}render(){let t=this.config?.type.includes("controller")?"controller":"channel";return c`<p>
        ${this.error||"Select a registered Microclimate device. Entity renames do not change this binding."}
      </p>
      <label
        >Device<select
          aria-label="Device"
          .value=${this.config?.device_id??""}
          @change=${i=>this.change("device_id",i.target.value)}
        >
          <option value="">Select device</option>
          ${this.devices.filter(i=>i.kind===t).map(i=>c`<option
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
      >${t==="channel"?c`<details>
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
                    @click=${()=>{this.colorError="",this.change("temperature_colors",this.colors().filter((n,a)=>a!==r))}}
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
          </details>`:h}`}};var St=class extends K{},Et=class extends K{};customElements.define("microclimate-channel-card",St);customElements.define("microclimate-controller-card",Et);customElements.define("microclimate-card-editor",ct);var kt=window;kt.customCards=kt.customCards??[];kt.customCards.push({type:"microclimate-channel-card",name:"Microclimate channel",description:"Daily, Multi and seasonal schedule with explicit Save/Cancel."},{type:"microclimate-controller-card",name:"Microclimate controller",description:"Shared season start dates."});
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
