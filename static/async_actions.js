document.addEventListener('DOMContentLoaded', ()=>{
    // Attach handlers to forms with class js-async-form
    document.querySelectorAll('form.js-async-form').forEach(form=>{
        form.addEventListener('submit', async (e)=>{
            e.preventDefault();
            const action = form.dataset.action || '';
            const url = form.action;
            const formData = new FormData(form);
            try{
                const resp = await fetch(url, {
                    method: form.method || 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin'
                });
                if(!resp.ok){
                    // fallback: reload on failure
                    console.warn('Async action failed, reloading', resp.status);
                    window.location.reload();
                    return;
                }
                const data = await resp.json().catch(()=>null);
                if(!data){
                    window.location.reload();
                    return;
                }
                // Handle known action responses
                if(action === 'like' || action === 'dislike'){
                    // update counts and button states on watch page
                    if(data.likes !== undefined){
                        const likesEl = document.getElementById('likes-count');
                        if(likesEl) likesEl.textContent = data.likes;
                    }
                    if(data.dislikes !== undefined){
                        const dislikesEl = document.getElementById('dislikes-count');
                        if(dislikesEl) dislikesEl.textContent = data.dislikes;
                    }
                    const likeBtn = form.querySelector('.js-like-btn') || document.querySelector('.js-like-btn');
                    const dislikeBtn = form.querySelector('.js-dislike-btn') || document.querySelector('.js-dislike-btn');
                    if(data.is_liked){
                        likeBtn && likeBtn.classList.add('btn-accent') && likeBtn.classList.remove('btn-primary');
                    } else {
                        likeBtn && likeBtn.classList.remove('btn-accent') && likeBtn.classList.add('btn-primary');
                    }
                    if(data.is_disliked){
                        dislikeBtn && dislikeBtn.classList.add('btn-accent') && dislikeBtn.classList.remove('btn-primary');
                    } else {
                        dislikeBtn && dislikeBtn.classList.remove('btn-accent') && dislikeBtn.classList.add('btn-primary');
                    }
                } else if(action === 'subscribe' || url.includes('/subscribe/')){
                    // data.subscribed, data.subs_count
                    const subscribeBtn = form.querySelector('.js-subscribe-btn') || document.querySelector('.js-subscribe-btn');
                    if(data.subscribed){
                        subscribeBtn && (subscribeBtn.textContent = 'Subscribed') && subscribeBtn.classList.remove('btn-accent') && subscribeBtn.classList.add('btn-primary');
                    } else {
                        subscribeBtn && (subscribeBtn.textContent = 'Subscribe') && subscribeBtn.classList.remove('btn-primary') && subscribeBtn.classList.add('btn-accent');
                    }
                    const subsCountEl = document.getElementById('subs-count');
                    if(subsCountEl && data.subs_count !== undefined) subsCountEl.textContent = data.subs_count;
                } else {
                    // generic: if server returned redirect target, follow it
                    if(data.redirect){ window.location.href = data.redirect; }
                }
            }catch(err){
                console.error('Async action error', err);
                window.location.reload();
            }
        });
    });
});
