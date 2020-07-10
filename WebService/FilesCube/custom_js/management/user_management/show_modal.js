/*
Author: Baixu
Date: 2020-06-24
Desc: 用户管理相关的模态框显示代码（新建用户、删除用户等）
 */

function show_del_user_modal(username){
    //弹出用于“删除用户”的模态框，username为在模态框中显示的待删除用户的用户名
    document.getElementById('del_user_username').value = username;
    $('#del_user_myModal').modal('show');
}

function show_new_user_modal(){
    alert('new_user');
    let volume_list = get_volume_list();
    let volume_paths_using_in_combobox = [];
    for(let i in volume_list){
        volume_paths_using_in_combobox.push({
            'value': volume_list[i]['volume_path'],
            'text': volume_list[i]['volume_path'],
        });
    }
    $('#new_user_volume').combobox('loadData', volume_paths_using_in_combobox)
    $('#new_user_myModal').modal('show');
}

function show_modify_user_modal(username, original_root_dir){
    document.getElementById('modify_user_username').value = username;
    document.getElementById('modify_user_original_root_dir').value = original_root_dir;
    $('#modify_user_myModal').modal('show');
}
