#!/usr/bin/env node
const fs = require('fs');
const content = fs.readFileSync('Agents.md','utf8');
const agentRegex = /Agent: ([A-Za-z0-9]+)/g;
const agents = [];
let m;
while((m = agentRegex.exec(content)) !== null){
  agents.push(m[1]);
}
let log = '# Agents Dry Run\n';
for(const agent of agents){
  log += `- ${agent} simulated\n`;
  console.log(`Simulating ${agent}`);
}
fs.mkdirSync('docs', {recursive: true});
log += `Dry run completed for ${agents.length} agents\n`;
fs.writeFileSync('docs/agents_drycheck.md', log);
console.log('Dry run completed for', agents.length, 'agents');
