const fs = require('fs'), vm = require('vm'), crypto = require('crypto'), assert = require('assert');
const sourceCode=fs.readFileSync(__dirname+'/plaud_gemini_workspace.gs','utf8');
function runtime(text='Speaker 1 [00:01]: Confirm the inspection date.') {
 let value=text, created=0, failMove=false;
 const props={},docs={},file={getId:()=> 'input-1',getName:()=> 'meeting.txt',getSize:()=>Buffer.byteLength(value),getBlob:()=>({getDataAsString:()=>value}),getUrl:()=> 'https://drive.google.com/file/d/input-1/view',getLastUpdated:()=>new Date('2026-09-30T12:00:00Z')};
 const context={console:{log(){}},LockService:{getUserLock:()=>({tryLock:()=>true,releaseLock(){}})},PropertiesService:{getScriptProperties:()=>({getProperty:k=>k === 'PLAUD_INBOX_ID' ? 'test-inbox' : 'test-sources'}),getUserProperties:()=>({getProperty:k=>props[k],setProperty:(k,v)=>props[k]=v})},DriveApp:{getFolderById:()=>({getFiles:()=>{let i=0;return {hasNext:()=>i<1,next:()=>{i++;return file;}};}}),getFileById:id=>({isTrashed:()=>false,moveTo(){if(failMove)throw Error('unavailable');}})},Utilities:{DigestAlgorithm:{SHA_256:'sha256'},Charset:{UTF_8:'utf8'},computeDigest:(_,v)=>[...crypto.createHash('sha256').update(v).digest()]},DocumentApp:{create:()=>{const id='doc-'+(++created);let body='';const d={getId:()=>id,getUrl:()=> 'https://docs.google.com/document/d/'+id+'/edit',getBody:()=>({setText:t=>body=t,getText:()=>body}),saveAndClose(){}};docs[id]=d;return d;},openById:id=>docs[id]}};
 vm.createContext(context);vm.runInContext(sourceCode,context);
 return {run:()=>context.prepareGeminiSources(),count:()=>created,setText:t=>value=t,fail:()=>failMove=true};
}
const r=runtime();assert.equal(r.run().results[0].status,'prepared');assert.equal(r.run().results[0].status,'already_prepared');assert.equal(r.count(),1);r.setText('Changed recording export');assert.equal(r.run().results[0].status,'prepared');assert.equal(r.count(),2);
assert.equal(runtime('').run().results[0].status,'empty_or_pending');
assert.equal(runtime('a'.repeat(160000)).run().results[0].status,'split_required');
const f=runtime();f.fail();assert.throws(()=>f.run(),/incomplete/);assert.throws(()=>f.run(),/avoid duplication/);assert.equal(f.count(),1);
console.log('PASS: creation/readback, idempotence, changed version, empty input, size cap, and failure checkpoint with mocks.');
