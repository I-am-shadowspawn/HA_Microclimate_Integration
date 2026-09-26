var M="microclimate_integration/card/",We=e=>!e||["succeeded","failed","partial","uncertain","stopped"].includes(e.status);var oe={snapshot_unavailable:"Device data unavailable. Check the integration and permissions.",snapshot_invalid:"Controller data is incomplete. Refresh before editing.",schema_mismatch:"Card/backend version mismatch. Update both before editing.",job_invalid:"Save status is incomplete. Check the controller before another Save.",ack_invalid:"Save acknowledgement was invalid. Check request status before another Save.",ack_lost:"Save acknowledgement was lost. Check request status before another Save.",recovery_invalid:"Request status was incomplete. Check the controller before another Save.",recovery_unavailable:"Cannot determine Save status. Reconnect and check again; no update has been retried.",stopping:"Stopping after the current request; applied changes remain.",stop_failed:"Could not stop. Check the current operation status.",controller_time:"Controller-local time (timezone not reported)",select_device:"Select a Microclimate device.",subscribe_failed:"Unable to load this device. Check the integration version, device and permissions.",job_unavailable:"Save status unavailable. Refresh and review before another Save.",confirmed:"Changes confirmed by API readback.",partial:"Some changes may already be applied. Refresh and review before saving again.",draft_discarded:"Draft discarded; no changes sent.",no_record:"No retained Save record found. Verify controller settings before discarding this draft; it will not be resubmitted automatically.",rebase_blocked:"Mode or connection changed. Discard this draft and edit fresh settings.",rebase_review:"Draft retained against fresh observations. Review every difference before a new Save.",repair_review:"Review the rebuilt list before Save. Unknown values require correction.",preset_downloaded:"Schedule preset downloaded in native Celsius/% units; no controller identity included.",preset_loaded:"Preset loaded into a local draft. Review changes, then Save or Cancel.",preset_too_large:"Preset file is too large.",preset_json_invalid:"Invalid preset JSON.",device_list_invalid:"The device list is incomplete. Refresh before choosing a device.",device_list_unavailable:"Unable to list authorized Microclimate devices.",editor_intro:"Select a registered Microclimate device. Entity renames do not change this binding.",editor_device:"Device",editor_select_device:"Select device",editor_title:"Title",editor_read_only:"Always read only",editor_colors:"Temperature colours",editor_colors_help:"Inclusive lower bounds in \xB0C, also when HA displays \xB0F. Below the lowest bound uses its colour. Percentage targets use teal.",editor_lower:"Lower temperature (\xB0C)",editor_color:"Colour",editor_add_color:"Add temperature colour",editor_reset_color:"Reset temperature colours",editor_color_number:"Colour {number}",editor_remove_color:"Remove colour {number}",editor_color_value:"Colour {number} value",editor_color_lower:"Colour {number} lower temperature \xB0C",dates_help:"Shared by every channel on this controller. Dates follow one annual cycle; a December/January wrap is allowed.",seasonal_dates_help:"Dates shared by all channels. Edit dates in the controller card.",repair_needed:"Existing points need review. Opening this card makes no changes.",repair_observation:"Edit to review/rebuild; observations are unchanged.",clear_tail:" (clear tail)",color_invalid:"Temperature colours require unique Celsius bounds from 0 to 100 and #RRGGBB colours.",preset_unit_missing:"Schedule unit is unavailable.",preset_incomplete:"Complete the supported schedule before exporting.",preset_invalid:"Invalid schedule preset.",preset_format:"Unsupported schedule preset format.",preset_mode:"Preset mode and native units must match this channel.",preset_points:"Invalid schedule points.",preset_count:"Incorrect number of schedule points.",preset_point:"Invalid schedule point.",multi_count:"Multi needs 2\u20138 points.",mode_count:"{mode} needs {count} points.",complete_points:"Complete every time and target (0\u2013100).",empty_point:"Midnight with target zero is reserved for unused slots.",multi_order:"Multi starts must be distinct and chronological.",day_night_order:"Day and Night must have distinct starts.",dates_format:"Use DD/MM for every season date.",dates_calendar:"Use valid calendar dates; 29/02 is not supported.",dates_distinct:"Season starts must be distinct.",dates_cycle:"Seasons must follow one annual cycle (one year wrap is allowed).",separate_mode:"Save one mode change separately from other edits.",not_editable:"{label} is not editable.",range_error:"{label}: enter {minimum}\u2013{maximum}{suffix}.",date_edit:"Use a valid DD/MM date; unset dates cannot be written.",option_edit:"Choose a supported mode.",whole_minutes:" whole minutes",unknown:"Unknown",connecting:"Connecting\u2026",draft_preview:" \xB7 Draft preview",offline:" \xB7 Offline",mismatch:"Card/backend version mismatch. Update both before editing.",wrong_device:"Select a {kind} device for this card.",unsaved:"Unsaved schedule changes",unsaved_prompt:"Save or discard this draft before changing devices?",stay:"Stay",discard_draft:"Discard draft",save_then_switch:"Save then switch",edit:"Edit",season_dates:"Season start dates",schedule_heading:"Configured schedule \xB7 controller local time",constant_unmapped:"Constant target writing is not mapped.",periodic_unmapped:"Periodic interval/duration editing is not supported.",timing_unknown:"Timing mode unknown.",point_rebuild:"Review/rebuild point list",add_point:"Add point",remove_selected:"Remove selected",multi_help:"2\u20138 consecutive points. Inserting/removing shifts later points; unused tail slots are cleared.",preset_help:"Presets contain schedule points only, in native Celsius or percent. Import stays local until Save. To copy between cards, download then import on a compatible channel.",download_preset:"Download preset",import_preset:"Import preset",channel_settings:"Channel settings",settings_help:"Save each mode change separately. Schedule modes share the same stored time/target pairs.",save_unresolved:"Save result is unresolved.",check_request:"Check request status",settings_changed:"Settings changed since editing began.",refresh_review:"Refresh and review draft",write_warning:"Save sends changes sequentially. Intermediate settings may affect the controller; confirmed changes cannot be rolled back automatically.",changed_fields:"{count} changed fields \xB7 review",stop_remaining:"Stop remaining changes",cancel:"Cancel",save_changes:"Save changes",change_results:"Change results",job_progress:"{status} \xB7 {confirmed}/{total} confirmed",starts:"Starts {date}",carry:"Configured carry-over \xB7 ",unknown_boundaries:"Unknown or incomplete boundaries",point:"Point {number}",day:"Day",night:"Night",season:"Season {number}",season_day:"Season {number} Day",season_night:"Season {number} Night",multi:"Multi",day_and_night:"Day & Night",day_night_option:"Day Night",constant:"Constant",periodic:"Periodic",seasonal:"Seasonal",fixed:"fixed",heating:"heating",cooling:"cooling",pulse:"pulse",dimming:"dimming",slot_table:"{label} slot table",boundary_label:"{label} {time} boundary",selected_target:"{label} selected target slider",point_start:"{label} {point} start",point_target:"{label} {point} target {unit}",timeline_label:"{label} configured 24-hour timeline",selected_target_label:"{label} selected target slider",point_target_summary:"target"};function p(e,t={},i=oe){return(i[e]??oe[e]).replace(/\{(\w+)\}/g,(n,s)=>String(t[s]??`{${s}}`))}function q(e,t,i={},n={}){return p(e,i,n[t??""]??n[t?.split("-")[0]??""]??oe)}function T(){let e=crypto.getRandomValues(new Uint8Array(16));e[6]=e[6]&15|64,e[8]=e[8]&63|128;let t=Array.from(e,i=>i.toString(16).padStart(2,"0")).join("");return`${t.slice(0,8)}-${t.slice(8,12)}-${t.slice(12,16)}-${t.slice(16,20)}-${t.slice(20)}`}function F(e,t=100){return typeof e=="number"&&Number.isFinite(e)&&e>=0&&e<=t}function ae(e){return F(e,86399)&&Number.isInteger(e)}function le(e,t){return e==="Multi"?t>=2&&t<=8:e==="Day Night"?t===2:e==="Seasonal"?t===8:!1}function Ce(e){if(typeof e!="string"||e.length!==5||!/^[0-9]{2}\/[0-9]{2}$/.test(e))return null;let[t,i]=e.split("/").map(Number),n=new Date(Date.UTC(2001,i-1,t));return n.getUTCMonth()!==i-1||n.getUTCDate()!==t?null:Math.floor((n.getTime()-Date.UTC(2001,0,1))/864e5)}var Ke=e=>e.seconds===0&&e.target_native===0,$=e=>e===null?"":`${Math.floor(e/3600).toString().padStart(2,"0")}:${Math.floor(e/60%60).toString().padStart(2,"0")}:${(e%60).toString().padStart(2,"0")}`;function Xe(e){if(!/^\d{2}:\d{2}(:\d{2})?$/.test(e))return null;let[t,i,n=0]=e.split(":").map(Number);return t<24&&i<60&&n<60?t*3600+i*60+n:null}var v=(e,t,i)=>t==="\xB0C"&&i?e*9/5+32:e,X=(e,t,i)=>t==="\xB0C"&&i?(e-32)*5/9:e;function z(e){let t=String(e.fields.find(r=>r.key===`${e.channel}_timing_type`)?.value??""),i=[],n=t==="Day Night"?2:["Multi","Seasonal"].includes(t)?8:0;for(let r=1;r<=n;r++)i.push({draft_id:T(),source_slot:r,seconds:e.fields.find(o=>o.key===`${e.channel}_period_${r}_time`)?.value??null,target_native:e.fields.find(o=>o.key===`${e.channel}_period_${r}_setpoint`)?.value??null});if(t==="Multi")for(;i.length&&Ke(i.at(-1));)i.pop();let s={base:e,values:Object.fromEntries(e.fields.filter(r=>!r.index&&(!r.shared||!e.channel)).map(r=>[r.key,r.value])),points:i,mode:t,repair:!1};return s.repair=t==="Multi"&&w(s)!==null,s}function w(e){if(!["Multi","Day Night","Seasonal"].includes(e.mode))return null;if(!le(e.mode,e.points.length))return e.mode==="Multi"?p("multi_count"):p("mode_count",{mode:e.mode,count:e.mode==="Day Night"?2:8});if(e.points.some(t=>!ae(t.seconds)||!F(t.target_native)))return p("complete_points");if(e.mode==="Multi"){if(e.points.some(Ke))return p("empty_point");if(e.points.some((t,i)=>i>0&&t.seconds<=e.points[i-1].seconds))return p("multi_order")}else if(e.points.some((t,i)=>i%2===0&&t.seconds===e.points[i+1]?.seconds))return p("day_night_order");return null}function Ht(e){let t=[];for(let i of e){if(i==="00/00")continue;if(typeof i!="string"||!/^\d{2}\/\d{2}$/.test(i))return p("dates_format");let n=Ce(i);if(n===null)return p("dates_calendar");t.push(n)}return new Set(t).size!==t.length?p("dates_distinct"):t.length>1&&t.reduce((i,n,s)=>i+(t[(s+1)%t.length]-n+365)%365,0)!==365?p("dates_cycle"):null}function R(e){return Object.fromEntries(Object.entries(e.values).filter(([t,i])=>i!==e.base.fields.find(n=>n.key===t)?.value))}function de(e){let t=z(e.base);return JSON.stringify(e.points.map(i=>[i.seconds,i.target_native]))!==JSON.stringify(t.points.map(i=>[i.seconds,i.target_native]))}function Ye(e){let t=R(e);if(Object.keys(t).filter(s=>e.base.fields.find(r=>r.key===s)?.kind==="enum").length)return{kind:"mode",fields:t};let n={kind:e.base.channel?"channel":"season_dates",fields:t};return de(e)&&(n.schedule={mode:e.mode,points:e.points}),n}var S=e=>Object.keys(R(e)).length>0||de(e);function ce(e){let t=R(e),i=Object.keys(t);if(i.filter(s=>e.base.fields.find(r=>r.key===s)?.kind==="enum").length&&(i.length>1||de(e)))return p("separate_mode");for(let s of i){let r=e.base.fields.find(a=>a.key===s),o=t[s];if(!r.writable)return p("not_editable",{label:r.label});if(["number","setpoint","ramp"].includes(r.kind)&&(!F(o,r.maximum)||o<r.minimum||r.kind==="ramp"&&!Number.isInteger(o)))return p("range_error",{label:r.label,minimum:r.minimum,maximum:r.maximum,suffix:r.kind==="ramp"?p("whole_minutes"):""});if(r.kind==="date"&&Ce(o)===null)return p("date_edit");if(r.kind==="enum"&&(typeof o!="string"||!r.options.includes(o)))return p("option_edit")}if(!e.base.channel&&i.length){let s=e.base.fields.filter(r=>r.kind==="date").map(r=>t[r.key]??(r.validity==="unset"?"00/00":r.value));return Ht(s)}return de(e)?w(e):null}function Ge(e){if(!e.length||e.some(n=>n.seconds===null||n.target_native===null))return[];let t=[...e].sort((n,s)=>n.seconds-s.seconds);if(new Set(t.map(n=>n.seconds)).size!==t.length)return[];let i=t.map((n,s)=>({point:n,start:n.seconds,end:t[s+1]?.seconds??86400,carry:s===t.length-1&&t[0].seconds>0}));return t[0].seconds>0&&i.unshift({point:t.at(-1),start:0,end:t[0].seconds,carry:!0}),i}var G=e=>({ok:!0,value:e}),j=(e="malformed")=>({ok:!1,reason:e}),E=e=>!!e&&typeof e=="object"&&!Array.isArray(e),y=e=>typeof e=="string"&&e.length>0&&e.length<=1024,D=e=>y(e)&&e.length<=128,Y=e=>typeof e=="number"&&Number.isFinite(e),he=e=>Y(e)&&Number.isInteger(e)&&e>=0,B=e=>e===null||typeof e=="string",Lt=e=>B(e)||Y(e),qt=new Set(["enum","date","time","number","setpoint","ramp"]),Ft=new Set(["pending","running","succeeded","failed","partial","uncertain","stopped"]),zt=new Set(["not-sent","pending","confirmed","failed","uncertain"]);function Bt(e){return E(e)?D(e.key)&&qt.has(String(e.kind))&&typeof e.label=="string"&&(e.index===null||he(e.index)&&e.index>=1&&e.index<=8)&&typeof e.shared=="boolean"&&Lt(e.value)&&D(e.entity_id)&&(e.validity===void 0||typeof e.validity=="string")&&typeof e.writable=="boolean"&&B(e.reason)&&Array.isArray(e.options)&&e.options.every(y)&&B(e.unit)&&Y(e.minimum)&&Y(e.maximum)&&(e.step==="any"||Y(e.step)):!1}function Qe(e,t){return E(e)?e.schema_version!==1?j("unsupported"):!D(e.runtime_generation)||!D(e.revision)||e.device_id!==t||!y(e.name)||!y(e.model)||e.kind!=="channel"&&e.kind!=="controller"||(e.kind==="channel"?!y(e.channel):e.channel!==null)||!Array.isArray(e.fields)||!e.fields.every(Bt)||!Array.isArray(e.observations)||!e.observations.every(i=>E(i)&&y(i.name)&&typeof i.value=="string"&&B(i.unit))||typeof e.online!="boolean"||typeof e.writes_enabled!="boolean"||typeof e.busy!="boolean"||new Set(e.fields.map(i=>i.key)).size!==e.fields.length?j():G(e):j()}function Ze(e,t){return!E(e)||e.operation_id!==t||!he(e.sequence)||!y(e.status)||!Ft.has(e.status)||!y(e.phase)||!he(e.confirmed)||!he(e.total)||e.confirmed>e.total||!Array.isArray(e.fields)||!e.fields.every(i=>E(i)&&D(i.key)&&typeof i.label=="string"&&y(i.status)&&zt.has(i.status))||!B(e.reason)||e.reason_message!==void 0&&!B(e.reason_message)?j():G(e)}function et(e){return!Array.isArray(e)||!e.every(t=>E(t)&&D(t.device_id)&&(t.kind==="channel"||t.kind==="controller")&&y(t.name))?j():G(e)}function Pe(e){return E(e)&&D(e.operation_id)?G({operation_id:e.operation_id}):j()}function tt(e){return e===null?G(null):Pe(e)}function Me(e){return E(e)&&y(e.error)?e.error:null}function it(e){return E(e)?{code:D(e.code)?e.code:void 0,message:y(e.message)?e.message:void 0}:{}}var ue=class{constructor(t,i){this.changed=t;this.onSelect=i;this.connected=!1;this.navigateAfterSave=!1;this.epoch=0;this.watch=0;this.subscribed="";this._view=void 0;this._draft=void 0;this._job=void 0;this._error="";this._notice="";this._saving=!1;this._submissionUnknown=!1;this._pendingConfig=void 0;this._config=void 0;this.reconnect=()=>{this.release(),this.subscribe()}}t(t,i={}){return q(t,this.hass?.language,i)}get view(){return this._view}set view(t){this._view=t,this.changed()}get draft(){return this._draft}set draft(t){this._draft=t,this.changed()}get job(){return this._job}set job(t){this._job=t,this.changed()}get error(){return this._error}set error(t){this._error=t,this.changed()}get notice(){return this._notice}set notice(t){this._notice=t,this.changed()}get saving(){return this._saving}set saving(t){this._saving=t,this.changed()}get submissionUnknown(){return this._submissionUnknown}set submissionUnknown(t){this._submissionUnknown=t,this.changed()}get pendingConfig(){return this._pendingConfig}set pendingConfig(t){this._pendingConfig=t,this.changed()}get config(){return this._config}set config(t){this._config=t,this.changed()}setHass(t){let i=this.hass?.connection!==t.connection;i&&(this.hass?.connection.removeEventListener?.("ready",this.reconnect),this.release()),this.hass=t,i&&t.connection.addEventListener?.("ready",this.reconnect),this.subscribe()}setConfig(t){if(!t.device_id||typeof t.device_id!="string")throw new Error(this.t("select_device"));if(this.config?.device_id!==t.device_id){if(this.draft&&S(this.draft)){this.pendingConfig=t;return}this.release(),this.view=void 0,this.job=void 0,this.onSelect(""),this.requestId=void 0,this.submissionUnknown=!1,this.saving=!1}this.config={...t},this.subscribe()}connect(){this.connected=!0,this.hass?.connection.addEventListener?.("ready",this.reconnect),this.subscribe()}disconnect(){this.connected=!1,this.hass?.connection.removeEventListener?.("ready",this.reconnect),this.release()}release(){this.epoch++,this.watch++,this.saving&&this.requestId&&!this.job&&(this.submissionUnknown=!0),this.unsubscribe?.(),this.unsubJob?.(),this.unsubscribe=void 0,this.unsubJob=void 0,this.subscribed=""}async subscribe(){if(!this.connected||!this.hass||!this.config||this.subscribed)return;let t=this.epoch;this.subscribed=this.config.device_id;try{let i=await this.hass.connection.subscribeMessage(n=>{if(t!==this.epoch)return;if(Me(n)){this.error=this.t("snapshot_unavailable"),this.view=void 0;return}let r=Qe(n,this.config.device_id);if(!r.ok){this.error=this.t(r.reason==="unsupported"?"schema_mismatch":"snapshot_invalid"),this.view=void 0;return}this.view=r.value,this.error=""},{type:M+"subscribe",device_id:this.config.device_id});if(t!==this.epoch){i();return}this.unsubscribe=i,this.job?await this.watchJob(this.job.operation_id):this.submissionUnknown&&await this.recoverRequest()}catch{t===this.epoch&&(this.subscribed="",this.error=this.t("subscribe_failed"))}}async watchJob(t){let i=++this.watch;this.unsubJob?.();let n=this.epoch,s=await this.hass.connection.subscribeMessage(r=>{if(n!==this.epoch||i!==this.watch)return;if(Me(r)){this.error=this.t("job_unavailable"),this.saving=!1,this.submissionUnknown=!0;return}let o=Ze(r,t);if(!o.ok){this.error=this.t("job_invalid"),this.saving=!1,this.submissionUnknown=!0;return}let a=o.value;if(!(this.job?.operation_id===a.operation_id&&a.sequence<=this.job.sequence)&&(this.job=a,We(a)))if(this.saving=!1,a.status==="succeeded"){if(this.draft=void 0,this.submissionUnknown=!1,this.requestId=void 0,this.notice=this.t("confirmed"),this.navigateAfterSave&&this.pendingConfig){let l=this.pendingConfig;this.pendingConfig=void 0,this.navigateAfterSave=!1,this.setConfig(l)}}else this.notice=this.t("partial")},{type:M+"operation",operation_id:t});n!==this.epoch||i!==this.watch?s():this.unsubJob=s}edit(){this.canEdit&&(this.draft=z(this.view),this.job=void 0,this.notice="",this.onSelect(this.draft.points[0]?.draft_id??""))}navigate(t){if(t==="stay"){this.pendingConfig=void 0;return}if(t==="save"){this.navigateAfterSave=!0,this.save();return}let i=this.pendingConfig;this.pendingConfig=void 0,this.draft=void 0,i&&this.setConfig(i)}cancel(){this.draft=void 0,this.notice=this.t("draft_discarded"),this.error=""}async save(){if(!this.draft||!S(this.draft)||ce(this.draft)||this.conflict||this.saving||this.submissionUnknown||!this.canEdit)return;this.saving=!0,this.error="",this.requestId=T();let t=this.epoch,i=this.requestId,n=this.config.device_id;try{let s=await this.hass.callWS({type:M+"save",schema_version:1,device_id:this.config.device_id,runtime_generation:this.draft.base.runtime_generation,base_revision:this.draft.base.revision,request_id:this.requestId,patch:Ye(this.draft)});if(t!==this.epoch||i!==this.requestId||n!==this.config?.device_id)return;let r=Pe(s);if(!r.ok)throw new Error(this.t("ack_invalid"));this.job={operation_id:r.value.operation_id,sequence:-1,status:"pending",phase:"Preflight",confirmed:0,total:0,fields:[],reason:null},await this.watchJob(r.value.operation_id)}catch(s){if(this.saving=!1,t!==this.epoch||i!==this.requestId||n!==this.config?.device_id)return;let r=it(s);this.submissionUnknown=!r.code,this.error=r.message??this.t("ack_lost"),this.submissionUnknown&&await this.recoverRequest()}}async recoverRequest(){if(!this.requestId)return;let t=this.epoch,i=this.requestId,n=this.config.device_id;try{let s=await this.hass.callWS({type:M+"request",device_id:this.config.device_id,request_id:this.requestId});if(t!==this.epoch||i!==this.requestId||n!==this.config?.device_id)return;let r=tt(s);if(!r.ok)throw new Error(this.t("recovery_invalid"));r.value?(this.submissionUnknown=!1,this.saving=!0,await this.watchJob(r.value.operation_id)):this.error=this.t("no_record")}catch{if(t!==this.epoch||i!==this.requestId||n!==this.config?.device_id)return;this.error=this.t("recovery_unavailable")}}async stop(){if(this.job){let t=this.epoch,i=this.job.operation_id;try{if(await this.hass.callWS({type:M+"stop",operation_id:i}),t!==this.epoch||i!==this.job?.operation_id)return;this.notice=this.t("stopping")}catch{t===this.epoch&&(this.error=this.t("stop_failed"))}}}rebase(){if(!this.draft||!this.view)return;let t=this.draft,i=z(this.view),n=R(t);if(i.mode!==t.mode||i.base.runtime_generation!==t.base.runtime_generation){this.error=this.t("rebase_blocked");return}this.draft={...t,base:this.view,values:{...i.values,...n}},this.job=void 0,this.notice=this.t("rebase_review")}get conflict(){return!!this.draft&&!!this.view&&(this.draft.base.revision!==this.view.revision||this.draft.base.runtime_generation!==this.view.runtime_generation)}get canEdit(){return!!this.view&&this.view.schema_version===1&&this.view.online&&!this.view.busy&&this.view.writes_enabled&&!this.config?.read_only&&this.view.fields.some(t=>t.writable)}};var Te=[{temperature:0,color:"#f6c85f"},{temperature:20,color:"#f5a623"},{temperature:25,color:"#ef7d16"},{temperature:30,color:"#d94b24"},{temperature:35,color:"#b52222"}];function pe(e){if(e!==void 0&&(!Array.isArray(e)||e.length===0||e.some(t=>!t||typeof t.temperature!="number"||!Number.isFinite(t.temperature)||t.temperature<0||t.temperature>100||typeof t.color!="string"||!/^#[0-9a-f]{6}$/i.test(t.color))||new Set(e.map(t=>t.temperature)).size!==e.length))throw new Error(p("color_invalid"))}function Vt(e,t=Te){if(e===null||!Number.isFinite(e))return"#737373";let i=[...t].sort((n,s)=>n.temperature-s.temperature);return(i.filter(n=>e>=n.temperature).at(-1)??i[0]).color}function Jt(e){let t=[1,3,5].map(n=>{let s=parseInt(e.slice(n,n+2),16)/255;return s<=.04045?s/12.92:((s+.055)/1.055)**2.4});return t[0]*.2126+t[1]*.7152+t[2]*.0722>.179?"#000000":"#ffffff"}function nt(e,t,i){let n=t==="\xB0C"?Vt(e,i):"#327b80";return`--segment-color:${n};--segment-text:${Jt(n)}`}var st="microclimate.schedule.v1",rt=4096;function ot(e){let t=e.base.fields.find(i=>i.key===`${e.base.channel}_period_1_setpoint`);if(t?.unit==="\xB0C")return"celsius";if(t?.unit==="%")return"percent";throw new Error(p("preset_unit_missing"))}function at(e){if(!["Day Night","Multi","Seasonal"].includes(e.mode)||w(e))throw new Error(p("preset_incomplete"));return{format:st,mode:e.mode,unit:ot(e),points:e.points.map(t=>({seconds:t.seconds,target_native:t.target_native}))}}function lt(e,t){if(!t||typeof t!="object"||Array.isArray(t))throw new Error(p("preset_invalid"));let i=t;if(Object.keys(i).sort().join(",")!=="format,mode,points,unit"||i.format!==st)throw new Error(p("preset_format"));if(i.mode!==e.mode||i.unit!==ot(e))throw new Error(p("preset_mode"));if(!Array.isArray(i.points))throw new Error(p("preset_points"));if(!le(e.mode,i.points.length))throw new Error(p("preset_count"));let n=i.points.map(o=>{if(!o||typeof o!="object"||Object.keys(o).sort().join(",")!=="seconds,target_native"||!ae(o.seconds)||!F(o.target_native))throw new Error(p("preset_point"));return{draft_id:T(),seconds:o.seconds,target_native:o.target_native}}),s={...e,points:n,repair:!1},r=w(s);if(r)throw new Error(r);return s}var fe=globalThis,me=fe.ShadowRoot&&(fe.ShadyCSS===void 0||fe.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Re=Symbol(),dt=new WeakMap,Q=class{constructor(t,i,n){if(this._$cssResult$=!0,n!==Re)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=i}get styleSheet(){let t=this.o,i=this.t;if(me&&t===void 0){let n=i!==void 0&&i.length===1;n&&(t=dt.get(i)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),n&&dt.set(i,t))}return t}toString(){return this.cssText}},ct=e=>new Q(typeof e=="string"?e:e+"",void 0,Re),Z=(e,...t)=>{let i=e.length===1?e[0]:t.reduce((n,s,r)=>n+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+e[r+1],e[0]);return new Q(i,e,Re)},ht=(e,t)=>{if(me)e.adoptedStyleSheets=t.map(i=>i instanceof CSSStyleSheet?i:i.styleSheet);else for(let i of t){let n=document.createElement("style"),s=fe.litNonce;s!==void 0&&n.setAttribute("nonce",s),n.textContent=i.cssText,e.appendChild(n)}},De=me?e=>e:e=>e instanceof CSSStyleSheet?(t=>{let i="";for(let n of t.cssRules)i+=n.cssText;return ct(i)})(e):e;var{is:Wt,defineProperty:Kt,getOwnPropertyDescriptor:Xt,getOwnPropertyNames:Yt,getOwnPropertySymbols:Gt,getPrototypeOf:Qt}=Object,ge=globalThis,ut=ge.trustedTypes,Zt=ut?ut.emptyScript:"",ei=ge.reactiveElementPolyfillSupport,ee=(e,t)=>e,Ue={toAttribute(e,t){switch(t){case Boolean:e=e?Zt:null;break;case Object:case Array:e=e==null?e:JSON.stringify(e)}return e},fromAttribute(e,t){let i=e;switch(t){case Boolean:i=e!==null;break;case Number:i=e===null?null:Number(e);break;case Object:case Array:try{i=JSON.parse(e)}catch{i=null}}return i}},ft=(e,t)=>!Wt(e,t),pt={attribute:!0,type:String,converter:Ue,reflect:!1,useDefault:!1,hasChanged:ft};Symbol.metadata??=Symbol("metadata"),ge.litPropertyMetadata??=new WeakMap;var A=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,i=pt){if(i.state&&(i.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((i=Object.create(i)).wrapped=!0),this.elementProperties.set(t,i),!i.noAccessor){let n=Symbol(),s=this.getPropertyDescriptor(t,n,i);s!==void 0&&Kt(this.prototype,t,s)}}static getPropertyDescriptor(t,i,n){let{get:s,set:r}=Xt(this.prototype,t)??{get(){return this[i]},set(o){this[i]=o}};return{get:s,set(o){let a=s?.call(this);r?.call(this,o),this.requestUpdate(t,a,n)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??pt}static _$Ei(){if(this.hasOwnProperty(ee("elementProperties")))return;let t=Qt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(ee("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(ee("properties"))){let i=this.properties,n=[...Yt(i),...Gt(i)];for(let s of n)this.createProperty(s,i[s])}let t=this[Symbol.metadata];if(t!==null){let i=litPropertyMetadata.get(t);if(i!==void 0)for(let[n,s]of i)this.elementProperties.set(n,s)}this._$Eh=new Map;for(let[i,n]of this.elementProperties){let s=this._$Eu(i,n);s!==void 0&&this._$Eh.set(s,i)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let i=[];if(Array.isArray(t)){let n=new Set(t.flat(1/0).reverse());for(let s of n)i.unshift(De(s))}else t!==void 0&&i.push(De(t));return i}static _$Eu(t,i){let n=i.attribute;return n===!1?void 0:typeof n=="string"?n:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,i=this.constructor.elementProperties;for(let n of i.keys())this.hasOwnProperty(n)&&(t.set(n,this[n]),delete this[n]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ht(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,i,n){this._$AK(t,n)}_$ET(t,i){let n=this.constructor.elementProperties.get(t),s=this.constructor._$Eu(t,n);if(s!==void 0&&n.reflect===!0){let r=(n.converter?.toAttribute!==void 0?n.converter:Ue).toAttribute(i,n.type);this._$Em=t,r==null?this.removeAttribute(s):this.setAttribute(s,r),this._$Em=null}}_$AK(t,i){let n=this.constructor,s=n._$Eh.get(t);if(s!==void 0&&this._$Em!==s){let r=n.getPropertyOptions(s),o=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:Ue;this._$Em=s;let a=o.fromAttribute(i,r.type);this[s]=a??this._$Ej?.get(s)??a,this._$Em=null}}requestUpdate(t,i,n,s=!1,r){if(t!==void 0){let o=this.constructor;if(s===!1&&(r=this[t]),n??=o.getPropertyOptions(t),!((n.hasChanged??ft)(r,i)||n.useDefault&&n.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(o._$Eu(t,n))))return;this.C(t,i,n)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,i,{useDefault:n,reflect:s,wrapped:r},o){n&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,o??i??this[t]),r!==!0||o!==void 0)||(this._$AL.has(t)||(this.hasUpdated||n||(i=void 0),this._$AL.set(t,i)),s===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(i){Promise.reject(i)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[s,r]of this._$Ep)this[s]=r;this._$Ep=void 0}let n=this.constructor.elementProperties;if(n.size>0)for(let[s,r]of n){let{wrapped:o}=r,a=this[s];o!==!0||this._$AL.has(s)||a===void 0||this.C(s,void 0,r,a)}}let t=!1,i=this._$AL;try{t=this.shouldUpdate(i),t?(this.willUpdate(i),this._$EO?.forEach(n=>n.hostUpdate?.()),this.update(i)):this._$EM()}catch(n){throw t=!1,this._$EM(),n}t&&this._$AE(i)}willUpdate(t){}_$AE(t){this._$EO?.forEach(i=>i.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(i=>this._$ET(i,this[i])),this._$EM()}updated(t){}firstUpdated(t){}};A.elementStyles=[],A.shadowRootOptions={mode:"open"},A[ee("elementProperties")]=new Map,A[ee("finalized")]=new Map,ei?.({ReactiveElement:A}),(ge.reactiveElementVersions??=[]).push("2.1.2");var Ne=globalThis,mt=e=>e,_e=Ne.trustedTypes,gt=_e?_e.createPolicy("lit-html",{createHTML:e=>e}):void 0,Ie="$lit$",C=`lit$${Math.random().toFixed(9).slice(2)}$`,Oe="?"+C,ti=`<${Oe}>`,O=document,ie=()=>O.createComment(""),ne=e=>e===null||typeof e!="object"&&typeof e!="function",He=Array.isArray,wt=e=>He(e)||typeof e?.[Symbol.iterator]=="function",je=`[ 	
\f\r]`,te=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,_t=/-->/g,bt=/>/g,N=RegExp(`>|${je}(?:([^\\s"'>=/]+)(${je}*=${je}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),vt=/'/g,yt=/"/g,xt=/^(?:script|style|textarea|title)$/i,Le=e=>(t,...i)=>({_$litType$:e,strings:t,values:i}),d=Le(1),Ui=Le(2),ji=Le(3),b=Symbol.for("lit-noChange"),c=Symbol.for("lit-nothing"),$t=new WeakMap,I=O.createTreeWalker(O,129);function kt(e,t){if(!He(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return gt!==void 0?gt.createHTML(t):t}var St=(e,t)=>{let i=e.length-1,n=[],s,r=t===2?"<svg>":t===3?"<math>":"",o=te;for(let a=0;a<i;a++){let l=e[a],u,f,h=-1,g=0;for(;g<l.length&&(o.lastIndex=g,f=o.exec(l),f!==null);)g=o.lastIndex,o===te?f[1]==="!--"?o=_t:f[1]!==void 0?o=bt:f[2]!==void 0?(xt.test(f[2])&&(s=RegExp("</"+f[2],"g")),o=N):f[3]!==void 0&&(o=N):o===N?f[0]===">"?(o=s??te,h=-1):f[1]===void 0?h=-2:(h=o.lastIndex-f[2].length,u=f[1],o=f[3]===void 0?N:f[3]==='"'?yt:vt):o===yt||o===vt?o=N:o===_t||o===bt?o=te:(o=N,s=void 0);let m=o===N&&e[a+1].startsWith("/>")?" ":"";r+=o===te?l+ti:h>=0?(n.push(u),l.slice(0,h)+Ie+l.slice(h)+C+m):l+C+(h===-2?a:m)}return[kt(e,r+(e[i]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),n]},se=class e{constructor({strings:t,_$litType$:i},n){let s;this.parts=[];let r=0,o=0,a=t.length-1,l=this.parts,[u,f]=St(t,i);if(this.el=e.createElement(u,n),I.currentNode=this.el.content,i===2||i===3){let h=this.el.content.firstChild;h.replaceWith(...h.childNodes)}for(;(s=I.nextNode())!==null&&l.length<a;){if(s.nodeType===1){if(s.hasAttributes())for(let h of s.getAttributeNames())if(h.endsWith(Ie)){let g=f[o++],m=s.getAttribute(h).split(C),_=/([.?@])?(.*)/.exec(g);l.push({type:1,index:r,name:_[2],strings:m,ctor:_[1]==="."?ve:_[1]==="?"?ye:_[1]==="@"?$e:L}),s.removeAttribute(h)}else h.startsWith(C)&&(l.push({type:6,index:r}),s.removeAttribute(h));if(xt.test(s.tagName)){let h=s.textContent.split(C),g=h.length-1;if(g>0){s.textContent=_e?_e.emptyScript:"";for(let m=0;m<g;m++)s.append(h[m],ie()),I.nextNode(),l.push({type:2,index:++r});s.append(h[g],ie())}}}else if(s.nodeType===8)if(s.data===Oe)l.push({type:2,index:r});else{let h=-1;for(;(h=s.data.indexOf(C,h+1))!==-1;)l.push({type:7,index:r}),h+=C.length-1}r++}}static createElement(t,i){let n=O.createElement("template");return n.innerHTML=t,n}};function H(e,t,i=e,n){if(t===b)return t;let s=n!==void 0?i._$Co?.[n]:i._$Cl,r=ne(t)?void 0:t._$litDirective$;return s?.constructor!==r&&(s?._$AO?.(!1),r===void 0?s=void 0:(s=new r(e),s._$AT(e,i,n)),n!==void 0?(i._$Co??=[])[n]=s:i._$Cl=s),s!==void 0&&(t=H(e,s._$AS(e,t.values),s,n)),t}var be=class{constructor(t,i){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=i}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:i},parts:n}=this._$AD,s=(t?.creationScope??O).importNode(i,!0);I.currentNode=s;let r=I.nextNode(),o=0,a=0,l=n[0];for(;l!==void 0;){if(o===l.index){let u;l.type===2?u=new V(r,r.nextSibling,this,t):l.type===1?u=new l.ctor(r,l.name,l.strings,this,t):l.type===6&&(u=new we(r,this,t)),this._$AV.push(u),l=n[++a]}o!==l?.index&&(r=I.nextNode(),o++)}return I.currentNode=O,s}p(t){let i=0;for(let n of this._$AV)n!==void 0&&(n.strings!==void 0?(n._$AI(t,n,i),i+=n.strings.length-2):n._$AI(t[i])),i++}},V=class e{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,i,n,s){this.type=2,this._$AH=c,this._$AN=void 0,this._$AA=t,this._$AB=i,this._$AM=n,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,i=this._$AM;return i!==void 0&&t?.nodeType===11&&(t=i.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,i=this){t=H(this,t,i),ne(t)?t===c||t==null||t===""?(this._$AH!==c&&this._$AR(),this._$AH=c):t!==this._$AH&&t!==b&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):wt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==c&&ne(this._$AH)?this._$AA.nextSibling.data=t:this.T(O.createTextNode(t)),this._$AH=t}$(t){let{values:i,_$litType$:n}=t,s=typeof n=="number"?this._$AC(t):(n.el===void 0&&(n.el=se.createElement(kt(n.h,n.h[0]),this.options)),n);if(this._$AH?._$AD===s)this._$AH.p(i);else{let r=new be(s,this),o=r.u(this.options);r.p(i),this.T(o),this._$AH=r}}_$AC(t){let i=$t.get(t.strings);return i===void 0&&$t.set(t.strings,i=new se(t)),i}k(t){He(this._$AH)||(this._$AH=[],this._$AR());let i=this._$AH,n,s=0;for(let r of t)s===i.length?i.push(n=new e(this.O(ie()),this.O(ie()),this,this.options)):n=i[s],n._$AI(r),s++;s<i.length&&(this._$AR(n&&n._$AB.nextSibling,s),i.length=s)}_$AR(t=this._$AA.nextSibling,i){for(this._$AP?.(!1,!0,i);t!==this._$AB;){let n=mt(t).nextSibling;mt(t).remove(),t=n}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},L=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,i,n,s,r){this.type=1,this._$AH=c,this._$AN=void 0,this.element=t,this.name=i,this._$AM=s,this.options=r,n.length>2||n[0]!==""||n[1]!==""?(this._$AH=Array(n.length-1).fill(new String),this.strings=n):this._$AH=c}_$AI(t,i=this,n,s){let r=this.strings,o=!1;if(r===void 0)t=H(this,t,i,0),o=!ne(t)||t!==this._$AH&&t!==b,o&&(this._$AH=t);else{let a=t,l,u;for(t=r[0],l=0;l<r.length-1;l++)u=H(this,a[n+l],i,l),u===b&&(u=this._$AH[l]),o||=!ne(u)||u!==this._$AH[l],u===c?t=c:t!==c&&(t+=(u??"")+r[l+1]),this._$AH[l]=u}o&&!s&&this.j(t)}j(t){t===c?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},ve=class extends L{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===c?void 0:t}},ye=class extends L{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==c)}},$e=class extends L{constructor(t,i,n,s,r){super(t,i,n,s,r),this.type=5}_$AI(t,i=this){if((t=H(this,t,i,0)??c)===b)return;let n=this._$AH,s=t===c&&n!==c||t.capture!==n.capture||t.once!==n.once||t.passive!==n.passive,r=t!==c&&(n===c||s);s&&this.element.removeEventListener(this.name,this,n),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},we=class{constructor(t,i,n){this.element=t,this.type=6,this._$AN=void 0,this._$AM=i,this.options=n}get _$AU(){return this._$AM._$AU}_$AI(t){H(this,t)}},Et={M:Ie,P:C,A:Oe,C:1,L:St,R:be,D:wt,V:H,I:V,H:L,N:ye,U:$e,B:ve,F:we},ii=Ne.litHtmlPolyfillSupport;ii?.(se,V),(Ne.litHtmlVersions??=[]).push("3.3.3");var At=(e,t,i)=>{let n=i?.renderBefore??t,s=n._$litPart$;if(s===void 0){let r=i?.renderBefore??null;n._$litPart$=s=new V(t.insertBefore(ie(),r),r,void 0,i??{})}return s._$AI(e),s};var qe=globalThis,x=class extends A{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let i=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=At(i,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return b}};x._$litElement$=!0,x.finalized=!0,qe.litElementHydrateSupport?.({LitElement:x});var ni=qe.litElementPolyfillSupport;ni?.({LitElement:x});(qe.litElementVersions??=[]).push("4.2.2");var Ct=Z`
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
`;var P={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},xe=e=>(...t)=>({_$litDirective$:e,values:t}),J=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,i,n){this._$Ct=t,this._$AM=i,this._$Ci=n}_$AS(t,i){return this.update(t,i)}update(t,i){return this.render(...i)}};var{I:si}=Et,Pt=e=>e;var Tt=e=>e.strings===void 0,Mt=()=>document.createComment(""),W=(e,t,i)=>{let n=e._$AA.parentNode,s=t===void 0?e._$AB:t._$AA;if(i===void 0){let r=n.insertBefore(Mt(),s),o=n.insertBefore(Mt(),s);i=new si(r,o,e,e.options)}else{let r=i._$AB.nextSibling,o=i._$AM,a=o!==e;if(a){let l;i._$AQ?.(e),i._$AM=e,i._$AP!==void 0&&(l=e._$AU)!==o._$AU&&i._$AP(l)}if(r!==s||a){let l=i._$AA;for(;l!==r;){let u=Pt(l).nextSibling;Pt(n).insertBefore(l,s),l=u}}}return i},U=(e,t,i=e)=>(e._$AI(t,i),e),ri={},ke=(e,t=ri)=>e._$AH=t,Rt=e=>e._$AH,Se=e=>{e._$AR(),e._$AA.remove()};var K=xe(class extends J{constructor(e){if(super(e),e.type!==P.PROPERTY&&e.type!==P.ATTRIBUTE&&e.type!==P.BOOLEAN_ATTRIBUTE)throw Error("The `live` directive is not allowed on child or event bindings");if(!Tt(e))throw Error("`live` bindings can only contain a single expression")}render(e){return e}update(e,[t]){if(t===b||t===c)return t;let i=e.element,n=e.name;if(e.type===P.PROPERTY){if(t===i[n])return b}else if(e.type===P.BOOLEAN_ATTRIBUTE){if(!!t===i.hasAttribute(n))return b}else if(e.type===P.ATTRIBUTE&&i.getAttribute(n)===t+"")return b;return ke(e),t}});var Dt=(e,t,i)=>{let n=new Map;for(let s=t;s<=i;s++)n.set(e[s],s);return n},Fe=xe(class extends J{constructor(e){if(super(e),e.type!==P.CHILD)throw Error("repeat() can only be used in text expressions")}dt(e,t,i){let n;i===void 0?i=t:t!==void 0&&(n=t);let s=[],r=[],o=0;for(let a of e)s[o]=n?n(a,o):o,r[o]=i(a,o),o++;return{values:r,keys:s}}render(e,t,i){return this.dt(e,t,i).values}update(e,[t,i,n]){let s=Rt(e),{values:r,keys:o}=this.dt(t,i,n);if(!Array.isArray(s))return this.ut=o,r;let a=this.ut??=[],l=[],u,f,h=0,g=s.length-1,m=0,_=r.length-1;for(;h<=g&&m<=_;)if(s[h]===null)h++;else if(s[g]===null)g--;else if(a[h]===o[m])l[m]=U(s[h],r[m]),h++,m++;else if(a[g]===o[_])l[_]=U(s[g],r[_]),g--,_--;else if(a[h]===o[_])l[_]=U(s[h],r[_]),W(e,l[_+1],s[h]),h++,_--;else if(a[g]===o[m])l[m]=U(s[g],r[m]),W(e,s[h],s[g]),g--,m++;else if(u===void 0&&(u=Dt(o,m,_),f=Dt(a,h,g)),u.has(a[h]))if(u.has(a[g])){let k=f.get(o[m]),Ae=k!==void 0?s[k]:null;if(Ae===null){let Je=W(e,s[h]);U(Je,r[m]),l[m]=Je}else l[m]=U(Ae,r[m]),W(e,s[h],Ae),s[k]=null;m++}else Se(s[g]),g--;else Se(s[h]),h++;for(;m<=_;){let k=W(e,l[_+1]);U(k,r[m]),l[m++]=k}for(;h<=g;){let k=s[h++];k!==null&&Se(k)}return this.ut=o,ke(e,l),b}});function Ut(e,t,i,n){let s=e.mode==="Multi"&&e.working&&w(e.working)?[]:Ge(t),r=e.fieldFor(1),o=t.find(a=>a.draft_id===e.selected)??t[0];return d`<section class="row">
      <div class="row-title">
        <span>${i}</span>${n!==void 0?d`<small>${e.t("starts",{date:n??e.t("unknown")})}</small>`:c}
      </div>
      <div
        class="timeline"
        aria-label=${e.t("timeline_label",{label:i})}
      >
        ${s.map(a=>d`<div
              class="segment ${a.carry?"carry":""}"
              style=${`left:${a.start/864}%;width:${(a.end-a.start)/864}%;${nt(a.point.target_native,r?.unit,e._config?.temperature_colors)}`}
              title=${`${a.carry?e.t("carry"):""}${$(a.start)}\u2013${$(a.end===86400?0:a.end)} \xB7 ${e.format(a.point.target_native,r)}`}
            >
              <span
                >${a.end-a.start>3600?e.format(a.point.target_native,r):""}</span
              >
            </div>`)}
        ${s.length===0?d`<div class="empty muted">
              ${e.t("unknown_boundaries")}
            </div>`:c}
        ${Fe(t,a=>a.draft_id,a=>a.seconds===null?c:d`<button
                  class="handle"
                  style=${`left:${a.seconds/864}%`}
                  data-point-id=${a.draft_id}
                  aria-label=${e.t("boundary_label",{label:e.mode==="Multi"?e.t("point",{number:t.indexOf(a)+1}):i+" "+(t.indexOf(a)%2===0?e.t("day"):e.t("night")),time:$(a.seconds)})}
                  aria-pressed=${o?.draft_id===a.draft_id}
                  title=${$(a.seconds)}
                  @click=${()=>e.selected=a.draft_id}
                  @pointerdown=${l=>e.pointerDown(l,a)}
                  @pointermove=${e.pointerMove}
                  @pointerup=${e.pointerUp}
                  @pointercancel=${e.pointerUp}
                  @lostpointercapture=${e.pointerUp}
                  @keydown=${l=>e.key(l,a)}
                ></button>`)}
      </div>
      <div class="axis">
        <span>00</span><span>04</span><span>08</span><span>12</span
        ><span>16</span><span>20</span><span>24</span>
      </div>
      ${e.draft&&o?d`<label class="field slider">
            ${e.mode==="Multi"?e.t("point",{number:t.indexOf(o)+1}):t.indexOf(o)%2===0?e.t("day"):e.t("night")}
            ${e.t("point_target_summary")} · ${$(o.seconds)} ·
            ${e.format(o.target_native,e.fieldFor(1))}<input
              aria-label=${e.t("selected_target_label",{label:i})}
              type="range"
              min=${v(0,e.fieldFor(1)?.unit??null,e.fahrenheit)}
              max=${v(100,e.fieldFor(1)?.unit??null,e.fahrenheit)}
              step="0.5"
              .value=${String(v(o.target_native??0,e.fieldFor(1)?.unit??null,e.fahrenheit))}
              ?disabled=${e.saving||!e.allScheduleWritable}
              @input=${a=>e.updatePoint(o.draft_id,{target_native:X(Number(a.target.value),e.fieldFor(1)?.unit??null,e.fahrenheit)})}
          /></label>`:c}
      <details class="slot-table">
        <summary>${e.t("slot_table",{label:i})}</summary>
        <div class="point-list">
          ${Fe(t,a=>a.draft_id,(a,l)=>{let u=e.mode==="Multi"?e.t("point",{number:e.working.points.indexOf(a)+1}):l%2===0?e.t("day"):e.t("night");return d`<div
                class="point ${e.selected===a.draft_id?"selected":""}"
              >
                <button @click=${()=>e.selected=a.draft_id}>
                  ${u}</button
                >${e.draft?d`<input
                        aria-label=${e.t("point_start",{label:i,point:u})}
                        type="time"
                        step="1"
                        .value=${K($(a.seconds))}
                        ?disabled=${e.saving||!e.allScheduleWritable}
                        @input=${f=>e.updatePoint(a.draft_id,{seconds:Xe(f.target.value)},!1)}
                        @change=${()=>e.updatePoint(a.draft_id,{})}
                      /><input
                        aria-label=${e.t("point_target",{label:i,point:u,unit:e.unit(r)})}
                        type="number"
                        min=${v(0,r?.unit??null,e.fahrenheit)}
                        max=${v(100,r?.unit??null,e.fahrenheit)}
                        step="any"
                        .value=${K(a.target_native===null?"":String(v(a.target_native,r?.unit??null,e.fahrenheit)))}
                        ?disabled=${e.saving||!e.allScheduleWritable}
                        @input=${f=>{let h=f.target.value;e.updatePoint(a.draft_id,{target_native:h===""?null:X(Number(h),r?.unit??null,e.fahrenheit)})}}
                      />`:d`<span>${$(a.seconds)||e.t("unknown")}</span
                      ><span>${e.format(a.target_native,r)}</span>`}
              </div>`})}
        </div>
      </details>
    </section>`}function jt(e){if(!e.draft)return[];let t=e.draft,i=Object.entries(R(t)).map(([n,s])=>{let r=t.base.fields.find(a=>a.key===n),o=a=>typeof a=="number"?e.format(a,r):a??e.t("unknown");return`${r.label}: ${o(r.value)} \u2192 ${o(s)}`});if(["Multi","Day Night","Seasonal"].includes(t.mode)){let n=t.mode==="Day Night"?2:8;for(let s=1;s<=n;s++){let r=t.points[s-1];for(let o of["time","setpoint"]){let a=t.base.fields.find(f=>f.key===`${t.base.channel}_period_${s}_${o}`);if(!a)continue;let l=r?o==="time"?r.seconds:r.target_native:0;if(l===a.value)continue;let u=f=>o==="time"?$(f)||e.t("unknown"):e.format(f,a);i.push(`${a.label}: ${u(a.value)} \u2192 ${u(l)}${r?"":e.t("clear_tail")}`)}}}return i}function Nt(e,t){let i=e.draft&&Object.hasOwn(e.draft.values,t.key)?e.draft.values[t.key]:t.value,n=!!e.draft&&S(e.draft),s=e.saving||!t.writable||t.kind==="enum"&&n&&!Object.hasOwn(R(e.draft),t.key);return d`<label class="field"
      ><span>${t.label}${e.unit(t)?` (${e.unit(t)})`:""}</span>${e.draft?t.kind==="enum"?d`<select
              aria-label=${t.label}
              .value=${K(String(i??""))}
              ?disabled=${s}
              @change=${r=>e.setField(t,r)}
            >
              <option value="" disabled>${e.t("unknown")}</option>
              ${t.options.map(r=>d`<option value=${r} ?selected=${r===i}>
                    ${e.optionLabel(r)}
                  </option>`)}
            </select>`:d`<input
              aria-label=${t.label}
              type=${t.kind==="date"?"text":"number"}
              placeholder=${t.kind==="date"?"DD/MM":""}
              maxlength=${t.kind==="date"?5:c}
              min=${v(t.minimum,t.unit,e.fahrenheit)}
              max=${v(t.maximum,t.unit,e.fahrenheit)}
              step=${t.step}
              .value=${K(i===null?"":String(typeof i=="number"?v(i,t.unit,e.fahrenheit):i))}
              ?disabled=${s}
              @input=${r=>e.setField(t,r)}
            />`:d`<strong
            >${typeof i=="number"?e.format(i,t):i??e.t("unknown")}</strong
          >`}${t.writable?c:d`<small class="muted">${t.reason}</small>`}</label
    >`}function It(e,t){return d`
      ${e.submissionUnknown?d`<div class="alert error">
            ${e.t("save_unresolved")}
            <button @click=${e.recoverRequest}>${e.t("check_request")}</button>
          </div>`:c}${e.notice?d`<div role="status" class="alert">${e.notice}</div>`:c}
      ${e.draft?d`${t?d`<div role="alert" class="alert error">${t}</div>`:c}${e.conflict&&!e.saving?d`<div class="alert error">
                  ${e.t("settings_changed")}
                  <button @click=${e.rebase}>
                    ${e.t("refresh_review")}
                  </button>
                </div>`:c}
            <p class="muted">
              ${e.t("write_warning")}
            </p>
            <details class="review" open>
              <summary>
                ${e.t("changed_fields",{count:e.reviewChanges().length})}
              </summary>
              ${e.reviewChanges().map(i=>d`<div>${i}</div>`)}
            </details>
            <div class="actions">
              ${e.saving?d`<button @click=${e.stop}>
                    ${e.t("stop_remaining")}
                  </button>`:d`<button @click=${e.cancel}>${e.t("cancel")}</button
                    ><button
                      class="primary"
                      ?disabled=${!S(e.draft)||!!t||e.conflict||!e.canEdit||e.draft.repair||e.submissionUnknown}
                      @click=${e.save}
                    >
                      ${e.t("save_changes")}
                    </button>`}
            </div>`:c}
      ${e.job?d`<section aria-live="polite" class="alert">
            <strong
              >${e.t("job_progress",{status:e.job.status,confirmed:e.job.confirmed,total:e.job.total})}</strong
            ><progress
              max=${Math.max(1,e.job.total)}
              value=${e.job.confirmed}
            ></progress
            >${e.job.reason?d`<p>${e.job.reason_message??e.job.reason.replaceAll("_"," ")}</p>`:c}
            <details>
              <summary>${e.t("change_results")}</summary>
              ${e.job.fields.map(i=>d`<div class="status">${i.label}: ${i.status}</div>`)}
            </details>
          </section>`:c}
`}function Ot(e){let t=e.view,i=e.working,n=e.draft?ce(e.draft):null,s=i?.points??[],r=s.find(a=>a.draft_id===e.selected),o=e.localName==="microclimate-controller-card"?"controller":"channel";return t&&t.kind!==o?d`<ha-card
        >${e.t("wrong_device",{kind:o})}</ha-card
      >`:d`<ha-card
      ><header>
        <div>
          <h2>${e._config?.title??t?.name??"Microclimate"}</h2>
          <div class="muted">
            ${t?.model??e.t("connecting")}${e.draft?e.t("draft_preview"):""}${t&&!t.online?e.t("offline"):""}
          </div>
        </div>
        ${!e.draft&&e.canEdit?d`<button class="primary" @click=${e.edit}>${e.t("edit")}</button>`:c}
      </header>
      ${e.pendingConfig?d`<section
            role="dialog"
            aria-label=${e.t("unsaved")}
            class="alert"
          >
            <p>${e.t("unsaved_prompt")}</p>
            <div class="actions">
              <button @click=${()=>e.navigate("stay")}>${e.t("stay")}</button
              ><button
                ?disabled=${e.saving||e.submissionUnknown}
                @click=${()=>e.navigate("discard")}
              >
                ${e.t("discard_draft")}</button
              ><button
                ?disabled=${!!n||e.conflict||e.saving||!e.canEdit}
                @click=${()=>e.navigate("save")}
              >
                ${e.t("save_then_switch")}
              </button>
            </div>
          </section>`:c}${e.error?d`<div role="alert" class="alert error">${e.error}</div>`:c}${t?.schema_version!==1&&t?d`<div class="alert error">
            ${e.t("mismatch")}
          </div>`:c}
      ${t&&i?d`${t.kind==="controller"?d`<h3>${e.t("season_dates")}</h3>
                <p class="muted">
                  ${e.t("dates_help")}
                </p>
                <div class="form">
                  ${t.fields.filter(a=>a.kind==="date").map(a=>e.setting(a))}
                </div>`:d` <div class="badges">
                  ${t.fields.filter(a=>a.kind==="enum").map(a=>d`<span class="badge"
                          >${a.value??e.t("unknown")}</span
                        >`)}
                </div>
                ${e._config?.show_observations!==!1&&t.observations.length?d`<div class="observations">
                      ${t.observations.map(a=>d`<div class="observation">
                            <span class="muted">${a.name}</span
                            ><strong>${a.value} ${a.unit??""}</strong>
                          </div>`)}
                    </div>`:c}
                <h3>${e.t("schedule_heading")}</h3>
                <p class="muted">${e.t("controller_time")}</p>
                ${e.mode==="Seasonal"?d`<p class="muted">
                        ${e.t("seasonal_dates_help")}
                      </p>
                      ${[0,1,2,3].map(a=>e.row(s.slice(a*2,a*2+2),e.t("season",{number:a+1}),t.fields.find(l=>l.key===`season_${a+1}_start_pin`)?.value??null))}`:["Multi","Day Night"].includes(e.mode)?e.row(s,e.mode==="Multi"?e.t("multi"):e.t("day_and_night")):d`<div class="alert">
                        ${e.mode==="Constant"?e.t("constant_unmapped"):e.mode==="Periodic"?e.t("periodic_unmapped"):e.t("timing_unknown")}
                      </div>`}
                ${e.draft&&e.mode==="Multi"?d`${i.repair?d`<div class="alert error">
                            ${e.t("repair_needed")}
                            <button @click=${e.repair}>
                              ${e.t("point_rebuild")}
                            </button>
                          </div>`:c}
                      <div class="actions">
                        <button
                          ?disabled=${s.length>=8||e.saving||!e.allScheduleWritable}
                          @click=${e.add}
                        >
                          ${e.t("add_point")}</button
                        ><button
                          ?disabled=${s.length<=2||!r||e.saving||!e.allScheduleWritable}
                          @click=${()=>r&&e.removePoint(r.draft_id)}
                        >
                          ${e.t("remove_selected")}
                        </button>
                      </div>
                      <p class="muted">
                        ${e.t("multi_help")}
                      </p>`:c}
                ${!e.draft&&i.repair?d`<div class="alert error">
                      ${w(i)} ${e.t("repair_observation")}
                    </div>`:c}
                ${["Day Night","Multi","Seasonal"].includes(e.mode)?d`<div class="actions">
                      <button
                        ?disabled=${!!w(i)}
                        @click=${e.downloadPreset}
                      >${e.t("download_preset")}</button>
                      ${e.draft?d`<button
                              ?disabled=${e.saving||!e.canEdit||!e.allScheduleWritable}
                              @click=${()=>e.renderRoot.querySelector("#preset-file")?.click()}
                            >${e.t("import_preset")}</button>
                            <input
                              id="preset-file"
                              type="file"
                              accept=".json,application/json"
                              hidden
                              @change=${e.loadPreset}
                            />`:c}
                    </div>
                    <p class="muted">${e.t("preset_help")}</p>`:c}
                <details class="settings" ?open=${!!e.draft}>
                  <summary>${e.t("channel_settings")}</summary>
                  <p class="muted">
                    ${e.t("settings_help")}
                  </p>
                  <div class="form">
                    ${t.fields.filter(a=>!a.index&&!a.shared).map(a=>e.setting(a))}
                  </div>
                </details>`}`:c}
      ${It(e,n)}
    </ha-card>`}var re=class extends x{constructor(){super(...arguments);this.session=new ue(()=>this.requestUpdate(),i=>{this.selected=i});this.selected="";this.unload=i=>{this.draft&&S(this.draft)&&(i.preventDefault(),i.returnValue="")}}static{this.properties={selected:{state:!0}}}static{this.styles=Ct}t(i,n={}){return q(i,this.hass?.language,n)}optionLabel(i){let n={fixed:"fixed",heating:"heating",cooling:"cooling",pulse:"pulse",dimming:"dimming",Constant:"constant","Day Night":"day_night_option",Multi:"multi",Periodic:"periodic",Seasonal:"seasonal"};return n[i]?this.t(n[i]):i}get _config(){return this.session.config}get _hass(){return this.session.hass}get view(){return this.session.view}get draft(){return this.session.draft}set draft(i){this.session.draft=i}get job(){return this.session.job}get error(){return this.session.error}set error(i){this.session.error=i}get notice(){return this.session.notice}set notice(i){this.session.notice=i}get saving(){return this.session.saving}get submissionUnknown(){return this.session.submissionUnknown}get pendingConfig(){return this.session.pendingConfig}set pendingConfig(i){this.session.pendingConfig=i}set hass(i){this.session.setHass(i)}get hass(){return this.session.hass}setConfig(i){pe(i.temperature_colors),this.session.setConfig(i)}connectedCallback(){super.connectedCallback(),window.addEventListener("beforeunload",this.unload),this.session.connect()}disconnectedCallback(){super.disconnectedCallback(),window.removeEventListener("beforeunload",this.unload),this.drag=void 0,this.session.disconnect()}static getConfigElement(){return document.createElement("microclimate-card-editor")}static getStubConfig(){return{device_id:""}}getCardSize(){return this.view?.kind==="controller"?5:this.mode==="Seasonal"?15:8}getGridOptions(){return{columns:12,min_columns:6}}get fahrenheit(){return this._hass?.config?.unit_system.temperature==="\xB0F"}get mode(){return this.draft?.mode??String(this.view?.fields.find(i=>i.key===`${this.view?.channel}_timing_type`)?.value??"")}get working(){if(this.draft)return this.draft;if(this.view)return this.observedDraft?.base!==this.view&&(this.observedDraft=z(this.view)),this.observedDraft}get conflict(){return this.session.conflict}get canEdit(){return this.session.canEdit}unit(i){return i?.unit==="\xB0C"&&this.fahrenheit?"\xB0F":i?.unit??""}format(i,n){return i===null?this.t("unknown"):`${Number(v(i,n?.unit??null,this.fahrenheit).toFixed(3))} ${this.unit(n)}`}fieldFor(i,n="setpoint"){return this.view?.fields.find(s=>s.key===`${this.view?.channel}_period_${i}_${n}`)}get allScheduleWritable(){let i=this.mode==="Day Night"?2:8;return Array.from({length:i},(n,s)=>["time","setpoint"].every(r=>this.fieldFor(s+1,r)?.writable)).every(Boolean)}edit(){this.session.edit()}navigate(i){this.session.navigate(i)}cancel(){this.session.cancel()}updatePoint(i,n,s=!0){if(!this.draft||this.saving||!this.allScheduleWritable)return;let r=this.draft.points.map(o=>o.draft_id===i?{...o,...n}:o);s&&this.mode==="Multi"&&!this.draft.repair&&r.sort((o,a)=>(o.seconds??1/0)-(a.seconds??1/0)),this.draft={...this.draft,points:r}}add(){if(!this.draft||this.draft.points.length>=8||!this.allScheduleWritable)return;let i=new Set(this.draft.points.map(r=>r.seconds)),n=43200;for(;i.has(n)&&n<86399;)n++;if(i.has(n))for(n=1;i.has(n);)n++;let s={draft_id:T(),seconds:n,target_native:20};this.draft={...this.draft,points:[...this.draft.points,s].sort((r,o)=>(r.seconds??1/0)-(o.seconds??1/0))},this.selected=s.draft_id,this.focusPoint(s.draft_id)}removePoint(i){!this.draft||this.draft.points.length<=2||!this.allScheduleWritable||(this.draft={...this.draft,points:this.draft.points.filter(n=>n.draft_id!==i)},this.selected=this.draft.points[0]?.draft_id??"",this.selected&&this.focusPoint(this.selected))}async focusPoint(i){await this.updateComplete,Array.from(this.renderRoot.querySelectorAll(".handle")).find(s=>s.dataset.pointId===i)?.focus()}repair(){this.draft&&(this.draft={...this.draft,repair:!1,points:this.draft.points.filter(i=>!(i.seconds===0&&i.target_native===0)).sort((i,n)=>(i.seconds??1/0)-(n.seconds??1/0))},this.notice=this.t("repair_review"))}downloadPreset(){if(!(!this.working||!this.view?.channel))try{let i=JSON.stringify(at(this.working),null,2),n=URL.createObjectURL(new Blob([i],{type:"application/json"})),s=document.createElement("a");s.href=n,s.download=`microclimate-${this.mode.toLowerCase().replaceAll(" ","-")}-schedule.json`,s.click(),setTimeout(()=>URL.revokeObjectURL(n),0),this.notice=this.t("preset_downloaded")}catch(i){this.error=i.message}}async loadPreset(i){let n=i.target,s=n.files?.[0];if(n.value="",!(!s||!this.draft||this.saving||!this.canEdit||!this.allScheduleWritable))try{if(s.size>rt)throw new Error(this.t("preset_too_large"));let r=JSON.parse(await s.text());this.draft=lt(this.draft,r),this.selected=this.draft.points[0]?.draft_id??"",this.notice=this.t("preset_loaded"),this.error=""}catch(r){this.error=r instanceof SyntaxError?this.t("preset_json_invalid"):r.message}}setField(i,n){if(!this.draft||this.saving)return;let s=n.target,r=s.value;["number","ramp","setpoint"].includes(i.kind)&&(r=s.value===""?null:X(Number(s.value),i.unit,this.fahrenheit)),this.draft={...this.draft,values:{...this.draft.values,[i.key]:r}}}save(){return this.session.save()}recoverRequest(){return this.session.recoverRequest()}stop(){return this.session.stop()}rebase(){this.session.rebase()}pointerDown(i,n){if(!this.draft||this.saving||!this.allScheduleWritable)return;let s=i.currentTarget;this.selected=n.draft_id,this.drag={id:n.draft_id,x:i.clientX,pointer:i.pointerId,start:n.seconds??0,el:s,moved:!1},s.setPointerCapture(i.pointerId)}pointerMove(i){let n=this.drag;if(!n||n.pointer!==i.pointerId||Math.abs(i.clientX-n.x)<5&&!n.moved)return;n.moved=!0,i.preventDefault();let s=n.el.parentElement.getBoundingClientRect(),r=Math.min(86399,Math.max(0,Math.round((i.clientX-s.left)/s.width*86400/300)*300));this.updatePoint(n.id,{seconds:r})}pointerUp(){this.drag=void 0}key(i,n){!this.draft||this.saving||(i.key==="ArrowLeft"||i.key==="ArrowRight"?(i.preventDefault(),this.updatePoint(n.draft_id,{seconds:Math.max(0,Math.min(86399,(n.seconds??0)+(i.key==="ArrowRight"?1:-1)*(i.shiftKey?300:60)))})):i.key==="Delete"&&this.mode==="Multi"&&(i.preventDefault(),this.removePoint(n.draft_id)))}row(i,n,s){return Ut(this,i,n,s)}reviewChanges(){return jt(this)}setting(i){return Nt(this,i)}render(){return Ot(this)}};var Ee=class extends x{constructor(){super(...arguments);this.devices=[];this.error="";this.colorError="";this.epoch=0}static{this.properties={config:{state:!0},devices:{state:!0},error:{state:!0},colorError:{state:!0}}}static{this.styles=Z`
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
  `}t(i,n={}){return q(i,this._hass?.language,n)}set hass(i){if(this._hass===i)return;this._hass=i;let n=++this.epoch;this.devices=[],i.callWS({type:M+"list"}).then(s=>{if(n!==this.epoch)return;let r=et(s);if(!r.ok){this.error=this.t("device_list_invalid");return}this.devices=r.value,this.error=""}).catch(()=>{n===this.epoch&&(this.error=this.t("device_list_unavailable"))})}setConfig(i){this.config={...i}}change(i,n){this.config={...this.config,[i]:n},this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:this.config},bubbles:!0,composed:!0}))}colors(){return this.config?.temperature_colors??Te}changeColor(i,n,s){let r=this.colors().map((o,a)=>a===i?{...o,[n]:n==="temperature"?s.trim()?Number(s):NaN:s}:{...o});try{pe(r),this.colorError="",this.change("temperature_colors",r)}catch(o){this.colorError=o.message}}render(){let i=this.config?.type.includes("controller")?"controller":"channel";return d`<p>
        ${this.error||this.t("editor_intro")}
      </p>
      <label
        >${this.t("editor_device")}<select
          aria-label=${this.t("editor_device")}
          .value=${this.config?.device_id??""}
          @change=${n=>this.change("device_id",n.target.value)}
        >
          <option value="">${this.t("editor_select_device")}</option>
          ${this.devices.filter(n=>n.kind===i).map(n=>d`<option
                  value=${n.device_id}
                  ?selected=${n.device_id===this.config?.device_id}
                >
                  ${n.name}
                </option>`)}
        </select></label
      ><label
        >${this.t("editor_title")}<input
          .value=${this.config?.title??""}
          @input=${n=>this.change("title",n.target.value)} /></label
      ><label
        ><input
          type="checkbox"
          .checked=${!!this.config?.read_only}
          @change=${n=>this.change("read_only",n.target.checked)}
        />${this.t("editor_read_only")}</label
      >${i==="channel"?d`<details>
            <summary>${this.t("editor_colors")}</summary>
            <p>
              ${this.t("editor_colors_help")}
            </p>
            ${this.colorError?d`<p role="alert">${this.colorError}</p>`:c}
            ${this.colors().map((n,s)=>d`<fieldset>
                  <legend>${this.t("editor_color_number",{number:s+1})}</legend>
                  <label
                    >${this.t("editor_lower")}<input
                      type="number"
                      min="0"
                      max="100"
                      step="any"
                      aria-label=${this.t("editor_color_lower",{number:s+1})}
                      .value=${String(n.temperature)}
                      @change=${r=>this.changeColor(s,"temperature",r.target.value)}
                  /></label>
                  <label
                    >${this.t("editor_color")}<input
                      type="color"
                      aria-label=${this.t("editor_color_value",{number:s+1})}
                      .value=${n.color}
                      @input=${r=>this.changeColor(s,"color",r.target.value)}
                  /></label>
                  <button
                    ?disabled=${this.colors().length===1}
                    @click=${()=>{this.colorError="",this.change("temperature_colors",this.colors().filter((r,o)=>o!==s))}}
                  >
                    ${this.t("editor_remove_color",{number:s+1})}
                  </button>
                </fieldset>`)}
            <button
              ?disabled=${this.colors().length>=101}
              @click=${()=>{let n=new Set(this.colors().map(r=>r.temperature)),s=0;for(;n.has(s);)s++;this.change("temperature_colors",[...this.colors(),{temperature:s,color:"#b52222"}])}}
            >
              ${this.t("editor_add_color")}
            </button>
            <button
              @click=${()=>{this.colorError="",this.change("temperature_colors",void 0)}}
            >
              ${this.t("editor_reset_color")}
            </button>
          </details>`:c}`}};var ze=class extends re{},Be=class extends re{};customElements.define("microclimate-channel-card",ze);customElements.define("microclimate-controller-card",Be);customElements.define("microclimate-card-editor",Ee);var Ve=window;Ve.customCards=Ve.customCards??[];Ve.customCards.push({type:"microclimate-channel-card",name:"Microclimate channel",description:"Daily, Multi and seasonal schedule with explicit Save/Cancel."},{type:"microclimate-controller-card",name:"Microclimate controller",description:"Shared season start dates."});
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
