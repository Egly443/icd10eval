#!/usr/bin/env node

const url = process.argv[2] || "http://127.0.0.1:8001/";
const targets = await fetch("http://127.0.0.1:9222/json/list").then(response => response.json());
const target = targets.find(item => item.type === "page");
if (!target) throw new Error("No Chrome page target is available");

const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.addEventListener("open", resolve, {once: true});
  socket.addEventListener("error", reject, {once: true});
});

let commandId = 0;
const pending = new Map();
const problems = [];
socket.addEventListener("message", event => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) {
    const handlers = pending.get(message.id);
    pending.delete(message.id);
    message.error ? handlers.reject(new Error(message.error.message)) : handlers.resolve(message.result);
  } else if (message.method === "Runtime.exceptionThrown" || message.method === "Log.entryAdded") {
    problems.push(message.params);
  }
});
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = ++commandId;
  pending.set(id, {resolve, reject});
  socket.send(JSON.stringify({id, method, params}));
});

await send("Page.enable");
await send("Runtime.enable");
await send("Log.enable");
await send("Page.navigate", {url});
await new Promise(resolve => setTimeout(resolve, 1200));
await send("Runtime.evaluate", {expression: "document.querySelector('.generate-button').click()"});
await new Promise(resolve => setTimeout(resolve, 1800));
const evaluation = await send("Runtime.evaluate", {
  expression: `({
    staticMode: window.STATIC_SITE === true,
    generated: !document.querySelector('#episode-shell').hidden,
    episodeId: document.querySelector('#episode-id').textContent,
    seedLocked: document.querySelector('#seed').disabled,
    downloadReady: document.querySelector('#download-link').href.startsWith('blob:'),
    videoDuration: Math.round(document.querySelector('#explainer video').duration),
    videoReady: document.querySelector('#explainer video').readyState > 0,
  })`,
  returnByValue: true,
});
const result = evaluation.result.value;
if (!result.staticMode || !result.generated || !result.seedLocked || !result.downloadReady || !result.videoReady || result.videoDuration !== 60 || problems.length) {
  throw new Error(JSON.stringify({result, problems}, null, 2));
}
console.log(JSON.stringify({result, problems}, null, 2));
socket.close();
