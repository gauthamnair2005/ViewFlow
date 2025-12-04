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
                        // Safely build bell icon + label to avoid injecting raw HTML
                        const ns = 'http://www.w3.org/2000/svg';
                        function makeBellLabel(labelText){
                            // clear
                            while(subscribeBtn.firstChild) subscribeBtn.removeChild(subscribeBtn.firstChild);
                            const svg = document.createElementNS(ns, 'svg');
                            svg.setAttribute('viewBox','0 0 24 24'); svg.setAttribute('width','18'); svg.setAttribute('height','18'); svg.setAttribute('fill','currentColor');
                            const path = document.createElementNS(ns,'path');
                            path.setAttribute('d','M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-2 1H8v-6c0-2.48 1.51-4.5 4-4.5s4 2.02 4 4.5v6z');
                            svg.appendChild(path);
                            subscribeBtn.appendChild(svg);
                            const span = document.createElement('span'); span.className = 'sub-text'; span.textContent = ' ' + labelText;
                            subscribeBtn.appendChild(span);
                        }
                        if(data.subscribed){
                            subscribeBtn.classList.remove('btn-primary'); subscribeBtn.classList.add('btn-accent');
                            makeBellLabel('Subscribed');
                        } else {
                            subscribeBtn.classList.remove('btn-accent'); subscribeBtn.classList.add('btn-primary');
                            makeBellLabel('Subscribe');
                        }
                    }
                    const subsCountEl = document.getElementById('subs-count');
                    if(subsCountEl && data.subs_count !== undefined) subsCountEl.textContent = data.subs_count;
                } else if(action === 'watch-later'){
                    const wlBtn = form.querySelector('.js-watch-later-btn') || document.querySelector('.js-watch-later-btn');
                    if(wlBtn && data.success){
                        // create safe svg element
                        const ns = 'http://www.w3.org/2000/svg';
                        function makeSvgPath(d){ const svg = document.createElementNS(ns,'svg'); svg.setAttribute('viewBox','0 0 24 24'); svg.setAttribute('width','18'); svg.setAttribute('height','18'); svg.setAttribute('fill','currentColor'); const p = document.createElementNS(ns,'path'); p.setAttribute('d', d); svg.appendChild(p); return svg; }
                        const clockPath = 'M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z';
                        while(wlBtn.firstChild) wlBtn.removeChild(wlBtn.firstChild);
                        if(data.in_watch_later){
                            wlBtn.classList.remove('btn-primary');
                            wlBtn.classList.add('btn-accent');
                            wlBtn.appendChild(makeSvgPath(clockPath));
                            const sp = document.createElement('span'); sp.textContent = ' Saved to Watch Later'; wlBtn.appendChild(sp);
                            // Update form action to remove
                            form.action = form.action.replace('/add/', '/remove/');
                        } else {
                            wlBtn.classList.remove('btn-accent');
                            wlBtn.classList.add('btn-primary');
                            wlBtn.appendChild(makeSvgPath(clockPath));
                            const sp = document.createElement('span'); sp.textContent = ' Watch Later'; wlBtn.appendChild(sp);
                            // Update form action to add
                            form.action = form.action.replace('/remove/', '/add/');
                        }
                    }
                } else if(action === 'toggle-playlist'){
                    if(data.success){
                        const btn = form.querySelector('.js-playlist-btn');
                        const isAdding = form.action.includes('/add/');
                        
                        if(isAdding){
                            // Changed to added state
                            while(btn.firstChild) btn.removeChild(btn.firstChild);
                            const ns='http://www.w3.org/2000/svg';
                            const svgAdd=document.createElementNS(ns,'svg'); svgAdd.setAttribute('viewBox','0 0 24 24'); svgAdd.setAttribute('width','18'); svgAdd.setAttribute('height','18'); svgAdd.setAttribute('fill','var(--accent)'); const pAdd=document.createElementNS(ns,'path'); pAdd.setAttribute('d','M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'); svgAdd.appendChild(pAdd);
                            btn.appendChild(svgAdd);
                            const txt = document.createTextNode(' ' + btn.textContent.trim()); btn.appendChild(txt);
                            form.action = form.action.replace('/add/', '/remove/');
                        } else {
                            // Changed to removed state
                            while(btn.firstChild) btn.removeChild(btn.firstChild);
                            const ns='http://www.w3.org/2000/svg';
                            const svgRem=document.createElementNS(ns,'svg'); svgRem.setAttribute('viewBox','0 0 24 24'); svgRem.setAttribute('width','18'); svgRem.setAttribute('height','18'); svgRem.setAttribute('fill','transparent'); svgRem.style.border='1px solid var(--text-sec)'; svgRem.style.borderRadius='2px';
                            btn.appendChild(svgRem);
                            const txt2 = document.createTextNode(' ' + btn.textContent.trim()); btn.appendChild(txt2);
                            form.action = form.action.replace('/remove/', '/add/');
                        }

                        // Update main save button
                        const saveBtn = document.getElementById('vf-save-btn');
                        if(saveBtn){
                            while(saveBtn.firstChild) saveBtn.removeChild(saveBtn.firstChild);
                            const ns='http://www.w3.org/2000/svg';
                            const svgSave=document.createElementNS(ns,'svg'); svgSave.setAttribute('viewBox','0 0 24 24'); svgSave.setAttribute('width','18'); svgSave.setAttribute('height','18'); svgSave.setAttribute('fill','currentColor'); const pSave=document.createElementNS(ns,'path'); pSave.setAttribute('d','M14 10H2v2h12v-2zm0-4H2v2h12V6zm4 8v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zM2 16h8v-2H2v2z'); svgSave.appendChild(pSave);
                            saveBtn.appendChild(svgSave);
                            const saveTxt = document.createElement('span');
                            if(data.is_saved_in_any){
                                saveTxt.textContent = ' Saved';
                                saveBtn.classList.remove('btn-primary'); saveBtn.classList.add('btn-accent');
                            } else {
                                saveTxt.textContent = ' Save';
                                saveBtn.classList.remove('btn-accent'); saveBtn.classList.add('btn-primary');
                            }
                            saveBtn.appendChild(saveTxt);
                        }
                    }
                } else if(action === 'comment'){
                    if(data.success && data.comment){
                        const list = document.getElementById('comments-list');
                        const div = document.createElement('div');
                        div.className = 'comment';
                        div.id = 'comment-' + data.comment.id;
                        div.style.cssText = 'display:flex; gap:10px; margin-bottom:20px; animation: fadeIn 0.3s ease;';
                        
                        // Build avatar node safely
                        const anchor = document.createElement('a');
                        anchor.href = data.comment.user_url || '#';
                        if(data.comment.profile_pic){
                            const img = document.createElement('img'); img.src = data.comment.profile_pic; img.className = 'avatar'; img.style.width = '40px'; img.style.height = '40px'; img.style.objectFit = 'cover';
                            anchor.appendChild(img);
                        } else {
                            const avatarDiv = document.createElement('div'); avatarDiv.className = 'avatar'; avatarDiv.style.width = '40px'; avatarDiv.style.height = '40px'; avatarDiv.textContent = data.comment.initial || '?';
                            anchor.appendChild(avatarDiv);
                        }
                        div.appendChild(anchor);
                        const main = document.createElement('div'); main.style.flex = '1';
                        const meta = document.createElement('div'); meta.style.marginBottom = '4px';
                        const userLink = document.createElement('a'); userLink.href = data.comment.user_url || '#'; userLink.style.fontWeight = 'bold'; userLink.style.fontSize = '0.9rem'; userLink.style.marginRight = '8px'; userLink.textContent = data.comment.user || 'User';
                        const dateSpan = document.createElement('span'); dateSpan.style.color = 'var(--text-sec)'; dateSpan.style.fontSize = '0.8rem'; dateSpan.textContent = data.comment.date || '';
                        meta.appendChild(userLink); meta.appendChild(dateSpan);
                        const p = document.createElement('p'); p.style.margin = '0'; p.style.fontSize = '0.95rem'; p.textContent = data.comment.content || '';
                        main.appendChild(meta); main.appendChild(p);
                        div.appendChild(main);
                        const right = document.createElement('div');
                        const delForm = document.createElement('form'); delForm.method = 'POST'; delForm.action = '/comment/' + (data.comment.id) + '/delete'; delForm.className = 'js-async-form'; delForm.dataset.action = 'delete-comment';
                        const delBtn = document.createElement('button'); delBtn.type = 'submit'; delBtn.className = 'btn'; delBtn.style.padding = '4px 8px'; delBtn.style.fontSize = '0.8rem'; delBtn.style.opacity = '0.7'; delBtn.title = 'Delete'; delBtn.textContent = '✕';
                        delForm.appendChild(delBtn); right.appendChild(delForm); div.appendChild(right);
                        
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
