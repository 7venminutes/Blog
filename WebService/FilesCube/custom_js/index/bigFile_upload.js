/*
Author: Baixu
Date: 2020-06-30
Desc: 将文件分片上传给服务器、以实现大文件传输、断点续传等功能
 */
var bigFileUploader;

function prepare_webUploader(file_path){
    /*
    配置上传组件webUploader, 向file_path中上传文件
    每次点开二级界面“上传文件”时都会调用该函数、配置webUploader中的相关参数
     */

    if(null == bigFileUploader)
        // 第一次调用该函数时 bigFileUploader还未被初始化，此时跳转到另外一个函数初始化并配置webUploader
        prepare_webUploader_when_bigFileUploader_not_existing(file_path)

    else{
        let task_id = WebUploader.Base.guid();//产生文件唯一标识符task_id
        bigFileUploader.option('formData', {
            mode: 0,
            task_id: task_id,
            file_path: file_path,
        });
        bigFileUploader.off('beforeFileQueued');
        bigFileUploader.on('beforeFileQueued', function() { // 开始上传时，调用该方法
            let have_access = false;
            $.ajax({
                type : "POST",
                url : "/filescube/tools/upload/check/",
                async: false,
                data : {
                    file_path: file_path,
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                },
                dataType : "json",
                success : function(response) {
                    have_access = response['haveAccess']
                }
            });
            alert('您没有权限向该目录下传输文件')
            return have_access;
        });
        bigFileUploader.off('uploadSuccess');
        bigFileUploader.on('uploadSuccess', function(file) { // 整个文件的所有分片都上传成功后，调用该方法
            var data = {
                'task_id': task_id,
                'filename': file.source['name'],
                'file_path': file_path,
            };
            $.get('/filescube/tools/upload_success', data);
            let progress_bar = $('.progress-bar');
            progress_bar.css('width', '100%');
            progress_bar.text('100%');
            progress_bar.addClass('progress-bar-success');
            progress_bar.text(file.source['name']+'上传完成');
            display_file_list(file_path);
        });
    }
}

function prepare_webUploader_when_bigFileUploader_not_existing(file_path){
    /*
    当bigFileUploader未被赋值时调用该函数，对webUploader进行配置
     */
    var fileMd5;
    $(document).ready(function() {
        let progress_bar = $('.progress-bar');
        var task_id = WebUploader.Base.guid(); // 产生文件唯一标识符task_id

        bigFileUploader = WebUploader.create({
            swf: './static/webuploader/Uploader.swf',
            server: '/filescube/tools/upload_part/', // 上传分片地址
            pick: '#picker',
            auto: true,
            chunked: true,
            chunkSize: 20 * 1024 * 1024,
            chunkRetry: 3,
            threads: 4,
            duplicate: true,
            formData: { // 上传分片的http请求中一同携带的数据
                mode: 0,
                task_id: task_id,
                file_path: file_path,
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
            },
        });
        bigFileUploader.on('beforeFileQueued', function() { // 开始上传时，调用该方法
            let have_access = false;
            $.ajax({
                type : "POST",
                url : "/filescube/tools/upload/check/",
                async: false,
                data : {
                    file_path: file_path,
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                },
                dataType : "json",
                success : function(response) {
                    have_access = response['haveAccess']
                }
            });
            if(!have_access){
                alert('您没有权限向该路径下传输文件');
            }
            return have_access;
        });
        bigFileUploader.on('fileQueued', function(file){
            //alert('file_already_queued');
            bigFileUploader.upload(file);
        });
        bigFileUploader.on('startUpload', function() { // 开始上传时，调用该方法
            progress_bar.css('width', '0%');
            progress_bar.text('0%');
            progress_bar.removeClass('progress-bar-danger');
            progress_bar.removeClass('progress-bar-success');
            progress_bar.addClass('active progress-bar-striped');
        });

        bigFileUploader.on('uploadProgress', function(file, percentage) { // 一个分片上传成功后，调用该方法
            progress_bar.css('width', percentage * 100 - 1 + '%');
            progress_bar.text(Math.floor(percentage * 100 - 1) + '%' + file.source['name']);
        });

        bigFileUploader.on('uploadSuccess', function(file) { // 整个文件的所有分片都上传成功后，调用该方法
            var data = {
                'task_id': task_id,
                'filename': file.source['name'],
                'file_path': file_path,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            };
            $.get('/filescube/tools/upload_success', data);
            progress_bar.css('width', '100%');
            progress_bar.text('100%');
            progress_bar.addClass('progress-bar-success');
            progress_bar.text(file.source['name']+'上传完成');
            display_file_list(file_path);
        });

        bigFileUploader.on('uploadError', function(file) { // 上传过程中发生异常，调用该方法
            progress_bar.css('width', '100%');
            progress_bar.text('100%');
            progress_bar.addClass('progress-bar-danger');
            progress_bar.text(file.source['name']+'上传失败');
        });

        bigFileUploader.on('uploadComplete', function(file) { // 上传结束，无论文件最终是否上传成功，该方法都会被调用
            progress_bar.removeClass('active progress-bar-striped');
        });
        progress_bar.css('width', '100%');
        progress_bar.text('您还未选择待上传的文件');


    });

    }
