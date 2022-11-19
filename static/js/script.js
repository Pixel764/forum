$(document).ready(function(){
    // Comment delete button
    const commentDeleteBtn = $('form[name=commentDeleteForm] > input[type=submit]')
    commentDeleteBtn.click(function(e){
        let answer = confirm('You sure want delete comment?')
        if (!answer){
            e.preventDefault()
        }
    })

    // Post delete button
    const postDeleteBtn = $('form[name=post_delete_form] > input[type=submit]')
    postDeleteBtn.click(function(e){
        let answer = confirm('You sure want delete this post?')
        if (!answer){
            e.preventDefault()
        }
    })

    // ajax request for post like
    const postLikeBtn = $('form[name=post_like_form] > input[name=like]')

    postLikeBtn.click(function(e){
        e.preventDefault()

        csrf = $('form[name=post_like_form] > input[name=csrfmiddlewaretoken]').val()

        $.ajax({
            url: window.location.href,
            cache: false,
            method: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf,
                'like': ''
            },
            dataType: 'json',
            success: function(data){
                postLikeBtn.attr({'value': `Like ${data.likes}`})
            },
            error: function(data){
                let loginURL = $('#auth_links > a[href*=login]').attr('href')
                window.location.replace(loginURL)
            }
        })
    })
})