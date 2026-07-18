#!/usr/bin/env node

import fs from "node:fs";

const [url, outputPath, timeArg = "17.8", widthArg = "1440", heightArg = "1000"] = process.argv.slice(2);
if (!url || !outputPath) throw new Error("Usage: cdp_video_review.mjs <url> <screenshot> [seconds] [width] [height]");

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
await send("Emulation.setDeviceMetricsOverride", {
  width: Number(widthArg), height: Number(heightArg), deviceScaleFactor: 1, mobile: Number(widthArg) < 700,
});
await send("Page.navigate", {url});
await new Promise(resolve => setTimeout(resolve, 1800));
await send("Runtime.evaluate", {
  expression: `new Promise(async resolve => {
    const video = document.querySelector('#explainer video');
    video.muted = true;
    await video.play();
    await new Promise(frameReady => video.requestVideoFrameCallback(frameReady));
    await new Promise(settled => setTimeout(settled, 250));
    video.currentTime = ${Number(timeArg)};
    const check = setInterval(() => {
      if (Math.abs(video.currentTime - ${Number(timeArg)}) < 0.2) {
        clearInterval(check);
        video.requestVideoFrameCallback(() => {
          video.pause();
          resolve(video.currentTime);
        });
      }
    }, 50);
  })`,
  awaitPromise: true,
});
await new Promise(resolve => setTimeout(resolve, 400));
const evaluation = await send("Runtime.evaluate", {
  expression: `(() => {
    const video = document.querySelector('#explainer video');
    const rect = video.getBoundingClientRect();
    return {
      currentTime: video.currentTime,
      duration: video.duration,
      readyState: video.readyState,
      rect: {x: rect.x + scrollX, y: rect.y + scrollY, width: rect.width, height: rect.height},
      pageOverflow: document.documentElement.scrollWidth > innerWidth,
    };
  })()`,
  returnByValue: true,
});
const review = evaluation.result.value;
const shot = await send("Page.captureScreenshot", {
  format: "png",
  captureBeyondViewport: true,
  clip: {...review.rect, scale: 1},
});
fs.writeFileSync(outputPath, Buffer.from(shot.data, "base64"));
if (problems.length || review.readyState < 2 || Math.abs(review.currentTime - Number(timeArg)) > 0.2) {
  throw new Error(JSON.stringify({review, problems}, null, 2));
}
console.log(JSON.stringify({review, problems, screenshot: outputPath}, null, 2));
socket.close();
