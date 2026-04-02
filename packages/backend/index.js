const http=require('http');const PORT=process.env.PORT||3000;
http.createServer((req,res)=>{
  res.setHeader('Content-Type','application/json');
  if(req.url==='/api/proxy'||req.url==='/health'||req.url==='/') return res.end(JSON.stringify({system:"Constellation25-Monorepo",status:"online",pathos:"connected",agents:25,workspace:"packages/backend",ts:new Date().toISOString()}));
  if(req.url==='/api/agents') return res.end(JSON.stringify({count:25,agents:["AlfAi","Alpi","ComandR","VerseBot","Echo","NoTeTaL","Recon","PR","KoreSync","Grail","Swifty","Zion","Chronos","SCAF","Explorer","Starg8","CacheF","Synthi","Nexus","Kinect","AiTrek","Shado","Ledger","ZaLe","MyBUY'o"]}));
  res.end(JSON.stringify({error:"not_found"}));
}).listen(PORT,()=>console.log(`🚀 C25 Monorepo Backend :${PORT}`));
