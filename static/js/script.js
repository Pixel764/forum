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
        let answer = confirm('You sure want delete post?')
        if (!answer){
            e.preventDefault()
        }
    })

    // ajax request for post like and dislike
    let loginURL = $('#auth_links > a[href*=login]').attr('href')

    function loginURLRedirect(status){
        if (status == 403 && loginURL){
            window.location.replace(loginURL)
        }
        else {
            console.log(status)
        }
    }

    const csrf = $('form[name=post_rating_form] > input[name=csrfmiddlewaretoken]').val()

    const postLikeBtn = $('input[name=post_like]')
    postLikeBtn.click(function(e){
        e.preventDefault()

        $.ajax({
            url: postLikeBtn.attr('action'),
            cache: false,
            method: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf,
            },
            dataType: 'json',
            success: function(data){
                postDislikeBtn.attr({'value': `↓ ${data.dislikes}`})
                postLikeBtn.attr({'value': `↑ ${data.likes}`})
            },
            error: function(data){
                loginURLRedirect(data.status)
            }
        })
    })

    const postDislikeBtn = $('input[name=post_dislike]')
    postDislikeBtn.click(function(e){
        e.preventDefault()

        $.ajax({
            url: postDislikeBtn.attr('action'),
            cache: false,
            method: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf,
            },
            dataType: 'json',
            success: function(data){
                postLikeBtn.attr({'value': `↑ ${data.likes}`})
                postDislikeBtn.attr({'value': `↓ ${data.dislikes}`})
            },
            error: function(data){
                loginURLRedirect(data.status)
            }
        })
    })

    // ajax request for comment like and dislike
    let commentLikeButtons = $('input[name=comment_like]')
    commentLikeButtons.click(function(e){
        e.preventDefault()
        let parent = $(this).parent()

        $.ajax({
            url: $(this).attr('action'),
            cache: false,
            method: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf,
            },
            dataType: 'json',
            success: function(data){
                parent.children('input[name=comment_like]').attr({'value': `↑ ${data.likes}`})
                parent.children('input[name=comment_dislike]').attr({'value': `↓ ${data.dislikes}`})
            },
            error: function(data){
                loginURLRedirect(data.status)
            }
        })
    })

    let commentDislikeButtons = $('form[name=comment_rating_form] > input[name=comment_dislike]')
    commentDislikeButtons.click(function(e){
        e.preventDefault()
        let parent = $(this).parent()

        $.ajax({
            url: $(this).attr('action'),
            cache: false,
            method: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf,
            },
            dataType: 'json',
            success: function(data){
                parent.children('input[name=comment_like]').attr({'value': `↑ ${data.likes}`})
                parent.children('input[name=comment_dislike]').attr({'value': `↓ ${data.dislikes}`})
            },
            error: function(data){
                window.location.replace(loginURL)
            }
        })
    })
})