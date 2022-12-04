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

    // ajax request for post like and dislike
    let loginURL = $('#auth_links > a[href*=login]').attr('href')
    const csrf = $('form[name=post_rating_form] > input[name=csrfmiddlewaretoken]').val()

    const postLikeBtn = $('form[name=post_rating_form] > input[name=like]')
    postLikeBtn.click(function(e){
        e.preventDefault()

        $.ajax({
            url: postLikeBtn.attr('action'),
            cache: false,
            method: 'GET',
            data: {
                'csrfmiddlewaretoken': csrf,
            },
            dataType: 'json',
            success: function(data){
                postDislikeBtn.attr({'value': `↓ ${data.dislikes}`})
                postLikeBtn.attr({'value': `↑ ${data.likes}`})
            },
            error: function(data){
                window.location.replace(loginURL)
            }
        })
    })

    const postDislikeBtn = $('form[name=post_rating_form] > input[name=dislike]')
    postDislikeBtn.click(function(e){
        e.preventDefault()

        $.ajax({
            url: postDislikeBtn.attr('action'),
            cache: false,
            method: 'GET',
            data: {
                'csrfmiddlewaretoken': csrf,
            },
            dataType: 'json',
            success: function(data){
                postLikeBtn.attr({'value': `↑ ${data.likes}`})
                postDislikeBtn.attr({'value': `↓ ${data.dislikes}`})
            },
            error: function(data){
                window.location.replace(loginURL)
            }
        })
    })
})