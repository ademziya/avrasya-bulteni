// Ana sayfa için script
(function() {
    const container = document.getElementById('yayinlarContainer');
    const filterButtons = document.getElementById('filterButtons');
    if (!container) return;

    fetch('data/yayinlar.json')
        .then(r => r.json())
        .then(data => {
            renderYayinlar(data);
            setupFilters(data);
        })
        .catch(() => {
            container.innerHTML = '<p style="padding:40px 0;color:#6b5f53;">Veriler yüklenemedi. Lütfen daha sonra tekrar deneyin.</p>';
        });

    function renderYayinlar(yayinlar) {
        container.innerHTML = yayinlar.map(y => kartHtml(y)).join('');
    }

    function kartHtml(y) {
        const etiketler = y.etiket && y.etiket.length
            ? y.etiket.map(e => `<span style="background:#e0d6c8;font-size:0.7rem;padding:2px 8px;border-radius:3px;margin-right:4px;">${e}</span>`).join('')
            : '';
        const linkSayfa = y.tur === 'makale' ? 'makaleler.html' 
            : y.tur === 'kitap' ? 'kitaplar.html' 
            : 'sempozyumlar.html';
        return `
            <article class="card">
                <div class="card-meta">
                    <span class="card-tag ${y.tur}">${y.tur === 'makale' ? 'Makale' : y.tur === 'kitap' ? 'Kitap' : 'Sempozyum'}</span>
                    <span class="card-source">${y.kaynak || ''}</span>
                </div>
                <h3 class="card-title"><a href="${y.link || '#'}" target="_blank" rel="noopener">${y.baslik}</a></h3>
                ${y.yazarlar ? `<p class="card-authors">${y.yazarlar}</p>` : ''}
                ${y.dergi ? `<p class="card-journal">${y.dergi}</p>` : ''}
                <p class="card-abstract">${y.ozet}</p>
                <div style="margin-bottom:10px;">${etiketler}</div>
                <div class="card-footer">
                    <span class="card-date">${y.tarih || ''}</span>
                    <a href="${linkSayfa}" class="card-link">Detay →</a>
                </div>
            </article>
        `;
    }

    function setupFilters(data) {
        if (!filterButtons) return;
        filterButtons.addEventListener('click', function(e) {
            if (e.target.classList.contains('filter-btn')) {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                const tur = e.target.dataset.tur;
                const filtered = tur === 'tumu' ? data : data.filter(y => y.tur === tur);
                renderYayinlar(filtered);
            }
        });
    }
})();
