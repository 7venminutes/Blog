/*
Author: Baixu
Date: 2020-06-22
Desc: index.html(网站首页)中对文件系统中各个目录项进行增删改查的AJAX提交代码
 */
//依赖脚本：custom_js/index/global_variables.js

function download_single_file(){
    /*
    点击下载模态框中的下载按钮之后触发该函数、下载downloadurl指向的资源
     */
    window.open('http://'+document.getElementById('downloadurl').value,'_blank');
}

function back(){
    console.log('click_back');
    let file_dir = get_data_dir();
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url:"/filescube/index/back_to_parent_dir/",
        type:"post",
        data:{"file_dir":file_dir,
            'csrfmiddlewaretoken': csrf,},
        success:function (data_list) {
            // access_list->json字符串
            data_list = JSON.parse(data_list);
            console.log(data_list);
            if(data_list['have_access']===true){
                if(data_list['have_parent']===true){
                    set_data_list(data_list['file_list']);
                    set_data_dir(data_list['new_current_path']);
                    document.getElementById('path_to_go').value = data_list['new_current_path'];
                    /*为datagrid fileInfo_dataGrid载入数据*/
                    let file_list = []
                    let length = 0
                    for(let i in data_list['file_list']){
                        if(data_list['file_list'][i]['file_type']==='dir'){
                            length = file_list.push({'icon':'<img src=\''+get_folder_icon_dir()+'\' alt="文件夹图标">', 'type':data_list['file_list'][i]['file_type'],
                                'name':data_list['file_list'][i]['file_name'],'size':data_list['file_list'][i]['file_size']});
                        }
                        else
                            length = file_list.push({'icon':'<img src=\''+get_file_icon_dir()+'\' alt="文件图标">','type':data_list['file_list'][i]['file_type'],
                                'name':data_list['file_list'][i]['file_name'],'size':data_list['file_list'][i]['file_size']});
                    }
                    console.log(length)
                    fileInfo_dataGrid.datagrid('loadData',file_list);
                }
                else{
                    alert('已经是当前文件夹的根目录了');
                }
            }
            else {
                alert('无法返回上级目录，无权限');
            }
        }
    });
}

function rename_or_move(){
    console.log("rename or move");
    let file_type = document.getElementById('rename_myModal_file_type').value;
    console.log(file_type);
    let curr_path = document.getElementById('rename_myModal_curr_path').value;
    let curr_name = document.getElementById('rename_myModal_curr_name').value;
    let des_path = document.getElementById('rename_myModal_des_path').value;
    let des_name = document.getElementById('rename_myModal_des_name').value;
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url:"/filescube/index/rename_or_move/",
        type:"post",
        data:{"file_type":file_type,
            "curr_path":curr_path,
            "curr_name":curr_name,
            "des_path":des_path,
            "des_name":des_name,
            "csrfmiddlewaretoken":csrf},
        success:function(data){
            data = JSON.parse(data);
            if(data['state'] === 'failed')
                alert(data['details']);
            else{
                let node = navigationTree.tree('find',data['details']['file_id']);
                let new_parent_node = navigationTree.tree('find',data['details']['new_parent_id']);
                if(node!=null)
                    navigationTree.tree('remove',node.target);
                if(new_parent_node!=null)
                    navigationTree.tree('reload',new_parent_node.target)
                //刷新datagrid中的数据
                click_button('go_button', get_data_dir());
            }
        }
    });
}

function make_dir(){
    console.log('make_dir');
    let mkdir_path = document.getElementById('mkdir_path').value;
    let mkdir_name = document.getElementById('mkdir_name').value;
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url:"/filescube/index/make_dir/",
        type:"post",
        data:{"mkdir_path":mkdir_path,
            "mkdir_name":mkdir_name,
            "csrfmiddlewaretoken":csrf,},
        success:function (data) {
            //改变datagrid和tree中的展示状态
            data = JSON.parse(data);
            console.log("点击mkdir后，后端的回复");
            console.log(data);
            if(data['state']==='success'){
                let file_info = data['file_info'];
                let node = navigationTree.tree('find', file_info['file_parent_id']);
                if(node != null)
                    navigationTree.tree('reload', node.target);
                //刷新datagrid中的数据
                click_button('go_button', get_data_dir());
            }
            else{
                alert(data['details']);
            }
        }
    });
}

function remove_file(){
    console.log('remove_file');
    let remove_path = document.getElementById('del_myModal_path').value;
    let remove_name = document.getElementById('del_myModal_name').value;
    let remove_file_type = document.getElementById('del_myModal_file_type').value;
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url:"/filescube/index/remove_file/",
        type:"post",
        data:{"remove_path":remove_path,
            "remove_name":remove_name,
            "remove_file_type":remove_file_type,
            "csrfmiddlewaretoken":csrf,},
        success:function (data) {
            //改变datagrid和tree中的展示状态
            data = JSON.parse(data);
            console.log("点击remove后，后端的回复");
            console.log(data);
            if(data['state']==='success'){
                let remove_file_id = data['remove_file_id'];
                let node = navigationTree.tree('find', remove_file_id);
                if(node != null)
                    navigationTree.tree('remove',node.target);
                //刷新datagrid中的数据
                display_file_list(get_data_dir());
            }
            else{
                alert(data['details']);
            }
        }
    });
}

