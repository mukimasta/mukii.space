/* SoundMat homepage: footnote cards, design-notes carousel, image strip. */

/* footnotes: a trigger in the text opens the card right after its paragraph */
(function(){
  document.querySelectorAll('.tn').forEach(function(b){b.addEventListener('click',function(){
    var c=document.getElementById(b.getAttribute('aria-controls'));if(!c)return;
    var open=c.hasAttribute('hidden');if(open)c.removeAttribute('hidden');else c.setAttribute('hidden','');
    b.setAttribute('aria-expanded',open)})});
})();

/* design notes: one card in front, two peeking behind; arrows, swipe, arrow keys */
(function(){
  var stack=document.getElementById('nstack');if(!stack)return;
  var cards=[].slice.call(stack.querySelectorAll('.ncard')),n=cards.length,cur=0,count=document.getElementById('ncount');
  function render(){cards.forEach(function(c,i){var p=(i-cur+n)%n;
      c.setAttribute('data-pos',p===0?'0':p===1?'1':p===2?'2':'x');c.setAttribute('aria-hidden',p===0?'false':'true');
      c.setAttribute('aria-label',(i+1)+' / '+n)});
    count.textContent=(cur+1)+' / '+n}
  function go(d){cur=(cur+d+n)%n;render()}
  document.getElementById('nprev').addEventListener('click',function(){go(-1)});
  document.getElementById('nnext').addEventListener('click',function(){go(1)});
  var x0=null;
  stack.addEventListener('pointerdown',function(e){x0=e.clientX});
  stack.addEventListener('pointerup',function(e){if(x0===null)return;var dx=e.clientX-x0;x0=null;if(Math.abs(dx)>40)go(dx<0?1:-1)});
  stack.addEventListener('pointercancel',function(){x0=null});
  stack.parentNode.addEventListener('keydown',function(e){if(e.key==='ArrowLeft')go(-1);else if(e.key==='ArrowRight')go(1)});
  render();
})();

/* image strip: arrows, mouse drag; disabled arrows at the ends */
(function(){
  var row=document.getElementById('srow');if(!row)return;
  var prev=document.getElementById('sprev'),next=document.getElementById('snext');
  function ends(){prev.disabled=row.scrollLeft<=2;next.disabled=row.scrollLeft+row.clientWidth>=row.scrollWidth-2}
  function step(d){row.scrollBy({left:d*Math.round(row.clientWidth*0.7),behavior:'smooth'})}
  prev.addEventListener('click',function(){step(-1)});next.addEventListener('click',function(){step(1)});
  row.addEventListener('scroll',ends,{passive:true});window.addEventListener('resize',ends);
  var down=false,x0=0,s0=0,moved=false;
  row.addEventListener('pointerdown',function(e){if(e.pointerType!=='mouse')return;down=true;moved=false;x0=e.clientX;s0=row.scrollLeft});
  window.addEventListener('pointermove',function(e){if(!down)return;var dx=e.clientX-x0;if(Math.abs(dx)>4){moved=true;row.classList.add('dragging')}if(moved)row.scrollLeft=s0-dx});
  window.addEventListener('pointerup',function(){if(!down)return;down=false;row.classList.remove('dragging')});
  row.addEventListener('click',function(e){if(moved){e.preventDefault();e.stopPropagation();moved=false}},true);
  ends();
})();
