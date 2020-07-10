/*
Author: Baixu
Date: 2020-06-23
Desc: 首页中所有跟模态框交互的代码
 */
function show_task_window(){
    $('#task-window').window('open');
}

function show_upload_modal(upload_path){
    //显示上传文件的模态框, upload_path为希望模态框“上传路径”一栏中显示的值
    set_upload_path( upload_path );
       prepare_webUploader(upload_path);
    let upload_window = $('#upload_window')
    upload_window.window('setTitle', '文件上传(上传路径：'+upload_path+')');
    upload_window.window('open');
}

function show_mkdir_modal(mkdir_path){
    //显示新建文件夹的模态框，mkdir_path为对应模态框中“新建路径”一栏中显示的值
    document.getElementById('mkdir_path').value = mkdir_path;
    $('#mkdir_myModal').modal('show');
}

function show_download_modal(download_path, download_filename){
    /*显示用于下载文件的模态框，
    download_path为模态框中所显示的下载文件所在的文件夹
    download_filename为模态框中所显示的下载文件的文件名*/
    document.getElementById('download_path').value = download_path;
    document.getElementById('download_filename').value = download_filename;
    document.getElementById('downloadurl').value =
        window.location.host + '/filescube/tools/download/' + download_path + download_filename;
    $('#download_myModal').modal('show');
}

function show_remove_file_modal(del_path, del_filename, file_type){
    /*显示用于删除目录项的模态框
    del_path为待删除目录项的所在路径
    del_filename为待删除目录项的名称
    file_type表示待删除的目录项为文件还是文件夹
    三个参数均用于在模态框中显示*/
    document.getElementById('del_myModal_path').value = del_path;
    document.getElementById('del_myModal_name').value = del_filename;
    document.getElementById('del_myModal_file_type').value = file_type;
    $('#del_myModal').modal('show');
}

function show_rename_or_move_modal(curr_path, curr_filename, file_type){
    /*
    显示用于移动目录项或重命名目录项的模态框（这两项操作共用一个模态框）
    curr_path为目录项当前所处的路径
    curr_filename为目录项当前的名称
    file_type为目录项的类型，文件('file')还是文件夹('dir')
     三个参数均用于在模态框中显示*/
    document.getElementById('rename_myModal_curr_path').value = curr_path;
    document.getElementById('rename_myModal_curr_name').value = curr_filename;
    document.getElementById('rename_myModal_file_type').value = file_type;
    //目标路径和文件新名称也用curr_path和curr_filename进行初始化
    document.getElementById('rename_myModal_des_path').value = curr_path;
    document.getElementById('rename_myModal_des_name').value = curr_filename;
    $('#rename_myModal').modal('show');
}
