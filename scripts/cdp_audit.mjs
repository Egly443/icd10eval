#!/usr/bin/env node

import fs from "node:fs";

const [url, outputPath, widthArg = "1440", heightArg = "1000"] = process.argv.slice(2);
if (!url || !outputPath) {
  throw new Error("Usage: cdp_audit.mjs <url> <screenshot-path> [width] [height]");
}

const width = Number(widthArg);
const height = Number(heightArg);
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
const events = [];
socket.addEventListener("message", event => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) {
    const {resolve, reject} = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) reject(new Error(message.error.message));
    else resolve(message.result);
  } else if (message.method) {
    events.push(message);
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
await send("Emulation.setDeviceMetricsOverride", {width, height, deviceScaleFactor: 1, mobile: width < 700});
await send("Page.navigate", {url});
await new Promise(resolve => setTimeout(resolve, 1800));

const auditExpression = `(() => {
  const all = [...document.querySelectorAll('*')];
  const visible = all.filter(el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
  });
  const overflow = visible.filter(el => el.scrollWidth > el.clientWidth + 2).slice(0, 12).map(el => ({
    tag: el.tagName, className: String(el.className).slice(0, 80), clientWidth: el.clientWidth, scrollWidth: el.scrollWidth
  }));
  const radii = visible.map(el => getComputedStyle(el).borderRadius).filter(value => value !== '0px');
  const gradients = visible.filter(el => getComputedStyle(el).backgroundImage.includes('gradient')).length;
  return {
    title: document.title,
    h1: document.querySelector('h1')?.innerText,
    viewport: [innerWidth, innerHeight],
    documentHeight: document.documentElement.scrollHeight,
    elementCount: all.length,
    articleCount: document.querySelectorAll('article').length,
    buttonCount: document.querySelectorAll('button, .button').length,
    gradientElementCount: gradients,
    roundedElementCount: radii.length,
    uniqueRadii: [...new Set(radii)].slice(0, 20),
    horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
    overflowingElements: overflow,
    bodyFont: getComputedStyle(document.body).fontFamily,
    bodyBackground: getComputedStyle(document.body).backgroundColor,
    reducedMotionSupported: matchMedia('(prefers-reduced-motion: reduce)').matches,
  };
})()`;
const evaluation = await send("Runtime.evaluate", {expression: auditExpression, returnByValue: true});
const metrics = await send("Page.getLayoutMetrics");
const content = metrics.cssContentSize;
const screenshot = await send("Page.captureScreenshot", {
  format: "png",
  captureBeyondViewport: true,
  clip: {x: 0, y: 0, width: Math.min(content.width, width), height: content.height, scale: 1},
});
fs.writeFileSync(outputPath, Buffer.from(screenshot.data, "base64"));

const consoleProblems = events
  .filter(event => event.method === "Runtime.exceptionThrown" || event.method === "Log.entryAdded")
  .map(event => event.params);
console.log(JSON.stringify({audit: evaluation.result.value, consoleProblems, screenshot: outputPath}, null, 2));
socket.close();
