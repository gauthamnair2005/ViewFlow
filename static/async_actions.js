document.addEventListener('DOMContentLoaded', ()=>{
    // Attach handlers to forms with class js-async-form
    console.log('Async actions script loaded');
    const forms = document.querySelectorAll('form.js-async-form');
    console.log('Found', forms.length, 'async forms');
    
    forms.forEach(form=>{
        console.log('Attaching handler to form with action:', form.action, 'data-action:', form.dataset.action);
        form.addEventListener('submit', async (e)=>{
            e.preventDefault();
            console.log('Form submitted, prevented default');
            const action = form.dataset.action || '';
            let url = form.getAttribute('action');
            // Append ajax=1 to URL to ensure backend detects it even if headers are stripped
            if(url.indexOf('?') === -1) url += '?ajax=1';
            else url += '&ajax=1';
            
            const formData = new FormData(form);
            console.log('Making async request to:', url, 'with action:', action);
            try{
                const resp = await fetch(url, {
                    method: form.getAttribute('method') || 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin'
                });
                console.log('Response status:', resp.status, 'OK:', resp.ok);
                if(!resp.ok){
                    // fallback: log error but do not reload to avoid disruption
                    console.warn('Async action failed', resp.status);
                    return;
                }
                const data = await resp.json().catch((err)=>{
                    console.error('Failed to parse JSON response:', err);
                    return null;
                });
                console.log('Response data:', data);
                if(!data){
                    console.warn('No data returned');
                    return;
                }
                // Handle known action responses
                if(action === 'like' || action === 'dislike'){
                    console.log('Handling like/dislike action. Data:', data);
                    // update counts and button states on watch page
                    if(data.likes !== undefined){
                        const likesEl = document.getElementById('likes-count');
                        console.log('Updating likes count to:', data.likes);
                        if(likesEl) likesEl.textContent = data.likes;
                    }
                    if(data.dislikes !== undefined){
                        const dislikesEl = document.getElementById('dislikes-count');
                        console.log('Updating dislikes count to:', data.dislikes);
                        if(dislikesEl) dislikesEl.textContent = data.dislikes;
                    }
                    const likeBtn = form.querySelector('.js-like-btn') || document.querySelector('.js-like-btn');
                    const dislikeBtn = form.querySelector('.js-dislike-btn') || document.querySelector('.js-dislike-btn');
                    if(data.is_liked){
                        if(likeBtn) {
                            likeBtn.classList.add('btn-accent');
                            likeBtn.classList.remove('btn-primary');
                        }
                    } else {
                        if(likeBtn) {
                            likeBtn.classList.remove('btn-accent');
                            likeBtn.classList.add('btn-primary');
                        }
                    }
                    if(data.is_disliked){
                        if(dislikeBtn) {
                            dislikeBtn.classList.add('btn-accent');
                            dislikeBtn.classList.remove('btn-primary');
                        }
                    } else {
                        if(dislikeBtn) {
                            dislikeBtn.classList.remove('btn-accent');
                            dislikeBtn.classList.add('btn-primary');
                        }
                    }
                } else if(action === 'subscribe' || url.includes('/subscribe/')){
                    // data.subscribed, data.subs_count
                    const subscribeBtn = form.querySelector('.js-subscribe-btn') || document.querySelector('.js-subscribe-btn');
                    if(subscribeBtn) {
                        if(data.subscribed){
                            subscribeBtn.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-2 1H8v-6c0-2.48 1.51-4.5 4-4.5s4 2.02 4 4.5v6z"/></svg> Subscribed';
                            subscribeBtn.classList.remove('btn-accent');
                            subscribeBtn.classList.add('btn-primary');
                        } else {
                            subscribeBtn.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-2 1H8v-6c0-2.48 1.51-4.5 4-4.5s4 2.02 4 4.5v6z"/></svg> Subscribe';
                            subscribeBtn.classList.remove('btn-primary');
                            subscribeBtn.classList.add('btn-accent');
                        }
                    }
                    const subsCountEl = document.getElementById('subs-count');
                    if(subsCountEl && data.subs_count !== undefined) subsCountEl.textContent = data.subs_count;
                } else {
                    // generic: if server returned redirect target, follow it
                    if(data.redirect){ window.location.href = data.redirect; }
                }
            }catch(err){
                console.error('Async action error', err);
            }
        });
    });
});
