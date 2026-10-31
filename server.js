const express=require('express');
const Database=require('better-sqlite3');
const path=require('path');
const app=express();
const db=new Database(path.join(__dirname,'invoice_results.db'),{readonly:true});
app.use(express.static(path.join(__dirname,'public')));
app.get('/api/summary',(req,res)=>res.json(db.prepare('SELECT * FROM summary ORDER BY method').all().map(r=>({...r,top_error_fields:JSON.parse(r.top_error_fields_json||'[]')}))));
app.get('/api/invoices',(req,res)=>res.json(db.prepare('SELECT invoice_id FROM invoices ORDER BY invoice_id').all()));
app.get('/api/invoice/:id',(req,res)=>{
 const gt=db.prepare('SELECT ground_truth_json FROM invoices WHERE invoice_id=?').get(req.params.id);
 const rows=db.prepare('SELECT method,result_json,accuracy,error_count FROM results WHERE invoice_id=? ORDER BY method').all(req.params.id);
 if(!gt)return res.status(404).json({error:'Not found'});
 res.json({invoice_id:req.params.id,ground_truth:JSON.parse(gt.ground_truth_json),results:rows.map(r=>({...r,result:JSON.parse(r.result_json)}))});
});
app.get('/api/errors/:method',(req,res)=>{
 const d=require('./evaluation/details.json').filter(x=>x.method===req.params.method&&x.errors.length);
 res.json(d);
});
const port=process.env.PORT||3000;app.listen(port,()=>console.log(`Invoice dashboard: http://localhost:${port}`));
