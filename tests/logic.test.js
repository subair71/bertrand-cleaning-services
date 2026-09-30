import test from 'node:test';
import assert from 'node:assert/strict';
import {validate,validFiles,escapeHTML} from '../js/logic.js';
import {repository} from '../js/repository.js';
const base={name:'Sample',phone:'+33605597685',service:'home',address:'Sample address',details:'Demo enquiry'};
test('required fields and invalid phone/email are rejected',()=>{assert.equal(validate({},'quote').name,'required');assert.equal(validate({...base,phone:'not a number'},'quote').phone,'invalidPhone');assert.equal(validate({...base,email:'bad@'},'quote').email,'invalidEmail');assert.deepEqual(validate(base,'quote'),{})});
test('past bookings rejected; future requests valid',()=>{assert.equal(validate({...base,date:'2020-01-01',time:'10:00'},'booking').date,'invalidDate');assert.deepEqual(validate({...base,date:'2099-10-01',time:'10:00'},'booking'),{})});
test('file count, size and mime restrictions',()=>{const f={type:'image/jpeg',size:200};assert.equal(validFiles([f]),true);assert.equal(validFiles([f],5),false);assert.equal(validFiles([{type:'image/svg+xml',size:10}]),false);assert.equal(validFiles([{type:'image/png',size:5242881}]),false);assert.equal(validFiles([{type:'image/png',size:0}]),false)});
test('untrusted text escaped and demo reset clears added requests',()=>{assert.equal(escapeHTML('<script>"&'), '&lt;script&gt;&quot;&amp;');repository.save('requests',{id:'DEMO-TEST',name:'sample',photos:[]});assert.ok(repository.get('requests','DEMO-TEST'));repository.reset();assert.equal(repository.get('requests','DEMO-TEST'),undefined)});
