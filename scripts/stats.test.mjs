import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';import {test} from 'node:test';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
const source=script.slice(script.indexOf('function numberOrNull'),script.indexOf('function paintStats'));
const context=vm.createContext({Date,Number,String});vm.runInContext(source,context);
test('0은 실제 0으로 유지하고 누락값을 0으로 바꾸지 않음',()=>{assert.equal(context.numberOrNull(0),0);assert.equal(context.numberOrNull('767'),767);for(const v of [null,undefined,'',false,-1,'NaN','12.5'])assert.equal(context.numberOrNull(v),null)});
test('저장한 통계와 확인시각 복원, 미제공 댓글은 null 유지',()=>{const v=context.cleanStats({id:'Eir2GhnFJdc',viewCount:'100',commentCount:null,checkedAt:'2026-11-10T00:00:00Z'});assert.equal(v.viewCount,100);assert.equal(v.commentCount,null);assert.equal(context.cleanStats({id:'Eir2GhnFJdc',checkedAt:'invalid'}),null)});
test('실제 수집 데이터 7개 검증',()=>{const d=JSON.parse(fs.readFileSync(new URL('../stats.json',import.meta.url),'utf8'));assert.equal(Object.keys(d.videos).length,7);for(const [id,v] of Object.entries(d.videos)){assert.match(id,/^[\w-]{11}$/);assert.ok(Number.isFinite(Date.parse(v.checkedAt)));assert.ok(v.viewCount>0);assert.ok(v.commentCount===null||Number.isInteger(v.commentCount))}});