function display_file_list(dir){
    //在fileInfo_dataGrid中展示某路径下的目录项信息，dir为待查询路径
    console.log('click_go');
    let file_dir = dir;
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url:"/filescube/index/display_file_list/",
        type:"post",
        data:{"file_dir":file_dir,
            'csrfmiddlewaretoken': csrf,},
        success:function (data_list) {
            // access_list->json字符串
            data_list = JSON.parse(data_list);
            console.log('点击go之后从后端拿来的数据');
            console.log(data_list);
            if(data_list['have_access']===true){
                if(data_list['dir_exist']===true){
                    set_data_list(data_list['file_list']);
                    if(file_dir.charAt(file_dir.length-1)!=='/')
                        file_dir = file_dir + '/';
                    set_data_dir(file_dir);
                    document.getElementById('path_to_go').value = file_dir;
                    /*为datagrid fileInfo_dataGrid载入数据*/
                    let file_list = []
                    let length = 0
                    for(let i in data_list['file_list']){
                        if(data_list['file_list'][i]['file_type']==='dir'){
                            console.log(get_folder_icon_dir());
                            length = file_list.push({'icon':'<img src=\''+get_folder_icon_dir()+'\' alt="文件夹图标">','type':data_list['file_list'][i]['file_type'],
                                'name':data_list['file_list'][i]['file_name'],'size':data_list['file_list'][i]['file_size']});
                        }
                        else
                            length = file_list.push({'icon':'<img src=\''+get_file_icon_dir()+'\' alt="文件图标">','type':data_list['file_list'][i]['file_type'],
                                'name':data_list['file_list'][i]['file_name'],'size':data_list['file_list'][i]['file_size']});
                    }
                    console.log('即将load进datagrid的数据');
                    console.log(file_list);
                    fileInfo_dataGrid.datagrid('loadData',file_list);
                }
                else{
                    document.getElementById('path_to_go').value = get_data_dir();
                    alert('路径不存在');
                }
            }
            else {
                document.getElementById('path_to_go').value = get_data_dir();
                alert('无该目录下的访问权限');
            }
        }
    });
}

function go_to(file_dir) {
    display_file_list(file_dir);
}

function preview_txt_file(file_dir){
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url:"/filescube/tools/txt-preview/",
        type:"post",
        data:{"file_dir":file_dir,
            'csrfmiddlewaretoken': csrf,},
        success:function (raw_data) {
            let server_response = JSON.parse(raw_data);
            if(server_response['result'] === 'success'){
                let new_windows_id = get_a_file_windows_id();
                //console.log(file_preview_windows_status);
                var new_file_preview_window =
                    '<div id="file-preview-window'+new_windows_id+'" class="easyui-window" title="Modal Window"\n' +
                    '         data-options="closed:true" style="width:500px;height:200px;padding:10px;">\n' +
                    '<div class="easyui-layout" data-options="fit:true">' +
                    '<div data-options="region:\'center\'">\n' +
                    '        <input id="txt-preview-textbox'+new_windows_id+'" class="easyui-textbox"\n' +
                    '               data-options="multiline:true, fit:true">\n' +
                    '</div>' +
                    '<div data-options="region:\'west\'" style="width:33px">' +
                    '        <a class="easyui-linkbutton" data-options="iconCls:\'icon-save\'" ' +
                    '         onclick="save_file(\''+new_windows_id+'\')"></a>' +
                    '</div></div>' +
                    '</div>';
                $(new_file_preview_window).appendTo('#file-windows-container');
                $.parser.parse('#file-preview-window' + new_windows_id);
                let file_preview_window = $('#file-preview-window' + new_windows_id);
                file_preview_window.window({
                    draggable: true,
                    minimizable: false,
                    title: file_dir,
                    onClose: function(){
                        recycle_a_file_windows_id(new_windows_id);
                        file_preview_window.window('destroy');
                    },
                });

                $('#txt-preview-textbox' + new_windows_id).textbox('setText', server_response['details']);

                file_preview_window.window('setTitle', file_dir);
                file_preview_window.window('open');

            }
            else
                alert(server_response['details']);
        }
    });
}

function save_file(file_window_id){
    //向服务器提交file_window_id窗口中编辑后的文件
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    let file_dir = $('#file-preview-window'+file_window_id).window('options')['title'];
    let file_content = $('#txt-preview-textbox' + file_window_id).textbox('getText');
    console.log(file_content);
    $.ajax({
        url:"/filescube/tools/save-txt/",
        type:"post",
        data:{"file_dir":file_dir,
            'file_content': file_content,
            'csrfmiddlewaretoken': csrf,},
        success: function(data){
            let server_response = JSON.parse(data);
            if(server_response['state']==='success')
                alert(server_response['details']);
            else
                alert(server_response['details']);
        }
    });
}
