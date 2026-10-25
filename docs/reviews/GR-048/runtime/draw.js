// Evaluated through T3 preview_evaluate after clicking the canvas and pressing R.
// Actual eframe UI input -> engine edit; no app source or serialized byte mutation.
(async () => {
  const w = document.querySelector('iframe').contentWindow;
  const c = w.document.querySelector('canvas');
  const pause = () => new Promise(r => setTimeout(r, 100));
  c.dispatchEvent(new w.MouseEvent('mousemove', {bubbles:true,clientX:480,clientY:220}));
  c.dispatchEvent(new w.PointerEvent('pointerdown', {bubbles:true,clientX:480,clientY:220,button:0,buttons:1,pointerId:1,pointerType:'mouse'}));
  await pause();
  c.dispatchEvent(new w.MouseEvent('mousemove', {bubbles:true,clientX:760,clientY:400,button:0,buttons:1}));
  await pause();
  c.dispatchEvent(new w.PointerEvent('pointerup', {bubbles:true,clientX:760,clientY:400,button:0,buttons:0,pointerId:1,pointerType:'mouse'}));
  await pause();
  return {dirty:gr048.dirty,events:gr048.events};
})()
