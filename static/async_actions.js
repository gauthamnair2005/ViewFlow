document.addEventListener('DOMContentLoaded', ()=>{
    // Attach handlers to forms with class js-async-form
    console.log('Async actions script loaded');
    const forms = document.querySelectorAll('form.js-async-form');
    console.log('Found', forms.length, 'async forms');
    
    function attachHandler(form) {
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
                } else if(action === 'comment'){
                    if(data.success && data.comment){
                        const list = document.getElementById('comments-list');
                        const div = document.createElement('div');
                        div.className = 'comment';
                        div.id = 'comment-' + data.comment.id;
                        div.style.cssText = 'display:flex; gap:10px; margin-bottom:20px; animation: fadeIn 0.3s ease;';
                        
                        let avatarHtml = '';
                        if(data.comment.profile_pic){
                            avatarHtml = `<img src="${data.comment.profile_pic}" class="avatar" style="width:40px; height:40px; object-fit:cover;">`;
                        } else {
                            avatarHtml = `<div class="avatar" style="width:40px; height:40px;">${data.comment.initial}</div>`;
                        }
                        
                        div.innerHTML = `
                            <a href="${data.comment.user_url}">
                                ${avatarHtml}
                            </a>
                            <div style="flex:1;">
                                <div style="margin-bottom:4px;">
                                    <a href="${data.comment.user_url}" style="font-weight:bold; font-size:0.9rem; margin-right:8px;">${data.comment.user}</a>
                                    <span style="color:var(--text-sec); font-size:0.8rem;">${data.comment.date}</span>
                                </div>
                                <p style="margin:0; font-size:0.95rem;">${data.comment.content}</p>
                            </div>
                            <div>
                                <form method="POST" action="/comment/${data.comment.id}/delete" class="js-async-form" data-action="delete-comment">
                                    <button type="submit" class="btn" style="padding:4px 8px; font-size:0.8rem; opacity:0.7;" title="Delete">✕</button>
                                </form>
                            </div>
                        `;
                        
                        list.insertBefore(div, list.firstChild);
                        form.reset();
                        
                        // Re-attach handler to the new delete form
                        const newForm = div.querySelector('form');
                        if(newForm) attachHandler(newForm);
                    }
                } else if(action === 'delete-comment'){
                    if(data.success){
                        const commentDiv = form.closest('.comment');
                        if(commentDiv){
                            commentDiv.style.opacity = '0';
                            setTimeout(() => commentDiv.remove(), 300);
                        }
                    }
                } else {
                    // generic: if server returned redirect target, follow it
                    if(data.redirect){ window.location.href = data.redirect; }
                }
            }catch(err){
                console.error('Async action error', err);
            }
        });
    }

    forms.forEach(form => attachHandler(form));
});
