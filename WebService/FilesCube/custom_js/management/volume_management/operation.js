/*
Author: Baixu
Date: 2020-06-24
Desc: 卷管理相关的操作代码（新建卷、删除卷的AJAX代码，获取最新数据展示在volume_dg的代码）
 */

function display_volume_mapping() {
    console.log('display_volume_mapping');
    //let mkdir_path = document.getElementById('mkdir_path').value;
    //let mkdir_name = document.getElementById('mkdir_name').value;
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    return $.ajax({
        url: "/filescube/volume_management/display_volume_mapping/",
        type: "post",
        data: {"csrfmiddlewaretoken": csrf,},
        success: function (data) {
            //改变datagrid和tree中的展示状态
            data = JSON.parse(data);
            console.log("display_volume_mapping(),后端的回复");
            console.log(data['state']);
            console.log(data['details']);
            if (data['state'] === 'success') {
                let volume_list = [];
                for (var i in data['details']) {
                    let volume_type = '';
                    if (data['details'][i]['is_localhost'])
                        volume_type = 'localhost';
                    volume_list.push({
                        'volume_path': data['details'][i]['volume_path'],
                        'actual_path': data['details'][i]['actual_path'],
                        'size': data['details'][i]['size'],
                        'volume_type': volume_type
                    });
                }

                volume_list = JSON.stringify(volume_list);
                volume_list = eval(volume_list);
                console.log(volume_list);
                set_volume_list(volume_list);
                $('#volume_dg').datagrid('loadData',volume_list);
            } else {
                alert(data['details']);
                return '12345';
            }
        }
    });
}

//与后端交互、删除卷
function remove_volume()
{
    let path_in_hfs = document.getElementById('del_volume_path_in_hfs').value;
    let actual_path = document.getElementById('del_volume_actual_path').value;
    let is_localhost = false
    if(document.getElementById('del_volume_type').value==='localhost')
        is_localhost = true
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
            url:"/filescube/volume_management/remove_volume/",
            type:"post",
            data:{"path_in_hfs": path_in_hfs,
                "actual_path": actual_path,
                "is_localhost": is_localhost,
                "csrfmiddlewaretoken":csrf,},
            success:function (data) {
                //改变volume_dg中的展示状态
                data = JSON.parse(data);
                console.log("后端对于make_new_volume的回复");
                console.log(data);
                if(data['state']==='success'){
                    display_volume_mapping();
                }
                else{
                    alert(data['details']);
                }
            }
        });
}

//与后端交互、新增卷
function make_new_volume()
{
    let volume_name = document.getElementById('new_volume_path_in_hfs').value;
    let actual_path = document.getElementById('new_volume_actual_path').value;
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
            url:"/filescube/volume_management/make_new_volume/",
            type:"post",
            data:{"path_in_hfs": volume_name+'/',
                "actual_path": actual_path,
                "csrfmiddlewaretoken":csrf,},
            success:function (data) {
                //改变volume_dg中的展示状态
                data = JSON.parse(data);
                console.log("后端对于make_new_volume的回复");
                console.log(data);
                if(data['state']==='success'){
                    display_volume_mapping();
                }
                else{
                    alert(data['details']);
                }
            }
        });
}
