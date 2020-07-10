/*
Author: Baixu
Date: 2020-06-24
Desc: 卷管理相关的模态框显示代码（新建卷、删除卷等）
 */

function show_del_volume_modal(volume_path, actual_path){
    //弹出用于“删除卷”的模态框，volume_path和actual_path分别为待删除卷的在系统中的路径和所对应的实际路径
    //两者均用于在所弹出的模态框中展示
    document.getElementById('del_volume_path_in_hfs').value = volume_path;
    document.getElementById('del_volume_actual_path').value = actual_path
    $('#del_volume_myModal').modal('show');
}

function show_new_volume_modal(){
    $('#new_volume_myModal').modal('show');
}