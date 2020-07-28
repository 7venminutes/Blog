function show_transform_image(task_id, original_image_dir){
    let server_added_this_task = false;
    console.log('11111111111')
    console.log($('#style_selected').textbox('getText'));
    $.ajax({
        type: "POST",
        url: 'starry/submit_task/',
        async: false,
        data : {
            task_id: task_id,
            original_image_dir: original_image_dir,
            selected_style: $('#style_selected').textbox('getText'),
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
        },
        success: function(data){
            data = JSON.parse(data);
            server_added_this_task = data['success_established']
        }
    });
    if(!server_added_this_task){
        alert('服务器添加任务失败');
        return;
    }
    $.ajax({
        type: "GET",
        url: 'starry/how_many_unfinished_tasks_now/',
        async: false,
        success: function(data){
            data = JSON.parse(data);
            alert('图像风格迁移任务成功添加，前方排队还有'+data['task_num']+'人')
        }
    });
    let task_finished = false;
    let time_interval = 1000;  //轮询间隔1s
    while(!task_finished){
        $.ajax({
            type: "POST",
            url: 'starry/give_me_my_task/',
            async: false,
            data: {
                task_id: task_id,
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
            },
            success: function(response){
                response = JSON.parse(response);
                console.log(response['state']);
                console.log('');
                switch (response['state']) {
                    case 'success':
                        task_finished = true;
                        document.getElementById('image_after_transformed').src =
                            'http://' + window.location.host + '/filescube/' + response['image_dir'];
                        break;
                    case 'failed':
                        task_finished = true;
                        alert('任务失败');
                        break;
                    case 'processing':
                        console.log('开始处理您的任务，很快就好了');
                        break;
                    case 'new':
                        console.log('任务成功添加，排队中');
                        break;
                    case 'not_found':
                        task_finished = true;
                        alert('Ooops，您这次递交的任务被弄丢了，服务器找不到该任务');
                        break;
                }
            }
        });
        pause_sleep(time_interval);
    }
}
