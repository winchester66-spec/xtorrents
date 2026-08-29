
/* ---- HERO CAROUSEL ---- */
(function(){
  var catalog = window.XT_CATALOG || [];
  var slides = catalog.slice(0, 10).filter(function(m){ return m.poster; });
  if(!slides.length) return;
  var track = document.getElementById('carouselTrack');
  var dotsWrap = document.getElementById('carouselDots');
  var progressBar = document.getElementById('carouselProgress');
  if(!track) return;
  var current = 0, timer = null, progressTimer = null, progressPct = 0;
  var DURATION = 5500;

  function esc(s){ return String(s).replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

  slides.forEach(function(m, i){
    var cats = (m.categories||[]).filter(function(c){
      return c!=='1080p'&&c!=='720p'&&c!=='4K'&&!/^\d{4}$/.test(c)&&c!=='Filmes'&&c!=='Series';
    }).slice(0,2);
    var div = document.createElement('div');
    div.className = 'carousel-slide';
    div.innerHTML =
      '<div class="carousel-bg" style="background-image:url(\''+esc(m.poster)+'\')"></div>'+
      '<div class="carousel-inner">'+
        '<div class="carousel-info">'+
          '<div class="carousel-badge-row">'+
            cats.map(function(c){ return '<span class="carousel-cat">'+esc(c)+'</span>'; }).join('')+
            '<span class="carousel-yr">'+esc(m.year||'')+'</span>'+
          '</div>'+
          '<h2 class="carousel-title">'+esc(m.title)+'</h2>'+
          '<div class="carousel-meta-row">'+
            '<span>\u2605 '+esc(m.quality||'1080p')+'</span>'+
            '<span>'+esc(m.type||'Filme')+'</span>'+
          '</div>'+
          '<a href="/filme/'+esc(m.slug)+'" class="primary" style="text-decoration:none">&#9654;&nbsp;Ver agora</a>'+
        '</div>'+
        '<div class="carousel-poster-wrap">'+
          '<img src="'+esc(m.poster)+'" alt="'+esc(m.title)+'" loading="lazy">'+
        '</div>'+
      '</div>';
    track.appendChild(div);

    if(dotsWrap){
      var dot = document.createElement('button');
      dot.className = 'carousel-dot'+(i===0?' active':'');
      dot.setAttribute('aria-label','Slide '+(i+1));
      dot.addEventListener('click', function(){ goTo(i); });
      dotsWrap.appendChild(dot);
    }
  });

  function updateDots(){
    if(!dotsWrap) return;
    dotsWrap.querySelectorAll('.carousel-dot').forEach(function(d,i){ d.classList.toggle('active',i===current); });
  }

  function startProgress(){
    clearInterval(progressTimer);
    progressPct = 0;
    if(progressBar) progressBar.style.width = '0%';
    var step = 100 / (DURATION / 80);
    progressTimer = setInterval(function(){
      progressPct = Math.min(progressPct + step, 100);
      if(progressBar) progressBar.style.width = progressPct + '%';
    }, 80);
  }

  function goTo(n){
    current = ((n % slides.length) + slides.length) % slides.length;
    track.style.transform = 'translateX(-'+(current*100)+'%)';
    updateDots();
    resetTimer();
  }

  function resetTimer(){
    clearInterval(timer);
    startProgress();
    timer = setInterval(function(){ goTo(current+1); }, DURATION);
  }

  var prevBtn = document.getElementById('carouselPrev');
  var nextBtn = document.getElementById('carouselNext');
  if(prevBtn) prevBtn.addEventListener('click', function(){ goTo(current-1); });
  if(nextBtn) nextBtn.addEventListener('click', function(){ goTo(current+1); });

  var section = document.getElementById('heroCarousel');
  if(section){
    section.addEventListener('mouseenter', function(){ clearInterval(timer); clearInterval(progressTimer); });
    section.addEventListener('mouseleave', function(){ resetTimer(); });
  }
  resetTimer();
})();

/* ---- GENRE PILLS ---- */
(function(){
  document.querySelectorAll('.genre-pill').forEach(function(pill){
    pill.addEventListener('click', function(){
      var genre = pill.getAttribute('data-genre');
      if(genre === 'mais'){
        document.getElementById('catalogo').scrollIntoView({behavior:'smooth'});
        return;
      }
      document.querySelectorAll('.genre-pill').forEach(function(p){ p.classList.remove('active'); });
      pill.classList.add('active');
      var sel = document.getElementById('catFilter');
      if(sel){
        sel.value = genre;
        sel.dispatchEvent(new Event('change'));
      }
      document.getElementById('catalogo').scrollIntoView({behavior:'smooth'});
    });
  });
  // Sync genre pills with catFilter select (if changed manually)
  var sel = document.getElementById('catFilter');
  if(sel){
    sel.addEventListener('change', function(){
      document.querySelectorAll('.genre-pill').forEach(function(p){
        p.classList.toggle('active', p.getAttribute('data-genre') === sel.value);
      });
    });
  }
})();
