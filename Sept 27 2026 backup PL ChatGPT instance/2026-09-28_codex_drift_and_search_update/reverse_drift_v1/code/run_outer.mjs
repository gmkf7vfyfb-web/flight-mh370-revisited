import {Worker} from 'node:worker_threads';
import {readFile,writeFile,access} from 'node:fs/promises';
const root=new URL('../',import.meta.url);
const config=JSON.parse(await readFile(new URL('recovered/data/config.json',root)));
const models=[['bran2016','bran2016-surface-currents-20140308-23',null],['oscar_v2_final','oscar-v2-final-20140308-23',null],['glorys12_waverys','cmems-glorys12-surface-currents-20140308-24','cmems-waverys-surface-stokes-20140308-23']];
const tasks=[];
for(const day of [23,21]) for(const [currentModel,currentStem,stokesStem] of models) for(const seed of config.seeds) tasks.push({currentModel,currentStem,stokesStem,seed,observationUtc:`2014-03-${day}T04:00:00Z`,particleCount:64,diffusionRmsNmPerDay:5,kernelSigmasKm:[5,10,20],day});
await writeFile(new URL('outer_run_config.json',root),JSON.stringify({inherited:config,tasks,interpretation:'Conditional source compatibility. French observation clock time 04:00 UTC is assumed, not verified. Equal fixed family weights; no identity posterior or false-detection denominator.'},null,2));
let next=0;
async function consume(){while(next<tasks.length){const task=tasks[next++];const file=new URL(`runs/outer_${task.currentModel}_${task.day}_${task.seed}.json`,root);try{await access(file);continue;}catch{}
 console.log('START',task.currentModel,task.day,task.seed);
 const rows=await new Promise((resolve,reject)=>{const w=new Worker(new URL('./worker_outer.mjs',import.meta.url),{workerData:task});w.on('message',m=>{if(m.type==='result')resolve(m.rows);else if(m.completed%1500===0)console.log(task.currentModel,task.day,task.seed,m.completed);});w.on('error',reject);w.on('exit',c=>{if(c)reject(new Error(`worker exit ${c}`));});});
 await writeFile(file,JSON.stringify(rows)); console.log('DONE',task.currentModel,task.day,task.seed);
}}
await Promise.all(Array.from({length:3},consume));
