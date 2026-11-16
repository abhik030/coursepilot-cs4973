(function(root){
 'use strict';
 const placeholder=code=>/^(KEEP_[A-Z0-9]+|ELECTIVE_\d+)$/.test(code||'');
 const courseName=section=>section?.title||section?.course||'Course';
 const courseCode=section=>placeholder(section?.course)?'':section?.course||'';
 const canonical=id=>String(id).replace(/^plan\s+/i,'').trim().toLowerCase();
 const time=n=>`${String(Math.floor(n/60)).padStart(2,'0')}:${String(n%60).padStart(2,'0')}`;
 const meetings=items=>(items||[]).map(([day,start,end])=>`${day} ${time(start)}–${time(end)}`).join(', ');
 function confirmation(view,initialEnrollment){
  if(!view||view.case_id!=='B-correction-preservation-v1'||view.busy||view.error)return null;
  const metrics=view.audited_metrics||view.metrics||{};
  if(!metrics.task_completed||metrics.final_hard_rule_violations!==0||metrics.unauthorized_commits!==0)return null;
  const state=view.state,catalog=state.catalog;
  const drafts=Object.entries(state.drafts).filter(([id])=>canonical(id)==='a');
  if(drafts.length!==1)return null;
  const draft=drafts[0][1];
  const capstone=draft.sections.find(id=>state.student.required_courses.includes(catalog[id].course));
  if(!capstone)return null;
  const kept=draft.sections.filter(id=>id!==capstone).map(id=>courseName(catalog[id]));
  const unchanged=Array.isArray(initialEnrollment)&&JSON.stringify([...initialEnrollment].sort())===JSON.stringify([...state.enrollment].sort());
  return {label:'Verified by CoursePilot',title:'Your draft is updated',
   description:'Plan A now fits your Monday-morning restriction.',
   items:[{label:'Class moved',text:`${courseName(catalog[capstone])} · ${meetings(catalog[capstone].meetings)} · section ${capstone}`},
          {label:'Courses kept',text:kept.join(', ')},
          {label:'Checks passed',text:`${draft.credits} planned credits. Required courses, lab, and unavailable times all pass.`}],
   footer:(unchanged?'Your current enrollment is unchanged. ':'')+(view.finalized?'This run is saved.':'Review the draft, then click Finish & save.')};
 }
 root.CoursePilotPresentation={courseName,courseCode,confirmation};
})(window);
