import{aH as F,V as M,aY as U,a2 as z,ad as u,ae as L,a4 as B,W as E,aU as I,s as V,aa as Y,O as N,T as P,aO as W,ay as A,al as q,M as R}from"./element-plus-41a825d8.js";import{_ as G,a as J}from"./index-cb752fdf.js";import{r as m,j as K,e as Q,a8 as f,m as O,q as X,t,H as s,B as l,F as p,A as Z,E as ee,u as r}from"./vue-vendor-6e799941.js";import"./utils-531ce3b4.js";const te={class:"review-view"},se={class:"review-header"},ae={class:"header-left"},oe={class:"header-right"},le={class:"review-content"},ie={class:"metrics-cards"},ne={class:"metric-card"},de={class:"metric-icon blue"},re={class:"metric-info"},ce={class:"metric-value"},ue={class:"metric-card"},pe={class:"metric-icon green"},ve={class:"metric-info"},_e={class:"metric-value"},me={class:"metric-card"},fe={class:"metric-icon purple"},ge={class:"metric-info"},xe={class:"metric-value"},ye={class:"metric-card"},he={class:"metric-icon orange"},we={class:"metric-info"},be={class:"metric-value"},ke={class:"metric-card"},$e={class:"metric-icon cyan"},Re={class:"metric-info"},De={class:"metric-value"},Ce={class:"metric-card"},Ve={class:"metric-info"},Oe={class:"metric-card"},Te={class:"metric-icon red"},He={class:"metric-info"},Se={class:"metric-value"},je={class:"metric-card"},Fe={class:"metric-icon gray"},Me={class:"metric-info"},Ue={class:"metric-value"},ze={class:"charts-section"},Le={class:"chart-card"},Be={class:"chart-card"},Ee={class:"weekly-report-section"},Ie={class:"section-header"},Ye={class:"report-editor"},Ne={class:"report-actions"},Pe={__name:"ReviewView",setup(We){const g=m("week"),x=m([]),h=m(null),w=m(null),a=K({total:0,completed:0,completionRate:0,plannedHours:0,actualHours:0,deviation:0,overdueCount:0,avgOverdueDays:0}),y=m(""),D=m([{name:"高优先级",hours:12,percentage:30},{name:"开发",hours:20,percentage:50},{name:"沟通",hours:5,percentage:12.5},{name:"文档",hours:3,percentage:7.5}]),b=m({planned:[8,10,12,6,8,10,4],actual:[7,12,10,8,6,14,5],labels:["周一","周二","周三","周四","周五","周六","周日"]}),C=async()=>{try{let i,e;if(g.value==="week"){const n=new Date,_=n.getDay();i=new Date(n.setDate(n.getDate()-_+1)).toISOString().split("T")[0],e=new Date(n.setDate(n.getDate()+6)).toISOString().split("T")[0]}else if(g.value==="month"){const n=new Date;i=new Date(n.getFullYear(),n.getMonth(),1).toISOString().split("T")[0],e=new Date(n.getFullYear(),n.getMonth()+1,0).toISOString().split("T")[0]}else x.value&&(i=x.value[0],e=x.value[1]);const o=await J.personalPlan.getReviewStats({date_from:i,date_to:e});Object.assign(a,{total:o.total||0,completed:o.completed||0,completionRate:o.completionRate||0,plannedHours:o.planned_hours||0,actualHours:o.actual_hours||0,deviation:o.deviation||0,overdueCount:o.overdue_count||0,avgOverdueDays:o.avg_overdue_days||0}),k()}catch(i){console.error("加载复盘数据失败:",i),a.total=15,a.completed=12,a.completionRate=80,a.plannedHours=40,a.actualHours=45,a.deviation=12.5,a.overdueCount=2,a.avgOverdueDays=1.5,k()}},k=()=>{const i=a.completed,e=a.total,o=a.completionRate,n=["完成了后端API开发","完成了前端页面重构","修复了3个线上Bug"],_=["等待产品评审","文档待完善"];y.value=`本周工作总结

一、任务完成情况
本周计划任务 ${e} 项，实际完成 ${i} 项，完成率 ${o}%。

二、已完成工作
${n.map((d,c)=>`${c+1}. ${d}`).join(`
`)}

三、未完成原因
${_.map((d,c)=>`${c+1}. ${d}`).join(`
`)}

四、工时统计
计划工时：${a.plannedHours}小时
实际耗时：${a.actualHours}小时
偏差：${a.deviation>=0?"+":""}${a.deviation}%

五、下周计划
1. 继续推进项目开发
2. 完成剩余功能模块
3. 准备下周评审材料

六、风险与问题
${a.overdueCount>0?`有 ${a.overdueCount} 个任务延期，平均延期 ${a.avgOverdueDays} 天，需要加强进度管理。`:"暂无明显风险。"}
`},T=()=>{navigator.clipboard.writeText(y.value),R.success("已复制到剪贴板")},$=i=>{R.info(`导出${i.toUpperCase()}功能开发中`)},H=()=>{const i=new Blob([y.value],{type:"text/markdown"}),e=URL.createObjectURL(i),o=document.createElement("a");o.href=e,o.download=`周报_${new Date().toISOString().split("T")[0]}.md`,o.click(),URL.revokeObjectURL(e),R.success("导出成功")},S=()=>{if(h.value&&(h.value.innerHTML=`
      <div style="display: flex; align-items: flex-end; justify-content: space-around; height: 200px; padding: 20px;">
        ${b.value.labels.map((i,e)=>`
          <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
            <div style="display: flex; gap: 4px; align-items: flex-end; height: 160px;">
              <div style="width: 24px; background: #409EFF; border-radius: 4px 4px 0 0; height: ${b.value.planned[e]*12}px;"></div>
              <div style="width: 24px; background: #67c23a; border-radius: 4px 4px 0 0; height: ${b.value.actual[e]*12}px;"></div>
            </div>
            <span style="font-size: 12px; color: #909399;">${i}</span>
          </div>
        `).join("")}
      </div>
      <div style="display: flex; justify-content: center; gap: 24px; margin-top: 12px;">
        <div style="display: flex; align-items: center; gap: 6px;">
          <div style="width: 12px; height: 12px; background: #409EFF; border-radius: 2px;"></div>
          <span style="font-size: 12px; color: #606266;">计划工时</span>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
          <div style="width: 12px; height: 12px; background: #67c23a; border-radius: 2px;"></div>
          <span style="font-size: 12px; color: #606266;">实际耗时</span>
        </div>
      </div>
    `),w.value){const i=["#409EFF","#67c23a","#e6a23c","#f56c6c","#909399"];let e=0;w.value.innerHTML=`
      <div style="display: flex; align-items: center; padding: 20px; gap: 40px;">
        <div style="width: 140px; height: 140px; border-radius: 50%; background: conic-gradient(
          ${D.value.map((o,n)=>{const _=e;return e+=o.percentage,`${i[n%i.length]} ${_}% ${e}%`}).join(", ")}
        );"></div>
        <div style="flex: 1; display: flex; flex-direction: column; gap: 8px;">
          ${D.value.map((o,n)=>`
            <div style="display: flex; align-items: center; gap: 8px;">
              <div style="width: 12px; height: 12px; background: ${i[n%i.length]}; border-radius: 2px;"></div>
              <span style="flex: 1; font-size: 13px; color: #606266;">${o.name}</span>
              <span style="font-size: 13px; color: #909399;">${o.hours}小时 (${o.percentage}%)</span>
            </div>
          `).join("")}
        </div>
      </div>
    `}};return Q(()=>{C(),setTimeout(S,100)}),(i,e)=>{const o=f("el-radio-button"),n=f("el-radio-group"),_=f("el-date-picker"),d=f("el-icon"),c=f("el-button"),j=f("el-input");return O(),X("div",te,[t("div",se,[t("div",ae,[s(n,{modelValue:g.value,"onUpdate:modelValue":e[0]||(e[0]=v=>g.value=v),size:"default"},{default:l(()=>[s(o,{value:"week"},{default:l(()=>[...e[6]||(e[6]=[p("本周",-1)])]),_:1}),s(o,{value:"month"},{default:l(()=>[...e[7]||(e[7]=[p("本月",-1)])]),_:1}),s(o,{value:"custom"},{default:l(()=>[...e[8]||(e[8]=[p("自定义",-1)])]),_:1})]),_:1},8,["modelValue"]),g.value==="custom"?(O(),Z(_,{key:0,modelValue:x.value,"onUpdate:modelValue":e[1]||(e[1]=v=>x.value=v),type:"daterange","range-separator":"至","start-placeholder":"开始日期","end-placeholder":"结束日期","value-format":"YYYY-MM-DD",onChange:C},null,8,["modelValue"])):ee("",!0)]),t("div",oe,[s(c,{onClick:e[2]||(e[2]=v=>$("image"))},{default:l(()=>[s(d,null,{default:l(()=>[s(r(F))]),_:1}),e[9]||(e[9]=p(" 导出图片 ",-1))]),_:1}),s(c,{onClick:e[3]||(e[3]=v=>$("csv"))},{default:l(()=>[s(d,null,{default:l(()=>[s(r(M))]),_:1}),e[10]||(e[10]=p(" 导出CSV ",-1))]),_:1}),s(c,{onClick:e[4]||(e[4]=v=>$("pdf")),type:"primary"},{default:l(()=>[s(d,null,{default:l(()=>[s(r(U))]),_:1}),e[11]||(e[11]=p(" 导出PDF ",-1))]),_:1})])]),t("div",le,[t("div",ie,[t("div",ne,[t("div",de,[s(d,null,{default:l(()=>[s(r(z))]),_:1})]),t("div",re,[t("div",ce,u(a.total),1),e[12]||(e[12]=t("div",{class:"metric-label"},"计划任务",-1))])]),t("div",ue,[t("div",pe,[s(d,null,{default:l(()=>[s(r(L))]),_:1})]),t("div",ve,[t("div",_e,u(a.completed),1),e[13]||(e[13]=t("div",{class:"metric-label"},"已完成",-1))])]),t("div",me,[t("div",fe,[s(d,null,{default:l(()=>[s(r(B))]),_:1})]),t("div",ge,[t("div",xe,u(a.completionRate)+"%",1),e[14]||(e[14]=t("div",{class:"metric-label"},"完成率",-1))])]),t("div",ye,[t("div",he,[s(d,null,{default:l(()=>[s(r(E))]),_:1})]),t("div",we,[t("div",be,u(a.plannedHours),1),e[15]||(e[15]=t("div",{class:"metric-label"},"总计划工时",-1))])]),t("div",ke,[t("div",$e,[s(d,null,{default:l(()=>[s(r(I))]),_:1})]),t("div",Re,[t("div",De,u(a.actualHours),1),e[16]||(e[16]=t("div",{class:"metric-label"},"实际耗时",-1))])]),t("div",Ce,[t("div",{class:V(["metric-icon",a.deviation>=0?"green":"red"])},[s(d,null,{default:l(()=>[s(r(Y))]),_:1})],2),t("div",Ve,[t("div",{class:V(["metric-value",a.deviation>=0?"positive":"negative"])},u(a.deviation>=0?"+":"")+u(a.deviation)+"% ",3),e[17]||(e[17]=t("div",{class:"metric-label"},"偏差",-1))])]),t("div",Oe,[t("div",Te,[s(d,null,{default:l(()=>[s(r(N))]),_:1})]),t("div",He,[t("div",Se,u(a.overdueCount),1),e[18]||(e[18]=t("div",{class:"metric-label"},"延期任务",-1))])]),t("div",je,[t("div",Fe,[s(d,null,{default:l(()=>[s(r(P))]),_:1})]),t("div",Me,[t("div",Ue,u(a.avgOverdueDays),1),e[19]||(e[19]=t("div",{class:"metric-label"},"平均延期天数",-1))])])]),t("div",ze,[t("div",Le,[e[20]||(e[20]=t("h3",null,"计划vs实际工时对比",-1)),t("div",{class:"chart-container",ref_key:"barChartRef",ref:h},null,512)]),t("div",Be,[e[21]||(e[21]=t("h3",null,"标签耗时占比",-1)),t("div",{class:"chart-container",ref_key:"pieChartRef",ref:w},null,512)])]),t("div",Ee,[t("div",Ie,[e[23]||(e[23]=t("h3",null,"自动生成周报",-1)),s(c,{size:"small",onClick:T},{default:l(()=>[s(d,null,{default:l(()=>[s(r(W))]),_:1}),e[22]||(e[22]=p(" 一键复制 ",-1))]),_:1})]),t("div",Ye,[s(j,{modelValue:y.value,"onUpdate:modelValue":e[5]||(e[5]=v=>y.value=v),type:"textarea",rows:10,placeholder:"周报内容..."},null,8,["modelValue"])]),t("div",Ne,[s(c,{onClick:k},{default:l(()=>[s(d,null,{default:l(()=>[s(r(A))]),_:1}),e[24]||(e[24]=p(" 重新生成 ",-1))]),_:1}),s(c,{type:"primary",onClick:H},{default:l(()=>[s(d,null,{default:l(()=>[s(r(q))]),_:1}),e[25]||(e[25]=p(" 导出Markdown ",-1))]),_:1})])])])])}}},Ke=G(Pe,[["__scopeId","data-v-2eeeec35"]]);export{Ke as default};
